from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import json, math

OUT=Path('/root/cerebro-vital-slim/deliverables/daniely-creatina-cerebro-v3')
OUT.mkdir(parents=True, exist_ok=True)
AVATAR='/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png'
PHOTO='/root/.openclaw/media/inbound/file_409---84cb8f21-17ba-4088-bb34-535f580363c4.jpg'
PAPER='/tmp/paper_creatine_cover.png'
W,H=1080,1350
GOLD=(201,162,39)
WHITE=(255,255,255)
BG=(0,0,0)
fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fr='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size,bold=False):
    return ImageFont.truetype(fb if bold else fr,size)

def fit_text(draw,text,max_w,start,minimum=36):
    s=start
    while s>=minimum:
        f=font(s,True)
        if draw.textbbox((0,0),text,font=f)[2] <= max_w:
            return f
        s-=2
    return font(minimum,True)

def wrap(draw,text,f,max_w):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if draw.textbbox((0,0),t,font=f)[2] <= max_w:
            cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

img=Image.new('RGB',(W,H),(8,6,4))
upper=Image.new('RGB',(W,760),(18,14,10))
du=ImageDraw.Draw(upper)
for i in range(160):
    x=60+i*6
    y=90+int(25*math.sin(i/7))
    r=2+(i%3)
    du.ellipse((x-r,y-r,x+r,y+r), fill=(120+ i%40,95+i%30,40))
    if i<159:
        x2=60+(i+1)*6
        y2=90+int(25*math.sin((i+1)/7))
        du.line((x,y,x2,y2), fill=(100,80,35), width=2)
for i in range(70):
    x=80+i*13
    y=250+int(18*math.sin(i/5))
    du.line((x,y,x+24,y-16), fill=(180,145,60), width=2)
    du.line((x+24,y-16,x+48,y+10), fill=(180,145,60), width=2)
img.paste(upper,(0,0))
ov=Image.new('RGBA',(W,H),(0,0,0,0))
do=ImageDraw.Draw(ov)
for y in range(H):
    a=120 if y<760 else min(220,120+int((y-760)*0.4))
    do.line((0,y,W,y), fill=(0,0,0,a))
