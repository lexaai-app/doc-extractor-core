/* CRIAVERSO — interações da loja */
(function () {
  'use strict';

  /* ---------------------------------------------------- céu estrelado */
  var sky = document.getElementById('stars');
  if (sky) {
    var frag = document.createDocumentFragment();
    for (var i = 0; i < 90; i++) {
      var s = document.createElement('i');
      var size = (Math.random() * 1.9 + 0.7).toFixed(2);
      s.style.width = s.style.height = size + 'px';
      s.style.left = (Math.random() * 100).toFixed(2) + '%';
      s.style.top = (Math.random() * 100).toFixed(2) + '%';
      s.style.animationDelay = (Math.random() * 4).toFixed(2) + 's';
      s.style.animationDuration = (Math.random() * 3 + 3).toFixed(2) + 's';
      frag.appendChild(s);
    }
    sky.appendChild(frag);
  }

  /* ------------------------------------------------ marquee sem costura */
  var mq = document.getElementById('mq');
  if (mq) mq.innerHTML = mq.innerHTML + mq.innerHTML + mq.innerHTML + mq.innerHTML;

  /* ------------------------------------------------------- menu mobile */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  function closeMenu() {
    document.body.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
  }
  if (burger) {
    burger.addEventListener('click', function () {
      var open = document.body.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    });
  }
  if (nav) nav.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  /* ---------------------------------------------------- filtro do catálogo */
  var grid = document.getElementById('grid');
  var counter = document.getElementById('count');
  var filters = Array.prototype.slice.call(document.querySelectorAll('.filter'));
  var cards = grid ? Array.prototype.slice.call(grid.querySelectorAll('.p-card')) : [];

  function apply(cat) {
    var shown = 0;
    cards.forEach(function (card) {
      var match = cat === 'todos' || card.dataset.cat === cat;
      card.classList.toggle('hide', !match);
      if (match) shown++;
    });
    filters.forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.f === cat ? 'true' : 'false');
    });
    if (counter) counter.textContent = shown + (shown === 1 ? ' peça' : ' peças');
  }

  filters.forEach(function (btn) {
    btn.addEventListener('click', function () { apply(btn.dataset.f); });
  });

  /* atalhos do rodapé: rolam até o catálogo já filtrado */
  document.querySelectorAll('[data-jump]').forEach(function (a) {
    a.addEventListener('click', function () { apply(a.dataset.jump); });
  });

  /* --------------------------------------------------- reveal ao rolar */
  var revs = Array.prototype.slice.call(document.querySelectorAll('.rev'));
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduce || !('IntersectionObserver' in window)) {
    revs.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    revs.forEach(function (el) { io.observe(el); });
  }
})();
