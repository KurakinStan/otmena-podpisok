#!/usr/bin/env python3
# Сборщик сайта: берёт тексты из content.py и делает готовые HTML-страницы.
#
# Запуск из корня репозитория:   python3 tools/build.py
#
# Что получается:
#   index.html                 — главная с поиском и разделами
#   <slug>/index.html          — страница каждого сервиса (адрес вида /kinopoisk/)
#   kak-najti-vse-podpiski/    — общая статья
#   o-proekte/                 — о проекте
#   404.html, sitemap.xml, robots.txt
#
# Все ссылки внутри сайта относительные, поэтому сайт работает и по адресу
# kurakinstan.github.io/otmena-podpisok/, и на своём домене.
# После покупки домена поменяйте SITE_URL ниже и пересоберите.

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import CATEGORIES, SERVICES, UPDATED, UPDATED_ISO  # noqa: E402

# ---------- Настройки ----------
SITE_URL = 'https://kurakinstan.github.io/otmena-podpisok'  # без / в конце
SITE_NAME = 'Отмена подписок'
STORE_URL = 'https://chromewebstore.google.com/detail/keoemfgiodcimaiianaocegllcejdcei'
FEEDBACK_URL = 'https://forms.yandex.ru/u/6ab63f5ceb6146678c8c72f8/'
# Номер счётчика Яндекс Метрики (число). Пока None — счётчика нет.
METRIKA_ID = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE_SLUG = 'kak-najti-vse-podpiski'
ARTICLE_TITLE = 'Как найти все подписки, с которых списывают деньги'

BY_SLUG = {s['slug']: s for s in SERVICES}
CAT_NAMES = dict(CATEGORIES)

e = html.escape


def services_count():
    """«41 сервиса», «45 сервисов» — склонение для «инструкции для N …»."""
    n = len(SERVICES)
    word = 'сервиса' if n % 10 == 1 and n % 100 != 11 else 'сервисов'
    return f'{n} {word}'


def store_link(medium):
    return f'{STORE_URL}?utm_source=site&utm_medium={medium}'


# ---------- Общие куски страницы ----------

def metrika():
    if not METRIKA_ID:
        return ''
    return f'''<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({METRIKA_ID},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true}});</script>'''


def page(*, prefix, path, title, description, body, jsonld=None):
    """prefix — '../' для страниц во вложенной папке, '' для корня.
    path — адрес страницы от корня сайта ('' для главной, 'kinopoisk/')."""
    canonical = f'{SITE_URL}/{path}'
    ld = ''
    if jsonld:
        ld = '\n'.join(
            f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
            for x in jsonld
        )
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{SITE_URL}/assets/icon-128.png">
<meta name="theme-color" content="#1f6f6b">
<link rel="icon" href="{prefix}assets/favicon-32.png" type="image/png">
<link rel="stylesheet" href="{prefix}assets/style.css">
{ld}
{metrika()}
</head>
<body>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="{prefix or './'}"><img src="{prefix}assets/icon-128.png" alt="" width="28" height="28">{SITE_NAME}</a>
    <nav class="top-nav">
      <a href="{prefix or './'}#services">Все сервисы</a>
      <a href="{prefix}{ARTICLE_SLUG}/">Найти все подписки</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p>Инструкции бесплатные и без регистрации. Обновлено: {UPDATED}. Нашли ошибку или кнопка называется иначе? <a href="{FEEDBACK_URL}" target="_blank" rel="noopener">Напишите нам</a> — поправим.</p>
    <p>Сайт не связан с перечисленными сервисами. Названия сервисов принадлежат их владельцам. <a href="{prefix}o-proekte/">О проекте</a></p>
  </div>
