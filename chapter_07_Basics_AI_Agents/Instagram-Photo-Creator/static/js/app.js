/* Layer 0 client: upload -> poll -> results, plus settings actions. No pixel work here. */
(function () {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const SCENES = window.SCENES || [];
  const sceneName = (id) => (SCENES.find((s) => s.id === id) || {}).name || id;

  /* ---------------------------------------------------------------- studio */

  const form = $("#upload-form");
  if (form) {
    const input = $("#image");
    const drop = $("#drop");
    const preview = $("#preview");
    const dropLabel = $("#drop-label");
    const errorBox = $("#form-error");
    const goBtn = $("#go");
    const progressPanel = $("#progress-panel");
    const resultsPanel = $("#results-panel");
    const barFill = $("#bar-fill");
    const stageName = $("#stage-name");
    const stageMsg = $("#stage-msg");
    const stagesEl = $("#stages");
    const grid = $("#grid");
    const resultsMeta = $("#results-meta");
    const downloadAll = $("#download-all");
    const recreateBtn = $("#recreate");

    let poller = null;

    const showError = (msg, isError) => {
      errorBox.hidden = !msg;
      errorBox.textContent = msg || "";
      errorBox.className = "hint" + (isError ? " err" : " ok");
    };

    const bindFile = (file) => {
      if (!file) return;
      input.files = (() => {
        const dt = new DataTransfer();
        dt.items.add(file);
        return dt.files;
      })();
      dropLabel.textContent = file.name;
      preview.src = URL.createObjectURL(file);
      preview.hidden = false;
      showError("");
    };

    input.addEventListener("change", () => bindFile(input.files[0]));
    ["dragenter", "dragover"].forEach((ev) =>
      drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("hot"); }));
    ["dragleave", "drop"].forEach((ev) =>
      drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("hot"); }));
    drop.addEventListener("drop", (e) => bindFile(e.dataTransfer.files[0]));

    const setStage = (stage) => {
      stagesEl.querySelectorAll("li").forEach((li) => {
        const order = ["ingest", "segment", "generate", "composite", "canvas", "verify", "export"];
        const mine = order.indexOf(li.dataset.stage);
        const now = order.indexOf(stage);
        li.classList.toggle("done", now > mine && stage !== "done");
        li.classList.toggle("active", li.dataset.stage === stage);
      });
      if (stage === "done") stagesEl.querySelectorAll("li").forEach((li) => {
        li.classList.remove("active"); li.classList.add("done");
      });
    };

    const renderResults = (job, data) => {
      grid.innerHTML = "";
      (data.outputs || []).forEach((o) => {
        const m = o.metrics || {};
        const card = document.createElement("article");
        card.className = "card";
        card.innerHTML =
          '<img class="thumb" src="/result/' + job + "/" + o.index + '" alt="' + sceneName(o.scene_id) + '" loading="lazy" />' +
          '<div class="body">' +
            '<div class="title"><span>' + String(o.index).padStart(2, "0") + " · " + sceneName(o.scene_id) + '</span>' +
            '<span class="badge">' + (o.verdict || "pass") + "</span></div>" +
            '<div class="score">' + o.width + "×" + o.height +
              " · ΔE " + (m.deltaE_mean ?? "–") + " · SSIM " + (m.ssim_masked ?? "–") + "</div>" +
            '<a class="dl" href="/result/' + job + "/" + o.index + '" download>↓ Download this photo</a>' +
          "</div>";
        grid.appendChild(card);
      });
      resultsMeta.textContent = "Job " + job + " · seed " + data.seed +
        (data.message ? " · " + data.message : "") +
        " · 4K 9:16 masters, watermark applied.";
      downloadAll.href = "/download/" + job + ".zip";
      resultsPanel.hidden = false;
      resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    const poll = (job) => {
      clearInterval(poller);
      poller = setInterval(async () => {
        let data;
        try {
          const res = await fetch("/status/" + job);
          if (!res.ok) throw new Error("status " + res.status);
          data = await res.json();
        } catch (err) {
          return;
        }
        barFill.style.width = (data.progress || 0) + "%";
        stageName.textContent = data.stage || data.state;
        stageMsg.textContent = data.message || "";
        setStage(data.stage);

        if (data.state === "done") {
          clearInterval(poller);
          barFill.style.width = "100%";
          renderResults(job, data);
          goBtn.disabled = false;
          goBtn.textContent = "Create 4 photos";
        } else if (data.state === "failed") {
          clearInterval(poller);
          showError("Job failed at " + data.stage + ": " + (data.error || "unknown error"), true);
          goBtn.disabled = false;
          goBtn.textContent = "Create 4 photos";
        }
      }, 1500);
    };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!input.files.length) { showError("Choose a photo first.", true); return; }
      showError("");
      resultsPanel.hidden = true;
      progressPanel.hidden = false;
      goBtn.disabled = true;
      goBtn.innerHTML = '<span class="spin">◐</span> Creating…';
      stagesEl.querySelectorAll("li").forEach((li) => li.classList.remove("done", "active"));
      barFill.style.width = "2%";
      stageName.textContent = "queued";
      stageMsg.textContent = "Uploading";

      const body = new FormData();
      body.append("image", input.files[0]);
      body.append("product_name", $("#product_name").value);
      body.append("product_category", $("#product_category").value);

      try {
        const res = await fetch("/generate", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Upload rejected");
        progressPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        poll(data.job_id);
      } catch (err) {
        progressPanel.hidden = true;
        goBtn.disabled = false;
        goBtn.textContent = "Create 4 photos";
        showError(err.message, true);
      }
    });

    recreateBtn.addEventListener("click", async () => {
      const link = downloadAll.getAttribute("href") || "";
      const job = link.replace("/download/", "").replace(".zip", "");
      if (!job) return;
      recreateBtn.disabled = true;
      recreateBtn.textContent = "↻ Recreating…";
      try {
        const res = await fetch("/recreate/" + job, { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Recreate failed");
        resultsPanel.hidden = true;
        grid.innerHTML = "";
        progressPanel.hidden = false;
        goBtn.disabled = true;
        goBtn.innerHTML = '<span class="spin">◐</span> Creating…';
        stagesEl.querySelectorAll("li").forEach((li) => li.classList.remove("done", "active"));
        barFill.style.width = "2%";
        showError("");
        poll(data.job_id);
      } catch (err) {
        showError(err.message, true);
      } finally {
        recreateBtn.disabled = false;
        recreateBtn.textContent = "↻ Recreate";
      }
    });
  }

  /* -------------------------------------------------------------- settings */

  const llmForm = $("#llm-form");
  if (llmForm) {
    const testBtn = $("#test-conn");
    const testResult = $("#test-result");

    const payload = () => ({
      provider: $("#provider").value,
      api_key: $("#api_key").value,
      base_url: $("#base_url").value,
      text_model: $("#text_model").value,
      image_model: $("#image_model").value,
    });

    testBtn.addEventListener("click", async () => {
      testBtn.disabled = true;
      testBtn.innerHTML = '<span class="spin">◐</span> Testing…';
      testResult.hidden = false;
      testResult.className = "hint";
      testResult.textContent = "Contacting the LLM…";
      try {
        const res = await fetch("/settings/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload()),
        });
        const data = await res.json();
        if (data.ok) {
          testResult.className = "hint ok";
          testResult.textContent = "✓ Connection OK — " + data.model + " replied \"" +
            data.reply + "\" in " + data.latency_ms + " ms.";
        } else {
          testResult.className = "hint err";
          testResult.textContent = "✕ " + (data.error || "Connection failed") +
            (data.kind ? " [" + data.kind + "]" : "");
        }
      } catch (err) {
        testResult.className = "hint err";
        testResult.textContent = "✕ " + err.message;
      } finally {
        testBtn.disabled = false;
        testBtn.textContent = "⚡ Test connection";
      }
    });

    llmForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const res = await fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload()),
      });
      const data = await res.json();
      testResult.hidden = false;
      testResult.className = data.ok ? "hint ok" : "hint err";
      testResult.textContent = data.ok ? "✓ Saved. Key now " + data.settings.llm.api_key : "Save failed.";
      $("#api_key").value = "";
    });
  }

  const brandForm = $("#brand-form");
  if (brandForm) {
    const out = $("#brand-result");
    brandForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const res = await fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          background_provider: $("#background_provider").value,
          handle: $("#handle").value,
          position: $("#position").value,
          opacity: $("#opacity").value,
          size_pct: $("#size_pct").value,
        }),
      });
      const data = await res.json();
      out.hidden = false;
      out.className = data.ok ? "hint ok" : "hint err";
      out.textContent = data.ok ? "✓ Settings saved." : "Save failed.";
    });
  }
})();
