#!/usr/bin/env python3
"""Transplant native shape shells/groups into authored placeholders, retaining current text/style.

This deliberately rejects charts, tables, images and unresolved media dependencies.
Use host native-copy/authoring tools for those objects. No original file is overwritten.
"""
import argparse,json,math
from copy import deepcopy
from pathlib import Path
from pptx_parts import *

FILL_TAGS={'noFill','solidFill','gradFill','blipFill','pattFill','grpFill'}

def clean(node,record):
    for t in node.findall('.//a:t',NS):t.text=''
    for nv in node.findall('.//p:cNvPr',NS):
        for attr in ('descr','title'):nv.attrib.pop(attr,None)
    for h in node.xpath('.//a:hlinkClick|.//a:hlinkMouseOver',namespaces=NS):h.getparent().remove(h)
    palette=record.get('palette',{})
    for value in palette.values():
        value=value.lstrip('#')
        if len(value)!=6 or any(c not in '0123456789abcdefABCDEF'for c in value):raise ValueError('Palette values must be six-digit RGB hex colors')
    for el in node.findall('.//a:srgbClr',NS)+node.findall('.//a:schemeClr',NS):
        key=el.get('val');lookup=key if key in palette else key.upper()
        if lookup in palette:el.tag='{'+A+'}srgbClr';el.set('val',palette[lookup].lstrip('#').upper())
    if node.xpath('.//*[@r:id or @r:embed or @r:link]',namespaces=NS):raise ValueError('Donor has media/dependency relationships; use a supported native copy workflow')

def rotated_bound(node):
    b=frame(node)
    if b is None:raise ValueError('Donor needs an explicit transform')
    x,y,w,h=(b[k]*EMU_PER_PIXEL for k in ('x','y','w','h'));theta=math.radians(b['rotation_degrees'])
    rw,rh=abs(w*math.cos(theta))+abs(h*math.sin(theta)),abs(h*math.cos(theta))+abs(w*math.sin(theta))
    return x+(w-rw)/2,y+(h-rh)/2,rw,rh

