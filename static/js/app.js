// Live search suggestions inside the search modal.
(function () {
  var modalEl = document.getElementById('searchModal');
  var input = document.getElementById('searchInput');
  var box = document.getElementById('searchResults');
  if (!modalEl || !input || !box) return;

  var timer = null;

  modalEl.addEventListener('shown.bs.modal', function () { input.focus(); });

  function render(items) {
    box.innerHTML = '';
    if (!items.length) {
      var empty = document.createElement('div');
      empty.className = 'list-group-item text-muted';
      empty.textContent = 'No products found.';
      box.appendChild(empty);
      return;
    }
    items.forEach(function (p) {
      var a = document.createElement('a');
      a.href = p.url;
      a.className = 'list-group-item list-group-item-action suggest-item';
      var img = document.createElement('img');
      img.src = p.image;
      img.alt = '';
      var wrap = document.createElement('div');
      var name = document.createElement('div');
      name.className = 'fw-semibold small';
      name.textContent = p.name;
      var price = document.createElement('div');
      price.className = 'price small';
      price.textContent = '$' + p.price;
      wrap.appendChild(name);
      wrap.appendChild(price);
      a.appendChild(img);
      a.appendChild(wrap);
      box.appendChild(a);
    });
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    var q = input.value.trim();
    if (q.length < 2) { box.innerHTML = ''; return; }
    timer = setTimeout(function () {
      fetch(modalEl.dataset.suggestUrl + '?q=' + encodeURIComponent(q), { headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (data) { render(data.results || []); })
        .catch(function () { box.innerHTML = ''; });
    }, 250);
  });
})();
