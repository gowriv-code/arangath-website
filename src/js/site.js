/* Arangath site: mobile nav + blog category filter. Everything works without JS except the filter chips. */
(function () {
  var btn = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (btn && links) {
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('open')) { links.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
    });
  }
  var chips = document.querySelectorAll('.chip-filter button');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var cat = c.getAttribute('data-cat');
      chips.forEach(function (o) { o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
      var shown = 0;
      document.querySelectorAll('[data-post-cat]').forEach(function (p) {
        var ok = cat === 'all' || p.getAttribute('data-post-cat') === cat;
        p.hidden = !ok; if (ok) shown++;
      });
      var none = document.getElementById('filter-empty');
      if (none) none.hidden = shown !== 0;
    });
  });
})();