</footer>
<script src="{prefix}assets/site.js" defer></script>
</body>
</html>
'''


def cta(medium):
    """Блок про расширение. На телефоне показываем другой текст:
    расширение работает только в браузере на компьютере."""
    return f'''<aside class="cta">
  <img src="{'../' if medium != 'home' else ''}assets/icon-128.png" alt="" width="56" height="56">
  <div class="cta-text">
    <p class="cta-title">Чтобы больше не забывать про подписки</p>
    <p>Бесплатное расширение «Трекер подписок» для Chrome и Яндекс Браузера напомнит за несколько дней до списания и покажет, как отменить ненужное. Данные хранятся только на вашем компьютере.</p>
    <p class="cta-mobile">Расширение работает в браузере на компьютере. Отправьте ссылку себе, чтобы установить позже.</p>
    <div class="cta-actions">
      <a class="btn" href="{store_link(medium)}" target="_blank" rel="noopener">Установить бесплатно</a>
      <button class="btn btn-ghost share-btn" type="button" data-url="{store_link(medium)}" hidden>Отправить ссылку себе</button>
    </div>
  </div>
</aside>'''


def steps_html(steps):
    return '<ol class="steps">' + ''.join(f'<li>{s}</li>' for s in steps) + '</ol>'


GENERIC_AFTER = 'Обычно подписка работает до конца уже оплаченного периода, а следующего списания не будет. Проверьте, что статус сменился на «отменена» или появилась дата окончания — это и есть подтверждение.'
GENERIC_REFUND = 'Отмена останавливает будущие списания, но не возвращает уже оплаченное. Если деньги списали после отмены или по ошибке, напишите в поддержку сервиса: укажите дату, сумму и приложите скриншот отмены. Если оплата шла через App Store, Google Play или оператора — возврат просят у них. По закону «О защите прав потребителей» (ст. 32) от услуги можно отказаться в любой момент, оплатив только фактически понесённые расходы исполнителя.'


def service_page(s):
    name = s['name']
    plain = name.split(' (')[0]  # «Иви (ivi)» → «Иви» для заголовков
    title = f'Как отменить подписку {plain} — пошаговая инструкция ({UPDATED_ISO[:4]})'
    h1 = f'Как отменить подписку {plain}'
    desc = s['lead'] if len(s['lead']) <= 160 else s['lead'][:157].rsplit(' ', 1)[0] + '…'

    parts = []
    parts.append(f'<nav class="crumbs"><a href="../">Главная</a> › <a href="../#{s["cat"]}">{e(CAT_NAMES[s["cat"]])}</a></nav>')
    parts.append(f'<h1>{e(h1)}</h1>')
    parts.append(f'<p class="meta">Обновлено: {UPDATED}</p>')
    parts.append(f'<div class="answer"><p class="answer-label">Коротко</p><p>{s["lead"]}</p>')
    url, label = s['link']
    parts.append(f'<a class="btn" href="{e(url)}" target="_blank" rel="noopener nofollow">{e(label)} ↗</a></div>')

    # Оглавление по способам
    if len(s['methods']) > 1:
        toc = ''.join(f'<li><a href="#m{i}">{e(t)}</a></li>' for i, (t, _) in enumerate(s['methods'], 1))
        parts.append(f'<div class="toc"><p>Способы отмены:</p><ul>{toc}</ul></div>')

    for i, (t, steps) in enumerate(s['methods'], 1):
        parts.append(f'<section class="method" id="m{i}"><h2>{e(t)}</h2>{steps_html(steps)}</section>')

    if s['notes']:
        notes = ''.join(f'<li>{n}</li>' for n in s['notes'])
        parts.append(f'<section class="notes"><h2>Важно знать</h2><ul>{notes}</ul></section>')

    faq = [
        (f'Отменится ли подписка {plain}, если удалить приложение?',
         'Нет. Удаление приложения или выход из аккаунта подписку не отменяют — деньги продолжат списываться. Отменить нужно по инструкции выше.'),
        ('Что будет после отмены?', s['after'] or GENERIC_AFTER),
        ('Можно ли вернуть деньги?', s['refund'] or GENERIC_REFUND),
    ] + s['faq'] + [
        ('Не нашли подписку там, где описано?',
         f'Скорее всего, она оформлена через другой канал: App Store, Google Play, RuStore, мобильного оператора или банк. Посмотрите в банковской выписке, кто именно списывает деньги, — это подскажет, где отменять. Подробнее: <a href="../{ARTICLE_SLUG}/">как найти все свои подписки</a>.'),
    ]
    faq_html = ''.join(f'<details><summary>{e(q)}</summary><p>{a}</p></details>' for q, a in faq)
    parts.append(f'<section class="faq"><h2>Частые вопросы</h2>{faq_html}</section>')

    parts.append(cta(s['slug']))

    src = []
    if s['help']:
        src.append(f'<a href="{e(s["help"])}" target="_blank" rel="noopener nofollow">официальная справка сервиса</a>')
    src_text = ('Источник: ' + ', '.join(src) + '. ') if src else ''
    parts.append(f'<p class="source">{src_text}Названия кнопок у сервисов иногда меняются. Если у вас всё выглядит иначе, <a href="{FEEDBACK_URL}" target="_blank" rel="noopener">сообщите нам</a>.</p>')

    rel = []
    for r in s['related']:
        if r == ARTICLE_SLUG:
            rel.append(f'<li><a href="../{ARTICLE_SLUG}/">{ARTICLE_TITLE}</a></li>')
        elif r in BY_SLUG:
            rel.append(f'<li><a href="../{r}/">Как отменить подписку {e(BY_SLUG[r]["name"].split(" (")[0])}</a></li>')
    if rel:
        parts.append(f'<section class="related"><h2>Похожие инструкции</h2><ul>{"".join(rel)}</ul></section>')

    jsonld = [
        {
            '@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q,
                            'acceptedAnswer': {'@type': 'Answer', 'text': html_to_text(a)}} for q, a in faq],
        },
        {
            '@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': f'{SITE_URL}/'},
                {'@type': 'ListItem', 'position': 2, 'name': h1, 'item': f'{SITE_URL}/{s["slug"]}/'},
            ],
        },
    ]
    return page(prefix='../', path=f'{s["slug"]}/', title=title, description=desc,
                body='\n'.join(parts), jsonld=jsonld)


def html_to_text(a):
    import re
    return re.sub(r'<[^>]+>', '', a)


def index_page():
    groups = []
    for key, cat_name in CATEGORIES:
        items = [s for s in SERVICES if s['cat'] == key]
        if not items:
            continue
        lis = ''.join(
            f'<li data-search="{e((s["name"] + " " + s["search"]).lower())}"><a href="{s["slug"]}/">{e(s["name"])}</a></li>'
            for s in sorted(items, key=lambda x: x['name'].lower())
        )
        groups.append(f'<section class="cat" id="{key}"><h2>{e(cat_name)}</h2><ul class="svc-list">{lis}</ul></section>')

    body = f'''
