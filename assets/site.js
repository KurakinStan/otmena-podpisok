// 1) Поиск по сервисам на главной: прячем всё, что не подходит под запрос.
// 2) Кнопка «Отправить ссылку себе» на телефонах: открывает меню «Поделиться»
//    (или копирует ссылку, если «Поделиться» не поддерживается).

(function () {
  var input = document.getElementById('q');
  if (input) {
    var items = document.querySelectorAll('.svc-list li');
    var cats = document.querySelectorAll('.cat');
    var nothing = document.getElementById('nothing');

    var normalize = function (s) {
      return s.toLowerCase().replace(/ё/g, 'е').replace(/[^a-zа-я0-9+ ]/g, ' ').trim();
    };

    input.addEventListener('input', function () {
      var q = normalize(input.value);
      var shown = 0;
      items.forEach(function (li) {
        var ok = !q || normalize(li.getAttribute('data-search')).indexOf(q) !== -1;
        li.hidden = !ok;
        if (ok) shown++;
      });
      cats.forEach(function (cat) {
        cat.hidden = !cat.querySelector('li:not([hidden])');
      });
      nothing.hidden = shown > 0;
    });

    // Enter открывает первый найденный сервис
    input.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Enter') return;
      var first = document.querySelector('.svc-list li:not([hidden]) a');
      if (first) location.href = first.href;
    });
  }

  var isTouch = window.matchMedia && window.matchMedia('(hover: none) and (pointer: coarse)').matches;
  document.querySelectorAll('.share-btn').forEach(function (btn) {
    if (!isTouch) return;
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var url = btn.getAttribute('data-url');
      if (navigator.share) {
        navigator.share({ title: 'Трекер подписок — расширение для браузера', url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          btn.textContent = 'Ссылка скопирована';
        });
      }
    });
  });
})();
