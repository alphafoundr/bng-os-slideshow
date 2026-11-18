from PIL import Image,ImageDraw
from pathlib import Path
out=Path(__file__).resolve().parent/'_lines'
paths=sorted(out.glob('s*.png'))
for start in range(0,len(paths),6):
    sheet=Image.new('RGB',(1440,960),'#dddddd');draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(paths[start:start+6]):
        im=Image.open(p);im.thumbnail((720,450))
        x=(i%2)*720;y=(i//2)*320
        im.thumbnail((720,300));sheet.paste(im,(x,y+20));draw.text((x+10,y+3),p.stem,fill='black')
    sheet.save(out/f'contact-{start//6}.jpg')
