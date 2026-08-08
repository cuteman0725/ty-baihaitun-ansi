# -*- coding: utf-8 -*-
"""2613 白海豚 ANSI 動畫 —— 逐格畫面產生器
輸出: frames_plain.txt (純文字草稿) 與 ans/*.ans (含色碼)
"""
import os, unicodedata

W, H = 78, 18          # 地圖區
LAT_TOP, LAT_STEP = 34.0, 1.1        # row 0 = 34.0N
LON_L,  LON_STEP = 112.0, 0.55       # col 0 = 112.0E

def wide(ch):
    """PTT/Big5 終端機的真實寬度：cp950 雙位元組字元一律佔 2 欄。
    ◎ ○ ↑ ╲ ～ 這類字 Unicode 標成 Ambiguous，但在 Big5 站台是全形。"""
    if ord(ch) < 128:
        return False
    try:
        return len(ch.encode('cp950')) == 2
    except Exception:
        return unicodedata.east_asian_width(ch) in ('W', 'F')

def dispw(s):
    return sum(2 if wide(c) else 1 for c in s)

def rc(lat, lon):
    r = int(round((LAT_TOP - lat) / LAT_STEP))
    c = int(round((lon - LON_L) / LON_STEP))
    return r, c

class Canvas:
    def __init__(self):
        self.ch = [[' '] * W for _ in range(H)]
        self.co = [[None] * W for _ in range(H)]

    def put(self, r, c, s, color=None, over=True):
        if r < 0 or r >= H:
            return
        for x in s:
            w = 2 if wide(x) else 1
            if c < 0 or c + w > W:
                c += w
                continue
            if not over and self.ch[r][c] != ' ':
                c += w
                continue
            self.ch[r][c] = x
            self.co[r][c] = color
            if w == 2:
                self.ch[r][c + 1] = None
                self.co[r][c + 1] = None
            c += w

    def putll(self, lat, lon, s, color=None, over=True, dc=0, dr=0):
        r, c = rc(lat, lon)
        self.put(r + dr, c + dc, s, color, over)

    def plain(self):
        out = []
        for row in self.ch:
            out.append(''.join(x for x in row if x is not None).rstrip())
        return out

    def ansi(self):
        out = []
        for r in range(H):
            cur, buf = None, []
            for c in range(W):
                x = self.ch[r][c]
                if x is None:
                    continue
                col = self.co[r][c]
                if col != cur:
                    buf.append('\033[m' if col is None else '\033[%sm' % col)
                    cur = col
                buf.append(x)
            if cur is not None:
                buf.append('\033[m')
            line = ''.join(buf)
            while line.endswith(' '):
                line = line[:-1]
            out.append(line)
        return out

# ---------------- 色碼 ----------------
# 第二輪改版：角色化配色（主角＝亮青、實際路徑＝亮白、淘汰預測＝暗灰）
C_COAST = '37'        # 中國／日本海岸線 灰白
C_LAND  = '36'        # 地名 暗青
C_TW    = '1;32'      # 台灣 亮綠
C_HIGH  = '1;33'      # 副熱帶高壓「牆」 亮黃
C_TROU  = '1;34'      # 西風槽／北方拉力 亮藍
C_MG    = '1;35'      # 季風環流圈 MG 亮紫
C_PAST  = '1;37'      # 實際走過的路徑 亮白
C_GRID  = '1;30'      # 格點 暗灰
C_FCST  = '1;30'      # 預測／淘汰預測 暗灰虛線
C_EYE   = '1;5;36'    # 白海豚中心 閃爍亮青（主角，只有牠能閃）
C_EYE2  = '1;36'      # 白海豚中心 不閃
C_R7    = '33'        # 七級風圈 暗黃
C_R10   = '31'        # 十級風圈 暗紅
C_TXT   = '1;37'      # 上層字幕（故事）
C_NOTE  = '1;30'      # 下層字幕（氣象）
C_GAG   = '1;5;33'    # 梗字（跳！又跳！）閃爍黃
C_FCST2 = '36'        # 官方最新預測路徑 暗青
# 第三輪新增
C_CAST  = '1;33'      # 主播旁白 亮黃
C_BOARD = '1;33'      # 計分板標題 亮黃
C_FAIL  = '1;31'      # 計分板「✕」 亮紅
C_WAIT  = '1;33'      # 計分板「延後」 亮黃

# ---------------- 底圖 ----------------
CHINA = [(34.4,120.0),(33.5,120.3),(32.6,121.0),(31.9,121.7),(31.2,121.6),
         (30.5,121.0),(30.0,121.7),(29.4,121.9),(28.7,121.5),(28.0,120.9),
         (27.2,120.3),(26.5,119.9),(25.9,119.6),(25.3,119.0),(24.7,118.4),
         (24.4,118.0),(23.8,117.2),(23.3,116.5),(22.9,115.6),(22.6,114.6),
         (22.2,113.6),(21.8,112.7),(21.5,112.0)]

TAIWAN = [(25.3,121.5),(25.0,121.9),(24.5,121.9),(23.9,121.6),(23.2,121.3),
          (22.6,121.0),(22.0,120.7),(22.3,120.3),(23.0,120.1),(23.7,120.2),
          (24.4,120.7),(25.0,121.1),(25.3,121.5)]

LUZON = [(18.6,120.7),(18.4,121.6),(17.6,122.2),(16.6,122.3)]

RYUKYU = [(24.45,123.0),(24.34,124.16),(24.80,125.28),(26.20,127.0),
          (26.70,128.2),(27.30,128.9),(28.30,129.5),(29.6,130.3),(30.5,131.0)]

