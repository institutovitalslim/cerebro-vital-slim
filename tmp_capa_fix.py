#!/usr/bin/env python3
"""
Gerar capa corrigida com:
- Fundo contextual (laboratório/pesquisa)
- Círculo dourado com imagem temática
- Fonte grande com margem de segurança 1:1
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import sys

sys.path.insert(0, '/root/.openclaw/workspace/skills/tweet-carrossel/scripts')

# ── Constants ──
W, H = 1080, 1350
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (159, 136, 68)  # #9F8844
GOLD_LINE = (159, 136, 68, 180)
GRAY_TEXT = (180, 180, 180)

# Safe area para feed 1:1 (Instagram corta ~135px de topo/base)
SAFE_TOP = 135
SAFE_BOTTOM = H - 135
SAFE_HEIGHT = SAFE_BOTTOM - SAFE_TOP  # 1080px

# Layout proportions otimizados para preencher espaço
PHOTO_HEIGHT_RATIO = 0.45  # Menor = mais espaço para texto
TEXT_AREA_START = 0.48     # Texto começa mais cedo
LINE_Y_RATIO = 0.46        # Linha mais próxima
CIRCLE_SIZE = 140          # Círculo um pouco maior
CIRCLE_MARGIN = 25
CIRCLE_BORDER = 4

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/root/.openclaw/workspace/skills/tweet-carrossel/assets/DejaVuSans-Bold.ttf",
]

FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

MONTSERRAT_PATHS = [
    "/usr/share/fonts/truetype/montserrat/Montserrat-Black.ttf",
    "/usr/local/share/fonts/Montserrat-Black.ttf",
]

FOOTER_TEXT = "Dra. Daniely Freitas  |  CRM-BA 27588"

def find_font(paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    return None

def load_font(paths, size):
    path = find_font(paths)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_lab_background():
    """Criar fundo contextual de laboratório/pesquisa."""
    bg = Image.new("RGB", (W, H), (8, 8, 15))
    draw = ImageDraw.Draw(bg)
    
    # Grade de células/microscópio (subtil)
    for y in range(0, H, 100):
        for x in range(0, W, 100):
            draw.ellipse([x-20, y-20, x+20, y+20], outline=(20, 20, 35), width=2)
    
    # Tubos de ensaio verticais (lado esquerdo)
    for x in [80, 120, 160]:
        draw.rectangle([x, 100, x+20, 400], outline=(30, 30, 50), width=2)
        draw.ellipse([x-5, 85, x+25, 115], outline=(159, 136, 68, 100), width=2)
    
    # Microscópio (lado direito - silhueta)
    draw.ellipse([750, 150, 950, 350], outline=(25, 25, 40), width=2)
    draw.rectangle([840, 200, 890, 250], fill=(20, 20, 35))
    
    # Linhas horizontais (gel de eletroforese)
    for y in [500, 520, 540, 560]:
        draw.line([(50, y), (200, y)], fill=(35, 35, 55), width=1)
    
    # Efeito de iluminação do laboratório
    for y in range(H):
        alpha = int(15 * abs(y - H//2) / (H//2))
        draw.line([(0, y), (W, y)], fill=(alpha, alpha, alpha + 5))
    
    # Blur leve
    return bg.filter(ImageFilter.GaussianBlur(radius=2))

def remove_bg_simple(img):
    """Fallback simples para remover fundo escuro."""
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        # Se for muito escuro (provavelmente fundo)
        if item[0] < 50 and item[1] < 50 and item[2] < 50:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def make_circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask

def add_circle_inset(canvas, circle_img_path):
    if not os.path.isfile(circle_img_path):
        return
    
    circle_img = Image.open(circle_img_path).convert("RGBA")
    inner_size = CIRCLE_SIZE - CIRCLE_BORDER * 2
    circle_img = circle_img.resize((inner_size, inner_size), Image.LANCZOS)
    
    mask = make_circle_mask(inner_size)
    
    border_img = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_img)
    border_draw.ellipse((0, 0, CIRCLE_SIZE - 1, CIRCLE_SIZE - 1), fill=(*GOLD, 255))
    
    border_img.paste(circle_img, (CIRCLE_BORDER, CIRCLE_BORDER), mask)
    
    x = W - CIRCLE_SIZE - CIRCLE_MARGIN
    y = CIRCLE_MARGIN
    canvas.paste(border_img, (x, y), border_img)

def add_gold_line(canvas):
    draw = ImageDraw.Draw(canvas)
    y = int(H * LINE_Y_RATIO)
    margin = 40
    
    # Buscar símbolo V
    SYMBOL_CANDIDATES = [
        "/root/.openclaw/workspace/skills/tweet-carrossel/assets/simbolo_v.png",
        "/root/cerebro-vital-slim/cerebro/empresa/skills/tweet-carrossel/assets/simbolo_v.png",
    ]
    SYMBOL_PATH = next((p for p in SYMBOL_CANDIDATES if os.path.isfile(p)), None)
    SYMBOL_SIZE = 100
    
    if SYMBOL_PATH:
        symbol = Image.open(SYMBOL_PATH).convert("RGBA")
        symbol = symbol.resize((SYMBOL_SIZE, SYMBOL_SIZE), Image.LANCZOS)
        cx = W // 2
        sym_x = cx - SYMBOL_SIZE // 2
        sym_y = y - SYMBOL_SIZE // 2
        gap = SYMBOL_SIZE // 2 + 10
        draw.line([(margin, y), (cx - gap, y)], fill=GOLD_LINE, width=2)
        draw.line([(cx + gap, y), (W - margin, y)], fill=GOLD_LINE, width=2)
        canvas.paste(symbol, (sym_x, sym_y), symbol)
    else:
        draw.line([(margin, y), (W - margin, y)], fill=GOLD_LINE, width=2)

def render_headline_safe(draw, headline_lines, highlight_words, start_y):
    """Render headline com margem de segurança 1:1."""
    font_path = find_font(MONTSERRAT_PATHS) or find_font(FONT_PATHS)
    
    # Área disponível (dentro da safe area 1:1)
    safe_bottom = SAFE_BOTTOM - 60  # 60px acima do footer
    available_height = safe_bottom - start_y
    
    num_lines = len(headline_lines)
    
    # Calcular tamanho máximo de fonte que cabe na largura e altura
    max_font_size = 260
    min_font_size = 80
    
    best_size = min_font_size
    for size in range(max_font_size, min_font_size, -2):
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        line_height = int(size * 1.05)
        total_height = num_lines * line_height
        
        # Verificar largura
        max_width = max(draw.textlength(line, font=font) for line in headline_lines)
        
        if total_height <= available_height and max_width <= W - 80:
            best_size = size
            break
    
    font = ImageFont.truetype(font_path, best_size) if font_path else ImageFont.load_default()
    line_height = int(best_size * 1.05)
    total_height = num_lines * line_height
    
    # Centralizar verticalmente na área disponível (ou alinhar ao topo)
    y_offset = start_y
    
    highlight_set = set(w.strip().upper() for w in highlight_words)
    
    for i, line in enumerate(headline_lines):
        y = y_offset + i * line_height
        
        words = line.split(" ")
        total_line_width = draw.textlength(line, font=font)
        x_cursor = (W - total_line_width) // 2
        
        for word in words:
            word_clean = word.strip().upper().strip('"').strip("'").strip(",").strip(".")
            is_gold = word_clean in highlight_set
            color = GOLD if is_gold else WHITE
            
            draw.text((x_cursor, y), word, fill=color, font=font)
            word_width = draw.textlength(word + " ", font=font)
            x_cursor += word_width
    
    return y_offset + total_height

def add_footer(draw, y_pos):
    font = load_font(FONT_REG_PATHS, 18)
    bbox = draw.textbbox((0, 0), FOOTER_TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    x = (W - text_width) // 2
    draw.text((x, y_pos), FOOTER_TEXT, fill=GRAY_TEXT, font=font)

def build_cover():
    # Criar fundo contextual
    canvas = create_lab_background()
    
    # Carregar foto da Dra.
    foto = Image.open('/root/.openclaw/workspace/fotos_dra/originais/Imagem PNG 20.png')
    
    # Remover fundo (tentar rembg primeiro)
    try:
        from rembg import remove
        foto_nobg = remove(foto)
    except:
        foto_nobg = remove_bg_simple(foto)
    
    # Redimensionar foto
    target_h = int(H * PHOTO_HEIGHT_RATIO)
    ratio = target_h / foto_nobg.height
    new_w = int(foto_nobg.width * ratio)
    new_h = target_h
    foto_resized = foto_nobg.resize((new_w, new_h), Image.LANCZOS)
    
    # Posicionar foto (centralizada)
    x_offset = (W - new_w) // 2
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(foto_resized, (x_offset, 0), foto_resized)
    
    # Gradient fade na base da foto
    gradient = Image.new("RGBA", (W, new_h), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    fade_start = int(new_h * 0.5)
    for y in range(fade_start, new_h):
        alpha = int(255 * (y - fade_start) / (new_h - fade_start))
        grad_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    
    photo_rgba = canvas_rgba.crop((0, 0, W, new_h))
    photo_rgba = Image.alpha_composite(photo_rgba, gradient)
    canvas.paste(photo_rgba.convert("RGB"), (0, 0))
    
    # Adicionar círculo (criar imagem de laboratório/células)
    circle_img = Image.new("RGB", (300, 300), (30, 30, 50))
    circle_draw = ImageDraw.Draw(circle_img)
    # Células/microscópio simplificado
    circle_draw.ellipse([50, 50, 250, 250], outline=GOLD, width=3)
    circle_draw.ellipse([100, 100, 200, 200], outline=(200, 200, 200), width=2)
    circle_draw.ellipse([130, 130, 170, 170], outline=GOLD, width=2)
    circle_img.save('/tmp/circle_lab.png')
    
    canvas_rgba = canvas.convert("RGBA")
    add_circle_inset(canvas_rgba, '/tmp/circle_lab.png')
    canvas = canvas_rgba.convert("RGB")
    
    # Gold line
    add_gold_line(canvas)
    
    draw = ImageDraw.Draw(canvas)
    
    # Headline
    text_start_y = int(H * TEXT_AREA_START)
    headline_lines = ["UM REMÉDIO PARA EMAGRECER", "PODE SALVAR SEU ÚTERO"]
    highlight_words = ["REMÉDIO", "EMAGRECER", "SALVAR", "ÚTERO"]
    
    end_y = render_headline_safe(draw, headline_lines, highlight_words, text_start_y)
    
    # Footer (dentro da safe area)
    add_footer(draw, SAFE_BOTTOM - 30)
    
    # Salvar
    out_path = '/root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/slide_01_FINAL.jpg'
    canvas.save(out_path, "JPEG", quality=90, optimize=True)
    print(f"✓ Capa final: {out_path}")
    
    # Verificar se texto está dentro da safe area 1:1
    print(f"  Safe area: {SAFE_TOP}-{SAFE_BOTTOM}px (altura: {SAFE_HEIGHT})")
    print(f"  Texto começa em: {text_start_y}px")
    print(f"  Texto termina em: ~{end_y}px")
    print(f"  Dentro da safe area: {'SIM' if end_y < SAFE_BOTTOM - 30 else 'NÃO'}")

if __name__ == "__main__":
    build_cover()
