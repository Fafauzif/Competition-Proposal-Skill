#!/usr/bin/env python3
"""Create labelled contact sheets from an existing PDF; review aids, not slide artwork."""
import argparse,math,json
from pathlib import Path
import fitz
from PIL import Image,ImageDraw,ImageFont

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pdf',type=Path);ap.add_argument('--outdir',type=Path,required=True);ap.add_argument('--columns',type=int,default=4);ap.add_argument('--rows',type=int,default=4);ap.add_argument('--thumb-width',type=int,default=400);ap.add_argument('--slides',help='Comma-separated 1-based slides; default all');a=ap.parse_args()
    if not 1<=a.columns<=10 or not 1<=a.rows<=10 or a.thumb_width<100:ap.error('Use1–10 columns/rows and thumbnail width>=100')
    doc=fitz.open(a.pdf);nums=[int(x)for x in a.slides.split(',')]if a.slides else list(range(1,len(doc)+1))
    if any(n<1 or n>len(doc)for n in nums):ap.error('Slide outside PDF range')
    a.outdir.mkdir(parents=True,exist_ok=True);batch=a.columns*a.rows;files=[]
    for start in range(0,len(nums),batch):
        subset=nums[start:start+batch];height=max(round(a.thumb_width*doc[n-1].rect.height/doc[n-1].rect.width)for n in subset);gutter=18;label=32
        sheet=Image.new('RGB',(a.columns*(a.thumb_width+gutter)+gutter,math.ceil(len(subset)/a.columns)*(height+label+gutter)+gutter),'#e7e9eb');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=18)
        for j,n in enumerate(subset):
            page=doc[n-1];pix=page.get_pixmap(matrix=fitz.Matrix(a.thumb_width/page.rect.width,a.thumb_width/page.rect.width),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            x=gutter+(j%a.columns)*(a.thumb_width+gutter);y=gutter+(j//a.columns)*(height+label+gutter);draw.text((x,y),f'Slide {n}',font=font,fill='#111111');sheet.paste(im,(x,y+label))
        file=a.outdir/f'contact_{start//batch+1:02}.png';sheet.save(file);files.append(str(file))
    print(json.dumps({'slides':len(nums),'sheets':files}))
if __name__=='__main__':main()
