(() => {
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  const search = document.querySelector('.header-search');

  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') === 'true';
      menu.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
      if (search) search.classList.toggle('open', !open);
    });
  }

  // Homepage dynamic banner
  document.querySelectorAll('[data-banner]').forEach((banner) => {
    const slides = [...banner.querySelectorAll('.banner-slide')];
    if (!slides.length) return;

    const autoplayRequested = banner.dataset.autoplay === 'true';
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const autoplay = autoplayRequested && !reducedMotion;
    const interval = Number(banner.dataset.interval || 6500);
    const loop = banner.dataset.loop === 'true';
    const pauseHover = banner.dataset.pauseHover === 'true';
    const direction = banner.dataset.direction || 'rtl';
    const effect = banner.dataset.effect || 'fade';
    const overlay = Math.max(0, Math.min(90, Number(banner.dataset.overlay || 58))) / 100;
    banner.style.setProperty('--banner-overlay-alpha', String(overlay));
    const prevButton = banner.querySelector('[data-banner-prev]');
    const nextButton = banner.querySelector('[data-banner-next]');
    const pauseButton = banner.querySelector('[data-banner-pause]');
    const dotsWrap = banner.querySelector('[data-banner-dots]');

    let index = 0;
    let timer = null;
    let paused = false;

    const normalizeIndex = (candidate) => {
      if (candidate < 0) return loop ? slides.length - 1 : 0;
      if (candidate >= slides.length) return loop ? 0 : slides.length - 1;
      return candidate;
    };

    const render = (nextIndex) => {
      nextIndex = normalizeIndex(nextIndex);
      slides.forEach((slide, i) => {
        slide.classList.remove('is-active', 'is-before', 'is-after');
        slide.setAttribute('aria-hidden', i === nextIndex ? 'false' : 'true');

        if (i === nextIndex) {
          slide.classList.add('is-active');
        } else if (effect === 'slide') {
          if (direction === 'rtl') {
            slide.classList.add(i < nextIndex ? 'is-before' : 'is-after');
          } else {
            slide.classList.add(i < nextIndex ? 'is-after' : 'is-before');
          }
        }
      });

      index = nextIndex;
      if (dotsWrap) {
        [...dotsWrap.children].forEach((dot, i) => dot.classList.toggle('active', i === index));
      }
    };

    // Slide order always advances 1 → 2 → 3. The CSS direction controls whether the visual motion is right-to-left or left-to-right.
    const next = () => render(index + 1);
    const previous = () => render(index - 1);

    const stop = () => {
      if (timer) window.clearInterval(timer);
      timer = null;
    };

    const start = () => {
      stop();
      if (autoplay && !paused && slides.length > 1) timer = window.setInterval(next, interval);
    };

    const restart = () => {
      stop();
      start();
    };

    if (dotsWrap && slides.length > 1) {
      dotsWrap.innerHTML = '';
      slides.forEach((_, i) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `banner-dot${i === 0 ? ' active' : ''}`;
        button.setAttribute('aria-label', `Show banner ${i + 1}`);
        button.addEventListener('click', () => {
          render(i);
          restart();
        });
        dotsWrap.appendChild(button);
      });
    }

    if (nextButton) nextButton.addEventListener('click', () => { next(); restart(); });
    if (prevButton) prevButton.addEventListener('click', () => { previous(); restart(); });

    if (pauseButton) {
      pauseButton.addEventListener('click', () => {
        paused = !paused;
        pauseButton.textContent = paused ? 'Play' : 'Pause';
        pauseButton.setAttribute('aria-label', paused ? 'Play banner' : 'Pause banner');
        if (paused) stop(); else start();
      });
    }

    if (pauseHover) {
      banner.addEventListener('mouseenter', stop);
      banner.addEventListener('mouseleave', start);
    }

    render(0);
    start();
  });

})();