<section class="hero">
  <h1>Как отменить подписку</h1>
  <p class="hero-sub">Пошаговые инструкции для {services_count()}: онлайн-кинотеатры, музыка, банки, операторы, App Store и Google Play. Куда нажать, где искать кнопку и что делать, если её нет.</p>
  <label class="search">
    <span class="visually-hidden">Найти сервис</span>
    <input id="q" type="search" placeholder="Начните вводить: кинопоиск, иви, мтс…" autocomplete="off">
  </label>
  <p id="nothing" class="nothing" hidden>Такого сервиса пока нет. Посмотрите <a href="{ARTICLE_SLUG}/">как найти и отменить любую подписку</a> или <a href="{FEEDBACK_URL}" target="_blank" rel="noopener">попросите добавить инструкцию</a>.</p>
</section>
<div id="services">
{''.join(groups)}
</div>
<section class="article-teaser">
  <h2>Не знаете, какие подписки у вас есть?</h2>
  <p>Подписки прячутся в банке, App Store, Google Play, у оператора и в аккаунтах Яндекса и Сбера. <a href="{ARTICLE_SLUG}/">Собрали, где проверить всё за 15 минут →</a></p>
</section>
{cta('home')}
'''
    jsonld = [{
        '@context': 'https://schema.org', '@type': 'WebSite',
        'name': SITE_NAME, 'url': f'{SITE_URL}/', 'inLanguage': 'ru',
    }]
    return page(prefix='', path='', title='Как отменить подписку: инструкции для кинотеатров, музыки, банков и операторов',
                description=f'Пошаговые инструкции, как отменить подписку: Кинопоиск, Яндекс Плюс, Иви, Okko, СберПрайм, МТС и ещё {len(SERVICES) - 6} сервисов. Где кнопка отмены и как вернуть деньги.',
                body=body, jsonld=jsonld)


def article_page():
    body = f'''
