# -*- coding: utf-8 -*-
"""2613 白海豚 ANSI 動畫播放器
用法：
    python play.py            # 依各格預設停留時間播放
    python play.py 0.4        # 每格固定 0.4 秒
    python play.py 0.4 loop   # 固定 0.4 秒並循環播放
按 Ctrl+C 結束。
"""
import glob, os, sys, time

import json as _json
_hp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'holds.json')
HOLD = _json.load(open(_hp)) if os.path.exists(_hp) else {}

def main():
    fixed = None
    loop = 'loop' in sys.argv
    for a in sys.argv[1:]:
        try:
            fixed = float(a)
        except ValueError:
            pass

    here = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(here, 'ans', '*.ans')))
    if not files:
        print('找不到 ans/*.ans')
        return

    frames = []
    for f in files:
        with open(f, encoding='cp950', errors='replace', newline='') as fh:
            frames.append((os.path.basename(f)[:2], fh.read()))

    if os.name == 'nt':
        os.system('')          # 讓 Windows 主控台吃 ANSI escape

    try:
        while True:
            for key, body in frames:
                sys.stdout.write('\033[2J\033[H' + body)
                sys.stdout.flush()
                time.sleep(fixed if fixed else HOLD.get(key, 1.0))
            if not loop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[m\n')

if __name__ == '__main__':
    main()
