import sys
import os
import math
import colorsys
from functools import lru_cache
from PIL import Image

PALETTE_HEX = [
    "#282c34", "#abb2bf", "#e06c75", "#be5046",
    "#98c379", "#e5c07b", "#d19a66", "#61afef",
    "#3b6ea5", "#2a4d69",
    "#c678dd", "#56b6c2", "#4b5263", "#5c6370",
    "#d1603d", "#a63a2c",
    "#3a703f", "#2d472f",
    "#8ab4f8", "#5773c1", "#4a90e2", "#6c8ed9",
    "#a0a7b9", "#b0b5c1",
    "#d4cfc9", "#c9beb3", "#b8a79c",
]

SKIN_PALETTE_HEX = [
    "#dfb4a9", "#c89884", "#b97a57", "#a36e5a", "#8d5524", "#a66f52", "#d8a47f",
    "#f0c8b0", "#e3ad91", "#cfa386", "#b37355"
]

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

PALETTE_RGB = [hex_to_rgb(c) for c in PALETTE_HEX]
SKIN_PALETTE_RGB = [hex_to_rgb(c) for c in SKIN_PALETTE_HEX]

REF_X = 95.047
REF_Y = 100.000
REF_Z = 108.883

def srgb_to_xyz_rgb255(rgb):
    r, g, b = rgb
    r /= 255
    g /= 255
    b /= 255
    def inv_gamma(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055)/1.055)**2.4
    r = inv_gamma(r)
    g = inv_gamma(g)
    b = inv_gamma(b)
    x = (r*0.4124564 + g*0.3575761 + b*0.1804375)*100
    y = (r*0.2126729 + g*0.7151522 + b*0.0721750)*100
    z = (r*0.0193339 + g*0.1191920 + b*0.9503041)*100
    return x, y, z

def xyz_to_lab(x,y,z):
    x /= REF_X
    y /= REF_Y
    z /= REF_Z
    def f(t):
        return t**(1/3) if t > 0.008856 else (7.787*t)+(16/116)
    fx = f(x)
    fy = f(y)
    fz = f(z)
    L = 116*fy -16
    a = 500*(fx - fy)
    b = 200*(fy - fz)
    return L,a,b

def rgb_to_lab(rgb):
    return xyz_to_lab(*srgb_to_xyz_rgb255(rgb))

def deg2rad(d): return d * (math.pi / 180.0)
def rad2deg(r): return r * (180.0 / math.pi)

def cie_de2000(lab1, lab2):
    L1,a1,b1 = lab1
    L2,a2,b2 = lab2
    avg_L = (L1+L2)/2.0
    C1 = math.sqrt(a1*a1 + b1*b1)
    C2 = math.sqrt(a2*a2 + b2*b2)
    avg_C = (C1 + C2)/2.0
    G = 0.5*(1 - math.sqrt((avg_C**7)/(avg_C**7 + 25**7)))
    a1p = (1+G)*a1
    a2p = (1+G)*a2
    C1p = math.sqrt(a1p*a1p + b1*b1)
    C2p = math.sqrt(a2p*a2p + b2*b2)
    h1p = 0 if C1p==0 else (rad2deg(math.atan2(b1,a1p))%360)
    h2p = 0 if C2p==0 else (rad2deg(math.atan2(b2,a2p))%360)
    dLp = L2 - L1
    dCp = C2p - C1p
    dhp = 0
    if C1p*C2p==0:
        dhp = 0
    else:
        diff = h2p - h1p
        if abs(diff)<=180:
            dhp = diff
        elif diff>180:
            dhp = diff - 360
        else:
            dhp = diff + 360
    dHp = 2*math.sqrt(C1p*C2p)*math.sin(deg2rad(dhp/2))
    avg_Lp = (L1+L2)/2
    avg_Cp = (C1p+C2p)/2
    if C1p*C2p==0:
        avg_hp = h1p + h2p
    else:
        if abs(h1p - h2p) > 180:
            avg_hp = (h1p + h2p + 360)/2 if (h1p+h2p)<360 else (h1p + h2p - 360)/2
        else:
            avg_hp = (h1p + h2p)/2
    T = (1 - 0.17*math.cos(deg2rad(avg_hp - 30)) + 0.24*math.cos(deg2rad(2*avg_hp)) +
         0.32*math.cos(deg2rad(3*avg_hp + 6)) - 0.20*math.cos(deg2rad(4*avg_hp - 63)))
    delta_ro = 30*math.exp(-(((avg_hp - 275)/25)**2))
    R_C = 2*math.sqrt((avg_Cp**7)/(avg_Cp**7 + 25**7))
    S_L = 1 + ((0.015 * ((avg_Lp - 50)**2)) / math.sqrt(20 + ((avg_Lp - 50)**2)))
    S_C = 1 + 0.045*avg_Cp
    S_H = 1 + 0.015*avg_Cp*T
    R_T = -math.sin(deg2rad(2*delta_ro))*R_C
    k_L = k_C = k_H = 1
    return math.sqrt(
        (dLp/(k_L*S_L))**2 + (dCp/(k_C*S_C))**2 + (dHp/(k_H*S_H))**2 + R_T*(dCp/(k_C*S_C))*(dHp/(k_H*S_H))
    )