img=Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
ph=Image.open(PHOTO).convert('RGB')
pw,phh=ph.size
crop=ph.crop((int(pw*0.08), int(phh*0.02), int(pw*0.92), int(phh*0.92)))
new_h=760
new_w=int(crop.size[0]*new_h/crop.size[1])
crop=crop.resize((new_w,new_h), Image.LANCZOS)
img.paste(crop,((W-new_w)//2,0))
fade=Image.new('RGBA',(W,760),(0,0,0,0))
df=ImageDraw.Draw(fade)
for y in range(760):
    a=max(0,int((y-420)*0.7)) if y>420 else 0
    df.line((0,y,W,y), fill=(0,0,0,min(a,160)))
img=img.convert('RGBA')
img.alpha_composite(fade,(0,0))
base=ImageDraw.Draw(img)
base.ellipse((760,120,1000,360), fill=(20,20,20,210), outline=GOLD, width=6)
base.rounded_rectangle((820,170,940,305), radius=18, fill=(242,242,242), outline=(220,220,220), width=2)
base.rectangle((820,170,940,205), fill=(35,35,35))
base.text((842,214),'CREATINE', font=font(26,True), fill=(30,30,30))
base.text((846,248),'MONOHYDRATE', font=font(18,False), fill=(80,80,80))
for i in range(8):
    base.ellipse((785+i*22,325-(i%2)*8,795+i*22,335-(i%2)*8), fill=(212,177,73))

ydiv=770
base.line((110,ydiv,485,ydiv), fill=GOLD, width=4)
base.line((595,ydiv,970,ydiv), fill=GOLD, width=4)
base.ellipse((500,ydiv-22,580,ydiv+58), fill=(14,10,6), outline=GOLD, width=3)
base.text((540,ydiv+18),'V', font=font(44,True), fill=GOLD, anchor='mm')
headline=['UM DOS SUPLEMENTOS','MAIS SUBESTIMADOS','PARA O CÉREBRO']
colors=[WHITE,GOLD,WHITE]
y=840
for line,col,size in zip(headline,colors,[74,74,74]):
    f=fit_text(base,line,850,size)
    bbox=base.textbbox((0,0),line,font=f)
    x=(W-(bbox[2]-bbox[0]))//2
    base.text((x,y),line,font=f,fill=col)
    y += (bbox[3]-bbox[1]) + 16
footer='Dra. Daniely Freitas | CRM-BA 27588'
f=font(28,False)
bbox=base.textbbox((0,0),footer,font=f)
base.text(((W-(bbox[2]-bbox[0]))//2,1240), footer, font=f, fill=(165,155,138))
img.convert('RGB').save(OUT/'slide_01.png')

img=Image.new('RGB',(W,H),BG)
d=ImageDraw.Draw(img)
av=Image.open(AVATAR).convert('RGB').resize((72,72), Image.LANCZOS)
mask=Image.new('L',(72,72),0)
ImageDraw.Draw(mask).ellipse((0,0,72,72), fill=255)
av_rgba=Image.new('RGBA',(72,72),(0,0,0,0)); av_rgba.paste(av,(0,0),mask)
img_rgba=img.convert('RGBA'); img_rgba.paste(av_rgba,(64,90),av_rgba); img=img_rgba.convert('RGB'); d=ImageDraw.Draw(img)
d.text((154,94),'Dra. Daniely Freitas', font=font(32,True), fill=WHITE)
d.ellipse((446,102,470,126), fill=(29,155,240))
d.line((454,114,459,119), fill=WHITE, width=2); d.line((459,119,466,108), fill=WHITE, width=2)
d.text((154,136),'@dradaniely.freitas', font=font(22,False), fill=(113,118,123))
text='Este estudo reuniu 16 estudos clínicos randomizados, com 492 participantes, e encontrou melhora em memória, atenção e velocidade de processamento.'
lines=wrap(d,text,font(36,False),952)
y=230
for ln in lines:
    d.text((64,y),ln,font=font(36,False),fill=(200,200,200)); y+=52
paper=Image.open(PAPER).convert('RGB')
maxw,maxh=900,720
ratio=min(maxw/paper.size[0], maxh/paper.size[1])
paper=paper.resize((int(paper.size[0]*ratio), int(paper.size[1]*ratio)), Image.LANCZOS)
px=(W-paper.size[0])//2
py=520
img.paste(paper,(px,py))
d=ImageDraw.Draw(img)
d.rounded_rectangle((px-2,py-2,px+paper.size[0]+2,py+paper.size[1]+2), radius=24, outline=(55,55,55), width=2)
d.text((64,1260),'Frontiers in Nutrition, 2024 | PubMed 39070254', font=font(24,False), fill=(140,140,140))
img.save(OUT/'slide_02.png')

slides=[
  {"num":3,"paragraphs":["Esta revisão analisou 16 estudos clínicos randomizados.","Ao todo, foram 492 participantes, com idades entre 20,8 e 76,4 anos.","Não foi um estudo isolado. →"]},
  {"num":4,"paragraphs":["Os pesquisadores encontraram melhora significativa na memória.","Isso significa mais facilidade para guardar e recuperar informações.","E esse foi um dos achados mais consistentes da análise. →"]},
  {"num":5,"paragraphs":["Também houve melhora no tempo de atenção.","Na prática, isso sugere um cérebro mais rápido para responder e sustentar foco.","Especialmente em tarefas mentais mais exigentes. →"]},
  {"num":6,"paragraphs":["Outro ponto importante foi a melhora na velocidade de processamento.","Ou seja, o cérebro conseguiu lidar melhor com a informação em menos tempo.","Isso importa muito no raciocínio do dia a dia. →"]},
  {"num":7,"paragraphs":["Os melhores resultados apareceram principalmente em mulheres, em pessoas entre 18 e 60 anos e em pacientes com alguma condição de saúde.","Ou seja, o efeito não apareceu de forma aleatória. →"]},
  {"num":8,"paragraphs":["Em todos os estudos incluídos, a forma usada foi a creatina monohidratada.","Isso reforça que estamos falando da forma mais estudada da creatina.","E não de uma promessa genérica. →"]},
  {"num":9,"paragraphs":["A conclusão não é que creatina faz milagre.","A conclusão é outra: ela pode ajudar memória, atenção e velocidade mental quando existe indicação correta. →"]},
  {"num":10,"paragraphs":["Estamos falando de um suplemento que muita gente associa apenas à força muscular.","Mas a pesquisa mostra que ele também pode apoiar o funcionamento do cérebro.","E isso merece mais atenção.","Se este conteúdo fez sentido para você, salve este post."]}
]
Path('/tmp/creatina_v3_slides.json').write_text(json.dumps(slides, ensure_ascii=False, indent=2))
print('ok')
