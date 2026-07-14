(() => {
  // ---------- main view tabs (Muestra / Resultados) ----------
  const mainTabs = document.querySelectorAll(".main-tab");
  const views = {
    input: document.getElementById("view-input"),
    results: document.getElementById("view-results"),
  };
  const resultsTabBtn = document.getElementById("resultsTabBtn");
  const newSampleBtn = document.getElementById("newSampleBtn");
  const resultsSampleImg = document.getElementById("resultsSampleImg");

  function switchView(name) {
    mainTabs.forEach((t) => {
      const active = t.dataset.view === name;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    });
    Object.entries(views).forEach(([key, el]) => el.classList.toggle("active", key === name));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  mainTabs.forEach((t) => {
    t.addEventListener("click", () => {
      if (t.disabled) return;
      switchView(t.dataset.view);
    });
  });

  newSampleBtn.addEventListener("click", () => switchView("input"));

  // ---------- sub tabs (Subir foto / Tomar foto) ----------
  const tabs = document.querySelectorAll(".tab");
  const panels = {
    upload: document.getElementById("panel-upload"),
    camera: document.getElementById("panel-camera"),
  };

  const fileInput = document.getElementById("fileInput");
  const dropzone = document.getElementById("dropzone");

  const video = document.getElementById("video");
  const startCamBtn = document.getElementById("startCamBtn");
  const shotBtn = document.getElementById("shotBtn");
  const cameraMsg = document.getElementById("cameraMsg");
  const captureCanvas = document.getElementById("captureCanvas");

  const previewRow = document.getElementById("previewRow");
  const previewImg = document.getElementById("previewImg");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const clearBtn = document.getElementById("clearBtn");

  const errorMsg = document.getElementById("errorMsg");
  const loading = document.getElementById("loading");
  const resultsSection = document.getElementById("results");
  const cardsEl = document.getElementById("cards");
  const consensusTag = document.getElementById("consensusTag");
  const infoSection = document.getElementById("infoSection");
  const infoCardsEl = document.getElementById("infoCards");

  let currentBlob = null;
  let stream = null;

  // ---------- tabs ----------
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => { t.classList.remove("active"); t.setAttribute("aria-selected", "false"); });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");
      Object.values(panels).forEach((p) => p.classList.remove("active"));
      panels[tab.dataset.tab].classList.add("active");
      stopCamera();
    });
  });

  // ---------- upload ----------
  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) setSample(fileInput.files[0]);
  });

  ["dragover", "dragenter"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); })
  );
  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) setSample(file);
  });

  // ---------- camera ----------
  startCamBtn.addEventListener("click", async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      video.srcObject = stream;
      cameraMsg.hidden = true;
      shotBtn.disabled = false;
      startCamBtn.textContent = "Reiniciar cámara";
    } catch (err) {
      showError("No se pudo acceder a la cámara. Revisa los permisos del navegador.");
    }
  });

  shotBtn.addEventListener("click", () => {
    const w = video.videoWidth, h = video.videoHeight;
    if (!w || !h) return;
    captureCanvas.width = w;
    captureCanvas.height = h;
    const ctx = captureCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0, w, h);
    captureCanvas.toBlob((blob) => setSample(blob), "image/jpeg", 0.92);
  });

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
      video.srcObject = null;
      cameraMsg.hidden = false;
      shotBtn.disabled = true;
      startCamBtn.textContent = "Activar cámara";
    }
  }

  // ---------- sample handling ----------
  function setSample(blobOrFile) {
    hideError();
    currentBlob = blobOrFile;
    previewImg.src = URL.createObjectURL(blobOrFile);
    previewRow.hidden = false;
    previewRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  clearBtn.addEventListener("click", () => {
    currentBlob = null;
    fileInput.value = "";
    previewRow.hidden = true;
  });

  // ---------- analyze ----------
  analyzeBtn.addEventListener("click", async () => {
    if (!currentBlob) return;
    hideError();
    loading.hidden = false;
    analyzeBtn.disabled = true;

    const form = new FormData();
    const filename = currentBlob.name || "captura.jpg";
    form.append("image", currentBlob, filename);

    try {
      const resp = await fetch("/predict", { method: "POST", body: form });
      const data = await resp.json();
      if (!resp.ok) {
        showError(data.error || "Ocurrió un error al analizar la imagen.");
      } else {
        renderResults(data);
      }
    } catch (err) {
      showError("No se pudo conectar con el servidor. Intenta de nuevo.");
    } finally {
      loading.hidden = true;
      analyzeBtn.disabled = false;
    }
  });

  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.hidden = false;
  }
  function hideError() {
    errorMsg.hidden = true;
  }

  // ---------- render ----------
  const ACCENTS = { VGG16: "#6FA65C", DenseNet121: "#D8AA55", Xception: "#C6603E" };
  const CLASS_ACCENTS = {
    "Healthy": "#6FA65C",
    "Cordana": "#D8AA55",
    "Panama Disease": "#C6603E",
    "Yellow and Black Sigatoka": "#C6603E",
  };

  function renderResults(data) {
    resultsSampleImg.src = data.image_url || previewImg.src;
    consensusTag.textContent = data.all_agree ? "Consenso entre los 3 modelos" : "Los modelos no coinciden";
    consensusTag.className = "consensus-tag " + (data.all_agree ? "agree" : "disagree");

    cardsEl.innerHTML = "";
    data.results.forEach((r) => {
      const accent = ACCENTS[r.model] || "#6FA65C";
      const sortedProbs = Object.entries(r.probabilities_display).sort((a, b) => b[1] - a[1]);

      const card = document.createElement("div");
      card.className = "card";
      card.style.setProperty("--card-accent", accent);

      const breakdownHtml = sortedProbs.map(([label, prob]) => {
        const pct = (prob * 100).toFixed(1);
        const isTop = label === r.predicted_class_display;
        return `
          <div class="bd-row ${isTop ? "top" : ""}">
            <div class="bd-label"><span>${escapeHtml(label)}</span><span>${pct}%</span></div>
            <div class="bd-track"><div class="bd-fill" style="width:${pct}%"></div></div>
          </div>`;
      }).join("");

      card.innerHTML = `
        <div class="card-model"><span>${r.model}</span><span class="size">${r.input_size[0]}×${r.input_size[1]}</span></div>
        <div class="card-class">${escapeHtml(r.predicted_class_display)}</div>
        <div class="card-conf">${(r.confidence * 100).toFixed(1)}<small>% confianza</small></div>
        <div class="breakdown">${breakdownHtml}</div>
        <div class="card-meta">inferencia: ${r.inference_ms} ms</div>
      `;
      cardsEl.appendChild(card);
    });

    resultsTabBtn.disabled = false;
    renderInfoCards(data.disease_info || []);
    switchView("results");
  }

  function renderInfoCards(diseaseInfoList) {
    if (!diseaseInfoList.length) {
      infoSection.hidden = true;
      return;
    }
    infoCardsEl.innerHTML = "";
    diseaseInfoList.forEach((info) => {
      const accent = CLASS_ACCENTS[info.class_name] || "#6FA65C";
      const card = document.createElement("div");
      card.className = "info-card";
      card.style.setProperty("--card-accent", accent);

      const sintomasHtml = (info.sintomas || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("");
      const manejoHtml = (info.manejo || []).map((s) => `<li>${escapeHtml(s)}</li>`).join("");
      const agentHtml = info.agente_causal ? `<div class="info-agent">${escapeHtml(info.agente_causal)}</div>` : "";

      card.innerHTML = `
        <div class="info-card-head">
          <span class="info-card-title">${escapeHtml(info.display_name)}</span>
          <span class="info-severity">${escapeHtml(info.severidad || "")}</span>
        </div>
        ${agentHtml}
        <div class="info-cols">
          <div>
            <div class="info-col-label">Síntomas</div>
            <ul class="info-list">${sintomasHtml}</ul>
          </div>
          <div>
            <div class="info-col-label">Manejo recomendado</div>
            <ul class="info-list">${manejoHtml}</ul>
          </div>
        </div>
      `;
      infoCardsEl.appendChild(card);
    });
    infoSection.hidden = false;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
})();