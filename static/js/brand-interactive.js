/**
 * brand-interactive.js
 * 3D Cinematic Brand Logo & Senior Graphic Designer 3D Studio Replay Orchestrator
 * Features: 8-Template 3D Orbital Carousel, Interactive Font Chooser, Liquid Text Animations
 */

(function () {
    "use strict";

    const FONT_PRESETS = {
        royal: {
            name: "Alexander Morgan",
            cardClass: "preset-royal",
            defaultAnim: "gold",
            headerText: "CERTIFICATE OF ACHIEVEMENT",
            subText: "PROUDLY PRESENTED TO"
        },
        serif: {
            name: "ALEXANDER MORGAN",
            cardClass: "preset-serif",
            defaultAnim: "gold",
            headerText: "CERTIFICATE OF EXCELLENCE",
            subText: "CONFERRED UPON"
        },
        vogue: {
            name: "Alexander Morgan",
            cardClass: "preset-vogue",
            defaultAnim: "rose",
            headerText: "HONORARY CITATION",
            subText: "PROUDLY PRESENTED TO"
        },
        script: {
            name: "Alexander Morgan",
            cardClass: "preset-script",
            defaultAnim: "gold",
            headerText: "CERTIFICATE OF ACCOMPLISHMENT",
            subText: "THIS RECOGNITION IS GRANTED TO"
        },
        cyber: {
            name: "ALEXANDER MORGAN",
            cardClass: "preset-cyber",
            defaultAnim: "cyber",
            headerText: "CREDENTIAL VERIFICATION",
            subText: "SYSTEM ACCREDITATION ISSUED TO"
        }
    };

    const TEXT_ANIMS = {
        gold: "text-anim-gold-foil",
        cyber: "text-anim-cyber-cyan",
        rose: "text-anim-rose-gold",
        diamond: "text-anim-diamond-flare"
    };

    const SAMPLE_NAMES = [
        "Alexander Morgan",
        "Dr. Elena Rostova",
        "Sophia Laurent",
        "Lord Arthur Vance",
        "Prof. Kenji Takahashi",
        "Olivia Kensington"
    ];

    let _currentPreset = "royal";
    let _currentAnim = "gold";
    let _isOrbitPaused = false;
    let _introDismissTimer = null;
    let _nameIdx = 0;

    function buildIntroSplashHTML() {
        return `
            <div id="appIntroSplash" class="intro-splash-screen" role="dialog" aria-modal="true" aria-label="CertifyAI 3D Opening Animation">
                <!-- 3D Perspective Grid Background & Ambient Lighting -->
                <div class="intro-spotlight-cone"></div>
                <div class="intro-3d-grid"></div>
                <div class="intro-ambient-orb orb-1"></div>
                <div class="intro-ambient-orb orb-2"></div>
                <div class="intro-ambient-orb orb-3"></div>

                <!-- Elegant Minimalist Corner Close Button -->
                <button type="button" class="intro-corner-close-btn" onclick="window.dismissCertifyIntro(event)" title="Exit 3D Studio (Esc)">
                    <i class="fa-solid fa-xmark"></i>
                </button>

                <!-- 3D Spatial Typographic Floating Watermarks in Background -->
                <div class="intro-spatial-badge sbadge-1">
                    <i class="fa-solid fa-certificate text-warning"></i> 300 DPI VECTOR ENGINE
                </div>
                <div class="intro-spatial-badge sbadge-2">
                    <i class="fa-solid fa-shield-halved text-primary"></i> CRYPTOGRAPHIC WATERMARK
                </div>
                <div class="intro-spatial-badge sbadge-3">
                    <i class="fa-solid fa-wand-magic-sparkles text-info"></i> 3D PERSPECTIVE PARALLAX
                </div>
                <div class="intro-spatial-badge sbadge-4">
                    <i class="fa-solid fa-layer-group text-success"></i> 8 TEMPLATES IN ORBIT
                </div>

                <!-- 3D Background Revolving Orbital Templates Carousel -->
                <div class="intro-bg-carousel-stage" id="introBgCarouselStage">
                    <div class="intro-bg-carousel-cylinder" id="introBgCarouselCylinder">
                        <!-- Card 0: Midnight Luxury -->
                        <div class="orbit-tpl-card tpl-card-0 active-tpl" data-index="0" data-tpl="sustainability_midnight.png" data-name="Midnight Luxury" onclick="window.setIntroTemplate('sustainability_midnight.png', 'Midnight Luxury')" title="Click to apply Midnight Luxury">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_midnight.png" alt="Midnight Luxury" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-gold">Midnight Luxury</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">MIDNIGHT LUXURY</span>
                            </div>
                        </div>

                        <!-- Card 1: Classic Gold -->
                        <div class="orbit-tpl-card tpl-card-1" data-index="1" data-tpl="classic_gold.png" data-name="Classic Gold" onclick="window.setIntroTemplate('classic_gold.png', 'Classic Gold')" title="Click to apply Classic Gold">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/classic_gold.png" alt="Classic Gold" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-gold">Classic Gold</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">CLASSIC GOLD</span>
                            </div>
                        </div>

                        <!-- Card 2: Cyan Guilloche -->
                        <div class="orbit-tpl-card tpl-card-2" data-index="2" data-tpl="sustainability_cyan.png" data-name="Cyan Guilloche" onclick="window.setIntroTemplate('sustainability_cyan.png', 'Cyan Guilloche')" title="Click to apply Cyan Guilloche">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_cyan.png" alt="Cyan Guilloche" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-cyan">Cyan Guilloche</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">CYAN GUILLOCHE</span>
                            </div>
                        </div>

                        <!-- Card 3: Royal Sapphire -->
                        <div class="orbit-tpl-card tpl-card-3" data-index="3" data-tpl="modern_blue.png" data-name="Royal Sapphire" onclick="window.setIntroTemplate('modern_blue.png', 'Royal Sapphire')" title="Click to apply Royal Sapphire">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/modern_blue.png" alt="Royal Sapphire" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-blue">Royal Sapphire</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">ROYAL SAPPHIRE</span>
                            </div>
                        </div>

                        <!-- Card 4: Vintage Slate -->
                        <div class="orbit-tpl-card tpl-card-4" data-index="4" data-tpl="sustainability_slate.png" data-name="Vintage Slate" onclick="window.setIntroTemplate('sustainability_slate.png', 'Vintage Slate')" title="Click to apply Vintage Slate">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_slate.png" alt="Vintage Slate" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-slate">Vintage Slate</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">VINTAGE SLATE</span>
                            </div>
                        </div>

                        <!-- Card 5: Security Lace -->
                        <div class="orbit-tpl-card tpl-card-5" data-index="5" data-tpl="sustainability_lace.png" data-name="Security Lace" onclick="window.setIntroTemplate('sustainability_lace.png', 'Security Lace')" title="Click to apply Security Lace">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_lace.png" alt="Security Lace" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-emerald">Security Lace</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">SECURITY LACE</span>
                            </div>
                        </div>

                        <!-- Card 6: Royal Academic -->
                        <div class="orbit-tpl-card tpl-card-6" data-index="6" data-tpl="sustainability_academic.png" data-name="Royal Academic" onclick="window.setIntroTemplate('sustainability_academic.png', 'Royal Academic')" title="Click to apply Royal Academic">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_academic.png" alt="Royal Academic" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-crimson">Royal Academic</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">ROYAL ACADEMIC</span>
                            </div>
                        </div>

                        <!-- Card 7: Modern Minimalist -->
                        <div class="orbit-tpl-card tpl-card-7" data-index="7" data-tpl="sustainability_modern.png" data-name="Modern Minimalist" onclick="window.setIntroTemplate('sustainability_modern.png', 'Modern Minimalist')" title="Click to apply Modern Minimalist">
                            <div class="orbit-tpl-card-face orbit-card-front">
                                <div class="orbit-tpl-media">
                                    <img src="/static/sample_templates/sustainability_modern.png" alt="Modern Minimalist" loading="eager">
                                    <div class="orbit-tpl-sheen"></div>
                                </div>
                                <div class="orbit-tpl-badge">
                                    <span class="orbit-badge-dot"></span>
                                    <span class="orbit-badge-text text-glow-modern">Modern Minimalist</span>
                                    <span class="orbit-badge-pill">★ 300 DPI</span>
                                </div>
                            </div>
                            <div class="orbit-tpl-card-face orbit-card-back">
                                <div class="orbit-back-seal"><i class="fa-solid fa-award"></i></div>
                                <span class="orbit-back-brand">CertifyAI</span>
                                <span class="orbit-back-tag">MODERN MINIMALIST</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3D Kinetic Typographic Orbital Rings (Text Effects in Background) -->
                <div class="intro-kinetic-orbit-ring ring-1"></div>
                <div class="intro-kinetic-orbit-ring-2 ring-2"></div>

                <!-- Main Content Stage -->
                <div class="intro-content-stage">
                    <!-- 3D Floating Certificate Stage -->
                    <div class="intro-3d-card-wrapper" id="intro3dCardWrapper">
                        <div class="intro-3d-card preset-royal" id="intro3dCard">
                            <!-- Layer 0: Template Background Art with Smooth Crossfade -->
                            <div class="card-3d-layer card-3d-bg-art">
                                <img id="intro3dCardBg" src="/static/sample_templates/sustainability_midnight.png" class="card-3d-bg-img" alt="Certificate Background Artwork">
                                <div class="card-3d-bg-overlay"></div>
                            </div>

                            <!-- Layer 1: Metallic Certificate Frame (Depth Z: 10px) -->
                            <div class="card-3d-layer card-3d-base">
                                <div class="card-border-gold"></div>
                                <div class="card-corner corner-tl"></div>
                                <div class="card-corner corner-tr"></div>
                                <div class="card-corner corner-bl"></div>
                                <div class="card-corner corner-br"></div>
                            </div>

                            <!-- Layer 2: 3D Holographic Ribbon & Badge (Depth Z: 45px) -->
                            <div class="card-3d-layer card-3d-ribbon">
                                <div class="intro-gold-seal">
                                    <div class="seal-outer-spin"></div>
                                    <i class="fa-solid fa-crown seal-icon"></i>
                                </div>
                            </div>

                            <!-- Layer 3: 3D Embossed Title & Student Name with Animated Typography (Depth Z: 75px) -->
                            <div class="card-3d-layer card-3d-content">
                                <div class="card-3d-header" id="intro3dHeader">CERTIFICATE OF ACHIEVEMENT</div>
                                <div class="card-3d-sub" id="intro3dSub">PROUDLY PRESENTED TO</div>
                                <div class="card-3d-name text-anim-gold-foil" id="intro3dName" title="Click to cycle typography fonts">Alexander Morgan</div>
                                <div class="card-3d-course" id="intro3dCourse">ARTIFICIAL INTELLIGENCE & NEURAL ARCHITECTURES</div>
                                <div class="card-3d-meta" id="intro3dMeta">
                                    <span class="meta-tag"><i class="fa-solid fa-circle-check text-warning me-1"></i>VERIFIED ACCREDITATION</span>
                                    <span class="meta-divider">•</span>
                                    <span class="meta-id">ID: CERT-2026-AI</span>
                                </div>
                            </div>

                            <!-- Holographic Foil & Light Sweep Overlay -->
                            <div class="card-3d-sheen"></div>
                            <div class="card-3d-glare" id="intro3dGlare"></div>
                        </div>
                        <!-- 3D Realistic Grounding Shadow -->
                        <div class="intro-3d-card-shadow" id="intro3dCardShadow"></div>
                    </div>

                    <!-- Grand Brand Heading with Senior Designer Typography -->
                    <div class="intro-brand-heading mt-3">
                        <h1 class="intro-title">
                            <span class="intro-word-certify">Certify</span><span class="intro-word-ai text-gradient">AI</span>
                        </h1>
                        <p class="intro-subtitle-pill">
                            <span class="badge-dot-cyan"></span>
                            <span>3D CINEMATIC REPLAY &bull; <strong id="introActiveTplName">Midnight Luxury</strong></span>
                        </p>
                    </div>
                </div>

                <!-- Floating Studio HUD: Bottom Controls & Hints -->
                <div class="intro-designer-hud-bottom">
                    <div class="intro-orbit-hint d-none d-md-block">
                        <span><i class="fa-solid fa-sparkles text-warning me-1"></i> Touch or click any revolving template to apply &bull; Double-click to inspect &bull; Press <strong>ESC</strong> to close</span>
                    </div>
                </div>
            </div>
        `;
    }

    // =========================================================================
    // PUBLIC INTERACTION CONTROLLERS: FONTS, ANIMATIONS, TEMPLATES, ORBIT
    // =========================================================================
    window.setIntroFontPreset = function (presetKey) {
        const card = document.getElementById("intro3dCard");
        const nameEl = document.getElementById("intro3dName");
        const headerEl = document.getElementById("intro3dHeader");
        const subEl = document.getElementById("intro3dSub");
        if (!card || !nameEl) return;

        const p = FONT_PRESETS[presetKey];
        if (!p) return;
        _currentPreset = presetKey;

        // Animate burst transformation
        card.classList.remove("card-font-morph-burst");
        void card.offsetWidth; // force reflow
        card.classList.add("card-font-morph-burst");

        // Swap classes
        Object.values(FONT_PRESETS).forEach(item => card.classList.remove(item.cardClass));
        card.classList.add(p.cardClass);

        nameEl.textContent = p.name;
        if (headerEl && p.headerText) headerEl.textContent = p.headerText;
        if (subEl && p.subText) subEl.textContent = p.subText;

        // Auto-switch to preset's curated default animation if user hasn't chosen manually
        if (p.defaultAnim) {
            window.setIntroTextAnimation(p.defaultAnim, false);
        }

        // Update active HUD button
        document.querySelectorAll("#introFontButtonGroup .intro-hud-btn").forEach(btn => {
            if (btn.getAttribute("data-preset") === presetKey) btn.classList.add("active");
            else btn.classList.remove("active");
        });

        if (_introDismissTimer) {
            clearTimeout(_introDismissTimer);
            _introDismissTimer = null;
        }
    };

    window.setIntroTextAnimation = function (animKey, cancelTimer = true) {
        const nameEl = document.getElementById("intro3dName");
        if (!nameEl) return;

        const animClass = TEXT_ANIMS[animKey];
        if (!animClass) return;
        _currentAnim = animKey;

        Object.values(TEXT_ANIMS).forEach(cls => nameEl.classList.remove(cls));
        nameEl.classList.add(animClass);

        document.querySelectorAll(".intro-anim-btn").forEach(btn => {
            if (btn.getAttribute("data-anim") === animKey) btn.classList.add("active");
            else btn.classList.remove("active");
        });

        if (cancelTimer && _introDismissTimer) {
            clearTimeout(_introDismissTimer);
            _introDismissTimer = null;
        }
    };

    window.setIntroTemplate = function (tplFile, tplName) {
        const bgImg = document.getElementById("intro3dCardBg");
        const nameBadge = document.getElementById("introActiveTplName");
        if (bgImg) {
            bgImg.src = `/static/sample_templates/${tplFile}`;
            bgImg.style.opacity = "0.78";
        }
        if (nameBadge) nameBadge.textContent = tplName;

        document.querySelectorAll(".orbit-tpl-card").forEach(c => {
            if (c.getAttribute("data-tpl") === tplFile) c.classList.add("active-tpl");
            else c.classList.remove("active-tpl");
        });

        if (_introDismissTimer) {
            clearTimeout(_introDismissTimer);
            _introDismissTimer = null;
        }
    };

    window.toggleIntroOrbit = function () {
        const cylinder = document.getElementById("introBgCarouselCylinder");
        const btn = document.getElementById("introOrbitToggleBtn");
        if (!cylinder) return;

        _isOrbitPaused = !_isOrbitPaused;
        if (_isOrbitPaused) {
            cylinder.classList.add("is-paused");
            if (btn) btn.innerHTML = '<i class="fa-solid fa-play text-warning"></i> <span class="d-none d-lg-inline">Orbit</span>';
        } else {
            cylinder.classList.remove("is-paused");
            if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i> <span class="d-none d-lg-inline">Orbit</span>';
        }

        if (_introDismissTimer) {
            clearTimeout(_introDismissTimer);
            _introDismissTimer = null;
        }
    };

    let _isZoomedInspect = false;
    window.toggleIntroZoom = function () {
        const wrapper = document.getElementById("intro3dCardWrapper");
        const btn = document.getElementById("introZoomToggleBtn");
        if (!wrapper) return;

        _isZoomedInspect = !_isZoomedInspect;
        if (_isZoomedInspect) {
            wrapper.classList.add("is-zoomed-inspect");
            if (btn) btn.innerHTML = '<i class="fa-solid fa-magnifying-glass-minus text-warning"></i> <span class="d-none d-sm-inline">Zoom Out</span>';
        } else {
            wrapper.classList.remove("is-zoomed-inspect");
            if (btn) btn.innerHTML = '<i class="fa-solid fa-magnifying-glass-plus text-warning"></i> <span class="d-none d-sm-inline">Zoom</span>';
        }

        if (_introDismissTimer) {
            clearTimeout(_introDismissTimer);
            _introDismissTimer = null;
        }
    };

    window.cycleIntroFontOrName = function () {
        const presetKeys = Object.keys(FONT_PRESETS);
        const nextIdx = (presetKeys.indexOf(_currentPreset) + 1) % presetKeys.length;
        window.setIntroFontPreset(presetKeys[nextIdx]);
    };

    // =========================================================================
    // 3D OPENING SPLASH PARALLAX & LIFECYCLE
    // =========================================================================
    function setup3dOpeningSplash(force = false) {
        const splashEl = document.getElementById("appIntroSplash");
        if (!splashEl) return;

        const card = document.getElementById("intro3dCard");
        const glare = document.getElementById("intro3dGlare");
        const cylinder = document.getElementById("introBgCarouselCylinder");
        const nameEl = document.getElementById("intro3dName");

        // Click recipient name to cycle fonts with text animations
        if (nameEl) {
            nameEl.addEventListener("click", (e) => {
                e.stopPropagation();
                window.cycleIntroFontOrName();
            });
        }

        // Instant touch / click handler on revolving orbit cards (no dragging required)
        const orbitCards = splashEl.querySelectorAll(".orbit-tpl-card");
        orbitCards.forEach(cardEl => {
            const tplFile = cardEl.getAttribute("data-tpl");
            const tplName = cardEl.getAttribute("data-name");

            const activate = (e) => {
                e.stopPropagation();
                window.setIntroTemplate(tplFile, tplName);
            };

            cardEl.addEventListener("pointerdown", activate);
            cardEl.addEventListener("click", activate);
        });

        // 3D Parallax Tilt on Mouse Move (Central card only; cylinder keeps spinning purely via GPU keyframes)
        splashEl.addEventListener("mousemove", (e) => {
            if (!card || splashEl.classList.contains("splash-dismissed")) return;
            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;
            const dx = (e.clientX - cx) / cx;
            const dy = (e.clientY - cy) / cy;

            const rotX = -dy * 24;
            const rotY = dx * 24;
            card.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.04, 1.04, 1.04)`;

            if (glare) {
                const px = (e.clientX / window.innerWidth) * 100;
                const py = (e.clientY / window.innerHeight) * 100;
                glare.style.background = `radial-gradient(circle at ${px}% ${py}%, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.08) 50%, transparent 80%)`;
            }

            // User is actively exploring: pause auto-dismiss
            if (_introDismissTimer) {
                clearTimeout(_introDismissTimer);
                _introDismissTimer = null;
            }
        });

        splashEl.addEventListener("mouseleave", () => {
            if (card) card.style.transform = "";
        });

        // Double-click central certificate to toggle close-up inspection zoom
        if (card) {
            card.addEventListener("dblclick", (e) => {
                e.stopPropagation();
                window.toggleIntroZoom();
            });
        }

        const dismiss = () => {
            if (splashEl.classList.contains("splash-dismissed")) return;
            splashEl.classList.add("splash-dismissed");
            if (card) {
                card.style.transition = "transform 0.45s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.45s ease";
                card.style.transform = "rotateX(0deg) rotateY(0deg) scale3d(1.4, 1.4, 1.4) translateZ(120px)";
                card.style.opacity = "0";
            }
            setTimeout(() => { if (splashEl.parentNode) splashEl.remove(); }, 450);
        };

        window.dismissCertifyIntro = function (e) {
            if (e && e.stopPropagation) e.stopPropagation();
            dismiss();
        };

        // Only dismiss when clicking directly on the empty background backdrop
        splashEl.addEventListener("click", (e) => {
            if (e.target === splashEl) dismiss();
        });

        window.addEventListener("keydown", (e) => {
            if (e.key === "Escape") dismiss();
            if (e.key === "z" || e.key === "Z") window.toggleIntroZoom();
        });

        // Auto-dismiss logic:
        // When force == true (user clicked "3D Play"), do NOT auto-dismiss so they can freely explore!
        // When force == false (first load of the app), give a generous 16s window, cancellable by any mouse movement
        if (!force) {
            _introDismissTimer = setTimeout(dismiss, 16000);
        }
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

        const splashHtml = buildIntroSplashHTML();
        document.body.insertAdjacentHTML("afterbegin", splashHtml);
        setup3dOpeningSplash(true);
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
