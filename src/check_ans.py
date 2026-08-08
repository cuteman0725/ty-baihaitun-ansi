# -*- coding: utf-8 -*-
"""2613 白海豚 ANSI 短劇 —— 自動化驗收
用法：python check_ans.py
檢查項目：
  1. 每格欄寬 ≤ 80（PTT 終端機上限）
  2. 每格行數 = 24（一個 PTT 畫面）
  3. 全部字元可用 Big5(cp950) 編碼
  4. ptt_全片串接.ans ＋ PTT 標頭 3 行後，總行數是 23 的整數倍
  5. holds.json 與 ans/ 檔數一致，並印出總片長
  6. 故事稿 md 的逐格草稿也不超過 78 欄、code fence 成對
任何一項失敗 → 非 0 離開碼。
"""
import glob, json, os, re, sys

ESC = re.compile('\x1b\\[[0-9;]*m')
ROWS = 23      # PTT 內容區只有 23 行（第 24 行是狀態列）
PTT_HEAD = 3   # PTT 文章自動加的「作者／標題／時間」三行
MAXW = 80
FAIL = []


def wide(ch):
    if ord(ch) < 128:
        return False
    try:
        return len(ch.encode('cp950')) == 2
    except Exception:
        return True


def dispw(s):
    return sum(2 if wide(c) else 1 for c in s)


def strip(ln):
    return ESC.sub('', ln)


def check(cond, msg):
    if not cond:
        FAIL.append(msg)
    return cond


def main():
    here = os.path.dirname(os.path.abspath(__file__)) or '.'
    os.chdir(here)

    files = sorted(glob.glob('ans/*.ans'))
    check(files, 'ans/ 下找不到任何 .ans')
    maxw, heights, bad = 0, set(), set()

    for f in files:
        raw = open(f, encoding='cp950', newline='').read()
        lines = raw.split('\r\n')
        while lines and lines[-1] == '':
            lines.pop()
        heights.add(len(lines))
        check(len(lines) == ROWS, '%s 行數 %d ≠ %d' % (f, len(lines), ROWS))
        for n, ln in enumerate(lines, 1):
            t = strip(ln)
            w = dispw(t)
            maxw = max(maxw, w)
            check(w <= MAXW, '%s 第 %d 行寬 %d > %d' % (f, n, w, MAXW))
            for ch in t:
                try:
                    ch.encode('cp950')
                except Exception:
                    bad.add(ch)
    check(not bad, '出現非 Big5 字元：%s' % ''.join(sorted(bad)))

    # 串接檔（含封面卡，總行數必須是 ROWS 的整數倍，PageDown 才會格格對齊）
    cat = 'ptt_全片串接.ans'
    pages = 0
    if check(os.path.exists(cat), '找不到 %s' % cat):
        L = open(cat, encoding='cp950', newline='').read().split('\r\n')
        while L and L[-1] == '':
            L.pop()
        pages = (len(L) + PTT_HEAD) / ROWS
        check((len(L) + PTT_HEAD) % ROWS == 0,
              '%s：貼上 PTT 後總行數 %d（含標頭 %d 行）不是 %d 的整數倍'
              '——翻頁會對不齊，用 make_ptt.py --lead 調整封面卡'
              % (cat, len(L) + PTT_HEAD, PTT_HEAD, ROWS))
        check(len(L) >= len(files) * ROWS,
              '%s 行數 %d 少於 %d 格 × %d' % (cat, len(L), len(files), ROWS))
        for n, ln in enumerate(L, 1):
            check(dispw(strip(ln)) <= MAXW, '%s 第 %d 行超過 %d 欄' % (cat, n, MAXW))

    # holds
    total = 0.0
    if check(os.path.exists('holds.json'), '找不到 holds.json'):
        h = json.load(open('holds.json'))
        check(len(h) == len(files), 'holds.json 有 %d 筆，ans 有 %d 格' % (len(h), len(files)))
        total = sum(h.values())

    # 故事稿
    md = '2613白海豚_ANSI動畫故事稿.md'
    blocks = []
    if os.path.exists(md):
        txt = open(md, encoding='utf-8').read()
        fences = len(re.findall(r'^```', txt, re.M))
        check(fences % 2 == 0, '故事稿 code fence 不成對（%d）' % fences)
        blocks = re.findall(r'^```\n(.*?)^```', txt, re.S | re.M)
        for b in blocks:
            for ln in b.split('\n'):
                check(dispw(ln) <= 78, '故事稿草稿有一行 %d 欄 > 78：%s' % (dispw(ln), ln[:30]))

    print('─' * 56)
    print('  格數        %d' % len(files))
    print('  每格行數    %s' % sorted(heights))
    print('  最寬        %d 欄（上限 %d）' % (maxw, MAXW))
    print('  Big5        %s' % ('全部通過' if not bad else '有問題'))
    print('  總片長      %.1f 秒' % total)
    print('  故事稿草稿  %d 段' % len(blocks))
    print('  貼上 PTT 後  %g 個畫面（封面卡 1 ＋ 內容 %d）' % (pages, len(files)))
    print('─' * 56)
    if FAIL:
        print('✗ 失敗 %d 項：' % len(FAIL))
        for m in FAIL[:20]:
            print('   -', m)
        sys.exit(1)
    print('✓ 全數通過')


if __name__ == '__main__':
    main()
