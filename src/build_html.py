# -*- coding: utf-8 -*-
"""把 ans/*.ans 轉成單一自帶播放器的 HTML 預覽檔"""
import glob, json, os, re, html, unicodedata


def _wide(ch):
    if ord(ch) < 128:
        return False
    try:
        return len(ch.encode('cp950')) == 2
    except Exception:
        return unicodedata.east_asian_width(ch) in ('W', 'F')


WCH = {}          # 全形字 → 類別編號（給前端逐字量測、必要時橫向拉伸）


def cells(txt):
    """全形字各自鎖 2ch、半形連續段落照原樣 —— 保證瀏覽器對齊等同終端機"""
    out, buf = [], []
    for ch in txt:
        if _wide(ch):
            if buf:
                out.append(html.escape(''.join(buf))); buf = []
            k = WCH.setdefault(ch, len(WCH))
            out.append('<i class="c%d">%s</i>' % (k, html.escape(ch)))
        else:
            buf.append(ch)
    if buf:
        out.append(html.escape(''.join(buf)))
    return ''.join(out)

FG = {'30': '#555555', '31': '#aa0000', '32': '#00aa00', '33': '#aa5500',
      '34': '#0000aa', '35': '#aa00aa', '36': '#00aaaa', '37': '#aaaaaa'}
FGB = {'30': '#666666', '31': '#ff5555', '32': '#55ff55', '33': '#ffff55',
       '34': '#5555ff', '35': '#ff55ff', '36': '#55ffff', '37': '#ffffff'}
BG = {'40': '#000000', '41': '#aa0000', '42': '#00aa00', '43': '#aa5500',
      '44': '#0000aa', '45': '#aa00aa', '46': '#00aaaa', '47': '#aaaaaa'}


def conv(text):
    out, fg, bg, bold, blink = [], '37', None, False, False
    open_span = False

    def style():
        c = (FGB if bold else FG).get(fg, '#aaaaaa')
        s = 'color:%s' % c
        if bg:
            s += ';background:%s' % BG[bg]
        return s

    for tok in re.split(r'(\x1b\[[0-9;]*m)', text):
        if tok.startswith('\x1b['):
            codes = tok[2:-1].split(';')
            if codes == [''] or codes == ['0']:
                fg, bg, bold, blink = '37', None, False, False
            for c in codes:
                if c == '0' or c == '':
                    fg, bg, bold, blink = '37', None, False, False
                elif c == '1':
                    bold = True
                elif c == '5':
                    blink = True
                elif c in FG:
                    fg = c
                elif c in BG:
                    bg = c
            continue
        if not tok:
            continue
        if open_span:
            out.append('</span>')
        out.append('<span class="%s" style="%s">%s</span>' % (
            'bk' if blink else '', style(), cells(tok)))
        open_span = False
    return ''.join(out)


frames = []
holds = json.load(open('holds.json'))
for f in sorted(glob.glob('ans/*.ans')):
    key = os.path.basename(f)[:2]
    raw = open(f, encoding='cp950', newline='').read().rstrip('\r\n')
    lines = [conv(l) for l in raw.split('\r\n')]
    frames.append({'id': os.path.basename(f)[:-4], 'hold': holds.get(key, 1.0),
                   'html': '\n'.join(lines)})