KYUSHU = [(31.6,130.4),(32.5,130.2),(33.3,130.5),(33.5,131.6),(32.8,132.0),
          (34.0,133.0),(34.2,134.5),(34.3,135.5)]

def line_pts(pts, step=0.12):
    """把折線內插成密集點"""
    out = []
    for i in range(len(pts) - 1):
        (a1, o1), (a2, o2) = pts[i], pts[i + 1]
        n = max(2, int(max(abs(a2 - a1), abs(o2 - o1)) / step))
        for k in range(n + 1):
            t = k / n
            out.append((a1 + (a2 - a1) * t, o1 + (o2 - o1) * t))
    return out

PLACES = [(31.2,121.6,'上海',2,0),(28.0,120.9,'溫州',-8,0),(25.05,121.5,'台北',2,0),
          (26.2,127.7,'那霸',2,0),(24.34,124.16,'石垣',2,0),(24.78,141.3,'硫磺島',2,0),
          (18.6,120.7,'呂宋',2,0)]

def base(show_places=True, taiwan=True):
    cv = Canvas()
    # 2026/08/08：拿掉每 5 度的「+」格點——畫面乾淨很多，海岸線與路徑才是主角
    for pts, col in ((CHINA, C_COAST), (LUZON, C_COAST),
                     (RYUKYU, C_COAST), (KYUSHU, C_COAST)):
        for la, lo in line_pts(pts):
            r, c = rc(la, lo)
            cv.put(r, c, '.', col)
    if taiwan:
        for la, lo in line_pts(TAIWAN, 0.08):
            r, c = rc(la, lo)
            cv.put(r, c, '#', C_TW)
    cv.putll(24.78, 141.3, '^', C_COAST)     # 硫磺島
    if show_places:
        for la, lo, nm, dc, dr in PLACES:
            cv.putll(la, lo, nm, C_LAND, dc=dc, dr=dr)
    return cv

# ---------------- 路徑 ----------------
TRACK = [
    ('07/28', 16.5, 152.5, 'TD'), ('07/29', 17.6, 149.6, 'TS'),
    ('07/30', 18.9, 146.6, 'TY'), ('07/31', 20.3, 143.6, 'STY'),
    ('08/01', 21.8, 141.0, 'SS'), ('08/02', 22.9, 139.1, 'ERC'),
    ('08/03', 23.9, 137.3, 'SS'), ('08/04', 24.9, 135.6, 'ERC'),
    ('08/05', 25.7, 134.2, 'SS'), ('08/06', 26.4, 132.6, 'SS'),
    ('08/07', 26.6, 130.3, 'SS'), ('08/08', 27.0, 127.3, 'SS'),
    ('08/09', 27.5, 124.8, 'SS'), ('08/10', 28.0, 122.8, 'SS'),
    ('08/11', 28.6, 121.3, 'LAND'),
]
IDX = {t[0]: i for i, t in enumerate(TRACK)}

# 海豚跳：08/02~08/07 疊上擺線位移（單位：列）
WOBBLE = {'08/02': +1, '08/03': -1, '08/04': +1, '08/05': -1,
          '08/06': +1, '08/07': -1}

def draw_track(cv, upto, wob=False, mark='o', color=C_PAST):
    """畫已走過的路徑點"""
    for d, la, lo, k in TRACK[:IDX[upto] + 1]:
        r, c = rc(la, lo)
        if wob:
            r += WOBBLE.get(d, 0)
        cv.put(r, c, mark, color)

def draw_fcst(cv, frm, to, mark=':', color=C_FCST):
    a, b = IDX[frm], IDX[to]
    for i in range(a, b):
        la1, lo1 = TRACK[i][1], TRACK[i][2]
        la2, lo2 = TRACK[i + 1][1], TRACK[i + 1][2]
        for k in range(1, 8):
            t = k / 8
            r, c = rc(la1 + (la2 - la1) * t, lo1 + (lo2 - lo1) * t)
            cv.put(r, c, mark, color, over=False)

def eye(cv, day, wob=False, sym='◎', color=C_EYE, r7=0, r10=0):
    d = dict((t[0], t) for t in TRACK)[day]
    la, lo = d[1], d[2]
    r, c = rc(la, lo)
    if wob:
        r += WOBBLE.get(day, 0)
    if r7:
        ring(cv, r, c, r7, '*', C_R7)
    if r10:
        ring(cv, r, c, r10, 'X', C_R10)
    cv.put(r, c - 1, sym, color)
    return r, c

def ring(cv, r0, c0, km, ch, color):
    """以列/欄為單位的橢圓虛圈（1 列約 122km、1 欄約 55km*cos）"""
    import math
    rr = km / 122.0
    cc = km / 55.0
    for a in range(0, 360, 12):
        t = math.radians(a)
        r = int(round(r0 + rr * math.sin(t)))
        c = int(round(c0 + cc * math.cos(t)))
        if 0 <= r < H and 0 <= c < W:
            cv.put(r, c, ch, color, over=False)

def high(cv, cells, label='Ｈ', color=C_HIGH):
    for r, c in cells:
        cv.put(r, c, label, color)

# ---------------- 第二輪新增：角色化零件 ----------------
FACE_N  = '◎'          # 平常：地圖上的中心符號
FACE_HM = '◎_◎'        # 疑惑
FACE_OK = '◎ω◎'        # 放鬆／認同
FACE_NG = '◎皿◎'        # 倔強／不爽

