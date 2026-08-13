#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artes "Presença Confirmada" — ANAMAGES · Encontro de Diretores e Conselheiros 2026
Gera: stories 1080x1920 e post 1080x1080, a partir da foto do palestrante e da
logo oficial (branca sobre azul #26284E), no estilo "Magistratura Luminosa".
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_SRC = os.path.join(OUT_DIR, "insumos", "foto-painel.jpg")
LOGO_SRC = os.path.join(OUT_DIR, "insumos", "logo-anamages.jpg")
FONT_DIR = "/root/.claude/skills/synced/canvas-design/canvas-fonts"

# ---------------------------------------------------------------- paleta
NAVY      = (38, 40, 78)      # fundo exato da logo
NAVY_TOP  = (47, 50, 95)
NAVY_BOT  = (27, 29, 58)
DEEP      = (23, 25, 50)
GOLD      = (203, 166, 94)
GOLD_LT   = (232, 207, 148)
PERI      = (169, 177, 218)   # azul-lavanda (meia-voz)
WHITE     = (255, 255, 255)

F_SANS    = os.path.join(FONT_DIR, "Outfit-Regular.ttf")
F_SANS_B  = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
F_DISPLAY = os.path.join(FONT_DIR, "Gloock-Regular.ttf")
F_ITALIC  = os.path.join(FONT_DIR, "CrimsonPro-Italic.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def tracked_width(draw, text, fnt, tracking):
    """Largura de texto com espaçamento extra entre caracteres (px)."""
    if not text:
        return 0
    w = sum(draw.textlength(ch, font=fnt) for ch in text)
    return w + tracking * (len(text) - 1)


def draw_tracked(draw, xy, text, fnt, fill, tracking, anchor="center"):
    """Desenha texto com tracking manual. anchor: 'center'|'left'|'right' (x)."""
    x, y = xy
    total = tracked_width(draw, text, fnt, tracking)
    if anchor == "center":
        cx = x - total / 2
    elif anchor == "right":
        cx = x - total
    else:
        cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + tracking
    return total


def fit_font(draw, text, path, max_width, start_size, tracking_em=0.0):
    """Maior fonte cujo texto (com tracking proporcional) caiba em max_width."""
    size = start_size
    while size > 8:
        fnt = font(path, size)
        if tracked_width(draw, text, fnt, tracking_em * size) <= max_width:
            return fnt, tracking_em * size
        size -= 2
    return font(path, 8), tracking_em * 8


def wrap_text(draw, text, fnt, max_width, tracking=0.0):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tracked_width(draw, trial, fnt, tracking) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def v_gradient(size, top, bottom):
    w, h = size
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return col.resize((w, h))


def radial_glow(base, center, radius, color, peak_alpha):
    """Brilho radial suave (luz de cúpula) atrás da proclamação."""
    small = 256
    g = Image.new("L", (small, small), 0)
    gd = ImageDraw.Draw(g)
    for r in range(small // 2, 0, -1):
        a = int(peak_alpha * (1 - r / (small / 2)) ** 1.8)
        gd.ellipse([small/2 - r, small/2 - r, small/2 + r, small/2 + r], fill=a)
    g = g.resize((radius * 2, radius * 2)).filter(ImageFilter.GaussianBlur(6))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tile = Image.new("RGBA", g.size, color + (0,))
    tile.putalpha(g)
    overlay.paste(tile, (center[0] - radius, center[1] - radius), tile)
    return Image.alpha_composite(base, overlay)


def subtle_grain(img, opacity=10):
    noise = Image.effect_noise(img.size, 30)
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, ImageChops.overlay(img, noise_rgb), opacity / 100)


def rounded_mask(size, radius):
    m = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0]*2 - 1, size[1]*2 - 1],
                                        radius * 2, fill=255)
    return m.resize(size, Image.LANCZOS)


