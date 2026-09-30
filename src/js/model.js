/* Live illustrative models: layer toggles, tooltips, key-element buttons, flow pause.
   Plain DOM, no libraries. Flow animation itself is CSS and is off under prefers-reduced-motion. */
(function () {
  document.querySelectorAll('.model').forEach(function (model) {
    var svg = model.querySelector('svg');
    var tip = model.querySelector('.model-tip');
    var status = model.querySelector('.model-status');
    var stage = model.querySelector('.model-stage');
    if (!svg) return;

    function setLayer(name, on) {
      svg.querySelectorAll('[data-layer="' + name + '"]').forEach(function (g) { g.classList.toggle('off', !on); });
      var b = model.querySelector('.layer-btn[data-layer="' + name + '"]');
      if (b) b.setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    model.querySelectorAll('.layer-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        var on = b.getAttribute('aria-pressed') !== 'true';
        setLayer(b.getAttribute('data-layer'), on);
        hide();
      });
    });

    var flowBtn = model.querySelector('.flow-btn');
    if (flowBtn) flowBtn.addEventListener('click', function () {
      var paused = model.classList.toggle('paused');
      flowBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
      flowBtn.textContent = paused ? 'Resume flow' : 'Pause flow';
    });

    function show(text, x, y) {
      if (!tip) return;
      tip.textContent = text;
      var r = stage.getBoundingClientRect();
      var left = Math.min(Math.max(x - r.left + 14, 4), r.width - 120);
      tip.style.left = left + 'px';
      tip.style.top = Math.max(y - r.top - 44, 4) + 'px';
      tip.classList.add('on');
    }
    function hide() { if (tip) tip.classList.remove('on'); }

    var hot = svg.querySelectorAll('.hot');
    hot.forEach(function (g) {
      g.addEventListener('pointerenter', function (e) { show(g.getAttribute('data-tip'), e.clientX, e.clientY); });
      g.addEventListener('pointermove', function (e) { show(g.getAttribute('data-tip'), e.clientX, e.clientY); });
      g.addEventListener('pointerleave', hide);
      g.addEventListener('click', function (e) {
        e.stopPropagation();
        show(g.getAttribute('data-tip'), e.clientX, e.clientY);
        if (status) status.textContent = g.getAttribute('data-tip');
      });
    });
    document.addEventListener('click', function (e) { if (!model.contains(e.target)) hide(); });

    /* Keyboard route to the same information: one button per key element. */
    var keyBtns = model.querySelectorAll('.key-btn');
    function highlight(key) {
      hot.forEach(function (g) { g.classList.remove('hl'); });
      keyBtns.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
      var target = svg.querySelector('.hot[data-key="' + key + '"]');
      var btn = model.querySelector('.key-btn[data-key="' + key + '"]');
      if (!target) return;
      var layer = target.getAttribute('data-layer');
      var lb = model.querySelector('.layer-btn[data-layer="' + layer + '"]');
      if (lb && lb.getAttribute('aria-pressed') !== 'true') setLayer(layer, true);
      target.classList.add('hl');
      if (btn) btn.setAttribute('aria-pressed', 'true');
      if (status) status.textContent = target.getAttribute('data-tip');
    }
    keyBtns.forEach(function (b) {
      b.addEventListener('click', function () { highlight(b.getAttribute('data-key')); });
    });
  });
})();