def bubble(cv, r, c, text, color=C_TXT):
    """三列對話框：┌──┐ / │文字│ / └──┘  （r 為中間那列）"""
    w = dispw(text)
    bar = '─' * (w // 2)
    cv.put(r - 1, c, '┌' + bar + '┐', color)
    cv.put(r,     c, '│' + text + '│', color)
    cv.put(r + 1, c, '└' + bar + '┘', color)
    return w + 4

def wall(cv, r, c0, n, color=C_HIGH, ch='Ｈ'):
    """連續的副熱帶高壓牆（每個 Ｈ 佔 2 欄）"""
    cv.put(r, c0, ch * n, color)

def arrows_up(cv, rows, c, color=C_TROU, ch='↑'):
    for r in rows:
        cv.put(r, c, ch, color)

# ---------------- 第三輪新增：短劇零件 ----------------
import math

def trough(cv, c0, r0=0, color=C_TROU):
    """西風槽 ╲ ╲ v ╱ ╱，c0 = 起始欄"""
    for dr, dc, ch in [(0,0,'╲'),(1,4,'╲'),(2,8,'v'),(1,12,'╱'),(0,16,'╱')]:
        cv.put(r0 + dr, c0 + dc, ch, color)

def mg_ring(cv, part=1.0, color=C_MG, ch='.'):
    """MG 大橢圓；part<1 只畫上半（真相揭露時分兩格顯現）"""
    r0, c0 = rc(23.0, 133.0)
    for a in range(0, 360, 8):
        if part < 1.0 and math.sin(math.radians(a)) > 0:
            continue                      # 先只畫北半邊
        t = math.radians(a)
        r = int(round(r0 + 6.2 * math.sin(t)))
        c = int(round(c0 + 24.0 * math.cos(t)))
        if 0 <= r < H and 0 <= c < W:
            cv.put(r, c, ch, color, over=False)

BOARD_C = 62          # 計分板固定欄位（高壓牆一律不超過 col 61）

def board(cv, n=0, third=None, jumps=0, r0=0, c0=BOARD_C):
    """北轉邀請紀錄計分板。n＝已揭曉幾項；third＝第三項結果（'延後'）"""
    cv.put(r0, c0, '北轉邀請紀錄', C_BOARD)
    rows = [('① 招手', '×', C_FAIL),
            ('② 缺口', '×', C_FAIL),
            ('③ 北偏', third or '', C_WAIT)]
    for i in range(min(n, 3)):
        lab, res, col = rows[i]
        cv.put(r0 + 1 + i, c0, lab, '1;37')
        if res:
            cv.put(r0 + 1 + i, c0 + 9, res, col)
    if jumps:
        cv.put(r0 + 4, c0, '海豚跳 ×%d' % jumps, C_GAG)

def dash_west(cv, r, c_end, n=5, color=C_PAST):
    """往西衝的動線 ←───── ，c_end＝白海豚左緣"""
    cv.put(r, c_end - 2 * (n + 1), '←' + '─' * n, color)

# ---------------- 幕表 ----------------
FRAMES = []

def add(fid, act, title, cv, sub, sub2, note, hold, moves, blink):
    FRAMES.append(dict(id=fid, act=act, title=title, cv=cv, sub=sub, sub2=sub2,
                       note=note, hold=hold, moves=moves, blink=blink))

# ============================================================
# 第三輪改版：PTT ANSI 短劇
#   · running gag 1 —— 北轉邀請紀錄計分板（① ② ③）
#   · running gag 2 —— 海豚跳 ×1 / ×2 / ×3
#   · 主播旁白（只在最有戲的地方出現）
#   · 第 5~6 幕拉成七格高潮：缺口 → 抬頭 → 停頓 → 沒有！！ → 蛤？
#   · 第 7 幕改成「真相揭露」；片尾四格＋一格彩蛋
# 幕次：1 出生 / 2 長太快 / 3 北方第一次招手 / 4 開始海豚跳 /
#       5 北方真的開門了 / 6 結果還是不去 / 7 原來舞台比較大 /
#       8 一路跳著往西 / 片尾 / 彩蛋
# ============================================================

# ===== 第1幕　出生 =====
A1 = '第一幕　出生'

cv = base()
cv.putll(16.5, 152.5, '～', C_EYE2)
wall(cv, 3, 44, 8)
cv.put(2, 44, '副熱帶高壓：北方的一道牆', C_HIGH)
add('1-1', 1, A1, cv,
    '2026/07/28　2613 白海豚，出生。',
    '',
    '氣象：西北太平洋季風槽內擾動發展，初期強度僅熱帶性低氣壓。',
    '0.9s', '「～」原地閃兩下後定住', '～（1;36）')

cv = base()
wall(cv, 3, 44, 8)
for dla, dlo, mk, col in [(1.05, -1.9, 'a', C_TROU),
                          (0.55, -2.3, 'b', C_FCST),
                          (0.10, -2.5, 'c', C_FCST)]:
    la, lo = 17.6, 149.6
    for i in range(8):
        la += dla; lo += dlo
        r, c = rc(la, lo)
        cv.put(r, c, mk, col, over=False)
cv.putll(17.6, 149.6, 'o', C_EYE2)
cv.put(0, 62, 'a＝北轉、去日本', C_TROU)
cv.put(1, 62, 'b＝西北西', C_FCST)
cv.put(2, 62, 'c＝一路往西', C_FCST)
add('1-2', 1, A1, cv,
    '大家第一個問題：牠會不會往北？',
    '',
    '氣象：生成初期導引場弱，各模式對副高強度與西風槽時間的假設分歧大。',
    '1.0s', '三條預測線由中心往外逐格長出，a（北轉）先亮', 'a 線亮藍閃 2 下')

cv = base()
wall(cv, 3, 44, 8)
cv.putll(17.6, 149.6, 'o', C_EYE2)
arrows_up(cv, (13, 11, 9), 66)
cv.put(7, 58, '大家賭：北轉', C_TROU)
add('1-3', 1, A1, cv,
    '牌桌上，多數人押牠北轉——甚至可能擦過日本。',
    '',
    '氣象：當時集合預報偏北的成員確實不少。',
    '0.8s', '↑ 由下往上依序點亮', '↑ 跑馬燈（1;34）')

# ===== 第2幕　長太快了 =====
A2 = '第二幕　長太快了'

cv = base()
draw_track(cv, '07/30')
wall(cv, 3, 40, 10)
eye(cv, '07/30', sym='◎', color=C_EYE, r7=180)
cv.put(12, 60, '風眼形成', C_EYE2)
add('2-1', 2, A2, cv,
    '等等，牠怎麼突然長這麼快？',
    '',
    '氣象：垂直風切減弱、高層輻散良好，進入快速增強；針孔風眼形成。',
    '0.9s', 'o →◎ 兩階放大，暴風圈由內往外長出', '◎（1;5;36）開始閃')

cv = base()
draw_track(cv, '08/01')
wall(cv, 3, 40, 10)
eye(cv, '08/01', sym='◎', color=C_EYE, r7=250, r10=100)
cv.put(8, 62, '超強颱風', '1;5;33;45')
add('2-2', 2, A2, cv,
    '08/01　今年的風王候選人。北邊那道牆，還好好的。',
    '',
    '氣象：達最大潛勢強度；沿副熱帶高壓南緣的偏東風向西北西行進。',
    '0.9s', '十級風圈（紅 X）補進來，牆整排點亮', '「超強颱風」晶片閃爍')

# ===== 第3幕　北方第一次招手 =====
A3 = '第三幕　北方第一次招手'

cv = base()
draw_track(cv, '08/02', wob=True)
wall(cv, 3, 34, 8); wall(cv, 3, 54, 4)
trough(cv, 44)
arrows_up(cv, (7, 5), 50)
bubble(cv, 12, 52, '這邊有路喔↑', C_TROU)
eye(cv, '08/02', wob=True, sym='◎', color=C_EYE, r7=250)
add('3-1', 3, A3, cv,
    '北方伸出第一隻手。',
    '主播：「西風槽伸手了，白海豚上方出現弱點！」',
    '氣象（擬人化）：實際為中緯度西風槽東移，槽前偏南風提供向北的導引分量。',
    '0.8s', '槽的 ╲v╱ 由左往右畫出，↑ 由上往下伸到白海豚', '↑ 兩支輪流閃（1;34）')

cv = base()
draw_track(cv, '08/02', wob=True)
wall(cv, 3, 34, 8); wall(cv, 3, 54, 4)
trough(cv, 44)
arrows_up(cv, (7, 5), 50)
r0, c0 = rc(22.9, 139.1); r0 += 1
cv.put(r0, c0 - 2, FACE_HM, C_EYE)
bubble(cv, r0, c0 + 6, '不要。', C_EYE2)
add('3-2', 3, A3, cv,
    '白海豚：「不要。」',
    '',
    '氣象：此時實際位置較模式預期偏南，向北的導引分量並未真正建立。',
    '0.5s', '中心切成 ◎_◎，其餘凍結', '對話框「不要。」淡入')

cv = base()
draw_track(cv, '08/03', wob=True)
trough(cv, 58)
wall(cv, 3, 34, 14)
cv.put(2, 34, '高壓回補→', C_HIGH)
eye(cv, '08/03', wob=True, sym='◎', color=C_EYE, r7=250)
add('3-3', 3, A3, cv,
    '手縮回去了。牆，又補上了。',
    '',
    '氣象：西風槽提早東移出海、副熱帶高壓西伸回補，向北導引消失。',
    '0.7s', '槽整組往右位移 14 欄；Ｈ 由右往左逐顆補滿', 'Ｈ 新補上那段閃 3 下')

cv = base()
draw_track(cv, '08/03', wob=True)
wall(cv, 3, 34, 14)
for i in range(10):
    cv.putll(23.9 + i * 1.0, 137.3 - i * 0.35, '.', C_FCST, over=False)
draw_fcst(cv, '08/03', '08/11', ':', C_FCST2)
eye(cv, '08/03', wob=True, sym='◎', color=C_EYE)
board(cv, n=1)
cv.put(12, 24, '新預測：一路往西', C_PAST)
add('3-4', 3, A3, cv,
    '怎麼又西修？——北轉邀請 ①，失敗。',
    '',
    '氣象：官方與各模式路徑連續向西修正，早期偏北路徑遭淘汰。',
    '1.1s', '舊預測線整條轉暗灰；右上角計分板寫上「① 招手　×」', '「①　×」閃 2 下（1;31）')

# ===== 第4幕　開始海豚跳 =====
A4 = '第四幕　開始海豚跳'

cv = Canvas()
art = [
    '',
    '                     ---- 雙 眼 牆 特 寫 ----',
    '',
    '                   ,,,,,,,,,,,,,,,,,,,,,,,,,,,,',
    '                ,,,,                        ,,,,',
    '              ,,,      ....................      ,,,',
    '             ,,      ...                  ...      ,,',
    '            ,,     ..        ◎皿◎        ..     ,,',
    '             ,,      ...                  ...      ,,',
    '              ,,,      ....................      ,,,',
    '                ,,,,                        ,,,,',
    '                   ,,,,,,,,,,,,,,,,,,,,,,,,,,,,',
    '',
    '         內眼牆（....）＝原本的眼　　外眼牆（,,,,）＝新長出來的眼',
    '',
    '           外眼牆把內眼牆的水氣吃掉 → 強度先掉 → 再自己重整回來',
    '',
    '',
]
for i, t in enumerate(art):
    cv.put(i, 0, t, C_EYE2 if i in (1, 13) else (C_HIGH if i == 15 else None))
add('4-1', 4, A4, cv,
    '換眼了。怎麼又重整了？',
    '白海豚：（壞掉了，重組中）',
    '氣象：眼牆置換循環——外眼牆吃掉內眼牆，強度先掉再重整，來了好幾次。',
    '1.3s', '外眼牆逐格向內收縮 1 欄，內眼牆逐格變淡', '◎皿◎ 由亮轉暗再轉亮')

cv = base()
draw_track(cv, '08/03', wob=True)
wall(cv, 3, 32, 15)
board(cv, n=1, jumps=1)
r0, c0 = eye(cv, '08/03', wob=True, sym='◎', color=C_EYE, r7=230)
cv.put(r0 + 3, c0 + 2, '跳！', C_GAG)
add('4-2', 4, A4, cv,
    '跳！',
    '',
    '氣象：雙眼牆造成中心在平均路徑附近做擺線運動。',
    '0.45s', '◎ 往左 3 欄、往上 1 列；舊位置留下亮白 o', '「跳！」閃爍（1;5;33）')

cv = base()
draw_track(cv, '08/04', wob=True)
wall(cv, 3, 32, 15)
board(cv, n=1, jumps=2)
r0, c0 = eye(cv, '08/04', wob=True, sym='◎', color=C_EYE, r7=230)
cv.put(r0 - 3, c0 + 2, '又跳？', C_GAG)
add('4-3', 4, A4, cv,
    '又跳？',
    '主播：「等等，怎麼又跳起來了？」',
    '氣象：短時間上下擺動不等於正式轉向，主軌道仍是西行。',
    '0.45s', '◎ 往左 3 欄、往下 1 列，形成波浪軌跡；計數器 ×1 → ×2', '「又跳？」閃爍（1;5;33）')

cv = Canvas()
cv.put(1, 12, '主 路 徑 （ 平 均 移 動 ） ＝ 真 正 的 導 引 方 向', C_HIGH)
cv.put(3, 4, '西 ←', C_PAST)
cv.put(3, 9, '─' * 29, C_PAST)
cv.put(3, 67, ' 東', C_PAST)
cv.put(5, 12, '實 際 中 心 （ 每 3 小 時 定 位 ） ＝ 一 路 在 晃', C_EYE2)
CENTER, AMP = 10, 3.0
for c in range(10, 71):
    y = CENTER - AMP * math.sin((c - 10) / 60.0 * 3 * 2 * math.pi)
    cv.put(int(round(y)), c, 'o' if (c - 10) % 5 == 0 else '.',
           C_PAST if (c - 10) % 5 == 0 else '37')
for c in (15, 35, 55):
    y = CENTER - AMP * math.sin((c - 10) / 60.0 * 3 * 2 * math.pi)
    cv.put(int(round(y)), c - 1, '◎', C_EYE)
cv.put(15, 10, '跳！', C_GAG)
cv.put(15, 30, '又跳？', C_GAG)
cv.put(15, 50, '（等等還有第三次）', C_NOTE)
cv.put(16, 4, '上下擺動＝雙眼牆造成的擺線運動　　左右前進＝真正的導引方向', C_NOTE)
cv.put(17, 4, '兩件事要分開看：晃的是中心，走的是主軌道。', C_NOTE)
add('4-4', 4, A4, cv,
    '氣象人叫它擺線；鄉民叫它海豚跳。',
    '',
    '氣象：雙眼牆結構造成明顯擺線運動，短時間上下擺動不等於正式轉向。',
    '1.4s', '波浪由右往左一段段畫出，主路徑箭頭同時往左延伸', '兩個梗字依序閃')

# ===== 第5幕　北方真的開門了 =====
A5 = '第五幕　北方真的開門了'

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 30, 16)
trough(cv, 42)
board(cv, n=1)
eye(cv, '08/05', wob=True, sym='◎', color=C_EYE, r7=230)
add('5-1', 5, A5, cv,
    '北方 again。而且這次，是玩真的。',
    '主播：「西風槽逼近，高壓開始被切開了！」',
    '氣象：中緯度西風槽確實東移通過。',
    '0.7s', '槽整組由右往左壓過來 6 欄', '槽底 v 閃 2 下')

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', '1;5;34')
arrows_up(cv, (6, 5, 4), 44)
eye(cv, '08/05', wob=True, sym='◎', color=C_EYE)
add('5-2', 5, A5, cv,
    '這次總該北轉了吧？',
    '主播：「北方缺口真的打開了！」',
    '氣象：副熱帶高壓斷裂減弱，北方確實出現開口。',
    '0.8s', '牆中間 3 顆 Ｈ 逐格消失，↑ 由下往上點亮到缺口', '「北方缺口」1;5;34 閃爍')

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', '1;5;34')
arrows_up(cv, (6, 5, 4), 44)
r0, c0 = rc(25.7, 134.2); r0 -= 2
cv.put(r0, c0 - 1, '◎', C_EYE)
cv.put(r0 + 1, c0 + 1, '↗', C_GAG)
add('5-3', 5, A5, cv,
    '牠……真的往北抬了一格。',
    '主播：「白海豚抬頭了！」',
    '氣象：高壓斷裂處常成為北翹通道，此時北轉風險確實升高。',
    '0.6s', '◎ 往上抬 1 列，原位留亮白 o，下方補 ↗', '↗ 閃 1 下（假動作）')

