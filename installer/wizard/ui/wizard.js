/* FL MCP Studio — Wizard JS. Drives step navigation and calls Python via pywebview.api. */

(function () {
  "use strict";

  const TOTAL_STEPS = 9;
  let currentStep = 1;

  // ----- DOM helpers -----

  function showStep(n) {
    document.querySelectorAll(".step-panel").forEach((el) => {
      el.classList.toggle("hidden", Number(el.dataset.step) !== n);
    });
    document.querySelectorAll(".sidebar .step").forEach((el) => {
      const step = Number(el.dataset.step);
      el.classList.toggle("current", step === n);
    });
    currentStep = n;
  }

  function markStepDone(n) {
    const li = document.querySelector(`.sidebar .step[data-step="${n}"]`);
    if (li) li.classList.add("done");
  }

  function markStepError(n) {
    const li = document.querySelector(`.sidebar .step[data-step="${n}"]`);
    if (li) li.classList.add("error");
  }

  function setStatus(boxId, message, kind) {
    const box = document.getElementById(boxId);
    if (!box) return;
    box.textContent = message;
    box.classList.remove("ok", "error");
    if (kind) box.classList.add(kind);
  }

  function enableNext(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) btn.disabled = false;
  }

  function makeChecklistItem(label, value) {
    const li = document.createElement("li");
    li.classList.add(value ? "ok" : "missing");
    li.textContent = `${label}: ${value || "no detectado"}`;
    return li;
  }

  // ----- Action handlers -----

  async function runDetect() {
    const list = document.getElementById("diag-list");
    list.replaceChildren();
    const placeholder = document.createElement("li");
    placeholder.textContent = "Chequeando…";
    list.appendChild(placeholder);

    const r = await pywebview.api.detect();

    list.replaceChildren(
      makeChecklistItem("Claude Desktop", r.claude_desktop),
      makeChecklistItem("FL Studio", r.fl_studio_settings),
      makeChecklistItem("loopMIDI", r.loopmidi),
      makeChecklistItem("WebView2 Runtime", r.webview2 ? "instalado" : null),
    );
    enableNext("diag-next");
    if (r.is_ready) markStepDone(2);
  }

  async function runInstallLoopmidi() {
    setStatus("lm-status", "Descargando e instalando loopMIDI… (puede tardar un minuto)", null);
    const r = await pywebview.api.install_loopmidi();
    if (r.ok) {
      setStatus("lm-status", "✅ loopMIDI instalado", "ok");
      enableNext("lm-next");
      markStepDone(3);
    } else {
      setStatus("lm-status", `❌ Error: ${r.error}`, "error");
      markStepError(3);
    }
  }

  async function runCreatePort() {
    setStatus("port-status", "Creando puerto FL_MCP…", null);
    const r = await pywebview.api.create_port();
    if (r.ok) {
      setStatus("port-status", "✅ Puerto FL_MCP listo", "ok");
      enableNext("port-next");
      markStepDone(4);
    } else {
      setStatus("port-status", `❌ Error: ${r.error}`, "error");
      markStepError(4);
    }
  }

  async function runInstallScript() {
    setStatus("script-status", "Copiando device_test.py…", null);
    const r = await pywebview.api.install_script();
    if (r.ok) {
      setStatus("script-status", "✅ Script instalado en FL Studio", "ok");
      enableNext("script-next");
      markStepDone(5);
    } else {
      setStatus("script-status", `❌ Error: ${r.error}`, "error");
      markStepError(5);
    }
  }

  async function runRegisterMcp() {
    setStatus("mcp-status", "Editando claude_desktop_config.json…", null);
    // The wizard knows where it was installed; pass those paths to Python.
    // Defaults assume the install dir layout from sub-project D's Inno Setup script.
    const pythonExe = "C:/Program Files/FL MCP Studio/python-embed/python.exe";
    const triggerPy = "C:/Program Files/FL MCP Studio/trigger.py";
    const r = await pywebview.api.register_mcp(pythonExe, triggerPy);
    if (r.ok) {
      setStatus("mcp-status", "✅ Claude Desktop configurado", "ok");
      enableNext("mcp-next");
      markStepDone(6);
    } else {
      setStatus("mcp-status", `❌ Error: ${r.error}`, "error");
      markStepError(6);
    }
  }

  async function runTestConnection() {
    setStatus("test-status", "Mandando nota MIDI a FL Studio…", null);
    const r = await pywebview.api.test_connection();
    if (r.ok) {
      setStatus("test-status", "✅ FL Studio recibió la nota. Todo listo.", "ok");
      enableNext("test-next");
      markStepDone(8);
    } else {
      setStatus("test-status", `❌ ${r.error}`, "error");
      markStepError(8);
    }
  }

  async function runFinish() {
    await pywebview.api.mark_setup_completed();
    if (window.pywebview && pywebview.api.close_window) {
      pywebview.api.close_window();
    } else {
      window.close();
    }
  }

  // ----- Wire up -----

  function onActionClick(event) {
    const action = event.target.dataset.action;
    if (!action) return;

    switch (action) {
      case "next":
        if (currentStep === 1) {
          showStep(2);
          markStepDone(1);
          runDetect();
        } else if (currentStep === 7) {
          showStep(8);
          markStepDone(7);
        } else if (currentStep === 9) {
          // no-op; finish button handles 9
        } else {
          showStep(currentStep + 1);
        }
        break;
      case "back":
        if (currentStep > 1) showStep(currentStep - 1);
        break;
      case "install-loopmidi":
        runInstallLoopmidi();
        break;
      case "create-port":
        runCreatePort();
        break;
      case "install-script":
        runInstallScript();
        break;
      case "register-mcp":
        runRegisterMcp();
        break;
      case "test-connection":
        runTestConnection();
        break;
      case "finish":
        runFinish();
        break;
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", onActionClick);
  });
})();
