# -*- coding: utf-8 -*-
"""把 ans/*.ans 串成一篇可直接貼 PTT 的文章。

為什麼要這支（2026/08/09 依實貼 PTT 的行號重新校準）：

  PTT 終端機 24 列，最下面一行是狀態列，內容區 23 行。但**翻頁只前進 22 行**——
  上一頁的最後一行會變成下一頁的第一行（推文 hit1205 也提到這件事）。
  實測文章行號：第1頁 01~22、第2頁 22~44、第3頁 44~66 …… 每頁起點差 22。

  所以正確的做法是：
    · 每格 = **21 行內容 ＋ 1 行空白** = 22 行
    · 那行空白同時是本格的結尾與下一格畫面的頂端，重疊處看不出來
    · 每頁看到的就是「空白 ＋ 21 行內容 ＋ 空白」，剛好 23 行

  第二個偏移來源：PTT 文章最前面固定 4 行（作者／標題／時間＋分隔線）。
  4 ＋ 封面卡 18 行 ＝ 22 ＝ 第一頁，第一格才會從第二頁頂端開始。
  不同看板若標頭行數不同，用 --lead 加減即可。

用法：
    python make_ptt.py                # 預設：封面卡 18 行（PTT 標頭 4 行）
    python make_ptt.py --lead 17      # 標頭 5 行的看板
    python make_ptt.py --no-cover     # 不要封面卡，只串 33 格
    python make_ptt.py --rows 22      # 每格行數（跟 gen.py 一致，通常不用改）
"""
import argparse, glob, os, re, sys, unicodedata

ESC = re.compile('\x1b\\[[0-9;]*m')


def wide(ch):
    if ord(ch) < 128:
        return False
    try:
        return len(ch.encode('cp950')) == 2
    except Exception:
        return unicodedata.east_asian_width(ch) in ('W', 'F')


def dispw(s):
    return sum(2 if wide(c) else 1 for c in ESC.sub('', s))


def center(text, width=78):
    pad = max(0, (width - dispw(text)) // 2)
    return ' ' * pad + text


def cover(lines):
    """封面卡，總共剛好 `lines` 行"""
    body = [
        '',
        '\033[1;36m' + center('２６１３　白 海 豚') + '\033[m',
        '',
        '\033[1;37m' + center('一 隻 不 肯 往 北 游 的 海 豚') + '\033[m',
        '',
        '',
        '\033[1;37m' + center('北方三番兩次想把白海豚拐走，結果每次都失敗。') + '\033[m',
        '\033[1;37m' + center('牠不是跳一下，就是晃一下，然後若無其事地繼續往西。') + '\033[m',
        '',
        '',
        '\033[1;30m' + center('PTT / BePTT ANSI 氣象短劇　８ 幕 ＋ 片尾 ＋ 彩蛋　共 33 格') + '\033[m',
        '\033[1;30m' + center('故事是擬人的，物理是真的。') + '\033[m',
        '',
        '',
        '\033[1;5;33m' + center('↓　按 PageDown（或空白鍵）開始　↓') + '\033[m',
    ]
    if len(body) > lines:
        body = body[:lines]
    return body + [''] * (lines - len(body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lead', type=int, default=18,
                    help='封面卡行數（PTT 標頭 4 行時用 18）')
    ap.add_argument('--rows', type=int, default=22, help='每格行數（21 內容＋1 共用空行）')
    ap.add_argument('--head', type=int, default=4, help='PTT 文章標頭行數')
    ap.add_argument('--step', type=int, default=22, help='PTT 每次翻頁前進幾行')
    ap.add_argument('--no-cover', action='store_true')
    ap.add_argument('--out', default='ptt_全片串接.ans')
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__)) or '.'
    os.chdir(here)

    files = sorted(glob.glob('ans/*.ans'))
    if not files:
        print('ans/ 下找不到任何 .ans'); sys.exit(1)

    out = [] if a.no_cover else cover(a.lead)
    for f in files:
        raw = open(f, encoding='cp950', newline='').read().split('\r\n')
        # 注意：不能把結尾空行全部去掉——最後那行空白是「與下一格共用的邊界」，
        # 少了它翻頁就會差一行。只丟掉檔尾的終止符。
        while len(raw) > a.rows and raw[-1] == '':
            raw.pop()
        if len(raw) != a.rows:
            print('✗ %s 有 %d 行，應該是 %d 行（先跑 gen.py）' % (f, len(raw), a.rows))
            sys.exit(1)
        out += raw

    open(a.out, 'w', encoding='cp950', errors='replace', newline='').write(
        '\r\n'.join(out) + '\r\n')

    total = len(out) + a.head              # 貼上 PTT 後的文章總行數
    print('✓ %s' % a.out)
    print('  封面卡 %d 行 ＋ %d 格 × %d 行 ＝ %d 行'
          % (0 if a.no_cover else a.lead, len(files), a.rows, len(out)))
    print('  最寬 %d 欄' % max(dispw(l) for l in out))
    if not a.no_cover:
        print('  貼上 PTT 後：標頭 %d 行 ＋ %d 行 ＝ %d 行 ＝ %g 頁 × %d'
              % (a.head, len(out), total, total / a.step, a.step))
        if total % a.step:
            print('  ✗ 不是 %d 的整數倍，翻頁會對不齊——用 --lead 加減 %d 行'
                  % (a.step, total % a.step))
        else:
            print('  ✓ 每按一次 PageDown 正好換一格（第 1 頁是封面卡）')
        print('  若貼上後仍差幾行，用 --lead 加減再產一次即可')


if __name__ == '__main__':
    main()