TPL = """<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0e13">
<meta name="description" content="2613 白海豚颱風的 PTT ANSI 氣象短劇：北方三番兩次想把白海豚拐走，結果每次都失敗。8 幕＋片尾＋彩蛋共 33 格，約 31 秒。">
<meta property="og:title" content="2613 白海豚：一隻不肯往北游的海豚">
<meta property="og:description" content="PTT / BePTT ANSI 氣象短劇 v3.3 — 8 幕＋片尾＋彩蛋 33 格，約 31 秒。">
<meta property="og:type" content="website">
<title>2613 白海豚 ANSI 短劇 v3 — 預覽</title>
<style>
:root{--bg:#0b0e13;--panel:#151a22;--line:#252c38;--ink:#d7dee8;--dim:#7a8698;--acc:#55ffff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font-family:-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
header{padding:18px 20px 12px;border-bottom:1px solid var(--line)}
h1{margin:0 0 4px;font-size:19px;letter-spacing:.5px}
.sub{color:var(--dim);font-size:13px;line-height:1.7}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px 40px}
.screen{background:#000;border:1px solid var(--line);border-radius:8px;
        padding:10px;margin:14px 0 10px;overflow:hidden;position:relative;
        -webkit-user-select:none;user-select:none;touch-action:manipulation}
.tapL,.tapR{position:absolute;top:0;bottom:0;width:34%;z-index:2;cursor:pointer}
.tapL{left:0}.tapR{right:0}
pre{margin:0;font-family:"DejaVu Sans Mono","Noto Sans Mono CJK TC","Sarasa Mono TC",
    "MS Gothic",monospace;font-size:14px;line-height:1.25;white-space:pre;letter-spacing:0;
    display:inline-block}
pre i{display:inline-block;width:2ch;font-style:normal;text-align:center;
      overflow:hidden;vertical-align:top;transform-origin:center}
.bk{animation:bk 1s steps(1) infinite}
@keyframes bk{0%,49%{opacity:1}50%,100%{opacity:.18}}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;
     background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
button{background:#222a36;color:var(--ink);border:1px solid var(--line);border-radius:6px;
       padding:7px 14px;font-size:14px;cursor:pointer;font-family:inherit}
button:hover{background:#2c3746}
button.pri{background:var(--acc);color:#04202a;border-color:var(--acc);font-weight:700}
.meta{margin-left:auto;color:var(--dim);font-size:13px;font-variant-numeric:tabular-nums}
input[type=range]{width:220px;accent-color:var(--acc)}
.track{display:flex;gap:3px;margin:12px 0 0;flex-wrap:wrap}
.track b{flex:1 1 0;min-width:6px;height:10px;background:#2a3342;border-radius:2px;cursor:pointer}
.track b.on{background:var(--acc)}
.track b.act{background:#ffff55}
.note{color:var(--dim);font-size:12.5px;line-height:1.8;margin-top:16px;
      border-top:1px solid var(--line);padding-top:14px}
kbd{background:#222a36;border:1px solid var(--line);border-radius:4px;padding:1px 6px;font-size:12px}
@media (max-width:700px){
  header{padding:12px 14px 10px}
  h1{font-size:16px}
  .sub{font-size:12px;line-height:1.6}
  .wrap{padding:0 8px 28px}
  .screen{padding:6px;border-radius:6px}
  button{padding:11px 12px;font-size:15px;flex:1 1 auto;min-width:0}
  button.pri{flex:1 1 100%}
  .bar{gap:6px;padding:8px}
  .meta{width:100%;margin:2px 0 0;text-align:center;font-size:12px}
  input[type=range]{width:100%}
  label{flex:1 1 100%;display:flex;gap:8px;align-items:center}
  .kb{display:none}
}
</style></head><body>
<header><div class="wrap">
<h1>2613 白海豚：一隻不肯往北游的海豚</h1>
<div class="sub">PTT / BePTT ANSI 短劇預覽　v3.3　·　8 幕＋片尾＋彩蛋　33 格　·　78 欄 × 21 行　·　預設約 78 秒（原稿節奏 31 秒 × 2.5）<br>
北方三番兩次想把白海豚拐走，結果每次都失敗——牠不是跳一下，就是晃一下，然後若無其事繼續往西。</div>
</div></header>
<div class="wrap">
  <div class="screen" id="box">
    <div class="tapL" id="tapL"></div><div class="tapR" id="tapR"></div>
    <pre id="scr"></pre>
  </div>
  <div class="bar">
    <button class="pri" id="play">▶ 播放</button>
    <button id="prev">◀ 上一格</button>
    <button id="next">下一格 ▶</button>
    <button id="rst">⟲ 重頭</button>
    <label style="color:var(--dim);font-size:13px">停留
      <input type="range" id="spd" min="0.5" max="5" step="0.25" value="2.5">
      <b id="spdv" style="color:var(--acc);font-weight:600;white-space:nowrap"></b></label>
    <span class="meta" id="meta"></span>
  </div>
  <div class="track" id="track"></div>
  <div class="note">
    <span class="kb">鍵盤：<kbd>空白鍵</kbd> 播放／暫停　<kbd>←</kbd><kbd>→</kbd> 逐格　<kbd>R</kbd> 重頭。<br></span>
    輕觸畫面左／右半邊可以往前／往後一格；點進度條任一段可跳到該格。<br>
    預設每格停留原稿的 <b>2.5 倍</b>（全片約 78 秒），這樣三行字幕才讀得完；
    滑桿往左拉＝變快，往右拉＝更慢。<br>
    這頁只是預覽用；真正貼 PTT 的是 <code>ans/*.ans</code>（Big5 + CRLF）或
    <code>ptt_全片串接.ans</code>（封面卡 ＋ 33 格 × <b>22 行</b>——PTT 每頁可見 23 行但只前進 22 行，上一頁最後一行會變成下一頁第一行，所以每格是 21 行內容＋1 行共用空白）。
  </div>
</div>
<script>
const F = __FRAMES__;
const WCH = __WCH__;
// 逐字量測：有些系統的框線字（─│┌┐）在瀏覽器只有 1 格寬，會讓框看起來是虛線。
// 這裡量出實際寬度，只對「明顯偏窄」的字做橫向拉伸，補回終端機的等寬感。
(function fitWide(){
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
  document.getElementById('scr').appendChild(probe);
  probe.textContent = 'x'.repeat(40);
  const unit = probe.getBoundingClientRect().width / 40;
  const rules = [];
  for (const ch in WCH){
    probe.textContent = ch.repeat(20);
    const w = probe.getBoundingClientRect().width / 20;
    const k = (2 * unit) / w;
    // 只拉伸「必須首尾相接」的線條字；◎ ↑ ← 皿 這類符號維持原形置中即可
    if (k > 1.06 && '─│┌┐└┘├┤┬┴╲╱█▓'.includes(ch))
      rules.push(`.c${WCH[ch]}{transform:scaleX(${k.toFixed(3)})}`);
  }
  probe.remove();
  const st = document.createElement('style');
  st.textContent = rules.join(''); document.head.appendChild(st);
})();
// 手機自適應：量出「78 欄」在目前字型下的寬度，反推 font-size 讓它剛好塞滿畫面
function fitWidth(){
  const box = document.getElementById('box'), pre = document.getElementById('scr');
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font-size:100px';
  probe.style.fontFamily = getComputedStyle(pre).fontFamily;
  probe.textContent = 'x'.repeat(78);
  document.body.appendChild(probe);
  const w100 = probe.getBoundingClientRect().width;
  probe.remove();
  const avail = box.clientWidth - 12;
  const size = Math.max(4, Math.min(15, 100 * avail / w100));
  pre.style.fontSize = size.toFixed(2) + 'px';
}
addEventListener('resize', fitWidth);
addEventListener('orientationchange', () => setTimeout(fitWidth, 200));

let i = 0, timer = null, mult = 2.5;   // 停留倍率：往右拉＝每格停久一點
const scr = document.getElementById('scr'), meta = document.getElementById('meta');
const track = document.getElementById('track');
F.forEach((f, k) => { const b = document.createElement('b');
  b.onclick = () => { stop(); show(k); }; track.appendChild(b); });
const bars = [...track.children];
function show(k){ i = k; scr.innerHTML = F[k].html;
  meta.textContent = `第 ${k+1} / ${F.length} 格　${F[k].id}　停留 ${(F[k].hold*mult).toFixed(1)}s`;
  bars.forEach((b, j) => { b.className = j < k ? 'on' : (j === k ? 'act' : ''); }); }
const ms = k => F[k].hold * 1000 * mult;
function step(){ show((i + 1) % F.length);
  timer = setTimeout(i === F.length - 1 ? stop : step, ms(i)); }
function play(){ if (timer) return; document.getElementById('play').textContent = '❚❚ 暫停';
  timer = setTimeout(step, ms(i)); }
function stop(){ clearTimeout(timer); timer = null;
  document.getElementById('play').textContent = '▶ 播放'; }
document.getElementById('play').onclick = () => timer ? stop() : play();
document.getElementById('next').onclick = () => { stop(); show((i + 1) % F.length); };
document.getElementById('prev').onclick = () => { stop(); show((i - 1 + F.length) % F.length); };
document.getElementById('rst').onclick = () => { stop(); document.getElementById('tapL').onclick = () => { stop(); show((i - 1 + F.length) % F.length); };
document.getElementById('tapR').onclick = () => { stop(); show((i + 1) % F.length); };
show(0);
fitWidth();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitWidth); };
const TOTAL = F.reduce((a, f) => a + f.hold, 0);
function spdLabel(){
  document.getElementById('spdv').textContent =
    `×${mult}　全片 ${Math.round(TOTAL * mult)} 秒`;
  show(i);
}
document.getElementById('spd').oninput = e => { mult = +e.target.value; spdLabel(); };
spdLabel();
addEventListener('keydown', e => {
  if (e.key === ' '){ e.preventDefault(); timer ? stop() : play(); }
  if (e.key === 'ArrowRight'){ stop(); show((i + 1) % F.length); }
  if (e.key === 'ArrowLeft'){ stop(); show((i - 1 + F.length) % F.length); }
  if (e.key.toLowerCase() === 'r'){ stop(); document.getElementById('tapL').onclick = () => { stop(); show((i - 1 + F.length) % F.length); };
document.getElementById('tapR').onclick = () => { stop(); show((i + 1) % F.length); };
show(0);
fitWidth();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitWidth); }
});
document.getElementById('tapL').onclick = () => { stop(); show((i - 1 + F.length) % F.length); };
document.getElementById('tapR').onclick = () => { stop(); show((i + 1) % F.length); };
show(0);
fitWidth();
if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitWidth);
</script></body></html>"""

open('2613白海豚_ANSI動畫_預覽.html', 'w', encoding='utf-8').write(
    TPL.replace('__FRAMES__', json.dumps(frames, ensure_ascii=False))
       .replace('__WCH__', json.dumps(WCH, ensure_ascii=False)))
print('HTML written, frames =', len(frames))
