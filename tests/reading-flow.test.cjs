const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/podcast-listen.js'), 'utf8');
const index = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

test('the audio panel escapes catalog text and survives a malformed fragment', () => {
  // v4(분야별 재생) 칸: 칩 라벨은 esc()를 거치고, 주소의 # 해석은 hashId()로만 한다.
  assert.match(source, /esc\(text\)/);
  // 번호 목록·번호 배지·여러 개 고르기는 없다.
  assert.doesNotMatch(source, /podcast-cols|class = 'podcast-no'|data-pl-go/);
  assert.match(source, /esc\(ep\.audio\)/);
  assert.equal((source.match(/decodeURIComponent\(/g) || []).length, 1);
  const helper = source.slice(source.indexOf('const hashId ='), source.indexOf('const esc ='));
  const read = hash => vm.runInNewContext(helper + '; hashId()', { location: { hash } });
  assert.equal(read('#%'), '');
  assert.equal(read('#item%20ABC%2F1'), 'item ABC/1');
});

test('the deck ignores a malformed fragment and resolves a valid encoded id', () => {
  const decoder = index.slice(index.indexOf('function fragmentId('), index.indexOf('function scrollToFragment('));
  const read = vm.runInNewContext(decoder + '; fragmentId');
  assert.equal(read('#%'), '');
  assert.equal(read('#item%20ABC%2F1'), 'item ABC/1');
});

test('a late previous date cannot overwrite the failed current date in the calendar', async () => {
  const pending = new Map();
  const datesShown = [];
  const calls = {};
  const el = { setAttribute() {}, querySelector() { return null; }, addEventListener() {}, after() {} };
  const ctx = vm.createContext({
    CAL: { available: new Set(), selectedDate: null }, loadSequence: 0,
    document: { getElementById: id => id === 'v32-latest' ? null : el, createElement: () => el, addEventListener() {} },
    MutationObserver: class { observe() {} }, localStorage: { getItem: () => null },
    fetchMd: ds => new Promise(resolve => pending.set(ds, resolve)),
    esc: s => s, renderCal: () => datesShown.push(ctx.CAL.selectedDate), render() {}, loadDates() {},
    matchMedia: () => ({addEventListener() {}}),
  });
  ctx.window = ctx;
  // The desktop/mobile enhancements wrap the loader as a global on real pages.
  const sections = Array.from(index.matchAll(/<script>([\s\S]*?)<\/script>/g), match => match[1]);
  const body = sections[0];
  vm.runInContext(body.slice(body.indexOf('function showLoadError('),body.indexOf('function syncNetworkStatus(')),ctx);
  // Run the late enhancement layer too, so a stale post-load callback would be caught.
  el.querySelector = selector => selector === '.v3-sheet' ? el : null;
  vm.runInContext(sections[2],ctx);
  calls.first = ctx.loadAndRender('2026-11-17');
  calls.second = ctx.loadAndRender('2026-11-18');
  pending.get('2026-11-18')(null); await calls.second;
  pending.get('2026-11-17')('late markdown'); await calls.first;
  assert.deepEqual(datesShown, ['2026-11-18']);
  assert.equal(ctx.CAL.selectedDate, '2026-11-18');
  assert.match(el.innerHTML, /2026-11-18/);
});