<nav class="crumbs"><a href="../">Главная</a></nav>
<h1>{ARTICLE_TITLE}</h1>
<p class="meta">Обновлено: {UPDATED}</p>
<div class="answer"><p class="answer-label">Коротко</p><p>Подписки оформляются в разных местах, и общего списка нигде нет. Проверьте по очереди: выписку в банке, App Store или Google Play, RuStore, мобильного оператора и аккаунты Яндекса, Сбера и VK. Обычно это занимает 15–20 минут.</p></div>

<section class="method" id="bank"><h2>1. Банковская выписка — главный источник</h2>
<p>Банк видит все списания, откуда бы они ни шли. Поэтому начните с него.</p>
<ol class="steps">
<li>Откройте приложение банка и историю операций минимум за 6–12 месяцев: годовые подписки списываются раз в год, и их легко пропустить</li>
<li>Ищите повторяющиеся суммы и названия вроде YANDEX, OKKO, IVI, APPLE.COM/BILL, GOOGLE, KION</li>
<li>Попробуйте поиск по слову «подписка»: во многих банках есть отдельный раздел с подписками и автоплатежами</li>
<li>Проверьте привязки по СБП: некоторые сервисы списывают деньги со счёта без карты. Такие привязки тоже видно и можно отключить в приложении банка</li>
</ol>
<p>Название в выписке подскажет, где отменять. Например, APPLE.COM/BILL значит, что подписка оплачена через App Store, а не на сайте сервиса.</p>
</section>

<section class="method" id="stores"><h2>2. App Store, Google Play и RuStore</h2>
<ul>
<li><b>iPhone:</b> «Настройки» → ваше имя → «Подписки». <a href="../app-store/">Подробная инструкция</a></li>
<li><b>Android:</b> Google Play → значок профиля → «Платежи и подписки» → «Подписки». <a href="../google-play/">Подробная инструкция</a></li>
<li><b>RuStore:</b> вкладка «Моё» → «Подписки». <a href="../rustore/">Подробная инструкция</a></li>
</ul>
<p>Если у вас несколько аккаунтов Google или Apple, проверьте каждый.</p>
</section>

<section class="method" id="operator"><h2>3. Мобильный оператор</h2>
<p>Платные подписки на номере списываются с баланса телефона и в банке не видны. Проверьте их в приложении оператора или командой:</p>
<ul>
<li><a href="../mts/">МТС</a>: «Мой МТС» → «Подключённые услуги и сервисы», или *152*2#</li>
<li><a href="../megafon/">МегаФон</a>: раздел «Услуги и опции», или *583#</li>
<li><a href="../beeline/">Билайн</a>: «Мои информационно-развлекательные услуги», или *110*09#</li>
<li><a href="../t2/">T2</a>: раздел «Услуги», или *189#</li>
</ul>
<p>Команды операторы иногда меняют. Если не сработала — проверьте на сайте оператора.</p>
</section>

<section class="method" id="ecosystems"><h2>4. Аккаунты Яндекса, Сбера и VK</h2>
<ul>
<li><b>Яндекс:</b> на id.yandex.ru видна история платежей, а подписка Плюс управляется на plus.yandex.ru/my. <a href="../yandex-plus/">Как отменить Плюс</a></li>
<li><b>Сбер:</b> в СберБанк Онлайн есть раздел «Подписки», там же СберПрайм. <a href="../sberprime/">Как отменить СберПрайм</a></li>
<li><b>VK:</b> «Настройки» → «Управление аккаунтом VK ID» → «Подписки». <a href="../vk-muzyka/">Как отменить VK Музыку</a></li>
</ul>
</section>

<section class="method" id="mail"><h2>5. Почта</h2>
<p>Найдите в почте письма со словами «подписка», «автопродление», «чек», «пробный период». Сервисы присылают чек после каждого списания — так всплывают подписки, о которых вы забыли.</p>
</section>