def apply_record(root,donorroot,record):
    name=record['target_name'];targets=[s for s in root.findall('.//p:sp',NS)if nonvisual(s).get('name')==name]
    if len(targets)!=1:raise ValueError(('Expected one authored placeholder',name,len(targets)))
    ph=targets[0];mode=record.get('mode','shell');ids=[str(v)for v in record['donor_ids']]
    if not ids or len(ids)!=len(set(ids)):raise ValueError('Use distinct donor IDs')
    selected=[]
    for ident in ids:
        matches=[s for s in donorroot.iter()if nonvisual(s)is not None and nonvisual(s).get('id')==ident]
        if len(matches)!=1:raise ValueError(('Ambiguous/missing donor ID',ident))
        selected.append(matches[0])
    if any(a in b.iterancestors()for a in selected for b in selected if a is not b):raise ValueError('Do not select both a group and its descendant')
    if any(E.QName(s).localname not in ('sp','cxnSp','grpSp')for s in selected):raise ValueError('Only native shapes, connectors and shape groups are supported')
    donors=[deepcopy(s)for s in selected]
    for s in donors:clean(s,record)
    if mode=='shell':
        if len(donors)!=1 or E.QName(donors[0]).localname!='sp':raise ValueError('Shell mode needs one native shape')
        item=donors[0]
        for tag in ('nvSpPr','txBody'):
            old=item.find('p:'+tag,NS);new=ph.find('p:'+tag,NS)
            if old is not None:item.remove(old)
            if new is not None:item.insert(0 if tag=='nvSpPr'else len(item),deepcopy(new))
        pr,auth=item.find('p:spPr',NS),ph.find('p:spPr',NS)
        copytags={'xfrm'}|(FILL_TAGS if record.get('use_target_fill',True)else set())|({'ln'}if record.get('use_target_line',True)else set())
        for child in list(pr):
            if E.QName(child).localname in copytags:pr.remove(child)
        for child in auth:
            tag=E.QName(child).localname
            if tag not in copytags:continue
            if tag=='xfrm':pr.insert(0,deepcopy(child))
            elif tag in FILL_TAGS:
                geom=pr.find('a:prstGeom',NS)
                if geom is None:geom=pr.find('a:custGeom',NS)
                pr.insert(pr.index(geom)+1 if geom is not None else 1,deepcopy(child))
            else:
                before=next((e for e in pr if E.QName(e).localname in ('effectLst','effectDag','scene3d','sp3d','extLst')),None)
                pr.insert(pr.index(before)if before is not None else len(pr),deepcopy(child))
    elif mode=='group':
        if text(ph).strip():raise ValueError('Group placeholder must be blank; author target text separately')
        if len({id(s.getparent())for s in selected})!=1:raise ValueError('Group donors must share the same coordinate parent')
        item=E.Element('{'+P+'}grpSp');nv=E.SubElement(item,'{'+P+'}nvGrpSpPr')
        E.SubElement(nv,'{'+P+'}cNvPr',id=nonvisual(ph).get('id'),name=name);E.SubElement(nv,'{'+P+'}cNvGrpSpPr');E.SubElement(nv,'{'+P+'}nvPr')
        gp=E.SubElement(item,'{'+P+'}grpSpPr');xf=deepcopy(transform(ph))
        if xf is None:raise ValueError('Placeholder needs a frame')
        for tag in ('chOff','chExt'):
            for c in xf.findall('a:'+tag,NS):xf.remove(c)
        gp.append(xf)
        if record.get('source_box_px'):
            x,y,w,h=[float(record['source_box_px'][k])*EMU_PER_PIXEL for k in ('x','y','w','h')]
        else:
            bs=[rotated_bound(d)for d in donors];x=min(b[0]for b in bs);y=min(b[1]for b in bs);w=max(b[0]+b[2]for b in bs)-x;h=max(b[1]+b[3]for b in bs)-y
        if not all(math.isfinite(v)for v in (x,y,w,h))or w<=0 or h<=0:raise ValueError('Invalid donor group bounds')
        E.SubElement(xf,'{'+A+'}chOff',x=str(round(x)),y=str(round(y)));E.SubElement(xf,'{'+A+'}chExt',cx=str(round(w)),cy=str(round(h)))
        nid=max(int(n.get('id'))for n in root.findall('.//p:cNvPr',NS))+1;idmap={}
        # Respect donor z-order, even if the manifest lists IDs in a different order.
        position={id(s):list(s.getparent()).index(s)for s in selected}
        ordered_donors=[d for _,d in sorted(zip(selected,donors),key=lambda pair:position[id(pair[0])])]
        for d in ordered_donors:
            for nn in d.findall('.//p:cNvPr',NS):
                old=nn.get('id');idmap[old]=str(nid);nn.set('id',str(nid));nn.set('name',f'{name}.native.{old}');nid+=1
            item.append(d)
        for end in item.xpath('.//a:stCxn|.//a:endCxn',namespaces=NS):
            old=end.get('id')
            if old in idmap:end.set('id',idmap[old])
            else:end.getparent().remove(end)
    else:raise ValueError('Mode must be shell or group')
    ph.getparent().replace(ph,item)
    return {'target_name':name,'mode':mode,'donor_slide':record['donor_slide'],'donor_ids':ids}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--authored',type=Path,required=True);ap.add_argument('--donor',type=Path,required=True);ap.add_argument('--map',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.resolve()in (a.authored.resolve(),a.donor.resolve()):ap.error('Use a separate output path')
    cfg=json.loads(a.map.read_text());records=cfg['records']
    if cfg['donor_sha256']!=sha(a.donor.read_bytes()):raise ValueError('Donor hash differs from the inspected bank')
    parts=readzip(a.authored);bank=readzip(a.donor);ss=ordered(parts);ds=ordered(bank);report=[];seen=set()
    for rec in records:
        key=(rec['target_slide'],rec['target_name'])
        if key in seen:raise ValueError(('Repeated target placeholder',key))
        seen.add(key);n=int(rec['target_slide']);dn=int(rec['donor_slide'])
        if not 1<=n<=len(ss)or not 1<=dn<=len(ds):raise ValueError('Slide number outside source deck')
        part=ss[n-1][1];root=xml(parts[part]);donor=xml(bank[ds[dn-1][1]])
        report.append({'target_slide':n,**apply_record(root,donor,rec)});parts[part]=dump(root)
    errors=relationship_issues(parts)
    if errors:raise ValueError(errors)
    writezip(a.output,parts);rp=a.output.with_suffix('.reuse.json');rp.write_text(json.dumps({'authored_sha256':sha(a.authored.read_bytes()),'donor_sha256':cfg['donor_sha256'],'output_sha256':sha(a.output.read_bytes()),'reused':report},indent=2));print(json.dumps({'objects_reused':len(report),'output':str(a.output),'report':str(rp)}))
if __name__=='__main__':main()
