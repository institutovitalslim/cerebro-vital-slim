from PIL import Image, ImageDraw

# Create high-quality circular avatar from best source
src = Image.open('/root/.openclaw/workspace/fotos_dra/avatares/Imagem PNG 2.png').convert('RGBA')

# Center-crop to square
w, h = src.size
min_dim = min(w, h)
left = (w - min_dim) // 2
top = (h - min_dim) // 2
src = src.crop((left, top, left + min_dim, top + min_dim))

# Resize to 512x512 for high quality
size = 512
src = src.resize((size, size), Image.LANCZOS)

# Apply circular mask
mask = Image.new('L', (size, size), 0)
ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
out.paste(src, mask=mask)

# Save as new official avatar
out.save('/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png', 'PNG')
print('Avatar atualizado:', '/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png')
