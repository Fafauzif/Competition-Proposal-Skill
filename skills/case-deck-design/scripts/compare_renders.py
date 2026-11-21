#!/usr/bin/env python3
"""Compare mapped pages from two already rendered PDFs under a fixed rendering size."""
import argparse,json
from pathlib import Path
import fitz
from PIL import Image,ImageChops

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--before',type=Path,required=True);ap.add_argument('--after',type=Path,required=True);ap.add_argument('--mapping',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--width',type=int,default=1600);a=ap.parse_args()
    cfg=json.loads(a.mapping.read_text());rows=cfg if isinstance(cfg,list)else cfg.get('preserved',cfg.get('mapping',[]))
    if not rows:ap.error('Mapping is empty')
    if a.width<200:ap.error('Use a review width of at least200px')
    before,after=fitz.open(a.before),fitz.open(a.after);results=[]
    for row in rows:
        pages=[before[row['before']-1],after[row['after']-1]];images=[]
        for p in pages:
            pix=p.get_pixmap(matrix=fitz.Matrix(a.width/p.rect.width,a.width/p.rect.width),alpha=False);images.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
        same_size=images[0].size==images[1].size;box=ImageChops.difference(*images).getbbox()if same_size else None
        results.append({'before':row['before'],'after':row['after'],'pixel_identical':same_size and box is None,'difference_bbox':box,'same_size':same_size})
    out={'checked':len(results),'pixel_identical':all(r['pixel_identical']for r in results),'results':results,'boundary':'Rendered-PDF comparison only; use the same fonts and office-renderer settings for both source PDFs.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2));print(json.dumps({'checked':len(results),'pixel_identical':out['pixel_identical'],'output':str(a.output)}));raise SystemExit(0 if out['pixel_identical']else 1)
if __name__=='__main__':main()
