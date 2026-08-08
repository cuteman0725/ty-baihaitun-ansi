# -*- coding: utf-8 -*-
"""把 ans/*.ans 串成一篇可直接貼 PTT 的文章。

為什麼要這支：
  PTT 終端機 24 列，**最下面一行是狀態列**（瀏覽 第 x/y 頁…），
  所以文章內容區只有 **23 行**。每格做成 24 行的話，每翻一頁就會
  累積偏移一行，讀者得再多按一次「↓」才對得回來。
  → 每格固定 23 行，一格就是一畫面。

還有一個偏移來源：PTT 文章最前面會自動加「作者／標題／時間」三行。
  所以第一頁 = 那三行 + 我們的前 20 行，第一格會被切掉。
  解法是在最前面放一張 20 行的封面卡，把第一格推到第二頁的頂端。
  不同看板的標頭行數可能不同，用 --lead 調整封面卡的行數即可。

用法：
    python make_ptt.py                # 預設：封面卡 20 行（PTT 標頭 3 行）
    python make_ptt.py --lead 19      # 標頭 4 行的看板
    python make_ptt.py --no-cover     # 不要封面卡，只串 33 格
    python make_ptt.py --rows 23      # 每格行數（跟 gen.py 一致，通常不用改）
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
    ap.add_argument('--lead', type=int, default=20,
                    help='封面卡行數（PTT 標頭 3 行時用 20；標頭 4 行用 19）')
    ap.add_argument('--rows', type=int, default=23, help='每格行數')
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
        lines = open(f, encoding='cp950', newline='').read().split('\r\n')
        while lines and lines[-1] == '':
            lines.pop()
        if len(lines) != a.rows:
            print('✗ %s 有 %d 行，應該是 %d 行（先跑 gen.py）' % (f, len(lines), a.rows))
            sys.exit(1)
        out += lines

    open(a.out, 'w', encoding='cp950', errors='replace', newline='').write(
        '\r\n'.join(out) + '\r\n')

    pages = len(out) // a.rows
    print('✓ %s' % a.out)
    print('  封面卡 %d 行 ＋ %d 格 × %d 行 ＝ %d 行（%d 個畫面）'
          % (0 if a.no_cover else a.lead, len(files), a.rows, len(out), pages))
    print('  最寬 %d 欄' % max(dispw(l) for l in out))
    if not a.no_cover:
        print('  對齊：PTT 標頭 3 行 ＋ 封面卡 %d 行 ＝ 第 1 頁；'
              '之後每按一次 PageDown 正好換一格' % a.lead)
        print('  若貼上後對不齊，用 --lead 加減幾行再產一次即可')


if __name__ == '__main__':
    main()