# ===== 第6幕　結果還是不去 =====
A6 = '第六幕　結果還是不去'

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', '1;5;34')
arrows_up(cv, (6, 5, 4), 44)
r0, c0 = rc(25.7, 134.2); r0 -= 2
cv.put(r0, c0 - 3, FACE_HM, C_EYE)
add('6-1', 6, A6, cv,
    '',
    '主播：「要轉了嗎——？」',
    '氣象：移速由每小時 22 公里降到 14 公里——導引減弱先反映在速度上。',
    '0.5s', '全畫面凍結，只有中心切成 ◎_◎（刻意留白半拍）', '不閃')

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', C_FCST)
arrows_up(cv, (6, 5, 4), 44, color=C_FCST)
r0, c0 = eye(cv, '08/06', sym='◎', color=C_EYE)
dash_west(cv, r0, c0 - 1, 5)
add('6-2', 6, A6, cv,
    '……又沒轉。',
    '主播：「沒有！！牠又回去了！」',
    '氣象：高壓斷裂只讓導引減弱、移速下降，並未形成持續北向導引。',
    '0.8s', '◎ 掉回原緯度並往西衝，拖出 ←───── 尾跡', '↑ 與「北方缺口」同時轉暗灰')

cv = base()
draw_track(cv, '08/05', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', C_FCST)
arrows_up(cv, (6, 5, 4), 44, color=C_FCST)
bubble(cv, 1, 54, '蛤？', C_TROU)
eye(cv, '08/06', sym='◎', color=C_EYE)
bubble(cv, 12, 38, '◎皿◎　路過而已。', C_EYE2)
add('6-3', 6, A6, cv,
    '北方：「蛤？」　白海豚：「路過而已。」',
    '',
    '氣象：短時間的小幅北偏屬中心尺度變動，不是大尺度轉向。',
    '1.1s', '兩個對話框一上一下先後彈出', '◎皿◎ 閃 2 下當 punchline')

cv = base()
draw_track(cv, '08/06', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', C_FCST)
board(cv, n=2, jumps=2)
eye(cv, '08/06', sym='◎', color=C_EYE, r7=250)
add('6-4', 6, A6, cv,
    '北轉邀請 ②，一樣失敗。',
    '',
    '氣象：高壓斷裂 ≠ 一定北轉。導引是各層環境風的合成，不是只看一個系統。',
    '1.0s', '計分板寫上「② 缺口　×」', '「②　×」閃 2 下（1;31）')

# ===== 第7幕　原來舞台比較大 =====
A7 = '第七幕　原來舞台比較大'

cv = base()
draw_track(cv, '08/06', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', C_FCST)
eye(cv, '08/06', sym='◎', color=C_EYE)
bubble(cv, 1, 34, '高壓都裂了，為什麼還不來？', C_TROU)
add('7-1', 7, A7, cv,
    '北方：「高壓都裂了，為什麼還不來？」',
    '',
    '氣象：導引是各層環境風的合成，得看比副熱帶高壓更大的尺度。',
    '0.9s', '槽的殘跡淡出，畫面只剩牆、缺口、白海豚', '無（刻意安靜一格）')

cv = base()
draw_track(cv, '08/06', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
mg_ring(cv, part=0.5)
eye(cv, '08/06', sym='◎', color=C_EYE)
add('7-2', 7, A7, cv,
    '海面上，有東西慢慢浮出來。',
    '主播：「等等……」',
    '氣象：低層環流分析顯示，颱風北側之外還有更大範圍的氣旋式環流。',
    '0.7s', '大弧線先只顯現北半邊（由中心往外一圈）', 'MG 弧線由左往右流動')

cv = base()
draw_track(cv, '08/06', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
mg_ring(cv)
cv.put(6, 54, '↖', C_MG); cv.put(6, 22, '↙', C_MG)
cv.put(14, 22, '↘', C_MG); cv.put(14, 54, '↗', C_MG)
cv.put(16, 26, 'ＭＧ　季風環流圈　Monsoon Gyre', C_MG)
eye(cv, '08/06', sym='◎', color=C_EYE)
add('7-3', 7, A7, cv,
    '原來，舞台比我們看到的還大。',
    '',
    '氣象：季風環流圈（MG）——橫跨數千公里的低層氣旋式環流。',
    '1.4s', '弧線補齊南半邊，四角 ↙↘↖↗ 依序點亮（氣旋式旋轉）', '四角箭頭輪流閃（1;35）')

cv = base()
draw_track(cv, '08/06', wob=True)
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
mg_ring(cv)
for c0 in (48, 54, 60, 66):
    cv.put(10, c0, '←', '1;5;35')
bubble(cv, 13, 40, '走啦。', C_MG)
eye(cv, '08/06', sym='◎', color=C_EYE)
bubble(cv, 6, 44, '◎ω◎　走。', C_EYE2)
add('7-4', 7, A7, cv,
    'ＭＧ：「走啦。」　白海豚：「走。」',
    '',
    '氣象：補充觀點——MG 北側偏東風可能持續提供向西的背景導引（非唯一機制）。',
    '1.1s', '← 四支由右往左依序點亮，兩個對話框先後淡入', '← 跑馬燈（1;5;35）')

# ===== 第8幕　一路跳著往西 =====
A8 = '第八幕　一路跳著往西'

cv = base()
draw_track(cv, '08/07', wob=True)
draw_fcst(cv, '08/07', '08/11', ':', C_FCST2)
board(cv, n=2, jumps=3)
r0, c0 = eye(cv, '08/07', wob=True, sym='◎', color=C_EYE, r7=280)
cv.putll(26.2, 127.7, '那霸', '1;5;36', dc=2)
cv.put(r0 + 3, c0 + 8, '還在跳……', C_GAG)
add('8-1', 8, A8, cv,
    '還在跳……',
    '主播：「牠居然還在跳。」',
    '氣象：擺線運動持續；暴風圈直接籠罩沖繩本島至先島群島。',
    '0.7s', '◎ 往左 4 欄、往上 1 列；計數器 ×2 → ×3', '「那霸」與「還在跳……」交替閃')

cv = base()
draw_track(cv, '08/08', wob=True)
draw_fcst(cv, '08/08', '08/11', ':', C_FCST2)
eye(cv, '08/08', sym='◎', color=C_EYE, r7=300)
cv.putll(25.05, 121.5, '台北', '1;5;32', dc=2)
cv.put(12, 30, '連江　暴風侵襲率 60%', '1;31')
cv.put(13, 30, '基隆　暴風侵襲率 50%', C_HIGH)
add('8-2', 8, A8, cv,
    '08/08　台灣沒有正面對決，但風先到了。',
    '',
    '氣象：中心遠離，台灣主要受外圍環流影響；連江 60%、基隆 50%。',
    '1.0s', '暴風圈外緣一圈圈往左擴，兩行數字打字出現', '台灣全島 1;5;32 閃 2 下')

cv = base()
draw_track(cv, '08/09', wob=True)
draw_fcst(cv, '08/09', '08/11', ':', C_FCST2)
board(cv, n=3, third='延後', jumps=3)
eye(cv, '08/09', sym='◎', color=C_EYE, r7=300)
cv.put(12, 24, '進東海　移速再放慢　只抬了一點點', C_HIGH)
add('8-3', 8, A8, cv,
    '怎麼又只抬一下？——北轉邀請 ③，延後。',
    '白海豚：「你們慢慢等。」',
    '氣象：明顯的北向轉向被推遲到接近中國沿岸或登陸之後。',
    '1.0s', '計分板第三列寫上「③ 北偏　延後」', '「延後」1;33 閃 2 下')

cv = base()
draw_track(cv, '08/11', wob=True)
eye(cv, '08/11', sym='◎', color=C_EYE, r7=280)
cv.putll(28.0, 120.9, '溫州', '1;5;31', dc=-8)
cv.put(1, 44, '朝浙江沿海前進', '1;31')
add('8-4', 8, A8, cv,
    '方向從頭到尾只有一個：西。',
    '',
    '氣象：當時主流預報為朝浙江沿岸方向前進（非精確登陸點預報）。',
    '0.9s', '◎ 由東海走到浙江外海，暴風圈觸陸', '「溫州」閃爍（1;5;31）')

# ===== 片尾 =====
AF = '片尾'

cv = base()
for d, la, lo, k in TRACK:
    r, c = rc(la, lo)
    r += WOBBLE.get(d, 0)
    cv.put(r, c, 'o', C_GAG if d in WOBBLE else C_PAST)
for i in range(len(TRACK) - 1):
    la1, lo1, la2, lo2 = TRACK[i][1], TRACK[i][2], TRACK[i+1][1], TRACK[i+1][2]
    for kk in range(1, 6):
        t = kk / 6
        r, c = rc(la1 + (la2-la1)*t, lo1 + (lo2-lo1)*t)
        r += round(WOBBLE.get(TRACK[i][0], 0) * (1 - t) + WOBBLE.get(TRACK[i+1][0], 0) * t)
        cv.put(r, c, '.', C_PAST, over=False)
cv.put(2, 30, '北方一路都在招手', C_FCST)
for c0 in (34, 42, 50):
    cv.put(3, c0, '↑', C_FCST)
board(cv, n=3, third='延後', jumps=3)
eye(cv, '08/11', sym='◎', color=C_EYE)
cv.put(15, 58, '形成', C_HIGH)
add('F-1', 9, AF, cv,
    '全 程 回 顧：黃點就是海豚跳的那幾天。',
    '',
    '氣象：全程以西行分量為主；擺線段屬中心尺度變動，非正式轉向。',
    '1.6s', '整條路徑由東往西快轉重播一次，最後停在浙江', '計分板三列同時亮起')

cv = base()
draw_track(cv, '08/11', wob=True)
board(cv, n=3, third='延後', jumps=3)
eye(cv, '08/11', sym='◎', color=C_EYE)
bubble(cv, 8, 34, '所以你到底什麼時候要北轉？', C_TROU)
add('F-2', 9, AF, cv,
    '北方：「所以你到底什麼時候要北轉？」',
    '',
    '氣象：北方持續提供向北導引的機會，但需要夠深厚的環境風配合。',
    '1.2s', '對話框由左往右展開（打字機效果）', '對話框邊框閃 1 下')

cv = base()
draw_track(cv, '08/11', wob=True)
board(cv, n=3, third='延後', jumps=3)
r0, c0 = eye(cv, '08/11', sym='◎', color=C_EYE)
dash_west(cv, r0, c0 - 1, 4)
bubble(cv, 12, 34, '◎皿◎　下一報再說。', C_EYE2)
add('F-3', 9, AF, cv,
    '白海豚：「下一報再說。」',
    '',
    '氣象：路徑以最新一報官方預報為準；本片時間軸僅為回顧。',
    '1.4s', '◎ 拖著 ←────── 往西離場，對話框同時彈出', '◎皿◎ 閃 3 下')

cv = Canvas()
cv.put(3, 26, '2 6 1 3 　 白 海 豚', C_EYE2)
cv.put(5, 16, '一 隻 不 肯 往 北 游 的 海 豚', C_PAST)
cv.put(8, 34, '—　完　—', C_HIGH)
cv.put(11, 12, '北方一直在招手，白海豚卻一邊跳、一邊晃，一路往西。', C_TXT)
cv.put(14, 22, '北轉邀請　① ×　　② ×　　③ 延後', C_FAIL)
cv.put(15, 22, '海豚跳　　×３', C_GAG)
add('F-4', 9, AF, cv,
    '',
    '',
    '氣象：短期擺動不代表正式轉向；實際路徑仍以最新官方預報為準。',
    '1.6s', '文字由上往下逐行淡入', '「—　完　—」1;5;33 閃 2 下後轉常亮')

# ===== 彩蛋 =====
cv = base()
wall(cv, 3, 26, 7); wall(cv, 3, 50, 6)
cv.put(2, 42, '北方缺口', C_FCST)
arrows_up(cv, (6, 5, 4), 44, color=C_TROU)
cv.put(7, 42, '…', C_TROU)
bubble(cv, 12, 44, '喂？', C_TROU)
cv.put(6, 2, '◎→', C_EYE)
add('X-1', 10, '彩蛋', cv,
    '北方：「喂？」',
    '（白海豚已經走遠了）',
    '氣象：下一個系統仍需個案分析；本片為 2613 白海豚的回顧，不作預報。',
    '0.9s', '↑ 還在閃，白海豚已經在畫面左邊快出鏡', '「喂？」對話框閃 1 下')

# ---------------- 輸出 ----------------
import shutil
if os.path.isdir('ans'):
    shutil.rmtree('ans')          # 清掉上一版殘留的格子，避免新舊混播
os.makedirs('ans', exist_ok=True)
for _f in FRAMES:                      # 字幕寬度守門：三行文字都不得超過 76 欄
    for _k in ('sub', 'sub2', 'note'):
        assert dispw(_f[_k]) <= 76, (_f['id'], _k, dispw(_f[_k]), _f[_k])

plain_out = []
maxw = 0
for f in FRAMES:
    lines = f['cv'].plain()
    for ln in lines:
        maxw = max(maxw, dispw(ln))
    plain_out.append((f, lines))

with open('frames_plain.txt', 'w', encoding='utf-8') as fh:
    for f, lines in plain_out:
        fh.write('=== %s %s ===\n' % (f['id'], f['title']))
        fh.write('\n'.join(lines) + '\n\n')

print('frames:', len(FRAMES), 'max display width:', maxw)
# Big5 檢查
bad = set()
for f, lines in plain_out:
    for s in lines + [f['sub'], f['sub2'], f['note'], f['title'], f['moves'], f['blink']]:
        for ch in s:
            try:
                ch.encode('cp950')
            except Exception:
                bad.add(ch)
print('non-Big5 chars:', ''.join(sorted(bad)) or '(none)')

import json
json.dump([{k: (v if k != 'cv' else None) for k, v in f.items()} | {'lines': l}
           for f, l in plain_out], open('frames.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# .ans 輸出
for i, f in enumerate(FRAMES, 1):
    body = f['cv'].ansi()
    out = ['\033[m\033[1;36m' + f['title'] + '\033[m']
    out += body
    # 2026/08/08：PTT 內容區只有 23 行（第 24 行是狀態列），
    # 所以把「分隔線」與「進度條」併成同一行 —— 一格 = 一畫面才對得齊。
    n = f['act']
    _tag = {9: '片尾', 10: '彩蛋'}.get(n, '第%d幕/8' % n)
    _b = min(n, 8)
    _label = '  %s  %s ' % (_tag, f['id'])
    _used = (_b + 8) + dispw(_label)          # ▓ 佔 2 欄、- 佔 1 欄
    out.append('\033[1;33m' + '▓' * _b + '\033[1;30m' + '-' * (8 - _b) +
               _label + '-' * max(0, 78 - _used) + '\033[m')
    out.append('\033[1;37m' + f['sub'] + '\033[m')
    _c2 = '1;33' if f['sub2'].startswith(('主播', '實況')) else '1;37'
    out.append('\033[%sm' % _c2 + f['sub2'] + '\033[m')
    out.append('\033[1;30m' + f['note'] + '\033[m')
    open('ans/%02d_%s.ans' % (i, f['id'].replace('-', '_')), 'w',
         encoding='cp950', errors='replace', newline='').write(
             '\r\n'.join(out) + '\r\n' * 3)
print('ans files written')


# ---------------- Section C markdown ----------------
ACTNAME = {}
for f in FRAMES:
    ACTNAME[f['act']] = f['title']

md = []
last = None
for f, lines in plain_out:
    if f['act'] != last:
        last = f['act']
        md.append('\n### %s\n' % f['title'])
    md.append('#### 第 %s 格　（停留 %s）\n' % (f['id'], f['hold']))
    md.append('```')
    md.append('\n'.join(lines))
    md.append('```\n')
    md.append('| 項目 | 內容 |')
    md.append('|---|---|')
    md.append('| 移動元素 | %s |' % f['moves'])
    md.append('| 閃爍／切換 | %s |' % f['blink'])
    md.append('| 字幕 | %s |' % (f['sub'] + ('　' + f['sub2'].strip() if f['sub2'].strip() else '')))
    md.append('| 底部小字 | %s |' % f['note'])
    md.append('')
open('sectionC.md', 'w', encoding='utf-8').write('\n'.join(md))
print('sectionC.md written', len(md))

# 播放用停留秒數
holds = {}
for i, f in enumerate(FRAMES, 1):
    holds['%02d' % i] = float(f['hold'].rstrip('s'))
json.dump(holds, open('holds.json', 'w'), indent=1)
print('holds.json written')
