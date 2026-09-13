/**
 * effects.js
 * Premium Micro-interactions & UI Enhancements for CertifyAI
 * Fast, GPU-accelerated, and visually stunning
 */

(function () {
    "use strict";

    function ready(fn) {
        if (document.readyState !== "loading") fn();
        else document.addEventListener("DOMContentLoaded", fn);
    }

    ready(function () {
        initScrollProgress();
        initButtonRipples();
        initScrollReveal();
        initCardTilt3D();
        initAnimatedCounters();
        initCursorGlow();
        initPageTransitions();
        injectPremiumStyles();
    });

    // =========================================================================
    // SCROLL PROGRESS BAR
    // =========================================================================
    function initScrollProgress() {
        const bar = document.createElement("div");
        bar.id = "scrollProgressBar";
        bar.style.cssText = "position:fixed;top:0;left:0;width:100%;height:3px;background:linear-gradient(90deg,#2563eb,#60a5fa,#f59e0b);z-index:9999;transform-origin:left;transform:scaleX(0);pointer-events:none;transition:opacity .3s;";
        document.body.appendChild(bar);

        let ticking = false;
        window.addEventListener("scroll", () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const h = document.documentElement.scrollHeight - window.innerHeight;
                    bar.style.transform = `scaleX(${h > 0 ? Math.min(1, window.scrollY / h) : 0})`;
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    // =========================================================================
    // BUTTON RIPPLE EFFECTS
    // =========================================================================
    function initButtonRipples() {
        document.addEventListener("pointerdown", (e) => {
            const btn = e.target.closest(".btn");
            if (!btn) return;
            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height) * 2;
            const rip = document.createElement("span");
            rip.className = "btn-ripple-fx";
            rip.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px`;
            btn.appendChild(rip);
            setTimeout(() => rip.remove(), 600);
        }, { passive: true });
    }

    // =========================================================================
    // SCROLL REVEAL ANIMATIONS (IntersectionObserver for performance)
    // =========================================================================
    function initScrollReveal() {
        const revealEls = document.querySelectorAll(
            ".card-custom, .stepper-wrapper, .upload-dropzone, .tpl-gallery-card, .badge, h1, h2, h3, .btn-generate-3d, table, .alert"
        );

        if (!("IntersectionObserver" in window)) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("reveal-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

        revealEls.forEach((el, i) => {
            el.classList.add("reveal-item");
            el.style.transitionDelay = `${Math.min(i * 0.04, 0.35)}s`;
            observer.observe(el);
        });
    }

    // =========================================================================
    // 3D CARD TILT ON HOVER
    // =========================================================================
    function initCardTilt3D() {
        document.querySelectorAll(".card-custom").forEach(card => {
            let raf = null;

            card.addEventListener("mousemove", (e) => {
                cancelAnimationFrame(raf);
                raf = requestAnimationFrame(() => {
                    const rect = card.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / rect.width - 0.5;
                    const y = (e.clientY - rect.top) / rect.height - 0.5;
                    card.style.transform = `perspective(800px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg) translateZ(4px)`;
                    card.style.boxShadow = `${-x * 12}px ${y * 12}px 30px rgba(0,0,0,0.6), 0 0 20px rgba(37,99,235,0.12)`;
                });
            }, { passive: true });

            const reset = () => {
                cancelAnimationFrame(raf);
                card.style.transform = "";
                card.style.boxShadow = "";
            };
            card.addEventListener("mouseleave", reset, { passive: true });
            card.addEventListener("touchend", reset, { passive: true });
        });
    }

    // =========================================================================
    // ANIMATED STAT COUNTERS
    // =========================================================================
    function initAnimatedCounters() {
        const counterEls = document.querySelectorAll("[data-count]");
        if (!counterEls.length || !("IntersectionObserver" in window)) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                const target = parseInt(el.getAttribute("data-count"), 10);
                const duration = 1200;
                const start = performance.now();
                observer.unobserve(el);

                function tick(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    el.textContent = Math.round(eased * target).toLocaleString();
                    if (progress < 1) requestAnimationFrame(tick);
                }
                requestAnimationFrame(tick);
            });
        }, { threshold: 0.5 });

        counterEls.forEach(el => observer.observe(el));
    }

    // =========================================================================
    // SUBTLE CURSOR GLOW (desktop only, hardware accelerated)
    // =========================================================================
    function initCursorGlow() {
        if (window.matchMedia("(pointer: coarse)").matches) return; // skip touch

        const glow = document.createElement("div");
        glow.id = "cursorGlow";
        glow.style.cssText = "pointer-events:none;position:fixed;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,0.07) 0%,transparent 70%);transform:translate(-50%,-50%) translateZ(0);z-index:9998;transition:opacity .3s;will-change:transform;";
        document.body.appendChild(glow);

        let mx = -999, my = -999, raf = null;

        window.addEventListener("mousemove", (e) => {
            mx = e.clientX;
            my = e.clientY;
            if (!raf) {
                raf = requestAnimationFrame(() => {
                    glow.style.transform = `translate(${mx - 150}px, ${my - 150}px) translateZ(0)`;
                    raf = null;
                });
            }
        }, { passive: true });

        document.addEventListener("mouseleave", () => { glow.style.opacity = "0"; });
        document.addEventListener("mouseenter", () => { glow.style.opacity = "1"; });
    }

    // =========================================================================
    // PAGE LOAD ENTRANCE ANIMATION
    // =========================================================================
    function initPageTransitions() {
        // Fade main content in smoothly after splash
        const main = document.querySelector("main");
        if (main) {
            main.style.opacity = "0";
            main.style.transform = "translateY(12px)";
            main.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            setTimeout(() => {
                main.style.opacity = "1";
                main.style.transform = "translateY(0)";
            }, 100);
        }

        // Navbar entrance
        const nav = document.querySelector("header");
        if (nav) {
            nav.style.opacity = "0";
            nav.style.transform = "translateY(-100%)";
            nav.style.transition = "opacity 0.4s ease, transform 0.4s cubic-bezier(0.16,1,0.3,1)";
            setTimeout(() => {
                nav.style.opacity = "1";
                nav.style.transform = "translateY(0)";
            }, 50);
        }
    }

    // =========================================================================
    // INJECT PREMIUM STYLES
    // =========================================================================
    function injectPremiumStyles() {
        const style = document.createElement("style");
        style.textContent = `
            /* Button Ripple */
            .btn { position: relative; overflow: hidden; }
            .btn-ripple-fx {
                position: absolute; border-radius: 50%;
                background: rgba(255,255,255,0.22);
                transform: scale(0);
                animation: brf 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
                pointer-events: none;
            }
            @keyframes brf { to { transform: scale(1); opacity: 0; } }

            /* Scroll Reveal */
            .reveal-item {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.55s cubic-bezier(0.16,1,0.3,1), transform 0.55s cubic-bezier(0.16,1,0.3,1);
                will-change: opacity, transform;
            }
            .reveal-visible {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }

            /* Card 3D tilt transition */
            .card-custom {
                transition: transform 0.12s ease, box-shadow 0.12s ease !important;
                will-change: transform;
            }

            /* Glowing focus for inputs */
            .form-control:focus, .form-select:focus {
                box-shadow: 0 0 0 3px rgba(37,99,235,0.3) !important;
                border-color: #3b82f6 !important;
                transition: box-shadow 0.2s ease, border-color 0.2s ease;
            }

            /* Enhanced nav link transitions */
            .nav-link { transition: color 0.18s ease, background-color 0.18s ease !important; }
            .nav-link:hover { transform: none !important; }

            /* Smooth badge pulse */
            @keyframes badgePulse {
                0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
                50% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
            }
            .spinner-grow { animation-duration: 1.2s !important; }

            /* Premium button hover glow */
            .btn-primary:hover {
                box-shadow: 0 4px 20px rgba(37,99,235,0.45) !important;
                transform: translateY(-1px);
                transition: all 0.2s ease;
            }
            .btn-outline-light:hover, .btn-outline-secondary:hover {
                transform: translateY(-1px);
                transition: all 0.2s ease;
            }

            /* Table row hover with glow */
            .table-hover tbody tr {
                transition: background-color 0.15s ease;
            }

            /* Intro fill faster */
            .intro-progress-fill {
                animation-duration: 1.4s !important;
            }

            /* Smooth page-level fade */
            body { transition: opacity 0.3s ease; }
        `;
        document.head.appendChild(style);
    }

})();
