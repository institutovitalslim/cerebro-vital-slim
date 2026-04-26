#!/usr/bin/env python3
"""HomeMatch Club — Tinder-style hospitality exchange app mockups."""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

DIR = os.path.dirname(os.path.abspath(__file__))

# ── Palette ─────────────────────────────────────────────
BG          = "#0a0a0f"
CARD_BG     = "#1a1a2e"
GOLD        = "#d4af37"
GOLD_DARK   = "#8b7038"
WHITE       = "#f0f0f0"
OFF_WHITE   = "#b0b0b0"
DIM         = "#5a5a6a"
MATCH_GREEN = "#00b894"
NO_RED      = "#e74c3c"
INFO_BLUE   = "#3498db"
ORANGE_BUSY = "#e67e22"

W, H = 390, 844   # iPhone 14 proportions


def get_font(size, bold=False):
    """Try loading a system sans‑serif; fallback to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf",
        "/usr/share/fonts/TTF/DejaVuSans{}.ttf",
        "/usr/share/fonts/truetype/dejavu/FreeSans{}.ttf",
    ]
    suffix = "-Bold" if bold else ""
    for c in candidates:
        path = c.format(suffix)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{sRGB}.ttf", size)
    except Exception:
        return ImageFont.load_default()


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    """Draw a rounded rectangle. xy=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = xy
    # main rectangle + four corners via ellipse
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def circle(draw, center, radius, fill, outline=None, width=1):
    x, y = center
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill, outline=outline, width=width)


def draw_bottom_nav(draw, active="Feed"):
    """Bottom navigation bar with 4 icons+labels."""
    global H
    nav_h = 72
    nav_y = H - nav_h - 30  # safe area
    # subtle top border
    draw.line([(0, nav_y), (W, nav_y)], fill="#252540", width=1)

    # background
    draw.rectangle([(0, nav_y), (W, H)], fill="#0d0d1a")

    items = [
        ("🏠", "Feed"),
        ("💬", "Matches"),
        ("✉️", "Chat"),
        ("👤", "Perfil"),
    ]
    gap = W // 4
    f_small = get_font(10)
    for i, (emoji, label) in enumerate(items):
        cx = gap * i + gap // 2
        color = GOLD if label == active else DIM
        draw.text((cx, nav_y + 14), emoji, anchor="mt", fill=color, font=get_font(18))
        bbox = draw.textbbox((0, 0), label, font=f_small)
        tw = bbox[2] - bbox[0]
        draw.text((cx, nav_y + 38), label, anchor="mt", fill=color, font=f_small)


def draw_status_bar(draw):
    """Fake iOS status bar — dark."""
    f = get_font(14, bold=True)
    draw.text((28, 14), "9:41", fill=WHITE, font=f)
    # battery icon
    draw.rectangle([(W - 44, 14), (W - 22, 26)], outline=OFF_WHITE, width=1)
    draw.rectangle([(W - 20, 17), (W - 16, 22)], fill=OFF_WHITE)
    draw.rectangle([(W - 42, 16), (W - 24, 24)], fill=MATCH_GREEN)


