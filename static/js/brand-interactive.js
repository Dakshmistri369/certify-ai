/**
 * brand-interactive.js
 * 3D Cinematic Brand Logo & Interactive Opening Splash Orchestrator
 */

(function () {
    "use strict";

    function initBrandExperience() {
        setup3dOpeningSplash();
        setupInteractiveNavLogo();
    }

    function setup3dOpeningSplash() {
        const splashEl = document.getElementById("appIntroSplash");
        if (!splashEl) return;

        const card = document.getElementById("intro3dCard");
        const glare = document.getElementById("intro3dGlare");
        const statusText = document.getElementById("introStatusText");

        const statusSteps = [
            { time: 100, text: "STARTING UP..." },
            { time: 500, text: "LOADING STUDIO..." },
            { time: 900, text: "READY!" }
        ];

        statusSteps.forEach(s => {
            setTimeout(() => {
                if (statusText && !splashEl.classList.contains("splash-dismissed")) {
                    statusText.textContent = s.text;
                }
            }, s.time);
        });

        // 3D Parallax Tilt on Mouse Move
        splashEl.addEventListener("mousemove", (e) => {
            if (!card || splashEl.classList.contains("splash-dismissed")) return;
            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;
            const dx = (e.clientX - cx) / cx;
            const dy = (e.clientY - cy) / cy;

            const rotX = -dy * 28;
            const rotY = dx * 28;
            card.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.05, 1.05, 1.05)`;

            if (glare) {
                const px = (e.clientX / window.innerWidth) * 100;
                const py = (e.clientY / window.innerHeight) * 100;
                glare.style.background = `radial-gradient(circle at ${px}% ${py}%, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.05) 50%, transparent 80%)`;
            }
        });

        splashEl.addEventListener("mouseleave", () => {
            if (card) card.style.transform = "";
        });

        const dismiss = () => {
            if (splashEl.classList.contains("splash-dismissed")) return;
            splashEl.classList.add("splash-dismissed");
            if (card) {
                card.style.transition = "transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s ease";
                card.style.transform = "rotateX(0deg) rotateY(0deg) scale3d(1.8, 1.8, 1.8) translateZ(200px)";
                card.style.opacity = "0";
            }
            setTimeout(() => { if (splashEl.parentNode) splashEl.remove(); }, 450);
        };

        splashEl.addEventListener("click", dismiss);
        window.addEventListener("keydown", (e) => {
            if (e.key === "Escape" || e.key === " ") dismiss();
        });

        // Auto dismiss after 1.5s for fast loading
        setTimeout(dismiss, 1500);
    }

    function setupInteractiveNavLogo() {
        const logoWrapper = document.getElementById("brandLogoWrapper");
        const logoBadge = document.getElementById("interactiveBrandLogo");
        if (!logoWrapper || !logoBadge) return;

        logoWrapper.addEventListener("mousemove", (e) => {
            const rect = logoWrapper.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            logoBadge.style.transform = `rotateX(${-y * 24}deg) rotateY(${x * 24}deg) scale(1.1)`;
        });

        logoWrapper.addEventListener("mouseleave", () => {
            logoBadge.style.transform = "rotateX(0deg) rotateY(0deg) scale(1)";
        });

        logoWrapper.addEventListener("click", () => {
            logoBadge.style.transition = "transform 0.5s ease";
            logoBadge.style.transform = "rotate(360deg) scale(1.15)";
            setTimeout(() => {
                logoBadge.style.transform = "rotate(0deg) scale(1)";
                setTimeout(() => { logoBadge.style.transition = ""; }, 300);
            }, 500);
        });
    }

    window.replayCertifyIntro = function () {
        const existing = document.getElementById("appIntroSplash");
        if (existing) existing.remove();

        const splashHtml = `
            <div id="appIntroSplash" class="intro-splash-screen" role="dialog" aria-modal="true" aria-label="CertifyAI 3D Opening Animation">
                <div class="intro-3d-grid"></div>
                <div class="intro-ambient-orb orb-1"></div>
                <div class="intro-ambient-orb orb-2"></div>
                
                <div class="intro-content-stage">
                    <div class="intro-3d-card-wrapper" id="intro3dCardWrapper">
                        <div class="intro-3d-card" id="intro3dCard">
                            <div class="card-3d-layer card-3d-base">
                                <div class="card-border-gold"></div>
                                <div class="card-corner corner-tl"></div>
                                <div class="card-corner corner-tr"></div>
                                <div class="card-corner corner-bl"></div>
                                <div class="card-corner corner-br"></div>
                            </div>
                            <div class="card-3d-layer card-3d-ribbon">
                                <div class="intro-gold-seal">
                                    <div class="seal-outer-spin"></div>
                                    <i class="fa-solid fa-crown seal-icon"></i>
                                </div>
                            </div>
                            <div class="card-3d-layer card-3d-content">
                                <div class="card-3d-header">CERTIFICATE OF ACHIEVEMENT</div>
                                <div class="card-3d-sub">PROUDLY PRESENTED TO</div>
                                <div class="card-3d-name">Alexander Morgan</div>
                                <div class="card-3d-course">ARTIFICIAL INTELLIGENCE & NEURAL ARCHITECTURES</div>
                            </div>
                            <div class="card-3d-sheen"></div>
                            <div class="card-3d-glare" id="intro3dGlare"></div>
                        </div>
                        <div class="intro-orbit-ring ring-1"></div>
                        <div class="intro-orbit-ring ring-2"></div>
                    </div>

                    <div class="intro-brand-heading mt-4">
                        <h1 class="intro-title">
                            <span class="intro-word-certify">Certify</span><span class="intro-word-ai text-gradient">AI</span>
                        </h1>
                        <div class="intro-badge-pill">
                            <span class="intro-pulse-dot"></span> 300 DPI 3D STUDIO ENGINE
                        </div>
                    </div>

                    <p class="intro-tagline">Smart Certificate Generation Studio</p>

                    <div class="intro-progress-container">
                        <div class="intro-progress-track">
                            <div class="intro-progress-fill" id="introProgressBar"></div>
                        </div>
                        <div class="intro-status-text" id="introStatusText">INITIALIZING 3D ENGINE...</div>
                    </div>
                    <div class="intro-skip-hint">Click anywhere or press Space to skip</div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML("afterbegin", splashHtml);
        setup3dOpeningSplash();
    };

    // =========================================================================
    // 3D CINEMATIC GENERATION ENGINE CONTROLLER & TOUCH/MOUSE PARALLAX
    // =========================================================================
    let _genProgressTimer = null;
    let _currentGenPercent = 0;

    function setup3dGenLoaderParallax() {
        const overlay = document.getElementById("certify3dGenOverlay");
        const stage = document.getElementById("gen3dStage");
        const medallion = document.getElementById("gen3dMedallion");
        if (!overlay || !stage) return;

        function handleParallax(clientX, clientY) {
            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;
            const dx = (clientX - cx) / cx;
            const dy = (clientY - cy) / cy;

            const rotX = -dy * 18;
            const rotY = dx * 18;
            stage.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(30px)`;
            if (medallion) {
                medallion.style.transform = `translateZ(55px) rotateX(${rotX * 1.3}deg) rotateY(${rotY * 1.3}deg)`;
            }
        }

        // Mouse Move Parallax
        overlay.addEventListener("mousemove", (e) => {
            handleParallax(e.clientX, e.clientY);
        });

        // Touch Move Parallax for Mobile / Tablet
        overlay.addEventListener("touchmove", (e) => {
            if (e.touches && e.touches[0]) {
                handleParallax(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: true });

        overlay.addEventListener("mouseleave", () => {
            if (stage) stage.style.transform = "rotateX(0deg) rotateY(0deg) translateZ(0)";
            if (medallion) medallion.style.transform = "";
        });

        // Touch Medallion for 360 Spin Sparkle Easter Egg
        if (medallion) {
            medallion.addEventListener("click", () => {
                medallion.style.transition = "transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)";
                medallion.style.transform = "translateZ(80px) rotateY(360deg) scale(1.15)";
                setTimeout(() => {
                    medallion.style.transition = "";
                    medallion.style.transform = "";
                }, 600);
            });
        }
    }

    window.showCertify3DLoader = function (options = {}) {
        const overlay = document.getElementById("certify3dGenOverlay");
        if (!overlay) return;

        const totalRecords = options.totalRecords || 1;
        const totalCountEl = document.getElementById("gen3dTotalCount");
        const procCountEl = document.getElementById("gen3dProcessedCount");
        const progressFill = document.getElementById("gen3dProgressFill");
        const percentEl = document.getElementById("gen3dPercent");
        const stepText = document.getElementById("gen3dStepText");
        const statusMsg = document.getElementById("gen3dStatusMsg");

        if (totalCountEl) totalCountEl.textContent = totalRecords;
        if (procCountEl) procCountEl.textContent = "0";
        if (progressFill) progressFill.style.width = "4%";
        if (percentEl) percentEl.textContent = "4%";

        _currentGenPercent = 4;
        overlay.classList.add("active");

        const steps = [
            { pct: 20, step: "READING DATA", msg: `Processing ${totalRecords} student record${totalRecords > 1 ? 's' : ''}...` },
            { pct: 50, step: "GENERATING", msg: `Creating ${totalRecords} personalised certificate${totalRecords > 1 ? 's' : ''}...` },
            { pct: 75, step: "FINALISING", msg: "Adding seals, signatures & unique IDs..." },
            { pct: 90, step: "SAVING", msg: "Archiving & syncing to MongoDB Atlas..." }
        ];

        let stepIndex = 0;
        clearInterval(_genProgressTimer);

        _genProgressTimer = setInterval(() => {
            if (_currentGenPercent < 92) {
                _currentGenPercent += Math.max(1, Math.round((92 - _currentGenPercent) / 8));
                if (progressFill) progressFill.style.width = `${_currentGenPercent}%`;
                if (percentEl) percentEl.textContent = `${_currentGenPercent}%`;

                // Update items count dynamically
                const processed = Math.min(totalRecords, Math.ceil((_currentGenPercent / 100) * totalRecords));
                if (procCountEl) procCountEl.textContent = processed;

                // Step Progression
                if (stepIndex < steps.length && _currentGenPercent >= steps[stepIndex].pct) {
                    if (stepText) stepText.textContent = steps[stepIndex].step;
                    if (statusMsg) statusMsg.textContent = steps[stepIndex].msg;
                    stepIndex++;
                }
            }
        }, 180);
    };

    window.completeCertify3DLoader = function (onComplete) {
        clearInterval(_genProgressTimer);
        const overlay = document.getElementById("certify3dGenOverlay");
        const progressFill = document.getElementById("gen3dProgressFill");
        const percentEl = document.getElementById("gen3dPercent");
        const stepText = document.getElementById("gen3dStepText");
        const statusMsg = document.getElementById("gen3dStatusMsg");
        const totalCountEl = document.getElementById("gen3dTotalCount");
        const procCountEl = document.getElementById("gen3dProcessedCount");
        const medallion = document.getElementById("gen3dMedallion");

        if (progressFill) progressFill.style.width = "100%";
        if (percentEl) percentEl.textContent = "100%";
        if (stepText) stepText.textContent = "COMPLETE";
        if (statusMsg) statusMsg.textContent = "All certificates generated & archived successfully! 🎉";
        if (totalCountEl && procCountEl) procCountEl.textContent = totalCountEl.textContent;

        if (medallion) {
            medallion.style.boxShadow = "0 0 50px rgba(16, 185, 129, 0.9), inset 0 0 35px rgba(255, 255, 255, 0.8)";
            medallion.style.borderColor = "#10b981";
        }

        setTimeout(() => {
            if (overlay) overlay.classList.remove("active");
            if (medallion) {
                medallion.style.boxShadow = "";
                medallion.style.borderColor = "";
            }
            if (typeof onComplete === "function") {
                onComplete();
            }
        }, 550);
    };

    window.hideCertify3DLoader = function () {
        clearInterval(_genProgressTimer);
        const overlay = document.getElementById("certify3dGenOverlay");
        if (overlay) overlay.classList.remove("active");
    };

    function initBrandExperience() {
        setup3dOpeningSplash();
        setupInteractiveNavLogo();
        setup3dGenLoaderParallax();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initBrandExperience);
    } else {
        initBrandExperience();
    }
})();