def diamond(draw, cx, cy, r, fill):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def ornament(draw, cx, cy, half_span, color=GOLD, dcolor=None):
    """regra — losango — regra (o lacre entre laudas)."""
    dcolor = dcolor or GOLD_LT
    gap = 26
    draw.line([(cx - half_span, cy), (cx - gap, cy)], fill=color, width=2)
    draw.line([(cx + gap, cy), (cx + half_span, cy)], fill=color, width=2)
    diamond(draw, cx, cy, 7, dcolor)


# ---------------------------------------------------------------- insumos
def logo_transparent():
    """Logo branca com alfa (remove o fundo azul), aparada."""
    im = Image.open(LOGO_SRC).convert("RGB")
    bg = Image.new("RGB", im.size, NAVY)
    diff = ImageChops.difference(im, bg).convert("L")
    alpha = diff.point(lambda v: 255 if v > 78 else int(v * 3.2) if v > 14 else 0)
    out = im.copy()
    out.putalpha(alpha)
    bbox = alpha.getbbox()
    return out.crop(bbox)


def speaker_photo(target_w, target_h):
    """Recorte oficial do palestrante + graduação de retrato."""
    im = Image.open(PHOTO_SRC).convert("RGB")
    crop = im.crop((186, 420, 566, 945))          # 380 x 525 — foco no orador
    crop = crop.resize((target_w, target_h), Image.LANCZOS)
    crop = ImageEnhance.Brightness(crop).enhance(1.04)
    crop = ImageEnhance.Contrast(crop).enhance(1.10)
    crop = ImageEnhance.Color(crop).enhance(0.90)
    crop = crop.filter(ImageFilter.UnsharpMask(radius=2.2, percent=120, threshold=2))
    # sombras levemente esfriadas para pertencer ao campo azul
    cool = Image.new("RGB", crop.size, (30, 34, 70))
    crop = Image.blend(crop, ImageChops.multiply(crop, Image.new("RGB", crop.size, (238, 240, 252))), 0.5)
    crop = Image.blend(crop, cool, 0.06)
    return crop