<section class="notes"><h2>Если отменить не получается</h2>
<ul>
<li>Напишите в поддержку сервиса и сохраните переписку и скриншоты</li>
<li>Если сервис не отвечает, обратитесь в банк: он может помочь оспорить списание</li>
<li>Крайняя мера — перевыпустить карту. Но долг перед сервисом от этого не исчезает, а подписки по СБП и на номере телефона продолжат работать</li>
</ul>
</section>

<section class="method"><h2>Как не попадать на списания дальше</h2>
<ul>
<li>Отключайте автопродление сразу после того, как оформили пробный период: бесплатные дни обычно сохраняются</li>
<li>Заведите для подписок отдельную карту — так все расходы видны в одном месте</li>
<li>Записывайте подписки и даты списаний в одном месте, чтобы получать напоминания заранее</li>
</ul>
</section>

{cta(ARTICLE_SLUG)}

<section class="related"><h2>Популярные инструкции</h2><ul>
{''.join(f'<li><a href="../{x}/">Как отменить подписку {e(BY_SLUG[x]["name"].split(" (")[0])}</a></li>' for x in ['kinopoisk', 'yandex-plus', 'ivi', 'okko', 'sberprime', 'kion'])}
</ul></section>
'''
    return page(prefix='../', path=f'{ARTICLE_SLUG}/', title=f'{ARTICLE_TITLE}: проверка за 15 минут',
                description='Где искать все платные подписки: банковская выписка, App Store, Google Play, RuStore, мобильный оператор, Яндекс, Сбер и VK. Пошаговая проверка.',
                body=body)


def about_page():
    body = f'''
<nav class="crumbs"><a href="../">Главная</a></nav>
<h1>О проекте</h1>
<p>Здесь собраны понятные инструкции, как отменить платные подписки: куда нажать, где спрятана кнопка и что делать, если её нет. Мы сверяем шаги с официальными справками сервисов и обновляем их, когда сервисы меняют интерфейс.</p>
<p>Сайт сделан автором бесплатного браузерного расширения <a href="{store_link('about')}" target="_blank" rel="noopener">«Трекер подписок»</a>. Расширение помогает вести список подписок, напоминает о списаниях заранее и показывает инструкции по отмене прямо в браузере.</p>
<h2>Конфиденциальность</h2>
<p>Сайт не просит регистрироваться и не собирает персональные данные. Расширение хранит ваши подписки только на вашем компьютере.</p>
<h2>Связаться с нами</h2>
<p>Нашли ошибку, кнопка называется иначе или нужен новый сервис — <a href="{FEEDBACK_URL}" target="_blank" rel="noopener">напишите через форму</a>.</p>
<p>Сайт не связан с перечисленными сервисами. Все названия и товарные знаки принадлежат их владельцам.</p>
'''
    return page(prefix='../', path='o-proekte/', title=f'О проекте — {SITE_NAME}',
                description='Кто и зачем делает инструкции по отмене подписок.', body=body)


def not_found_page():
    # 404 открывается по любому адресу, поэтому ссылки — от корня сайта.
    base = SITE_URL.split('://', 1)[1].split('/', 1)
    root = '/' + (base[1] + '/' if len(base) > 1 else '')
    body = f'''<h1>Страница не найдена</h1>
<p>Возможно, адрес изменился. Перейдите <a href="{root}">на главную</a> и найдите нужный сервис через поиск.</p>'''
    return page(prefix=root, path='404.html', title=f'Страница не найдена — {SITE_NAME}',
                description='Страница не найдена.', body=body)


def write(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    write('index.html', index_page())
    for s in SERVICES:
        write(f'{s["slug"]}/index.html', service_page(s))
    write(f'{ARTICLE_SLUG}/index.html', article_page())
    write('o-proekte/index.html', about_page())
    write('404.html', not_found_page())

    urls = [''] + [f'{s["slug"]}/' for s in SERVICES] + [f'{ARTICLE_SLUG}/', 'o-proekte/']
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += ''.join(f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>{UPDATED_ISO}</lastmod></url>\n' for u in urls)
    sitemap += '</urlset>\n'
    write('sitemap.xml', sitemap)
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
    write('.nojekyll', '')
    print(f'Готово: {len(urls)} страниц')


if __name__ == '__main__':
    main()