# ═══════════════════════════════════════════════════════════
# 1. FEED CARD
# ═══════════════════════════════════════════════════════════
def gen_feed_card():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_status_bar(draw)

    card_x, card_y = 20, 60
    card_w, card_h = W - 40, H - 200

    # shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(
        [card_x + 6, card_y + 6, card_x + card_w + 6, card_y + card_h + 6],
        radius=28, fill=(0, 0, 0, 60)
    )
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    draw = ImageDraw.Draw(img)

    # card bg
    rounded_rect(draw, [card_x, card_y, card_x + card_w, card_y + card_h],
                 radius=28, fill=CARD_BG, outline=GOLD_DARK, width=1)

    # fake house photo — gradient panel
    photo_h = int(card_h * 0.70)
    for y in range(card_y, card_y + photo_h):
        p = (y - card_y) / photo_h
        r = int(10 + 40 * p)
        g = int(15 + 35 * p)
        b = int(30 + 60 * (1 - p * 0.5))
        draw.line([(card_x, y), (card_x + card_w, y)], fill=(r, g, b), width=1)

    # golden vignette on photo
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + photo_h],
        radius=28, fill=(0, 0, 0, 0)
    )
    # overlay bland estático para simular vignette
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # City name + flag emoji
    f_city = get_font(28, bold=True)
    draw.text((card_x + 20, card_y + 20), "🇵🇹  Cascais, Portugal",
              fill=WHITE, font=f_city)

    # Available dates pill
    pill_y = card_y + 65
    pill_text = "📅  12–19 Jul 2026"
    f_pill = get_font(13)
    bbox = draw.textbbox((0, 0), pill_text, font=f_pill)
    pw = bbox[2] - bbox[0] + 24
    ph = (bbox[3] - bbox[1]) + 14
    rounded_rect(draw, [card_x + 20, pill_y, card_x + 20 + pw, pill_y + ph],
                 radius=18, fill="#2a2a45")
    draw.text((card_x + 20 + pw // 2, pill_y + ph // 2), pill_text,
              anchor="mm", fill=OFF_WHITE, font=f_pill)

    # Amenities icons row
    icons_y = pill_y + ph + 14
    amenities = ["🛏️ 4q", "🚿 2ba", "🌊 Vista mar", "🚗 Garagem"]
    f_am = get_font(12)
    cx = card_x + 20
    for am in amenities:
        bbox = draw.textbbox((0, 0), am, font=f_am)
        aw = bbox[2] - bbox[0] + 16
        ah = (bbox[3] - bbox[1]) + 10
        rounded_rect(draw, [cx, icons_y, cx + aw, icons_y + ah],
                     radius=12, fill="#23233a")
        draw.text((cx + aw // 2, icons_y + ah // 2), am,
                  anchor="mm", fill=OFF_WHITE, font=f_am)
        cx += aw + 8

    # Owner circular photo + badge
    owner_cx = card_x + card_w - 50
    owner_cy = card_y + photo_h - 40
    circle(draw, (owner_cx, owner_cy), 40, fill="#334466")
    draw.text((owner_cx, owner_cy), "👤", anchor="mm", fill=WHITE, font=get_font(36))
    # gold ring
    circle(draw, (owner_cx, owner_cy), 42, fill=None, outline=GOLD, width=2)

    # badge "Host Ouro"
    badge_text = "🏅 Host Ouro"
    f_badge = get_font(11)
    bb = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw = bb[2] - bb[0] + 18
    bh = bb[3] - bb[1] + 10
    rounded_rect(draw, [owner_cx + 20, owner_cy + 28, owner_cx + 20 + bw, owner_cy + 28 + bh],
                 radius=10, fill="#8b7038")
    draw.text((owner_cx + 20 + bw // 2, owner_cy + 28 + bh // 2), badge_text,
              anchor="mm", fill=WHITE, font=f_badge)

    # Bottom info area inside card
    info_y = card_y + photo_h + 20
    f_title = get_font(20, bold=True)
    draw.text((card_x + 20, info_y), "Casa moderna com piscina",
              fill=WHITE, font=f_title)
    f_sub = get_font(14)
    draw.text((card_x + 20, info_y + 30), "Vila privativa • 250 m² • Wi-Fi Premium",
              fill=OFF_WHITE, font=f_sub)

    # Action buttons (X | Info | Heart)
    btn_y = card_y + card_h + 24
    btn_r = 34
    # X
    circle(draw, (W // 2 - 90, btn_y), btn_r, fill=NO_RED)
    draw.text((W // 2 - 90, btn_y), "✕", anchor="mm", fill=WHITE, font=get_font(28, bold=True))
    circle(draw, (W // 2 - 90, btn_y), btn_r + 3, fill=None, outline=NO_RED, width=2)

    # Info
    circle(draw, (W // 2, btn_y), btn_r, fill=INFO_BLUE)
    draw.text((W // 2, btn_y), "ℹ", anchor="mm", fill=WHITE, font=get_font(28, bold=True))
    circle(draw, (W // 2, btn_y), btn_r + 3, fill=None, outline=INFO_BLUE, width=2)

    # Heart
    circle(draw, (W // 2 + 90, btn_y), btn_r, fill=MATCH_GREEN)
    draw.text((W // 2 + 90, btn_y), "♥", anchor="mm", fill=WHITE, font=get_font(28, bold=True))
    circle(draw, (W // 2 + 90, btn_y), btn_r + 3, fill=None, outline=MATCH_GREEN, width=2)

    draw_bottom_nav(draw, active="Feed")
    return img.convert("RGB")


# ═══════════════════════════════════════════════════════════
# 2. MATCH SCREEN
# ═══════════════════════════════════════════════════════════
def gen_match_screen():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_status_bar(draw)

    # Confetti dots
    import random
    rng = random.Random(42)
    for _ in range(80):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H // 2 + 100)
        r = rng.randint(2, 6)
        color = rng.choice([GOLD, MATCH_GREEN, "#ff6b6b", "#ffd700", "#4ecdc4"])
        circle(draw, (cx, cy), r, fill=color)

    center_y = H // 2 - 60

    # "It's a Match!" text
    f_match = get_font(36, bold=True)
    draw.text((W // 2, center_y - 120), "It's a Match!",
              anchor="mm", fill=GOLD, font=f_match)
    f_sub = get_font(16)
    draw.text((W // 2, center_y - 80), "Vocês combinam para uma troca incrível",
              anchor="mm", fill=OFF_WHITE, font=f_sub)

    # Two house photos side-by-side
    house_w, house_h = 150, 180
    left_x = W // 2 - house_w - 14
    right_x = W // 2 + 14
    house_y = center_y - 10

    # Left house (mine)
    rounded_rect(draw, [left_x, house_y, left_x + house_w, house_y + house_h],
                 radius=20, fill="#1e1e3a")
    # fake gradient inside
    for y in range(house_y, house_y + house_h):
        p = (y - house_y) / house_h
        col = (20 + int(40 * p), 25 + int(30 * (1 - p)), 50 + int(20 * p))
        draw.line([(left_x, y), (left_x + house_w, y)], fill=col, width=1)
    draw.text((left_x + house_w // 2, house_y + house_h // 2), "🏠",
              anchor="mm", fill=WHITE, font=get_font(60))
    draw.text((left_x + house_w // 2, house_y + house_h + 10), "Sua casa",
              anchor="mm", fill=OFF_WHITE, font=get_font(13))

    # Right house (match)
    rounded_rect(draw, [right_x, house_y, right_x + house_w, house_y + house_h],
                 radius=20, fill="#1e1e3a")
    for y in range(house_y, house_y + house_h):
        p = (y - house_y) / house_h
        col = (30 + int(20 * p), 40 + int(40 * (1 - p)), 60 + int(20 * p))
        draw.line([(right_x, y), (right_x + house_w, y)], fill=col, width=1)
    draw.text((right_x + house_w // 2, house_y + house_h // 2), "🏖️",
              anchor="mm", fill=WHITE, font=get_font(60))
    draw.text((right_x + house_w // 2, house_y + house_h + 10), "Casa deles",
              anchor="mm", fill=OFF_WHITE, font=get_font(13))

    # Heart icon between the houses
    heart_x = W // 2
    heart_y = house_y + house_h // 2
    circle(draw, (heart_x, heart_y), 26, fill=MATCH_GREEN)
    draw.text((heart_x, heart_y - 1), "♥", anchor="mm", fill=WHITE, font=get_font(28, bold=True))

    # "Iniciar Conversa" big button
    btn_h = 56
    btn_y = house_y + house_h + 60
    rounded_rect(draw, [40, btn_y, W - 40, btn_y + btn_h],
                 radius=28, fill=MATCH_GREEN)
    f_btn = get_font(18, bold=True)
    draw.text((W // 2, btn_y + btn_h // 2), "Iniciar Conversa",
              anchor="mm", fill=WHITE, font=f_btn)

    # "Continuar explorando" text link
    draw.text((W // 2, btn_y + btn_h + 28), "Continuar explorando",
              anchor="mm", fill=DIM, font=get_font(14))

    return img


# ═══════════════════════════════════════════════════════════
# 3. CHAT SCREEN
# ═══════════════════════════════════════════════════════════
def gen_chat_screen():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_status_bar(draw)

    header_h = 90
    draw.rectangle([(0, 48), (W, header_h)], fill=CARD_BG)
    # back arrow
    draw.text((20, header_h // 2 + 6), "←", fill=WHITE, font=get_font(24, bold=True))

    # Match avatar
    circle(draw, (68, header_h // 2 + 6), 28, fill="#556688")
    draw.text((68, header_h // 2 + 6), "👩", anchor="mm", fill=WHITE, font=get_font(28))

    # Name + status
    f_name = get_font(18, bold=True)
    draw.text((106, header_h // 2 - 2), "Maria & João", fill=WHITE, font=f_name)
    f_status = get_font(13)
    draw.text((106, header_h // 2 + 20), "Online", fill=MATCH_GREEN, font=f_status)
    # green dot
    circle(draw, (174, header_h // 2 + 20), 4, fill=MATCH_GREEN)

    # Chat bubbles
    bubbles = [
        ("Oi! Adoramos a sua casa em Cascais! 🏖️", "left", OFF_WHITE, CARD_BG),
        ("Vocês têm disponibilidade para julho?", "left", OFF_WHITE, CARD_BG),
        ("Obrigado! Sim, temos as semanas de 12–19 e 26–02 abertas.", "right", WHITE, "#2e5a40"),
        ("Perfeito! A gente topa a troca. Qual o fluxo agora?", "left", OFF_WHITE, CARD_BG),
        ("Proponho enviar a proposta formal pelo app. Assim registramos tudo!", "right", WHITE, "#2e5a40"),
    ]

    y = header_h + 18
    max_w = W - 100
    for text, side, txt_color, bg_color in bubbles:
        f = get_font(14)
        # estimate width / height
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + " " + w if cur else w
            bb = draw.textbbox((0, 0), test, font=f)
            if bb[2] - bb[0] > max_w:
                lines.append(cur)
                cur = w
            else:
                cur = test
        lines.append(cur)

        lh = 22
        bw = max(draw.textbbox((0, 0), ln, font=f)[2] for ln in lines) + 24
        bh = len(lines) * lh + 16

        if side == "left":
            bx = 16
        else:
            bx = W - 16 - bw

        rounded_rect(draw, [bx, y, bx + bw, y + bh], radius=18, fill=bg_color)
        for i, ln in enumerate(lines):
            draw.text((bx + 14, y + 10 + i * lh), ln, fill=txt_color, font=f)

        y += bh + 10

    # "Proposta" special button inside chat
    btn_y = y + 10
    btn_h = 46
    rounded_rect(draw, [W // 2 - 110, btn_y, W // 2 + 110, btn_y + btn_h],
                 radius=23, fill="#2a1f10", outline=GOLD, width=2)
    draw.text((W // 2, btn_y + btn_h // 2), "✨  Enviar Proposta  ✨",
              anchor="mm", fill=GOLD, font=get_font(15, bold=True))

    # Input bar
    input_y = H - 90
    draw.rounded_rectangle([14, input_y, W - 14, input_y + 46],
                           radius=23, fill="#12121f", outline="#252540", width=1)
    draw.text((36, input_y + 23), "Digite uma mensagem...",
              anchor="lm", fill=DIM, font=get_font(14))
    # send button
    circle(draw, (W - 44, input_y + 23), 18, fill=MATCH_GREEN)
    draw.text((W - 44, input_y + 23), "↑", anchor="mm", fill=WHITE, font=get_font(18, bold=True))

    draw_bottom_nav(draw, active="Chat")
    return img


# ═══════════════════════════════════════════════════════════
# 4. PROFILE SCREEN
# ═══════════════════════════════════════════════════════════
def gen_profile_screen():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_status_bar(draw)

    # Profile header
    header_h = 200
    draw.rectangle([(0, 48), (W, header_h)], fill=CARD_BG)

    # Cover gradient on header
    for y in range(48, header_h):
        p = (y - 48) / (header_h - 48)
        col = (10 + int(20 * p), 10 + int(15 * p), 20 + int(30 * (1 - p)))
        draw.line([(0, y), (W, y)], fill=col, width=1)

    # Avatar
    av_cx = W // 2
    av_cy = header_h - 20
    circle(draw, (av_cx, av_cy), 54, fill=BG)
    circle(draw, (av_cx, av_cy), 50, fill="#445577")
    draw.text((av_cx, av_cy), "👨", anchor="mm", fill=WHITE, font=get_font(48))
    circle(draw, (av_cx, av_cy), 52, fill=None, outline=GOLD, width=2)

    # Name
    f_name = get_font(22, bold=True)
    draw.text((W // 2, header_h + 28), "Carlos Silva",
              anchor="mt", fill=WHITE, font=f_name)

    # Badge
    badge_text = "💎 Host Diamante"
    f_badge = get_font(12)
    bb = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw = bb[2] - bb[0] + 20
    bh = bb[3] - bb[1] + 10
    bx = W // 2 - bw // 2
    by = header_h + 56
    rounded_rect(draw, [bx, by, bx + bw, by + bh], radius=12, fill="#181824", outline=GOLD, width=1)
    draw.text((W // 2, by + bh // 2), badge_text, anchor="mm", fill=GOLD, font=f_badge)

    # Stats row
    stats_y = by + bh + 24
    stats = [("12", "Trocas"), ("4.9", "Nota"), ("8.4k", "Pontos")]
    sw = W // len(stats)
    for i, (num, label) in enumerate(stats):
        cx = sw * i + sw // 2
        draw.text((cx, stats_y), num, anchor="mt", fill=WHITE, font=get_font(22, bold=True))
        draw.text((cx, stats_y + 30), label, anchor="mt", fill=DIM, font=get_font(12))

    # Divider
    div_y = stats_y + 66
    draw.line([(30, div_y), (W - 30, div_y)], fill="#252540", width=1)

    # "Minha Casa" section
    sec_y = div_y + 20
    draw.text((26, sec_y), "🏠 Minha Casa", fill=WHITE, font=get_font(15, bold=True))

    # House preview card
    hc_y = sec_y + 34
    hc_h = 140
    rounded_rect(draw, [20, hc_y, W - 20, hc_y + hc_h],
                 radius=18, fill=CARD_BG, outline=GOLD_DARK, width=1)
    # fake house image area
    draw.rectangle([(20, hc_y), (120, hc_y + hc_h)], fill="#1e1e3a")
    draw.text((70, hc_y + hc_h // 2), "🏡", anchor="mm", fill=WHITE, font=get_font(36))
    # Details
    draw.text((136, hc_y + 14), "Apartamento em Lisboa", fill=WHITE, font=get_font(15, bold=True))
    draw.text((136, hc_y + 40), "2 quartos • 85 m² • Centro histórico",
              fill=OFF_WHITE, font=get_font(13))
    # edit button
    rounded_rect(draw, [136, hc_y + 82, 260, hc_y + 112], radius=8, fill="#181824")
    draw.text((198, hc_y + 97), "Editar imóvel", anchor="mm", fill=DIM, font=get_font(12))

    # Level progress
    prog_y = hc_y + hc_h + 34
    draw.text((26, prog_y), "Progresso para o próximo nível", fill=OFF_WHITE, font=get_font(13))
    bar_y = prog_y + 28
    bar_h = 12
    rounded_rect(draw, [20, bar_y, W - 20, bar_y + bar_h],
                 radius=6, fill="#181824")
    pct = 0.72
    bar_w = int((W - 40) * pct)
    # gold bar
    for x in range(20, 20 + bar_w):
        p = (x - 20) / bar_w if bar_w > 0 else 0
        gr = int(180 + 40 * math.sin(p * math.pi))
        draw.line([(x, bar_y + 1), (x, bar_y + bar_h - 1)], fill=(gr, int(gr * 0.75), int(gr * 0.4)), width=1)
    draw.text((W - 20, bar_y - 10), "72%", anchor="rb", fill=GOLD, font=get_font(11))

    # Settings links
    links_y = bar_y + bar_h + 30
    links = ["⚙️  Configurações", "🔔  Notificações", "❓  Ajuda & Suporte"]
    for i, link in enumerate(links):
        ly = links_y + i * 46
        draw.text((26, ly), link, fill=OFF_WHITE, font=get_font(14))
        draw.text((W - 30, ly), ">", fill=DIM, font=get_font(18))
        draw.line([(26, ly + 24), (W - 26, ly + 24)], fill="#181824", width=1)

    draw_bottom_nav(draw, active="Perfil")
    return img


# ═══════════════════════════════════════════════════════════
def main():
    screens = {
        "feed-card.png": gen_feed_card(),
        "match-screen.png": gen_match_screen(),
        "chat-screen.png": gen_chat_screen(),
        "profile-screen.png": gen_profile_screen(),
    }
    for name, img in screens.items():
        path = os.path.join(DIR, name)
        img.save(path, quality=95)
        print(f"✅  {name}  ({img.size[0]}×{img.size[1]})")
    print(f"\n📁  Todos salvos em: {DIR}")


if __name__ == "__main__":
    main()