def photo_card(canvas, box, radius=26, bottom_fade=110, top_fade=0):
    """Cola o retrato emoldurado (sombra + quilha de ouro) no canvas RGBA."""
    x, y, w, h = box
    # sombra de galeria
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    shd.rounded_rectangle([x - 6, y + 14, x + w + 6, y + h + 26], radius + 8,
                          fill=(8, 9, 22, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(sh)

    photo = speaker_photo(w, h).convert("RGBA")
    # vinheta interna + fade inferior (ancoragem da placa de nome)
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(46):
        a = int(46 * (1 - i / 46) ** 2)
        vd.rounded_rectangle([i, i, w - 1 - i, h - 1 - i], radius, outline=a, width=1)
    dark = Image.new("RGBA", (w, h), DEEP + (0,))
    dark.putalpha(vig)
    photo.alpha_composite(dark)
    if bottom_fade:
        fade = Image.new("L", (1, bottom_fade), 0)
        for i in range(bottom_fade):
            fade.putpixel((0, i), int(150 * (i / bottom_fade) ** 1.6))
        fade = fade.resize((w, bottom_fade))
        f = Image.new("RGBA", (w, bottom_fade), DEEP + (0,))
        f.putalpha(fade)
        photo.alpha_composite(f, (0, h - bottom_fade))
    if top_fade:
        fade = Image.new("L", (1, top_fade), 0)
        for i in range(top_fade):
            fade.putpixel((0, i), int(88 * (1 - i / top_fade) ** 1.5))
        fade = fade.resize((w, top_fade))
        f = Image.new("RGBA", (w, top_fade), DEEP + (0,))
        f.putalpha(fade)
        photo.alpha_composite(f, (0, 0))

    mask = rounded_mask((w, h), radius)
    canvas.paste(photo, (x, y), mask)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius, outline=GOLD, width=3)
    d.rounded_rectangle([x + 8, y + 8, x + w - 9, y + h - 9], radius - 7,
                        outline=(232, 207, 148, 90), width=1)
    return canvas


def base_canvas(W, H, glow_center, glow_radius):
    bg = v_gradient((W, H), NAVY_TOP, NAVY_BOT).convert("RGBA")
    bg = radial_glow(bg, glow_center, glow_radius, (72, 78, 140), 68)
    return bg


def hairline_frame(draw, W, H, inset=34):
    draw.rectangle([inset, inset, W - inset - 1, H - inset - 1],
                   outline=GOLD + (95,), width=2)
    c = 26  # cantoneiras
    for (cx, cy, sx, sy) in [(inset, inset, 1, 1), (W - inset - 1, inset, -1, 1),
                             (inset, H - inset - 1, 1, -1), (W - inset - 1, H - inset - 1, -1, -1)]:
        draw.line([(cx, cy), (cx + sx * c, cy)], fill=GOLD_LT + (200,), width=3)
        draw.line([(cx, cy), (cx, cy + sy * c)], fill=GOLD_LT + (200,), width=3)


# ---------------------------------------------------------------- conteúdo
KICKER   = "ENCONTRO DE DIRETORES E CONSELHEIROS · 2026"
H1A, H1B = "PRESENÇA", "CONFIRMADA"
TEMA_1   = "Inteligência Artificial (IA):"
TEMA_2   = "presente e futuro da Magistratura"
ROLE     = "PALESTRANTE"
NAME     = "Dr. Rodrigo Otávio Terças Santos"
DATA     = "14 DE AGOSTO · SEXTA-FEIRA · 11H"
LOCAL    = "WINDSOR BRASÍLIA HOTEL — BRASÍLIA/DF"


# ---------------------------------------------------------------- STORIES
def make_story():
    W, H = 1080, 1920
    img = base_canvas(W, H, (W // 2, 470), 620)
    d = ImageDraw.Draw(img)
    hairline_frame(d, W, H)

    logo = logo_transparent()
    lw = 470
    lh = int(logo.height * lw / logo.width)
    img.alpha_composite(logo.resize((lw, lh), Image.LANCZOS), (W//2 - lw//2, 108))
    y = 108 + lh + 52

    f_kick = font(F_SANS, 25)
    draw_tracked(d, (W//2, y), KICKER, f_kick, PERI, 25 * 0.18)
    y += 78

    f_h1a, tr_a = fit_font(d, H1A, F_SANS, 700, 96, 0.34)
    draw_tracked(d, (W//2, y), H1A, f_h1a, WHITE, tr_a)
    y += f_h1a.size + 26
    f_h1b, tr_b = fit_font(d, H1B, F_DISPLAY, 905, 132, 0.02)
    draw_tracked(d, (W//2, y), H1B, f_h1b, GOLD_LT, tr_b)
    y += f_h1b.size + 58

    ornament(d, W // 2, y, 130)
    y += 44

    # retrato
    pw, ph = 560, 774
    px, py = W//2 - pw//2, y
    img = photo_card(img, (px, py, pw, ph), bottom_fade=150, top_fade=110)
    d = ImageDraw.Draw(img)

    # placa de nome sobreposta à base do retrato
    plate_w, plate_h = 830, 158
    plx, ply = W//2 - plate_w//2, py + ph - 74
    pl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pld = ImageDraw.Draw(pl)
    pld.rounded_rectangle([plx, ply, plx + plate_w, ply + plate_h], 20,
                          fill=DEEP + (242,), outline=GOLD + (255,), width=2)
    img.alpha_composite(pl)
    d = ImageDraw.Draw(img)
    f_role = font(F_SANS_B, 24)
    draw_tracked(d, (W//2, ply + 26), ROLE, f_role, GOLD, 24 * 0.42)
    f_name, tr_n = fit_font(d, NAME, F_SANS_B, plate_w - 90, 42, 0.02)
    draw_tracked(d, (W//2, ply + 74), NAME, f_name, WHITE, tr_n)

    y = ply + plate_h + 46
    f_tema = font(F_ITALIC, 50)
    d.text((W//2, y), "“" + TEMA_1, font=f_tema, fill=WHITE, anchor="ma")
    d.text((W//2, y + 62), TEMA_2 + "”", font=f_tema, fill=WHITE, anchor="ma")
    y += 62 + 78

    ornament(d, W // 2, y, 96)
    y += 40

    f_data = font(F_SANS_B, 33)
    draw_tracked(d, (W//2, y), DATA, f_data, WHITE, 33 * 0.14)
    y += 56
    f_loc = font(F_SANS, 26)
    draw_tracked(d, (W//2, y), LOCAL, f_loc, PERI, 26 * 0.16)

    out = subtle_grain(img.convert("RGB"), 7)
    path = os.path.join(OUT_DIR, "presenca-confirmada_stories_1080x1920.png")
    out.save(path)
    return path


# ---------------------------------------------------------------- POST 1:1
def make_post():
    W, H = 1080, 1080
    img = base_canvas(W, H, (330, 420), 520)
    d = ImageDraw.Draw(img)
    hairline_frame(d, W, H, inset=30)

    logo = logo_transparent()
    lh = 88
    lw = int(logo.width * lh / logo.height)
    img.alpha_composite(logo.resize((lw, lh), Image.LANCZOS), (84, 84))

    d.line([(84, 218), (W - 84, 218)], fill=GOLD + (120,), width=2)
    f_kick = font(F_SANS, 23)
    draw_tracked(d, (W//2, 244), KICKER, f_kick, PERI, 23 * 0.20)

    # retrato à direita
    pw, ph = 380, 525
    px, py = W - 84 - pw, 318
    img = photo_card(img, (px, py, pw, ph), radius=22, bottom_fade=0, top_fade=70)
    d = ImageDraw.Draw(img)

    # coluna esquerda
    lx, lw_col = 84, 500
    y = 330
    f_h1a, tr_a = fit_font(d, H1A, F_SANS, 420, 60, 0.32)
    draw_tracked(d, (lx, y), H1A, f_h1a, WHITE, tr_a, anchor="left")
    y += f_h1a.size + 18
    f_h1b, tr_b = fit_font(d, H1B, F_DISPLAY, lw_col, 82, 0.02)
    draw_tracked(d, (lx, y), H1B, f_h1b, GOLD_LT, tr_b, anchor="left")
    y += f_h1b.size + 40

    d.line([(lx, y), (lx + 68, y)], fill=GOLD, width=3)
    y += 34

    f_tema = font(F_ITALIC, 37)
    for i, line in enumerate(["“" + TEMA_1] + wrap_text(d, TEMA_2 + "”", f_tema, lw_col)):
        d.text((lx, y), line, font=f_tema, fill=WHITE)
        y += 47
    y += 40

    f_role = font(F_SANS_B, 22)
    draw_tracked(d, (lx, y), ROLE, f_role, GOLD, 22 * 0.40, anchor="left")
    y += 44
    f_name = font(F_SANS_B, 42)
    d.text((lx, y), "Dr. Rodrigo Otávio", font=f_name, fill=WHITE)
    d.text((lx, y + 52), "Terças Santos", font=f_name, fill=WHITE)

    # dispositivo (rodapé)
    d.line([(84, 902), (W - 84, 902)], fill=GOLD + (120,), width=2)
    f_data = font(F_SANS_B, 30)
    draw_tracked(d, (W//2, 934), DATA, f_data, WHITE, 30 * 0.14)
    f_loc = font(F_SANS, 24)
    draw_tracked(d, (W//2, 986), LOCAL, f_loc, PERI, 24 * 0.16)

    out = subtle_grain(img.convert("RGB"), 7)
    path = os.path.join(OUT_DIR, "presenca-confirmada_post_1080x1080.png")
    out.save(path)
    return path


if __name__ == "__main__":
    print(make_story())
    print(make_post())