def saturate_color(rgb, factor=1.2):
    r, g, b = [v / 255.0 for v in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1.0, s * factor)
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
    return (int(r2 * 255), int(g2 * 255), int(b2 * 255))

def blend(c1, c2, alpha):
    return tuple(int(c1[i] * (1 - alpha) + c2[i] * alpha) for i in range(3))

def is_skin(rgb):
    r, g, b = [v / 255 for v in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h_deg = h * 360
    return (0 <= h_deg <= 40) and (0.15 <= s <= 0.6) and (v > 0.3)

palette_lab = [rgb_to_lab(c) for c in PALETTE_RGB]
skin_palette_lab = [rgb_to_lab(c) for c in SKIN_PALETTE_RGB]

@lru_cache(maxsize=200000)
def nearest_weighted_color_cached(r, g, b, use_skin=False):
    palette_rgb = SKIN_PALETTE_RGB if use_skin else PALETTE_RGB
    palette_lab_local = skin_palette_lab if use_skin else palette_lab
    saturate_factor = 1.06 if use_skin else 1.2
    lab = rgb_to_lab((r, g, b))
    best1_d = 1e9
    best2_d = 1e9
    best1_idx = -1
    best2_idx = -1
    for i, pal_lab in enumerate(palette_lab_local):
        d = cie_de2000(lab, pal_lab)
        if d < best1_d:
            best2_d, best2_idx = best1_d, best1_idx
            best1_d, best1_idx = d, i
        elif d < best2_d:
            best2_d, best2_idx = d, i
    c1 = palette_rgb[best1_idx]
    c2 = palette_rgb[best2_idx]
    c1s = saturate_color(c1, saturate_factor)
    c2s = saturate_color(c2, saturate_factor)
    w1 = 1 / (best1_d + 1e-6)
    w2 = 1 / (best2_d + 1e-6)
    ws = w1 + w2
    blended = tuple(int((c1s[i] * w1 + c2s[i] * w2) / ws) for i in range(3))
    return blended

def main():
    if len(sys.argv) < 2:
        print("Использование: python script.py <путь_к_изображению>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Файл '{path}' не найден")
        sys.exit(1)
    img = Image.open(path).convert("RGB")
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            orig = pixels[x, y]
            if is_skin(orig):
                pal_color = nearest_weighted_color_cached(orig[0], orig[1], orig[2], use_skin=True)
                pixels[x, y] = blend(orig, pal_color, 0.5)
            else:
                pal_color = nearest_weighted_color_cached(orig[0], orig[1], orig[2], use_skin=False)
                pixels[x, y] = blend(orig, pal_color, 0.7)

    output_name = f"OneDark_{os.path.basename(path)}"
    img.save(output_name)
    print(f"Обработано и сохранено: {output_name}")

if __name__ == "__main__":
    main()
