'use strict';

(async function () {
  const $ = (id) => document.getElementById(id);
  const gallery = $('gallery');
  const filters = $('filters');
  const lightbox = $('lightbox');
  const lbImg = $('lb-img');
  const lbCaption = $('lb-caption');

  $('year').textContent = new Date().getFullYear();

  let photos = [];
  try {
    const res = await fetch('photos.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    photos = (await res.json()).photos || [];
  } catch (err) {
    console.error('Failed to load photos.json:', err);
  }

  if (!photos.length) {
    $('empty').hidden = false;
    $('hero').hidden = true;
    return;
  }

  // Hero: first photo flagged as featured, else the first one.
  const hero = photos.find((p) => p.featured) || photos[0];
  $('hero-img').src = hero.src;
  $('hero-img').alt = hero.alt || hero.title || '';

  // Filters
  const categories = ['all', ...new Set(photos.map((p) => p.category).filter(Boolean))];
  let active = 'all';
  let visible = photos;

  for (const cat of categories) {
    const b = document.createElement('button');
    b.type = 'button';
    b.role = 'tab';
    b.textContent = cat;
    b.setAttribute('aria-selected', String(cat === active));
    b.addEventListener('click', () => {
      active = cat;
      for (const el of filters.children) el.setAttribute('aria-selected', String(el === b));
      render();
    });
    filters.appendChild(b);
  }

  function caption(p) {
    const frag = document.createDocumentFragment();
    if (p.title) {
      const s = document.createElement('strong');
      s.textContent = p.title;
      frag.appendChild(s);
    }
    const extra = [p.location, p.camera, p.year].filter(Boolean).join(' · ');
    if (extra) frag.appendChild(document.createTextNode((p.title ? ' — ' : '') + extra));
    return frag;
  }

  function render() {
    visible = active === 'all' ? photos : photos.filter((p) => p.category === active);
    gallery.replaceChildren();
    visible.forEach((p, i) => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.setAttribute('aria-label', `Open ${p.title || 'photo'}`);

      const img = document.createElement('img');
      img.loading = 'lazy';
      img.decoding = 'async';
      img.src = p.thumb || p.src;
      img.alt = p.alt || p.title || '';
      if (p.width && p.height) { img.width = p.width; img.height = p.height; }
      img.addEventListener('load', () => img.classList.add('loaded'), { once: true });

      const meta = document.createElement('span');
      meta.className = 'meta';
      meta.textContent = [p.title, p.location].filter(Boolean).join(' — ');

      btn.append(img, meta);
      btn.addEventListener('click', () => open(i));
      li.appendChild(btn);
      gallery.appendChild(li);
    });
  }

  // Lightbox
  let current = 0;
  function show(i) {
    current = (i + visible.length) % visible.length;
    const p = visible[current];
    lbImg.src = p.src;
    lbImg.alt = p.alt || p.title || '';
    lbCaption.replaceChildren(caption(p));
    // Preload neighbours for snappy navigation.
    for (const d of [1, -1]) new Image().src = visible[(current + d + visible.length) % visible.length].src;
  }
  function open(i) { show(i); lightbox.showModal(); }

  $('lb-close').addEventListener('click', () => lightbox.close());
  $('lb-prev').addEventListener('click', () => show(current - 1));
  $('lb-next').addEventListener('click', () => show(current + 1));
  lightbox.addEventListener('click', (e) => { if (e.target === lightbox) lightbox.close(); });
  document.addEventListener('keydown', (e) => {
    if (!lightbox.open) return;
    if (e.key === 'ArrowRight') show(current + 1);
    if (e.key === 'ArrowLeft') show(current - 1);
  });

  let touchX = null;
  lightbox.addEventListener('touchstart', (e) => { touchX = e.touches[0].clientX; }, { passive: true });
  lightbox.addEventListener('touchend', (e) => {
    if (touchX === null) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    touchX = null;
  });

  render();
})();
