'use strict';
(() => {
  const lessons = JSON.parse(document.getElementById('lesson-data').textContent);
  const KEY = 'fashion-learning-records-v1';
  const noteKeys = ['scene', 'attributes', 'connections', 'experiment'];
  const byId = id => lessons.find(m => m.id === id);
  const emptyRecord = () => ({notes: {}, answers: {}, graded: false, complete: false, example: 0});
  let state = {version: 1, current: lessons[0].id, records: {}};
  let storageAvailable = true;
  const saveStatus = document.getElementById('save-status');
  const safeText = v => typeof v === 'string' && v.length <= 50000;

  function sanitize(raw) {
    if (!raw || raw.version !== 1 || !raw.records || typeof raw.records !== 'object' || Array.isArray(raw.records)) throw new Error('記録ファイルの形式が違います。');
    const clean = {version: 1, current: byId(raw.current) ? raw.current : lessons[0].id, records: {}};
    for (const m of lessons) {
      const r = raw.records[m.id];
      if (!r || typeof r !== 'object') continue;
      const record = emptyRecord();
      for (const key of noteKeys) if (safeText(r.notes?.[key])) record.notes[key] = r.notes[key];
      m.quiz.forEach((q, i) => { if (Number.isInteger(r.answers?.[i]) && r.answers[i] >= 0 && r.answers[i] < q.options.length) record.answers[i] = r.answers[i]; });
      record.complete = r.complete === true;
      record.graded = r.graded === true;
      record.example = Number.isInteger(r.example) && r.example >= 0 && r.example < m.examples.length ? r.example : 0;
      clean.records[m.id] = record;
    }
    return clean;
  }
  try {
    const saved = localStorage.getItem(KEY);
    if (saved) state = sanitize(JSON.parse(saved));
  } catch (_) {
    storageAvailable = false;
    saveStatus.textContent = '保存済みの記録を読み込めませんでした。編集した記録は書き出して保管してください。';
  }
  const recordFor = id => state.records[id] || (state.records[id] = emptyRecord());
  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
      storageAvailable = true;
      saveStatus.textContent = '学習メモ・回答・学習済みの状態を、このブラウザに保存しました。';
    } catch (_) {
      storageAvailable = false;
      saveStatus.textContent = 'この環境では自動保存できません。「記録を書き出す」で保存してください。';
    }
  }
  function download(name, content, type) {
    const url = URL.createObjectURL(new Blob([content], {type}));
    const a = document.createElement('a');
    a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function updateBadges() {
    document.querySelectorAll('[data-done]').forEach(el => { el.textContent = recordFor(el.dataset.done).complete ? '✓ 学習済み' : ''; });
  }
  function setExample(article, m, index) {
    article.querySelectorAll('[data-example]').forEach(el => { el.hidden = Number(el.dataset.example) !== index; });
    article.querySelectorAll('[data-example-button]').forEach(el => el.setAttribute('aria-expanded', String(Number(el.dataset.exampleButton) === index)));
    recordFor(m.id).example = index;
  }
  function grade(article, m, persist) {
    const r = recordFor(m.id);
    let correct = 0;
    let answered = 0;
    m.quiz.forEach((q, i) => {
      const answer = r.answers[i];
      const exists = Number.isInteger(answer);
      const right = answer === q.answer;
      if (exists) answered++;
      if (right) correct++;
      const feedback = article.querySelector(`[data-feedback="${i}"]`);
      feedback.replaceChildren();
      const title = document.createElement('strong');
      title.textContent = !exists ? '未回答です。選んでから、もう一度確認しましょう。' : right ? '正解' : '見方をもう一度確認しましょう。';
      feedback.append(title);
      if (exists) {
        const text = document.createElement('p');
        text.textContent = `正解：${q.options[q.answer]} ${q.explanation}`;
        const link = document.createElement('a');
        link.className = 'time'; link.href = `${m.source.url}&t=${q.time}s`;
        link.target = '_blank'; link.rel = 'noopener'; link.textContent = '該当箇所を動画で確認 ↗';
        feedback.append(text, link);
      }
      feedback.hidden = false;
      feedback.classList.toggle('wrong', !right);
    });
    article.querySelector('[data-score]').textContent = `${m.quiz.length}問中 ${correct}問正解${answered < m.quiz.length ? ` ／ 未回答 ${m.quiz.length - answered}問` : ''}`;
    r.graded = true;
    if (persist) save();
  }
  function selectLesson(id) {
    if (!byId(id)) return;
    document.querySelectorAll('[data-lesson]').forEach(el => { el.hidden = el.dataset.lesson !== id; });
    document.querySelectorAll('[data-select-lesson]').forEach(el => {
      if (el.dataset.selectLesson === id) el.setAttribute('aria-current', 'true');
      else el.removeAttribute('aria-current');
    });
    state.current = id;
    document.querySelector('.edition').textContent = `学習ノート / ${String(lessons.length).padStart(2,'0')}本`;
  }
  function restoreUI() {
    for (const m of lessons) {
      const article = document.querySelector(`[data-lesson="${m.id}"]`);
      const r = recordFor(m.id);
      article.querySelectorAll('[data-note]').forEach(el => { el.value = r.notes[el.dataset.note] || ''; });
      article.querySelectorAll('[data-question]').forEach(el => { el.checked = r.answers[el.dataset.question] === Number(el.value); });
      article.querySelector('[data-complete]').checked = r.complete;
      setExample(article, m, r.example);
      if (r.graded) grade(article, m, false);
      else {
        article.querySelectorAll('[data-feedback]').forEach(el => { el.hidden = true; });
        article.querySelector('[data-score]').textContent = '';
      }
    }
    selectLesson(state.current);
    updateBadges();
  }
  for (const m of lessons) {
    const article = document.querySelector(`[data-lesson="${m.id}"]`);
    article.querySelectorAll('[data-example-button]').forEach(button => button.addEventListener('click', () => {
      setExample(article, m, Number(button.dataset.exampleButton)); save();
    }));
    article.querySelectorAll('[data-note]').forEach(el => el.addEventListener('input', () => {
      recordFor(m.id).notes[el.dataset.note] = el.value; save();
    }));
    article.querySelectorAll('[data-question]').forEach(el => el.addEventListener('change', () => {
      const r = recordFor(m.id); r.answers[el.dataset.question] = Number(el.value);
      r.graded = false;
      article.querySelectorAll('[data-feedback]').forEach(f => { f.hidden = true; });
      article.querySelector('[data-score]').textContent = '回答を変更しました。「回答を確認する」で再確認できます。';
      save();
    }));
    article.querySelector('[data-grade]').addEventListener('click', () => grade(article, m, true));
    article.querySelector('[data-complete]').addEventListener('change', event => {
      recordFor(m.id).complete = event.target.checked; updateBadges(); save();
    });
    article.querySelector('[data-export-notes]').addEventListener('click', () => {
      const r = recordFor(m.id);
      const fields = m.worksheet ? m.worksheet.map(([key, label]) => [key, label]) : [['scene', '場面と軸の服'], ['attributes', 'メイン・サブ属性'], ['connections', '共通点と拾われていない要素'], ['experiment', '比較した結果']];
      const content = [`# ${m.title}`, '', `出典：[${m.source.creator}](${m.source.url})`, '', ...fields.flatMap(([key, label]) => [`## ${label}`, '', r.notes[key] || '（未記入）', ''])].join('\n');
      download(`ファッション学習ワーク_${m.number}.md`, content, 'text/markdown;charset=utf-8');
    });
  }
  document.querySelectorAll('[data-select-lesson]').forEach(button => button.addEventListener('click', () => {
    history.replaceState(null, '', location.pathname + location.search);
    selectLesson(button.dataset.selectLesson); save();
    document.getElementById('lesson-content').focus({preventScroll:true});
    window.scrollTo({top:0, behavior:'instant'});
  }));
  document.querySelectorAll('[data-related-lesson]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    selectLesson(link.dataset.relatedLesson);
    history.replaceState(null, '', link.getAttribute('href'));
    document.getElementById('lesson-content').focus({preventScroll:true});
    document.getElementById(location.hash.slice(1))?.scrollIntoView({behavior:'instant'});
    save();
  }));
  window.addEventListener('hashchange', () => {
    const id = location.hash.slice(1);
    const m = lessons.find(lesson => id.startsWith(lesson.id + '-'));
    if (m) { selectLesson(m.id); document.getElementById(id)?.scrollIntoView({behavior:'instant'}); save(); }
  });
  document.getElementById('backup').addEventListener('click', () => {
    download('ファッション学習記録.json', JSON.stringify(state, null, 2), 'application/json');
    document.getElementById('backup-status').textContent = '記録ファイルを書き出しました。';
  });
  document.getElementById('restore').addEventListener('change', async event => {
    const input = event.target;
    const file = input.files[0];
    if (!file) return;
    try {
      if (file.size > 1000000) throw new Error('ファイルが大きすぎます。教材から書き出した記録を選んでください。');
      const imported = sanitize(JSON.parse(await file.text()));
      if (!Object.keys(imported.records).length) throw new Error('この教材に対応する記録がありません。');
      state.records = {...state.records, ...imported.records};
      state.current = imported.current;
      restoreUI(); save();
      document.getElementById('backup-status').textContent = storageAvailable ? '記録を読み込みました。' : '記録を読み込みました。自動保存は利用できないため、書き出して保管してください。';
    } catch (error) {
      document.getElementById('backup-status').textContent = `読み込めませんでした：${error.message}`;
    }
    input.value = '';
  });
  restoreUI();
  const hashId = location.hash.slice(1);
  const linkedLesson = lessons.find(m => hashId.startsWith(m.id + '-'));
  if (linkedLesson) selectLesson(linkedLesson.id);
  if (storageAvailable) save();
})();
