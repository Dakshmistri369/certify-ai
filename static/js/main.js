/**
 * main.js
 * Frontend Controller for CertifyAI - AI Certificate Generator Studio
 */

document.addEventListener("DOMContentLoaded", function () {
    // --- Application State ---
    const state = {
        config: window.INITIAL_CONFIG || {},
        currentTemplate: "classic_gold.png",
        templateWidth: 1920,
        templateHeight: 1080,
        activeField: "NAME",
        fields: {},
        studentRecords: [],
        cleanDummyText: true,
        currentStep: 1
    };

    // --- DOM Elements ---
    const stepItems = [1, 2, 3, 4, 5].map(i => document.getElementById(`step${['Upload', 'Design', 'Preview', 'Generate', 'Download'][i - 1]}Item`));
    const sectionPanes = ['sectionUpload', 'sectionDesign', 'sectionPreview', 'sectionGenerate', 'sectionDownload'].map(id => document.getElementById(id));

    const dataFileInput = document.getElementById("dataFileInput");
    const dataDropzone = document.getElementById("dataDropzone");
    const dataFileInfo = document.getElementById("dataFileInfo");
    const dataFileName = document.getElementById("dataFileName");
    const dataFileMeta = document.getElementById("dataFileMeta");
    const dataFileFormatBadge = document.getElementById("dataFileFormatBadge");
    const removeDataFileBtn = document.getElementById("removeDataFileBtn");

    const rawPasteTextarea = document.getElementById("rawPasteTextarea");
    const parseRawPasteBtn = document.getElementById("parseRawPasteBtn");
    const loadSampleDataBtn = document.getElementById("loadSampleDataBtn");
    const loadSample50DataBtn = document.getElementById("loadSample50DataBtn");

    const tableRecordCount = document.getElementById("tableRecordCount");
    const tableFormatBadge = document.getElementById("tableFormatBadge");
    const recordsTableBody = document.getElementById("recordsTableBody");
    const searchRecordsInput = document.getElementById("searchRecordsInput");
    const discoveredColumnsContainer = document.getElementById("discoveredColumnsContainer");
    const generateRecordsCount = document.getElementById("generateRecordsCount");

    const previewCanvasImage = document.getElementById("previewCanvasImage");
    const canvasContainer = document.getElementById("canvasContainer");
    const pinsOverlay = document.getElementById("pinsOverlay");
    const previewStudentSelect = document.getElementById("previewStudentSelect");
    const cleanDummyTextToggle = document.getElementById("cleanDummyTextToggle");
    const templateFileInput = document.getElementById("templateFileInput");

    const fieldTabs = document.getElementById("fieldTabs");
    const ctrlX = document.getElementById("ctrlX");
    const ctrlY = document.getElementById("ctrlY");
    const ctrlFontSize = document.getElementById("ctrlFontSize");
    const ctrlColor = document.getElementById("ctrlColor");
    const ctrlFontFamily = document.getElementById("ctrlFontFamily");
    const ctrlAlignment = document.getElementById("ctrlAlignment");
    const activeFieldLabel = document.getElementById("activeFieldLabel");
    const deleteActiveFieldBtn = document.getElementById("deleteActiveFieldBtn");

    const generateBulkBtn = document.getElementById("generateBulkBtn");
    const stickyGenerateBtn = document.getElementById("stickyGenerateBtn");
    const generationProgressContainer = document.getElementById("generationProgressContainer");
    const generationProgressBar = document.getElementById("generationProgressBar");
    const progressStatusText = document.getElementById("progressStatusText");
    const progressCountText = document.getElementById("progressCountText");
    const statusBarText = document.getElementById("statusBarText");

    // Modals
    const batchSuccessModal = document.getElementById("batchSuccessModal") ? new bootstrap.Modal(document.getElementById("batchSuccessModal")) : null;
    const singlePreviewModal = document.getElementById("singlePreviewModal") ? new bootstrap.Modal(document.getElementById("singlePreviewModal")) : null;
    const recordEditModal = document.getElementById("recordEditModal") ? new bootstrap.Modal(document.getElementById("recordEditModal")) : null;
    const newFieldModal = document.getElementById("newFieldModal") ? new bootstrap.Modal(document.getElementById("newFieldModal")) : null;

    // --- Step Navigation ---
    function goToStep(stepNum) {
        state.currentStep = Math.max(1, Math.min(5, stepNum));
        stepItems.forEach((item, idx) => {
            if (item) item.classList.toggle("active", idx + 1 === state.currentStep);
        });
        sectionPanes.forEach((pane, idx) => {
            if (pane) pane.classList.toggle("active", idx + 1 === state.currentStep);
        });
        if (state.currentStep === 3) {
            renderCanvasPins();
            updateLivePreview();
        }
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    stepItems.forEach((item, idx) => {
        if (item) item.addEventListener("click", () => goToStep(idx + 1));
    });

    document.getElementById("btnNextToDesign")?.addEventListener("click", () => goToStep(2));
    document.getElementById("btnBackToUpload")?.addEventListener("click", () => goToStep(1));
    document.getElementById("btnNextToPreview")?.addEventListener("click", () => goToStep(3));
    document.getElementById("btnBackToDesign")?.addEventListener("click", () => goToStep(2));
    document.getElementById("btnNextToGenerate")?.addEventListener("click", () => goToStep(4));
    document.getElementById("btnBackToPreview")?.addEventListener("click", () => goToStep(3));
    document.getElementById("btnNextToDownload")?.addEventListener("click", () => goToStep(5));
    document.getElementById("btnStartNewBatch")?.addEventListener("click", () => goToStep(1));

    // --- Initialize Fields from Config ---
    function loadTemplateConfig(templateName) {
        state.currentTemplate = templateName;
        const tplCfg = state.config.templates?.[templateName] || state.config.templates?.["classic_gold.png"] || {};
        state.templateWidth = tplCfg.width || 1920;
        state.templateHeight = tplCfg.height || 1080;
        state.fields = JSON.parse(JSON.stringify(tplCfg.fields || {
            NAME: { label: "Student Name", x: 960, y: 490, font_size: 76, color: "#0C0C0C", font_family: "GreatVibes-Regular.ttf", alignment: "center" },
            COURSE: { label: "Course Name", x: 960, y: 660, font_size: 32, color: "#9B3922", font_family: "Montserrat-Bold.ttf", alignment: "center" },
            DATE: { label: "Date", x: 580, y: 880, font_size: 20, color: "#481E14", font_family: "Roboto-Regular.ttf", alignment: "center" },
            GRADE: { label: "Grade", x: 960, y: 740, font_size: 24, color: "#481E14", font_family: "Georgia-Regular.ttf", alignment: "center" },
            CERT_ID: { label: "Cert ID", x: 1340, y: 880, font_size: 20, color: "#481E14", font_family: "Roboto-Regular.ttf", alignment: "center" }
        }));
        
        if (previewCanvasImage) {
            previewCanvasImage.src = `/api/template-image/${encodeURIComponent(templateName)}?t=${Date.now()}`;
        }
        renderFieldTabs();
        selectActiveField(Object.keys(state.fields)[0] || "NAME");
        renderCanvasPins();
        loadTemplatePalette(templateName);
    }

    function loadTemplatePalette(templateName) {
        fetch(`/api/template-palette/${encodeURIComponent(templateName)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.info) {
                    const container = document.getElementById("paletteSwatchesContainer");
                    if (container && data.info.palette) {
                        container.innerHTML = data.info.palette.map(c => 
                            `<div class="palette-swatch" style="background-color: ${c};" title="${c}" onclick="document.getElementById('ctrlColor').value='${c}'; document.getElementById('ctrlColor').dispatchEvent(new Event('input'));"></div>`
                        ).join("");
                    }
                    const dimMeta = document.getElementById("tplDimMeta");
                    if (dimMeta) dimMeta.textContent = `${data.info.width}x${data.info.height} (${data.info.orientation})`;
                }
            })
            .catch(() => {});
    }

    // --- Data Records Ingestion & Table Display ---
    function handleExtractedData(data) {
        if (!data.success || !data.all_records) {
            alert(data.error || "Data extraction failed.");
            return;
        }
        state.studentRecords = data.all_records;
        const count = state.studentRecords.length;

        if (tableRecordCount) tableRecordCount.textContent = `${count} Students`;
        if (tableFormatBadge) tableFormatBadge.textContent = data.stats?.source_type?.toUpperCase() || "LOADED";
        if (generateRecordsCount) generateRecordsCount.textContent = count;
        if (statusBarText) statusBarText.textContent = `Ready — ${count} student records loaded`;
        document.getElementById("stepperDataSub").textContent = `${count} Records`;

        // File info banner
        if (dataFileInfo) {
            dataFileInfo.classList.remove("d-none");
            if (dataFileName) dataFileName.textContent = data.original_name || data.filename || "Uploaded Data";
            if (dataFileMeta) dataFileMeta.textContent = `${count} records parsed`;
            if (dataFileFormatBadge) dataFileFormatBadge.textContent = (data.stats?.source_type || "DATA").toUpperCase();
        }

        // Columns found
        if (discoveredColumnsContainer && data.all_fields) {
            discoveredColumnsContainer.innerHTML = data.all_fields.map(f => `<span class="badge bg-dark border border-subtle text-light fs-xs">{${f}}</span>`).join("");
        }

        // Student preview dropdown
        if (previewStudentSelect) {
            previewStudentSelect.innerHTML = state.studentRecords.map((r, i) => `<option value="${i}">#${i + 1}: ${r.NAME || 'Student'}</option>`).join("");
        }

        renderRecordsTable();
    }

    function renderRecordsTable(query = "") {
        if (!recordsTableBody) return;
        const q = query.toLowerCase().trim();
        const filtered = state.studentRecords.filter(r => 
            !q || Object.values(r).some(v => String(v).toLowerCase().includes(q))
        );

        if (filtered.length === 0) {
            recordsTableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No matching student records found.</td></tr>`;
            return;
        }

        recordsTableBody.innerHTML = filtered.map((r, i) => `
            <tr>
                <td class="text-muted">${i + 1}</td>
                <td class="fw-bold text-light">${r.NAME || ""}</td>
                <td><span class="badge bg-dark-subtle text-light border border-subtle">${r.COURSE || ""}</span></td>
                <td><span class="text-muted">${r.DATE || ""}</span></td>
                <td><span class="badge bg-secondary-subtle text-light">${r.GRADE || ""}</span></td>
                <td><code class="text-primary">${r.CERT_ID || ""}</code></td>
                <td class="text-end">
                    <button type="button" class="btn btn-sm btn-link text-info p-0 me-2" onclick="window.editStudentRecord(${i})" title="Edit"><i class="fa-solid fa-pen-to-square"></i></button>
                    <button type="button" class="btn btn-sm btn-link text-danger p-0" onclick="window.deleteStudentRecord(${i})" title="Delete"><i class="fa-solid fa-trash"></i></button>
                </td>
            </tr>
        `).join("");
    }

    if (searchRecordsInput) {
        searchRecordsInput.addEventListener("input", (e) => renderRecordsTable(e.target.value));
    }

    // Window helper functions for inline row actions
    window.editStudentRecord = function(idx) {
        const r = state.studentRecords[idx];
        if (!r || !recordEditModal) return;
        document.getElementById("editRecordIndex").value = idx;
        document.getElementById("editRecordName").value = r.NAME || "";
        document.getElementById("editRecordCourse").value = r.COURSE || "";
        document.getElementById("editRecordDate").value = r.DATE || "";
        document.getElementById("editRecordGrade").value = r.GRADE || "";
        document.getElementById("editRecordCertId").value = r.CERT_ID || "";
        recordEditModal.show();
    };

    window.deleteStudentRecord = function(idx) {
        if (confirm("Delete this student record?")) {
            state.studentRecords.splice(idx, 1);
            handleExtractedData({ success: true, all_records: state.studentRecords, stats: { source_type: "edited" } });
        }
    };

    document.getElementById("saveRecordBtn")?.addEventListener("click", () => {
        const idx = parseInt(document.getElementById("editRecordIndex").value);
        const record = {
            NAME: document.getElementById("editRecordName").value.trim(),
            COURSE: document.getElementById("editRecordCourse").value.trim(),
            DATE: document.getElementById("editRecordDate").value.trim(),
            GRADE: document.getElementById("editRecordGrade").value.trim(),
            CERT_ID: document.getElementById("editRecordCertId").value.trim()
        };
        if (!record.NAME) {
            alert("Student Name is required.");
            return;
        }
        if (idx >= 0) {
            state.studentRecords[idx] = { ...state.studentRecords[idx], ...record };
        } else {
            state.studentRecords.push(record);
        }
        recordEditModal?.hide();
        handleExtractedData({ success: true, all_records: state.studentRecords, stats: { source_type: "manual" } });
    });

    document.getElementById("openAddRecordModalBtn")?.addEventListener("click", () => {
        document.getElementById("editRecordIndex").value = -1;
        document.getElementById("editRecordName").value = "";
        document.getElementById("editRecordCourse").value = "Certificate Course";
        document.getElementById("editRecordDate").value = new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
        document.getElementById("editRecordGrade").value = "A+ Distinction";
        document.getElementById("editRecordCertId").value = `CERT-${new Date().getFullYear()}-${String(state.studentRecords.length + 1).padStart(4, '0')}`;
        recordEditModal?.show();
    });

    // --- File Upload & Paste Handlers ---
    function uploadDataFile(file) {
        if (!file) return;
        const formData = new FormData();
        formData.append("data_file", file);
        if (statusBarText) statusBarText.textContent = "Uploading & extracting data...";
        fetch("/api/upload-data", { method: "POST", body: formData })
            .then(res => res.json())
            .then(data => handleExtractedData(data))
            .catch(err => alert("Upload failed: " + err.message));
    }

    if (dataFileInput) {
        dataFileInput.addEventListener("change", (e) => {
            if (e.target.files.length) uploadDataFile(e.target.files[0]);
        });
    }

    if (dataDropzone) {
        dataDropzone.addEventListener("dragover", (e) => { e.preventDefault(); dataDropzone.classList.add("drag-over"); });
        dataDropzone.addEventListener("dragleave", () => dataDropzone.classList.remove("drag-over"));
        dataDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dataDropzone.classList.remove("drag-over");
            if (e.dataTransfer.files.length) uploadDataFile(e.dataTransfer.files[0]);
        });
    }

    if (parseRawPasteBtn) {
        parseRawPasteBtn.addEventListener("click", () => {
            const raw = rawPasteTextarea?.value?.trim();
            if (!raw) return alert("Please paste text first.");
            fetch("/api/parse-raw-data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ raw_text: raw })
            })
            .then(res => res.json())
            .then(data => handleExtractedData(data))
            .catch(err => alert("Parse error: " + err.message));
        });
    }

    loadSampleDataBtn?.addEventListener("click", () => {
        fetch("/api/sample-data/10").then(r => r.json()).then(handleExtractedData);
    });
    loadSample50DataBtn?.addEventListener("click", () => {
        fetch("/api/sample-data/50").then(r => r.json()).then(handleExtractedData);
    });

    removeDataFileBtn?.addEventListener("click", () => {
        state.studentRecords = [];
        handleExtractedData({ success: true, all_records: [], stats: { source_type: "none" } });
        if (dataFileInfo) dataFileInfo.classList.add("d-none");
    });

    // Export CSV / JSON
    document.getElementById("exportCsvBtn")?.addEventListener("click", (e) => {
        e.preventDefault();
        if (!state.studentRecords.length) return alert("No records to export.");
        const headers = Object.keys(state.studentRecords[0]);
        const csv = [headers.join(",")].concat(state.studentRecords.map(r => headers.map(h => `"${(r[h] || "").replace(/"/g, '""')}"`).join(","))).join("\n");
        const blob = new Blob([csv], { type: "text/csv" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "students_roster.csv";
        a.click();
    });

    document.getElementById("exportJsonBtn")?.addEventListener("click", (e) => {
        e.preventDefault();
        if (!state.studentRecords.length) return alert("No records to export.");
        const blob = new Blob([JSON.stringify(state.studentRecords, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "students_roster.json";
        a.click();
    });

    // --- Template Selection & Custom Upload ---
    document.querySelectorAll(".tpl-gallery-card").forEach(card => {
        const tpl = card.getAttribute("data-template");
        if (tpl) {
            card.addEventListener("click", () => {
                document.querySelectorAll(".tpl-gallery-card").forEach(c => c.classList.remove("active"));
                card.classList.add("active");
                document.getElementById("stepperDesignSub").textContent = card.querySelector(".tpl-card-name")?.textContent?.trim() || tpl;
                loadTemplateConfig(tpl);
            });
        }
    });

    if (templateFileInput) {
        templateFileInput.addEventListener("change", (e) => {
            if (!e.target.files.length) return;
            const formData = new FormData();
            formData.append("template_file", e.target.files[0]);
            fetch("/api/upload-template", { method: "POST", body: formData })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        state.config.templates[data.template_name] = {
                            name: data.original_name,
                            width: data.width,
                            height: data.height,
                            fields: data.fields
                        };
                        loadTemplateConfig(data.template_name);
                        document.getElementById("stepperDesignSub").textContent = data.original_name;
                        goToStep(3);
                    } else {
                        alert(data.error || "Template upload failed.");
                    }
                });
        });
    }

    if (cleanDummyTextToggle) {
        cleanDummyTextToggle.addEventListener("change", (e) => {
            state.cleanDummyText = e.target.checked;
            updateLivePreview();
        });
    }

    // --- Interactive Canvas Studio & Drag Pins ---
    function renderFieldTabs() {
        if (!fieldTabs) return;
        const keys = Object.keys(state.fields).filter(k => !k.startsWith("_"));
        fieldTabs.innerHTML = keys.map(k => 
            `<button class="nav-link ${k === state.activeField ? 'active' : ''} py-1 px-3 fs-xs" data-field="${k}" type="button">${state.fields[k].label || k}</button>`
        ).join("");

        fieldTabs.querySelectorAll("button").forEach(btn => {
            btn.addEventListener("click", () => selectActiveField(btn.getAttribute("data-field")));
        });
    }

    function selectActiveField(fieldKey) {
        state.activeField = fieldKey;
        const cfg = state.fields[fieldKey];
        if (!cfg) return;

        if (activeFieldLabel) activeFieldLabel.textContent = `{${fieldKey}}`;
        if (ctrlX) ctrlX.value = cfg.x || 100;
        if (ctrlY) ctrlY.value = cfg.y || 100;
        if (ctrlFontSize) ctrlFontSize.value = cfg.font_size || 32;
        if (ctrlColor) ctrlColor.value = cfg.color || "#0C0C0C";
        if (ctrlFontFamily) ctrlFontFamily.value = cfg.font_family || "Montserrat-Bold.ttf";
        if (ctrlAlignment) ctrlAlignment.value = cfg.alignment || "center";
        
        if (deleteActiveFieldBtn) {
            deleteActiveFieldBtn.classList.toggle("d-none", ["NAME", "COURSE", "DATE", "GRADE", "CERT_ID"].includes(fieldKey));
        }

        renderFieldTabs();
        highlightActivePin();
    }

    function renderCanvasPins() {
        if (!pinsOverlay || !previewCanvasImage) return;
        const rect = previewCanvasImage.getBoundingClientRect();
        if (!rect.width || !rect.height) return;

        const scaleX = rect.width / state.templateWidth;
        const scaleY = rect.height / state.templateHeight;

        pinsOverlay.innerHTML = "";
        Object.keys(state.fields).forEach(key => {
            if (key.startsWith("_")) return;
            const f = state.fields[key];
            const pin = document.createElement("div");
            pin.className = `field-pin ${key === state.activeField ? 'active' : ''}`;
            pin.id = `pin_${key}`;
            pin.textContent = f.label || key;
            pin.style.left = `${(f.x || 100) * scaleX}px`;
            pin.style.top = `${(f.y || 100) * scaleY}px`;

            // Drag handler
            let isDragging = false;
            pin.addEventListener("pointerdown", (e) => {
                isDragging = true;
                pin.setPointerCapture(e.pointerId);
                selectActiveField(key);
            });
            pin.addEventListener("pointermove", (e) => {
                if (!isDragging) return;
                const canvasRect = previewCanvasImage.getBoundingClientRect();
                const mouseX = Math.max(0, Math.min(canvasRect.width, e.clientX - canvasRect.left));
                const mouseY = Math.max(0, Math.min(canvasRect.height, e.clientY - canvasRect.top));
                const realX = Math.round(mouseX / scaleX);
                const realY = Math.round(mouseY / scaleY);
                
                f.x = realX;
                f.y = realY;
                pin.style.left = `${mouseX}px`;
                pin.style.top = `${mouseY}px`;
                if (ctrlX) ctrlX.value = realX;
                if (ctrlY) ctrlY.value = realY;
            });
            pin.addEventListener("pointerup", () => {
                if (isDragging) {
                    isDragging = false;
                    debouncedPreview();
                }
            });

            pinsOverlay.appendChild(pin);
        });
    }

    function highlightActivePin() {
        document.querySelectorAll(".field-pin").forEach(p => p.classList.remove("active"));
        const activePin = document.getElementById(`pin_${state.activeField}`);
        if (activePin) activePin.classList.add("active");
    }

    // Input changes update active field
    [ctrlX, ctrlY, ctrlFontSize, ctrlColor, ctrlFontFamily, ctrlAlignment].forEach(ctrl => {
        if (ctrl) {
            ctrl.addEventListener("input", () => {
                const f = state.fields[state.activeField];
                if (!f) return;
                f.x = parseInt(ctrlX.value) || f.x;
                f.y = parseInt(ctrlY.value) || f.y;
                f.font_size = parseInt(ctrlFontSize.value) || f.font_size;
                f.color = ctrlColor.value || f.color;
                f.font_family = ctrlFontFamily.value || f.font_family;
                f.alignment = ctrlAlignment.value || f.alignment;
                renderCanvasPins();
                debouncedPreview();
            });
        }
    });

    // Add new placeholder modal
    document.getElementById("addNewFieldBtn")?.addEventListener("click", () => {
        document.getElementById("newFieldKeyInput").value = "";
        document.getElementById("newFieldSampleVal").value = "";
        newFieldModal?.show();
    });

    document.getElementById("confirmNewFieldBtn")?.addEventListener("click", () => {
        const keyRaw = document.getElementById("newFieldKeyInput").value.trim();
        const fType = document.getElementById("newFieldTypeSelect").value;
        if (!keyRaw) return alert("Placeholder key is required.");
        const key = keyRaw.toUpperCase().replace(/[^A-Z0-9_]/g, '_');
        
        state.fields[key] = {
            label: key,
            type: fType,
            x: Math.round(state.templateWidth / 2),
            y: Math.round(state.templateHeight / 2),
            font_size: fType === 'qr' ? 140 : 28,
            color: "#0C0C0C",
            font_family: "Montserrat-Bold.ttf",
            alignment: "center"
        };
        newFieldModal?.hide();
        renderFieldTabs();
        selectActiveField(key);
        renderCanvasPins();
        debouncedPreview();
    });

    if (deleteActiveFieldBtn) {
        deleteActiveFieldBtn.addEventListener("click", () => {
            if (confirm(`Remove placeholder {${state.activeField}}?`)) {
                delete state.fields[state.activeField];
                renderFieldTabs();
                selectActiveField(Object.keys(state.fields)[0] || "NAME");
                renderCanvasPins();
                debouncedPreview();
            }
        });
    }

    // Save & Reset coordinates
    document.getElementById("saveCoordsBtn")?.addEventListener("click", () => {
        const cfg = state.config;
        if (!cfg.templates) cfg.templates = {};
        if (!cfg.templates[state.currentTemplate]) cfg.templates[state.currentTemplate] = {};
        cfg.templates[state.currentTemplate].fields = state.fields;
        
        fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cfg)
        }).then(r => r.json()).then(d => alert(d.message || "Layout saved."));
    });

    document.getElementById("resetCoordsBtn")?.addEventListener("click", () => {
        loadTemplateConfig(state.currentTemplate);
        debouncedPreview();
    });

    // Overlays toggles
    document.getElementById("toggleGridBtn")?.addEventListener("click", function() {
        this.classList.toggle("active");
        document.getElementById("designerGridOverlay")?.classList.toggle("d-none");
    });
    document.getElementById("toggleGuidesBtn")?.addEventListener("click", function() {
        this.classList.toggle("active");
        document.getElementById("designerGuidesOverlay")?.classList.toggle("d-none");
    });
    document.getElementById("toggleMarginsBtn")?.addEventListener("click", function() {
        this.classList.toggle("active");
        document.getElementById("designerMarginsOverlay")?.classList.toggle("d-none");
    });
    document.getElementById("togglePinsBtn")?.addEventListener("click", function() {
        this.classList.toggle("active");
        pinsOverlay?.classList.toggle("d-none");
    });

    if (previewStudentSelect) {
        previewStudentSelect.addEventListener("change", () => updateLivePreview());
    }

    // Debounced Live Preview
    let previewTimer = null;
    function debouncedPreview() {
        clearTimeout(previewTimer);
        previewTimer = setTimeout(updateLivePreview, 200);
    }

    function updateLivePreview() {
        const studentIdx = parseInt(previewStudentSelect?.value || "0");
        const student = state.studentRecords[studentIdx] || {
            NAME: "Alexander Morgan",
            COURSE: "Artificial Intelligence & Neural Architectures",
            DATE: "February 18, 2026",
            GRADE: "Grade A+",
            CERT_ID: "CERT-2026-9901"
        };

        fetch("/api/preview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                template_name: state.currentTemplate,
                student_data: student,
                fields_config: state.fields,
                clean_dummy_text: state.cleanDummyText
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.preview_image && previewCanvasImage) {
                previewCanvasImage.src = data.preview_image;
            }
        })
        .catch(() => {});
    }

    // --- Bulk Generation Engine ---
    function triggerBulkGeneration() {
        if (!state.studentRecords.length) {
            alert("No student records loaded. Please upload data in Step 1 first.");
            goToStep(1);
            return;
        }

        const exportFmt = document.querySelector('input[name="exportFormat"]:checked')?.value || "pdf";
        if (generationProgressContainer) generationProgressContainer.classList.remove("d-none");
        if (generationProgressBar) generationProgressBar.style.width = "40%";
        if (progressStatusText) progressStatusText.textContent = `Rendering ${state.studentRecords.length} certificates...`;
        if (progressCountText) progressCountText.textContent = "Processing...";

        // Trigger 3D Generation Experience
        if (window.showCertify3DLoader) {
            window.showCertify3DLoader({ totalRecords: state.studentRecords.length });
        }

        fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                template_name: state.currentTemplate,
                export_format: exportFmt,
                records: state.studentRecords,
                fields_config: state.fields,
                clean_dummy_text: state.cleanDummyText
            })
        })
        .then(res => res.json())
        .then(data => {
            if (generationProgressBar) generationProgressBar.style.width = "100%";
            if (progressCountText) progressCountText.textContent = "100%";
            if (progressStatusText) progressStatusText.textContent = "Complete!";

            if (data.success) {
                const finishUI = () => {
                    // Populate Step 5 Download Center
                    document.getElementById("sectionTotalCount").textContent = data.generated_count + data.failed_count;
                    document.getElementById("sectionSuccessCount").textContent = data.generated_count;
                    document.getElementById("sectionFailedCount").textContent = data.failed_count;

                    const combBtn = document.getElementById("sectionCombinedPdfBtn");
                    if (combBtn) combBtn.href = data.combined_pdf_url || "#";
                    const zipBtn = document.getElementById("sectionZipDownloadBtn");
                    if (zipBtn) zipBtn.href = data.zip_url || "#";

                    const tblBody = document.getElementById("sectionStudentTableBody");
                    if (tblBody && data.generated_records) {
                        tblBody.innerHTML = data.generated_records.map((r, i) => {
                            const file = r.files?.pdf || r.files?.png || "";
                            return `
                                <tr>
                                    <td class="text-center text-muted">${i + 1}</td>
                                    <td class="fw-bold text-light">${r.student_name}</td>
                                    <td>${r.course || ""}</td>
                                    <td><code>${r.cert_id || ""}</code></td>
                                    <td class="text-end pe-3">
                                        <a href="/download/certificate/${data.batch_id}/${file}" class="btn btn-sm btn-outline-primary rounded-pill px-3 py-0 fs-xs" download>
                                            <i class="fa-solid fa-download me-1"></i> Download
                                        </a>
                                    </td>
                                </tr>
                            `;
                        }).join("");
                    }

                    // Batch success modal
                    if (batchSuccessModal) {
                        document.getElementById("modalTotalCount").textContent = data.generated_count + data.failed_count;
                        document.getElementById("modalSuccessCount").textContent = data.generated_count;
                        document.getElementById("modalFailedCount").textContent = data.failed_count;
                        document.getElementById("modalCombinedPdfBtn").href = data.combined_pdf_url || "#";
                        document.getElementById("modalZipDownloadBtn").href = data.zip_url || "#";
                        batchSuccessModal.show();
                    }

                    goToStep(5);
                };

                if (window.completeCertify3DLoader) {
                    window.completeCertify3DLoader(finishUI);
                } else {
                    finishUI();
                }
            } else {
                if (window.hideCertify3DLoader) window.hideCertify3DLoader();
                alert(data.error || "Generation error.");
            }
        })
        .catch(err => {
            if (window.hideCertify3DLoader) window.hideCertify3DLoader();
            alert("Generation error: " + err.message);
        });
    }

    if (generateBulkBtn) generateBulkBtn.addEventListener("click", triggerBulkGeneration);
    if (stickyGenerateBtn) stickyGenerateBtn.addEventListener("click", triggerBulkGeneration);

    // Single PDF Downloads
    function downloadSinglePdf() {
        const studentIdx = parseInt(previewStudentSelect?.value || "0");
        const student = state.studentRecords[studentIdx] || {
            NAME: "Alexander Morgan",
            COURSE: "Certificate of Achievement",
            DATE: new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }),
            GRADE: "A+",
            CERT_ID: "CERT-2026-001"
        };

        if (window.showCertify3DLoader) {
            window.showCertify3DLoader({ totalRecords: 1 });
        }

        fetch("/api/generate-single-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                template_name: state.currentTemplate,
                student_data: student,
                fields_config: state.fields,
                clean_dummy_text: state.cleanDummyText
            })
        })
        .then(res => res.blob())
        .then(blob => {
            const doDownload = () => {
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = `${(student.NAME || "Certificate").replace(/[^a-zA-Z0-9]/g, '_')}_Certificate.pdf`;
                a.click();
            };
            if (window.completeCertify3DLoader) {
                window.completeCertify3DLoader(doDownload);
            } else {
                doDownload();
            }
        })
        .catch(err => {
            if (window.hideCertify3DLoader) window.hideCertify3DLoader();
            alert("Single PDF generation error: " + err.message);
        });
    }

    document.getElementById("directSinglePdfBtn")?.addEventListener("click", downloadSinglePdf);
    document.getElementById("stickySinglePdfBtn")?.addEventListener("click", downloadSinglePdf);
    document.getElementById("downloadPdfFromPreviewBtn")?.addEventListener("click", downloadSinglePdf);

    // Live preview popup modal
    document.getElementById("quickPreviewBtn")?.addEventListener("click", () => {
        const studentIdx = parseInt(previewStudentSelect?.value || "0");
        const student = state.studentRecords[studentIdx] || {
            NAME: "Alexander Morgan",
            COURSE: "Certificate of Achievement",
            DATE: new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }),
            GRADE: "A+",
            CERT_ID: "CERT-2026-001"
        };
        const modalImg = document.getElementById("previewModalImage");
        const spinner = document.getElementById("previewModalSpinner");
        if (spinner) spinner.classList.remove("d-none");
        if (modalImg) modalImg.classList.add("d-none");
        singlePreviewModal?.show();

        fetch("/api/preview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                template_name: state.currentTemplate,
                student_data: student,
                fields_config: state.fields,
                clean_dummy_text: state.cleanDummyText
            })
        })
        .then(r => r.json())
        .then(d => {
            if (spinner) spinner.classList.add("d-none");
            if (modalImg) {
                modalImg.src = d.preview_image;
                modalImg.classList.remove("d-none");
            }
        });
    });

    // Window resize updates pin scaling
    window.addEventListener("resize", () => {
        if (state.currentStep === 3) renderCanvasPins();
    });

    // Initial Load
    loadTemplateConfig("classic_gold.png");
});
