"""Self-test (Layer 3): deterministic checks behind TESTPLAN.md.

    python tools/selftest.py            # unit/contract checks (no network)
    python tools/selftest.py --network  # also probe the live LLM link

Exit code 0 = all ran checks passed.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import TMP_DIR, load_settings, save_settings  # noqa: E402
from tools import enforce_canvas as canvas_tool  # noqa: E402
from tools import generate_backgrounds as bg_tool  # noqa: E402
from tools import watermark as wm_tool  # noqa: E402
from tools.composite import build_product_layer, composite  # noqa: E402
from tools.ingest import ingest, validate  # noqa: E402
from tools.lib.errors import JobFailed  # noqa: E402
from tools.lib.imaging import trim_alpha  # noqa: E402
from tools.lib.scenes import SCENE_IDS, get_scene  # noqa: E402
from tools.segment import segment  # noqa: E402
from tools.verify import verify  # noqa: E402

WORK = Path(TMP_DIR) / "selftest"
SAMPLE = ROOT / "Input" / "Test.JPG"
CANVAS = {"width": 2160, "height": 3840}
TEST_CANVAS = {"width": 540, "height": 960}  # small canvas keeps the tool tests fast

RESULTS: list[tuple[str, bool, str]] = []


def check(tid: str, name: str, fn) -> None:
    try:
        detail = fn() or ""
        RESULTS.append((tid, True, detail))
        print(f"  PASS  {tid:5s} {name}  {detail}")
    except AssertionError as exc:
        RESULTS.append((tid, False, str(exc)))
        print(f"  FAIL  {tid:5s} {name}  {exc}")
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((tid, False, f"{type(exc).__name__}: {exc}"))
        print(f"  ERROR {tid:5s} {name}  {type(exc).__name__}: {exc}")
        traceback.print_exc()


def expect_fail(fn, kind: str) -> str:
    try:
        fn()
    except JobFailed as exc:
        assert exc.kind == kind, f"expected JobFailed[{kind}] got [{exc.kind}]"
        return f"raised {kind}"
    raise AssertionError(f"expected JobFailed[{kind}], nothing raised")


def make_bg(scene, canvas, seed, path):
    img = bg_tool.render_local(scene, (canvas["width"], canvas["height"]), seed)
    img.save(path)
    return path


def main(network: bool) -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    print("Instagram-Photo-Creator · self-test\n")

    # ---- ingest -----------------------------------------------------------
    print("ingest")
    check("T-01", "accepts a valid JPEG", lambda: (
        lambda r: f"{r['width']}x{r['height']} sha256:{r['sha256'][:8]}")(
        ingest(SAMPLE, WORK / "t01")))

    def t02():
        bad = WORK / "bad.gif"
        bad.write_bytes(b"GIF89a")
        return expect_fail(lambda: validate(bad), "BadExtension")
    check("T-02", "rejects a bad extension", t02)

    def t03():
        big = WORK / "big.jpg"
        big.write_bytes(b"\xff\xd8" + b"0" * (16 * 1024 * 1024))
        return expect_fail(lambda: validate(big), "InputTooLarge")
    check("T-03", "rejects >15 MB", t03)

    def t04():
        small = WORK / "small.png"
        Image.new("RGB", (400, 400), (200, 200, 200)).save(small)
        return expect_fail(lambda: ingest(small, WORK / "t04"), "InputTooSmall")
    check("T-04", "rejects a tiny image", t04)

    def t05():
        src = Image.new("RGB", (1200, 1600))
        for y in range(1600):
            for x in (0, 400, 800):
                src.putpixel((x, y), (255, 0, 0) if y < 800 else (0, 0, 255))
        exif = Image.Exif()
        exif[0x0112] = 6
        p = WORK / "exif.jpg"
        src.save(p, exif=exif)
        r = ingest(p, WORK / "t05")
        assert (r["width"], r["height"]) == (1600, 1200), f"not transposed: {r['width']}x{r['height']}"
        return f"1200x1600 -> {r['width']}x{r['height']}"
    check("T-05", "honours EXIF rotation", t05)

    # ---- segment ----------------------------------------------------------
    print("segment")
    seg = {}
    check("T-06", "non-empty matte on the sample", lambda: (
        lambda r: f"coverage={r['coverage']:.4f} method={r['method']}")(
        seg.update(segment(ingest(SAMPLE, WORK / "t06")["path"], WORK / "t06")) or seg))

    def t07():
        rgba = Image.open(seg["product_rgba"]).convert("RGBA")
        src = Image.open(WORK / "t06" / "source_srgb.png").convert("RGB")
        mask = np.asarray(rgba.split()[-1]) > 250
        a = np.asarray(src)[mask]
        b = np.asarray(rgba.convert("RGB"))[mask]
        assert a.shape[0] > 0, "no solid product pixels"
        assert np.array_equal(a, b), "product RGB was altered"
        return f"{a.shape[0]} solid px identical"
    check("T-07", "keeps original product RGB", t07)

    def t08():
        blank = WORK / "blank.png"
        Image.new("RGB", (1200, 1600), (255, 255, 255)).save(blank)
        return expect_fail(lambda: segment(blank, WORK / "t08"), "MaskEmpty")
    check("T-08", "raises on an empty matte", t08)

    # ---- scenes / backgrounds ---------------------------------------------
    print("scenes & backgrounds")
    scene = get_scene("marble")

    def t09():
        a = bg_tool.render_local(scene, (540, 960), 42)
        b = bg_tool.render_local(scene, (540, 960), 42)
        assert np.array_equal(np.asarray(a), np.asarray(b)), "not deterministic"
        return "seed 42 → identical"
    check("T-09", "renderer is deterministic", t09)

    scene_thumbs = {}

    def t10():
        sizes = []
        for sid in SCENE_IDS:
            img = bg_tool.render_local(get_scene(sid), (540, 960), 7)
            assert img.size == (540, 960), img.size
            scene_thumbs[sid] = np.asarray(img.resize((16, 16)), np.float32) / 255.0
            sizes.append(f"{sid}:{img.size[0]}x{img.size[1]}")
        return " ".join(sizes)
    check("T-10", "styled sets at exact size", t10)

    def t11():
        ids = list(scene_thumbs)
        worst = min(float(np.abs(scene_thumbs[a] - scene_thumbs[b]).mean())
                    for i, a in enumerate(ids) for b in ids[i + 1:])
        assert worst > 0.02, f"scenes too similar (min thumbnail L1 {worst:.4f})"
        return f"4 distinct materials, min thumbnail L1 {worst:.3f}"
    check("T-11", "the four sets are materially distinct", t11)

    # ---- composite / canvas / watermark ------------------------------------
    print("composite · canvas · watermark")
    state = {}

    def t12():
        state["layer"] = build_product_layer(seg["product_rgba"], TEST_CANVAS, scene)
        trimmed = trim_alpha(Image.open(seg["product_rgba"]).convert("RGBA"))
        src_ar = trimmed.width / trimmed.height
        out_ar = state["layer"].width / state["layer"].height
        assert abs(src_ar - out_ar) / src_ar < 0.001, f"aspect drifted {src_ar} -> {out_ar}"
        return f"aspect {src_ar:.4f} -> {out_ar:.4f}"
    check("T-12", "uniform scale, aspect preserved", t12)

    def t13():
        out = canvas_tool.enforce_canvas(Image.new("RGB", (1000, 1000), (10, 20, 30)), CANVAS)
        assert out.size == (2160, 3840), out.size
        return f"1000x1000 -> {out.size[0]}x{out.size[1]}"
    check("T-13", "canvas is exact, no stretch", t13)

    def t14():
        img = Image.new("RGB", (2160, 3840), (240, 240, 240))
        target = 0.15
        out, bbox = wm_tool.add_watermark(img, "@meraki.by.ankita", size_pct=target)
        w = bbox[2] - bbox[0]
        assert 0 < w <= int(0.35 * 2160), f"watermark width {w} beyond the 35% cap"
        assert abs(w - target * 2160) <= 0.03 * 2160, \
            f"watermark width {w}px not near target {int(target * 2160)}px"
        state["wm_bbox"] = bbox
        return f"bbox={bbox} width={w}px ({w / 2160:.1%})"
    check("T-14", "watermark drawn, sized to target", t14)

    def t15():
        bg = make_bg(scene, TEST_CANVAS, 11, WORK / "t15_bg.png")
        composed, pos = composite(bg, state["layer"], TEST_CANVAS, scene)
        m = verify(TEST_CANVAS, composed, state["layer"], pos,
                   seg["coverage"], state["wm_bbox"])
        assert m["verdict"] == "pass"
        return f"ΔE={m['deltaE_mean']} SSIM={m['ssim_masked']}"
    check("T-15", "passes a faithful composite", t15)

    def t16():
        bg = make_bg(scene, TEST_CANVAS, 12, WORK / "t16_bg.png")
        layer = state["layer"]
        arr = np.clip(np.asarray(layer.convert("RGB"), np.float32) * 1.35, 0, 255)
        drifted = Image.merge("RGBA", (*Image.fromarray(arr.astype(np.uint8)).split(),
                                       layer.split()[-1]))
        composed, pos = composite(bg, drifted, TEST_CANVAS, scene)
        return expect_fail(lambda: verify(TEST_CANVAS, composed, layer, pos,
                                          seg["coverage"], state["wm_bbox"]), "ColorDrift")
    check("T-16", "fails closed on colour drift", t16)

    def t17():
        layer = state["layer"]
        with_refl = make_bg(scene, TEST_CANVAS, 13, WORK / "t17_bg.png")
        img_a, pos = composite(with_refl, layer, TEST_CANVAS, scene)
        no_refl = {**scene, "reflection": None}
        img_b, _ = composite(with_refl, layer, TEST_CANVAS, no_refl)

        y = pos["base_y"] + 3
        box = (pos["left"], y, pos["left"] + layer.width, min(TEST_CANVAS["height"], y + 60))
        a = np.asarray(img_a.crop(box), np.float32)
        b = np.asarray(img_b.crop(box), np.float32)
        peak = float(np.abs(a - b).max())
        assert peak > 3.0, f"reflection contributed almost nothing (peak Δ {peak:.3f})"
        return f"mirrored floor copy below the base (peak Δ {peak:.0f})"
    check("T-17", "glossy scenes reflect the product", t17)

    def t18():
        from tools.export import export
        finals = []
        for i, sid in enumerate(SCENE_IDS, start=1):
            finals.append({"index": i, "scene_id": sid,
                           "image": Image.new("RGB", (2160, 3840), (30 * i, 40, 60)),
                           "metrics": {"deltaE_mean": 0.5, "ssim_masked": 0.99},
                           "verdict": "pass"})
        r = export("selftest_export", finals, {"job_id": "selftest_export"}, out_root=WORK)
        files = sorted(p.name for p in Path(r["out_dir"]).glob("*.jpg"))
        assert len(files) == 4, files
        assert Path(r["manifest"]).exists() and Path(r["zip"]).exists()
        return f"{len(files)} jpg + manifest + zip"
    check("T-18", "export writes 4 JPEGs + manifest + ZIP", t18)

    # ---- config -----------------------------------------------------------
    print("config")

    def t19():
        before = load_settings()["llm"]["api_key"]
        after = save_settings({"llm": {"api_key": ""}})["llm"]["api_key"]
        assert before == after, "empty patch clobbered the key"
        return "empty api_key patch is a no-op"
    check("T-19", "empty key patch never clobbers", t19)

    def t20():
        import os
        p = Path(os.environ.get("U2NET_HOME", ""))
        assert str(ROOT) in str(p), f"U2NET_HOME outside project: {p}"
        return str(p.relative_to(ROOT))
    check("T-20", "model weights contained in-project", t20)

    # ---- optional live link ------------------------------------------------
    if network:
        print("network")
        from tools.llm_client import describe_image_model, test_connection

        def t42():
            r = test_connection()
            assert r["ok"], r.get("error")
            return f"{r['model']} {r['reply']} {r['latency_ms']}ms"
        check("T-21", "test connection succeeds", t42)

        def t43():
            r = test_connection({"api_key": "definitely-not-a-real-key"})
            assert not r["ok"], "a bogus key was accepted"
            return f"rejected with kind={r['kind']}"
        check("T-22", "bad key is rejected", t43)

        def t44():
            r = describe_image_model()
            return f"image model {'available' if r['ok'] else 'quota-blocked → local fallback'}"
        check("T-23", "image-model quota is reported", t44)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main("--network" in sys.argv))
