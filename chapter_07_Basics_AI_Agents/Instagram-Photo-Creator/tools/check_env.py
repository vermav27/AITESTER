"""Phase 2 handshake (Layer 3): validate configuration + live-test the LLM link.

    python tools/check_env.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import load_settings, mask_key  # noqa: E402
from tools.llm_client import describe_image_model, test_connection  # noqa: E402
from tools.lib.scenes import SCENE_IDS  # noqa: E402


def main() -> int:
    s = load_settings()
    print("Settings")
    print(f"  provider           : {s['llm']['provider']}")
    print(f"  api_key            : {mask_key(s['llm']['api_key']) or '(missing)'}")
    print(f"  base_url           : {s['llm']['base_url']}")
    print(f"  text_model         : {s['llm']['text_model']}")
    print(f"  image_model        : {s['llm']['image_model']}")
    print(f"  background_provider: {s['background_provider']}")
    print(f"  brand handle       : {s['brand']['handle']}")
    print(f"  canvas             : {s['canvas']['width']}x{s['canvas']['height']}")
    print(f"  scenes             : {', '.join(SCENE_IDS)}")

    print("\nLink checks")
    text = test_connection()
    print(f"  text model   : {'OK' if text['ok'] else 'FAIL'} "
          f"({text.get('latency_ms')} ms) {text.get('reply') or text.get('error')}")
    img = describe_image_model()
    print(f"  image model  : {'OK' if img['ok'] else 'UNAVAILABLE'} "
          f"{img.get('model')} {'' if img['ok'] else '→ ' + str(img.get('error'))}")

    ok = s["llm"]["api_key"] != ""
    print("\nRESULT:", "environment ready" if ok else "FAILED - no API key")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
