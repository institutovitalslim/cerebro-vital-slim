/* IVS Motion Layer v0.1 — Instituto Vital Slim
   Implementação própria: integra Lenis, GSAP e Vanta de modo opcional e governado. */
(function () {
  'use strict';

  var DEFAULTS = {
    lenis: true,
    gsap: true,
    vanta: false,
    profile: 'presentation',
    debug: false,
    cdn: {
      lenis: 'https://cdn.jsdelivr.net/npm/lenis@1.3.25/dist/lenis.min.js',
      gsap: 'https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js',
      scrollTrigger: 'https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js',
      three: 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js',
      vantaWaves: 'https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.waves.min.js'
    }
  };

  function log(level, message, data) {
    if (!window.IVSMotionConfig || window.IVSMotionConfig.debug || level !== 'debug') {
      var fn = console[level] || console.info;
      fn.call(console, '[IVS Motion] ' + message, data || '');
    }
  }

  function mergeConfig() {
    var cfg = window.IVSMotionConfig || {};
    var merged = Object.assign({}, DEFAULTS, cfg);
    merged.cdn = Object.assign({}, DEFAULTS.cdn, cfg.cdn || {});
    return merged;
  }

  function reducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function loadScript(src, id) {
    return new Promise(function (resolve, reject) {
      if (id && document.getElementById(id)) return resolve();
      var s = document.createElement('script');
      s.src = src;
      if (id) s.id = id;
      s.async = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error('Falha ao carregar ' + src)); };
      document.head.appendChild(s);
    });
  }

  function splitTitles(root) {
    root.querySelectorAll('[data-ivs-motion="split-title"]').forEach(function (el) {
      if (el.dataset.ivsSplitDone === '1') return;
      var text = el.textContent.trim();
      el.setAttribute('aria-label', text);
      el.innerHTML = text.split(/\s+/).map(function (word) {
        return '<span class="ivs-motion-word">' + word.replace(/[&<>]/g, function (c) {
          return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];
        }) + '</span>';
      }).join(' ');
      el.dataset.ivsSplitDone = '1';
    });
  }

  function prepareDOM(root) {
    document.documentElement.classList.add('ivs-motion-ready');
    document.body.classList.add('ivs-motion-pending');
    splitTitles(root);
    root.querySelectorAll('[data-ivs-progress]').forEach(function (el) {
      el.classList.add('ivs-motion-progress');
      el.style.setProperty('--ivs-progress', '0%');
    });
    root.querySelectorAll('[data-ivs-counter]').forEach(function (el) {
      el.classList.add('ivs-motion-counter');
    });
  }

  function initLenis(cfg) {
    if (!cfg.lenis || reducedMotion() || window.Lenis === undefined) return null;
    var lenis = new window.Lenis({
      autoRaf: false,
      smoothWheel: true,
      anchors: true,
      lerp: cfg.profile === 'landing' ? 0.08 : 0.11
    });
    document.documentElement.classList.add('ivs-lenis', 'ivs-lenis-smooth');
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
    window.__IVS_LENIS__ = lenis;
    return lenis;
  }

  function animateWithoutGSAP(root) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'none';
        entry.target.style.transition = 'opacity var(--ivs-motion-duration) var(--ivs-motion-ease), transform var(--ivs-motion-duration) var(--ivs-motion-ease)';
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.14 });
    root.querySelectorAll('[data-ivs-motion="fade-up"], [data-ivs-motion="card"], .ivs-motion-section').forEach(function (el) {
      observer.observe(el);
    });
    root.querySelectorAll('[data-ivs-progress]').forEach(function (el) {
      el.style.setProperty('--ivs-progress', Math.max(0, Math.min(100, Number(el.dataset.ivsProgress || 0))) + '%');
    });
    root.querySelectorAll('[data-ivs-counter]').forEach(function (el) {
      el.textContent = (el.dataset.prefix || '') + el.dataset.ivsCounter + (el.dataset.suffix || '');
    });
  }

  function initGSAP(root) {
    if (reducedMotion() || !window.gsap) {
      animateWithoutGSAP(root);
      return;
    }
    var gsap = window.gsap;
    if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);

    gsap.utils.toArray('[data-ivs-motion="fade-up"], .ivs-motion-section').forEach(function (el, i) {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.78,
        ease: 'power3.out',
        delay: Math.min(i * 0.025, 0.2),
        scrollTrigger: window.ScrollTrigger ? { trigger: el, start: 'top 86%', once: true } : undefined
      });
    });

    gsap.utils.toArray('[data-ivs-motion="card"]').forEach(function (el, i) {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        rotateX: 0,
        duration: 0.68,
        ease: 'power2.out',
        delay: Math.min(i * 0.04, 0.26),
        scrollTrigger: window.ScrollTrigger ? { trigger: el, start: 'top 88%', once: true } : undefined
      });
    });

    gsap.utils.toArray('[data-ivs-motion="split-title"] .ivs-motion-word').forEach(function (word, i) {
      gsap.fromTo(word, { opacity: 0, y: 18, rotate: 1.5 }, {
        opacity: 1,
        y: 0,
        rotate: 0,
        duration: 0.52,
        ease: 'power3.out',
        delay: i * 0.025,
        scrollTrigger: window.ScrollTrigger ? { trigger: word.parentElement, start: 'top 88%', once: true } : undefined
      });
    });

    gsap.utils.toArray('[data-ivs-counter]').forEach(function (el) {
      var target = Number(el.dataset.ivsCounter || '0');
      var decimals = (String(el.dataset.ivsCounter || '').split('.')[1] || '').length;
      var obj = { value: 0 };
      gsap.to(obj, {
        value: target,
        duration: 1.35,
        ease: 'power2.out',
        onUpdate: function () {
          el.textContent = (el.dataset.prefix || '') + obj.value.toLocaleString('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
          }) + (el.dataset.suffix || '');
        },
        scrollTrigger: window.ScrollTrigger ? { trigger: el, start: 'top 90%', once: true } : undefined
      });
    });

    gsap.utils.toArray('[data-ivs-progress]').forEach(function (el) {
      var value = Math.max(0, Math.min(100, Number(el.dataset.ivsProgress || 0)));
      gsap.to(el, {
        '--ivs-progress': value + '%',
        duration: 1.1,
        ease: 'power2.out',
        scrollTrigger: window.ScrollTrigger ? { trigger: el, start: 'top 92%', once: true } : undefined
      });
    });
  }

  function initVanta(cfg) {
    if (!cfg.vanta || reducedMotion() || !window.VANTA || !window.VANTA.WAVES) return null;
    var nodes = document.querySelectorAll('[data-ivs-vanta]');
    nodes.forEach(function (el) {
      if (el.dataset.ivsVantaDone === '1') return;
      window.VANTA.WAVES({
        el: el,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 220.00,
        minWidth: 220.00,
        scale: 1.0,
        scaleMobile: 1.0,
        color: 0x182326,
        shininess: 18.0,
        waveHeight: 12.0,
        waveSpeed: 0.45,
        zoom: 0.82
      });
      el.dataset.ivsVantaDone = '1';
    });
  }

  async function boot() {
    var cfg = mergeConfig();
    var root = document;
    prepareDOM(root);
    if (reducedMotion() || document.documentElement.dataset.ivsMotion === 'off') {
      document.body.classList.remove('ivs-motion-pending');
      animateWithoutGSAP(root);
      return { reduced: true };
    }
    try {
      var jobs = [];
      if (cfg.lenis && !window.Lenis) jobs.push(loadScript(cfg.cdn.lenis, 'ivs-lenis-js'));
      if (cfg.gsap && !window.gsap) jobs.push(loadScript(cfg.cdn.gsap, 'ivs-gsap-js'));
      await Promise.all(jobs);
      if (cfg.gsap && window.gsap && !window.ScrollTrigger) await loadScript(cfg.cdn.scrollTrigger, 'ivs-scrolltrigger-js');
      if (cfg.vanta && document.querySelector('[data-ivs-vanta]')) {
        if (!window.THREE) await loadScript(cfg.cdn.three, 'ivs-three-js');
        if (!window.VANTA || !window.VANTA.WAVES) await loadScript(cfg.cdn.vantaWaves, 'ivs-vanta-waves-js');
      }
      initLenis(cfg);
      initGSAP(root);
      initVanta(cfg);
      document.body.classList.remove('ivs-motion-pending');
      log('info', 'camada inicializada', { profile: cfg.profile, vanta: cfg.vanta });
      return { ok: true, profile: cfg.profile };
    } catch (err) {
      log('warn', 'fallback sem bibliotecas externas', err.message);
      document.body.classList.remove('ivs-motion-pending');
      animateWithoutGSAP(root);
      return { ok: false, fallback: true, error: err.message };
    }
  }

  window.IVSMotion = { boot: boot, prepareDOM: prepareDOM, reducedMotion: reducedMotion };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
}());
