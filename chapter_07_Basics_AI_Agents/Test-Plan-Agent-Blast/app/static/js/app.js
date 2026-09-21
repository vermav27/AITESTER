/* Test Plan Agent — progressive enhancement only.
   Every action works without JavaScript; this adds inline feedback. */

(function () {
  "use strict";

  /* Example chips fill the prompt textarea. */
  document.querySelectorAll(".chip[data-example]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var textarea = document.getElementById("prompt");
      if (!textarea) return;
      textarea.value = chip.dataset.example;
      textarea.focus();
    });
  });

  /* Show a busy state while the pipeline runs (a local model can be slow). */
  var form = document.getElementById("generate-form");
  if (form) {
    form.addEventListener("submit", function () {
      var button = document.getElementById("submit-btn");
      var hint = document.getElementById("submit-hint");
      if (!button) return;
      button.disabled = true;
      button.textContent = "Working…";
      if (hint) {
        hint.textContent =
          "Fetching Jira, running the checklist, and drafting with the local model. This can take a minute.";
      }
      window.setTimeout(function () {
        button.textContent = "Still working…";
      }, 20000);
    });
  }

  /* Connection tests on the Settings page. */
  document.querySelectorAll("[data-test-url]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.dataset.testTarget);
      var settingsForm = document.getElementById("settings-form");
      if (!target) return;

      button.disabled = true;
      target.className = "test-result";
      target.textContent = "Testing…";

      var body = settingsForm ? new FormData(settingsForm) : new FormData();

      fetch(button.dataset.testUrl, { method: "POST", body: body })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          target.className = "test-result " + (data.ok ? "is-ok" : "is-error");
          target.textContent = (data.ok ? "✓ " : "✗ ") + data.message;
        })
        .catch(function () {
          target.className = "test-result is-error";
          target.textContent = "✗ Request failed. Is the server still running?";
        })
        .finally(function () {
          button.disabled = false;
        });
    });
  });

  /* Copy the generated plan to the clipboard. */
  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      var original = button.textContent;
      fetch(button.dataset.copy)
        .then(function (response) { return response.text(); })
        .then(function (text) { return navigator.clipboard.writeText(text); })
        .then(function () { button.textContent = "Copied ✓"; })
        .catch(function () { button.textContent = "Copy failed"; })
        .finally(function () {
          window.setTimeout(function () { button.textContent = original; }, 2200);
        });
    });
  });
})();
