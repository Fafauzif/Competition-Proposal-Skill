#!/usr/bin/env python3
"""Audit package relationships, mapped body/notes preservation and declared native links.

Does not check claim truth, font rendering, visual layout or native application behavior.
"""
import argparse,json
from pathlib import Path
from pptx_parts import *

def mappings(value):
    if isinstance(value,list):return value
    return value.get('preserved',value.get('mapping',[]))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pptx',type=Path);ap.add_argument('--base',type=Path);ap.add_argument('--mapping',type=Path);ap.add_argument('--expected-links',type=Path,help='List of {slide, shape_name, target_slide|url}');ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    parts=readzip(a.pptx);ss=ordered(parts);issues=relationship_issues(parts);details=[];links=[];counts={'slides':len(ss),'charts':0,'tables':0}
    for i,(_,part)in enumerate(ss,1):
        root=xml(parts[part]);rr={r.get('Id'):r for r in rels(parts,part)}
        ids=[n.get('id')for n in root.findall('.//p:cNvPr',NS)]
        if len(ids)!=len(set(ids)):issues.append({'kind':'duplicate_object_ids','slide':i})
        counts['charts']+=len(root.findall('.//c:chart',NS));counts['tables']+=len(root.findall('.//a:tbl',NS))
        for node in root.xpath('.//*[@r:id or @r:embed or @r:link]',namespaces=NS):
            for attr in ('id','embed','link'):
                rid=node.get('{'+R+'}'+attr)
                if rid and rid not in rr:issues.append({'kind':'missing_relationship_id','slide':i,'id':rid})
        for shape in root.iter():
            nv=nonvisual(shape)
            if nv is None:continue
            for h in shape.findall('.//a:hlinkClick',NS):
                r=rr.get(h.get('{'+R+'}id'))
                if r is None:continue
                links.append({'slide':i,'shape_name':nv.get('name'),'target':r.get('Target')if r.get('TargetMode')=='External'else resolve(part,r.get('Target'))})
    if a.base or a.mapping:
        if not(a.base and a.mapping):ap.error('--base and --mapping must be supplied together')
        base=readzip(a.base);bs=ordered(base)
        for row in mappings(json.loads(a.mapping.read_text())):
            op=bs[row['before']-1][1];np=ss[row['after']-1][1];same=base[op]==parts[np]
            on=[resolve(op,r.get('Target'))for r in rels(base,op)if r.get('Type')==R+'/notesSlide'];nn=[resolve(np,r.get('Target'))for r in rels(parts,np)if r.get('Type')==R+'/notesSlide']
            notes=len(on)==len(nn)and all(base[x]==parts[y]for x,y in zip(on,nn));d={'before':row['before'],'after':row['after'],'body_identical':same,'notes_identical':notes};details.append(d)
            if not same or not notes:issues.append({'kind':'preservation_difference',**d})
    expected=[]
    if a.expected_links:
        for spec in json.loads(a.expected_links.read_text()):
            target=spec.get('url')or ss[spec['target_slide']-1][1]
            matched=any(x['slide']==spec['slide']and x['shape_name']==spec['shape_name']and x['target']==target for x in links)
            expected.append({**spec,'passed':matched})
            if not matched:issues.append({'kind':'missing_or_wrong_expected_link',**spec})
    report={'sha256':sha(a.pptx.read_bytes()),'passed':not issues,'counts':counts,'issues':issues,'preservation':details,'expected_links':expected,'claim_boundary':__doc__}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'counts':counts,'issues':len(issues),'output':str(a.output)}));raise SystemExit(0 if report['passed']else 1)
if __name__=='__main__':main()
