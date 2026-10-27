"""教材データから、外部通信なしで読める単体HTMLを生成する。"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
e = lambda value: html.escape(str(value), quote=True)
lessons = json.loads((ROOT / 'lessons.json').read_text())
assert len({v['id'] for v in lessons}) == len(lessons), '教材IDが重複しています'

def jump(m, seconds, label='動画で確認'):
    return f'<a class="time" href="{e(m["source"]["url"])}&amp;t={seconds}s" target="_blank" rel="noopener">{e(label)} ↗</a>'

def badge(value):
    kind = 'clean' if value == 'きれいめ' else 'casual'
    return f'<span class="badge {kind}">{e(value)}</span>' if value != '—' else '<span class="muted">なし</span>'

def icon(kind):
    shapes = {
        'jacket': '<path d="M32 20 19 25 10 52l14 5 4-17-2 46h48l-2-46 4 17 14-5-9-27-13-5-18 12Z"/><path d="m32 20 18 23 18-23M50 43v43M34 23l-4 14 12 7-5 12 13-13m16-20 4 14-12 7 5 12-13-13"/>',
        'hoodie': '<path d="M32 26 19 31 10 55l14 5 5-16-3 42h48l-3-42 5 16 14-5-9-24-13-5C69 4 31 4 32 26Z"/><path d="M32 26q18 16 36 0M44 37v18m12-18v18m-18 9h24l4 13H34Z"/>',
        'shirt': '<path d="M35 20 20 27 8 50l15 8 6-16-3 44h48l-3-44 6 16 15-8-12-23-15-7-15 9Z"/><path d="m35 20 4 16 11-7 11 7 4-16M50 29v57"/><path d="M58 43h9v12h-9Z"/>',
        'pants': '<path d="M28 15h44l5 72H54l-4-46-4 46H23Z"/><path d="M28 25h44M50 15v26M30 30l10 9m30-9-10 9"/>',
        'shoe': '<path d="M15 45h25l12 12 26 6q13 2 13 17H12Z"/><path d="M12 80h79v8H12Zm29-31 10-6m-4 13 10-6m-3 12 10-6"/>',
        'cap': '<path d="M24 56q0-37 30-37t28 37ZM23 56h60l-15 18H9Z"/><path d="M54 19q-10 13-10 37"/>',
        'knit': '<path d="M35 20 20 27 8 50l15 8 6-16-3 44h48l-3-44 6 16 15-8-12-23-15-7q-15 15-30 0Z"/><path d="M29 78h42M35 26q15 12 30 0M56 48q-7-10-12 0t12 15q20-15 0-15Z"/>',
        'vest': '<path d="M32 18q-3 20-12 20v47h60V38q-9 0-12-20L50 39Z"/><path d="M50 39v46M27 66h14m18 0h14"/>',
        'beanie': '<path d="M23 65q0-42 27-42t27 42ZM20 65h60v18H20Z"/><circle cx="50" cy="15" r="8"/><path d="M33 65V43m11 22V31m12 34V31m11 34V43"/>',
        'tie': '<path d="M43 17h14l-3 13 8 45-12 13-12-13 8-45Z"/><path d="M46 30h8"/>',
        'chain': '<path d="M20 30q0 51 30 51t30-51"/><path d="m19 31 8 10m-5 3 9 9m-3 3 10 7m-5 5 11 5m1 4 10 1m4-3 10-5m0-6 9-7m-1-5 9-11"/>',
        'tee': '<path d="M35 20 20 27 8 50l15 8 6-16-3 44h48l-3-44 6 16 15-8-12-23-15-7q-15 15-30 0Z"/><path d="M35 25q15 13 30 0M28 80h44"/>',
        'coat': '<path d="M34 13 21 19 11 52l12 4 7-25-4 61h48l-4-61 7 25 12-4-10-33-13-6-16 12Z"/><path d="m34 13 16 26 16-26M50 39v53M33 62h9m16 0h9"/>',
        'bomber': '<path d="M34 20 21 27 9 58l15 5 6-23-3 41h46l-3-41 6 23 15-5-12-31-13-7-16 9Z"/><path d="M34 20q16 16 32 0M50 29v52M28 75h44M34 50l8-6m24 6-8-6"/>',
    }
    return '<svg class="garment" viewBox="0 0 100 100" aria-hidden="true">' + shapes[kind] + '</svg>'

def render(m):
    mid = e(m['id'])
    source = m['source']
    reading = m.get('reading', {
        'base_label': '種類から見た印象', 'base_text': 'ジャケット → きれいめ',
        'detail_label': '素材・形・サイズ感', 'detail_text': '広い肩幅・ゆとりなど → カジュアル',
        'result_label': '動画の例での読み方', 'result_text': 'メイン：きれいめ\nサブ：カジュアル',
        'time': 190, 'label': '属性の説明を見る · 3:10'
    })
    reading_html = '<div class="reading">' + ''.join(
        ('<span aria-hidden="true">' + ('＋' if i == 1 else '＝') + '</span>' if i else '')
        + f'<div class="{"reading-result" if i == 2 else ""}"><small>{e(reading[key+"_label"])}</small><strong>{e(reading[key+"_text"]).replace(chr(10),"<br>")}</strong></div>'
        for i,key in enumerate(['base','detail','result'])) + '</div>'
    concept_note = m.get('concept_note', '【教材の補足】同じ種類でも、実物の印象は違います。「なぜその属性に見えるか」を言葉にすると、手持ちの服でも応用しやすくなります。属性は点数や比率ではなく、説明のための言葉です。')
    comparison = ''
    if m.get('comparison'):
        comparison = '<div class="table-scroll"><table><caption>動画の説明を比較する</caption><thead><tr><th scope="col">見方</th><th scope="col">変えるところ</th><th scope="col">つながりの見方</th></tr></thead><tbody>' + ''.join(f'<tr><th scope="row">{e(x["name"])}</th><td>{e(x["change"])}</td><td>{e(x["connection"])}</td></tr>' for x in m['comparison']) + '</tbody></table></div>'
    relation = ''
    if m.get('relation'):
        relation = f'<div class="point"><strong>前回とのつながり</strong><p>{e(m["relation"]["text"])} <a href="#{e(m["relation"]["id"])}-summary" data-related-lesson="{e(m["relation"]["id"])}">第1本を振り返る</a></p></div>'
    source_notice = m.get('source_notice', '自動字幕には誤変換があります。冒頭のコーデ説明で字幕に「スラックス」と出る箇所は、前後の説明に沿ってジャケット・シャツ・デニム・革靴の例として整理しました。素材や見た目の細部は元動画で確認してください。')
    editorial_notice = m.get('editorial_notice', '要点・属性・具体例・外しは動画の内容の要約です。補足、模式図、実践ワーク、確認問題は教材用の編集です。動画で言及された別回の色合わせ理論は、今回の範囲には含めていません。')
    takeaways = ''.join(f'<article class="takeaway"><span class="number">0{i+1}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p>{jump(m,x["time"],x["label"])}</article>' for i,x in enumerate(m['takeaways']))
    concepts = ''.join(f'<div><dt>{e(x["name"])}</dt><dd>{e(x["text"])}</dd></div>' for x in m['concepts'])
    examples = ''
    for i, x in enumerate(m['examples']):
        cards = ''.join(f'<article class="item">{icon(y["type"])}<h4>{e(y["name"])}</h4><dl><div><dt>メイン</dt><dd>{badge(y["main"])}</dd></div><div><dt>サブ</dt><dd>{badge(y["sub"])}</dd></div></dl><p>{e(y["reason"])}</p></article>' for y in x['items'])
        examples += f'<div class="example-panel" id="{mid}-example-{i}" data-example="{i}"><div class="example-heading"><div><span class="kicker">軸にする服</span><h3>{e(x["anchor"])}</h3></div>{jump(m,x["time"],x["range"])}</div><p class="shared {e(x["sharedType"])}">共通する印象：<strong>{e(x["shared"])}</strong></p><div class="items">{cards}</div><div class="point"><strong>つながりを読む</strong><p>{e(x["point"])}</p></div><p class="hint">{e(x["caution"])}</p></div>'
    tabs = ''.join(f'<button class="tab" data-example-button="{i}" aria-controls="{mid}-example-{i}" aria-expanded="true">{e(x["title"])}</button>' for i,x in enumerate(m['examples']))
    pairs = ''.join(f'<article class="bridge-example"><h3>{e(x["title"])}</h3><div class="bridge-diagram" aria-label="橋渡しの関係"><div>{e(x["left"])}</div><span aria-hidden="true">↔</span><div class="bridge-center"><small>つなぐ役割</small>{e(x["bridge"])}</div><span aria-hidden="true">↔</span><div>{e(x["right"])}</div></div><p>{e(x["explanation"])}</p></article>' for x in m['accent']['pairs'])
    glossary = ''.join(f'<details><summary>{e(x["term"])}</summary><p><span class="small-label">{e(x["kind"])}</span>{e(x["text"])}</p></details>' for x in m['glossary'])
    questions = ''
    for i, q in enumerate(m['quiz']):
        options = ''.join(f'<label class="option"><input type="radio" name="{mid}-q{i}" value="{j}" data-question="{i}"><span>{e(s)}</span></label>' for j,s in enumerate(q['options']))
        questions += f'<fieldset class="question"><legend><span class="kicker">問 {i+1}</span>{e(q["question"])}</legend>{options}<div class="feedback" data-feedback="{i}" hidden></div></fieldset>'
    sections = [('summary','要点'),('concept','属性の見方'),('examples','具体例'),('accent','外し')]
    extension_html = ''
    for extension in m.get('extensions', []):
        key = extension['id']
        sections.append((key,extension['nav']))
        paragraphs = ''.join(f'<p>{e(p)}</p>' for p in extension.get('paragraphs', []))
        table = ''
        if extension.get('rows'):
            heads = ''.join(f'<th scope="col">{e(c)}</th>' for c in extension['columns'])
            rows = ''.join('<tr>' + ''.join(f'<{"th scope=\"row\"" if i == 0 else "td"}>{e(c)}</{"th" if i == 0 else "td"}>' for i,c in enumerate(row)) + '</tr>' for row in extension['rows'])
            table = f'<div class="table-scroll"><table><caption>{e(extension["caption"])}</caption><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table></div>'
        steps = '<ol class="analysis-steps">' + ''.join(f'<li>{e(step)}</li>' for step in extension['steps']) + '</ol>' if extension.get('steps') else ''
        extension_html += f'<section id="{mid}-{e(key)}"><div class="section-heading"><span>{len(sections):02}</span><h2>{e(extension["title"])}</h2></div>{paragraphs}{table}{steps}{jump(m,extension["time"],extension["range"])}</section>'
    sections += [('practice','実践ワーク'),('quiz','確認問題'),('source','用語・出典')]
    numbers = {key:f'{i+1:02}' for i,(key,_) in enumerate(sections)}
    nav = ''.join(f'<a href="#{mid}-{key}">{e(label)}</a>' for key,label in sections)
    goals = ''.join(f'<li>{e(s)}</li>' for s in m['goals'])
    tags = ''.join(f'<span>{e(t)}</span>' for t in m['tags'])
    worksheet = ''.join(f'<label class="work-field">{e(label)}<textarea data-note="{key}" rows="3" maxlength="50000" placeholder="{e(placeholder)}"></textarea></label>' for key,label,placeholder in m.get('worksheet', [
        ('scene','1. 着ていく場面と、軸にしたい1着','例：休日に街へ出かける。手持ちの黒いデニムを使う。'),
        ('attributes','2. 各アイテムのメイン・サブ属性','服の名前 → 強い印象 → 別の印象 → そう感じる素材・形・サイズ感'),
        ('connections','3. 共通点と、拾われていない要素','何が全体をつないでいる？ どの印象が1点だけになっている？'),
        ('experiment','4. 1点だけ変えて比較した結果','何を替えた？ どのつながりが増えた？ 鏡や写真でどう感じた？')]))
    return f'''<article class="lesson" data-lesson="{mid}">
<header class="lesson-head"><div class="kicker">LESSON {e(m['number'])} · 動画から学ぶ</div><h1>{e(m['title'])}</h1><p class="subtitle">{e(m['subtitle'])}</p><div class="tags">{tags}</div><p class="source-meta">{e(source['creator'])} ／ 元動画 {e(source['duration'])}</p></header>
<nav class="section-nav" aria-label="この教材の目次">{nav}</nav>
<section id="{mid}-summary"><div class="section-heading"><span>01</span><h2>まず押さえる、{len(m['takeaways'])}つの要点</h2></div><p class="lead">{e(m['intro'])}</p>{relation}<div class="takeaways">{takeaways}</div><details class="goals"><summary>この教材でできるようになること</summary><ul>{goals}</ul></details><p class="scope">ここで紹介するのは、投稿者が提案する組み合わせの見方です。好みや場面によって評価は変わるため、唯一の正解として扱わず、服を見る手がかりにします。</p></section>
<section id="{mid}-concept"><div class="section-heading"><span>02</span><h2>{e(m.get('concept_title','服の名前から、実物の特徴へ'))}</h2></div><dl class="concepts">{concepts}</dl>{reading_html}{comparison}<p class="hint">{e(concept_note)}</p>{jump(m,reading['time'],reading['label'])}</section>
<section id="{mid}-examples"><div class="section-heading"><span>03</span><h2>{len(m['examples'])}つの具体例で、つながりを見る</h2></div><p>動画で説明された属性を並べた図です。共通点に加えて、別の印象をどこで拾っているかも見てみましょう。</p><p class="hint">服のイラストは種類を示す模式図です。実際の色・素材・シルエットは、各例の動画リンクで確認できます。</p><div class="example-controls" aria-label="具体例を切り替える">{tabs}</div>{examples}</section>
<section id="{mid}-accent"><div class="section-heading"><span>04</span><h2>{e(m['accent'].get('title','「外し」にも、つながりがある'))}</h2></div><p class="lead">{e(m['accent']['text'])}</p>{pairs}<p class="hint">【教材の補足】図の矢印は、服同士の印象がつながる関係を示しています。服を着る順番や、組み合わせの採点を表すものではありません。</p>{jump(m,m['accent']['time'],m['accent']['range'])}</section>
{extension_html}
<section id="{mid}-practice"><div class="section-heading"><span>{numbers['practice']}</span><h2>手持ちの服で試してみる</h2></div><p class="lead">{e(m.get('practice_intro','【教材オリジナルのワーク】動画の見方を、自分の服に当てはめます。まずは買い足さず、手持ちの組み合わせを1点ずつ変えて比べてみましょう。'))}</p><div class="worksheet">{worksheet}</div><p class="hint">きれいめに見えることと、場面の服装規定に適していることは分けて確認しましょう。動画でもTPOが前提です。</p><div class="actions"><button class="secondary" data-export-notes>このワークをMarkdownで保存</button><label class="completion"><input type="checkbox" data-complete>この動画の教材を学習済みにする</label></div></section>
<section id="{mid}-quiz"><div class="section-heading"><span>{numbers['quiz']}</span><h2>見方を確かめる、{len(m['quiz'])}つの問題</h2></div><p>【教材オリジナルの問題】動画が説明した考え方を確かめます。実際のコーデの良し悪しを採点するものではありません。</p>{questions}<div class="actions"><button class="primary" data-grade>回答を確認する</button><p class="score" data-score role="status"></p></div></section>
<section id="{mid}-source"><div class="section-heading"><span>{numbers['source']}</span><h2>用語と、元動画への道しるべ</h2></div><div class="glossary">{glossary}</div><div class="source-box"><span class="kicker">REFERENCE · この教材の出典</span><h3><a href="{e(source['url'])}" target="_blank" rel="noopener">{e(source['title'])} ↗</a></h3><p>{e(source['creator'])} ／ 公開日：{e(source['published'])}<br>確認日：{e(source['checked'])}</p><p>{e(source['method'])}</p><p class="hint">{e(source_notice)}</p><p class="hint">{e(editorial_notice)}</p></div></section>
</article>'''

library = ''.join(f'<button class="lesson-select" data-select-lesson="{e(m["id"])}" aria-controls="lesson-content"><small>LESSON {e(m["number"])}</small><strong>{e(m["title"])}</strong><span>{e(m["source"]["creator"])} · {e(m["source"]["duration"])}</span><span class="done" data-done="{e(m["id"])}"></span></button>' for m in lessons)
body = ''.join(render(m) for m in lessons)
data = json.dumps(lessons, ensure_ascii=False).replace('</', '<\\/')
out = (ROOT/'template.html').read_text().replace('<!--STYLE-->', (ROOT/'style.css').read_text()).replace('<!--LIBRARY-->',library).replace('<!--BODY-->',body).replace('<!--DATA-->',data).replace('<!--APP-->',(ROOT/'app.js').read_text())
(ROOT/'ファッションを学ぶ.html').write_text(out)
print(f'生成完了：{len(lessons)}本 / {ROOT / "ファッションを学ぶ.html"}')
