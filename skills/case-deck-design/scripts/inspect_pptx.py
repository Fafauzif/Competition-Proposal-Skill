#!/usr/bin/env python3
"""Inventory native objects and explicit styles; rendering/inheritance review remains required."""
import argparse,json,collections
from pathlib import Path
from pptx_parts import *

def inventory(path):
    parts=readzip(path);slides=ordered(parts);root=xml(parts[PRES]);size=root.find('p:sldSz',NS)
    out={'file':str(Path(path).resolve()),'sha256':sha(Path(path).read_bytes()),'slide_count':len(slides),'slide_size_emu':dict(size.attrib),'slides':[],'style_boundary':'Explicit declarations only; use layout/master/theme and renders to resolve inherited values.'}
    for i,(_,part)in enumerate(slides,1):
        root=xml(parts[part]);rr={r.get('Id'):r for r in rels(parts,part)};items=[]
        for node in root.iter():
            nv=nonvisual(node)
            if nv is None:continue
            kind=E.QName(node).localname
            deps=[]
            for elem in node.iter():
                for attr in ('id','embed','link'):
                    rid=elem.get('{'+R+'}'+attr)
                    if rid and rid in rr:
                        r=rr[rid];external=r.get('TargetMode')=='External'
                        deps.append({'id':rid,'kind':r.get('Type').rsplit('/',1)[-1],'target':r.get('Target')if external else resolve(part,r.get('Target')),'external':external})
            item={'id':nv.get('id'),'name':nv.get('name',''),'kind':kind,'text':text(node),'frame_px':frame(node),'coordinates_local_to_group':any(E.QName(a).localname=='grpSp'for a in node.iterancestors()),'explicit_fonts':sorted(set(node.xpath('.//a:latin/@typeface',namespaces=NS))),'explicit_sizes_pt':sorted({int(s)/100 for s in node.xpath('.//a:rPr/@sz|.//a:defRPr/@sz|.//a:endParaRPr/@sz',namespaces=NS)}),'rgb_colors':sorted(set(node.xpath('.//a:srgbClr/@val',namespaces=NS))),'scheme_colors':sorted(set(node.xpath('.//a:schemeClr/@val',namespaces=NS))),'dependencies':list({(d['id'],d['target']):d for d in deps}.values())}
            if node.find('.//a:tbl',NS)is not None:item['native_table']=True
            if node.find('.//c:chart',NS)is not None:item['native_chart']=True
            items.append(item)
        notes=[resolve(part,r.get('Target'))for r in rr.values()if r.get('Type')==R+'/notesSlide']
        out['slides'].append({'slide':i,'part':part,'body_sha256':sha(parts[part]),'text':text(root),'objects':items,'notes_parts':notes,'dependency_types':sorted({r.get('Type').rsplit('/',1)[-1]for r in rr.values()})})
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pptx',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=inventory(args.pptx);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps({'slides':result['slide_count'],'objects':sum(len(s['objects'])for s in result['slides']),'output':str(args.output)}))
if __name__=='__main__':main()
