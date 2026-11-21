#!/usr/bin/env python3
"""Select/reorder base and authored slides without re-exporting retained slide bodies.

Manifest order contains {id, source: base|authored, slide}. Redirects map source keys
such as base:17 to logical output IDs. See native-reuse-and-assembly.md for limits.
"""
import argparse,json,posixpath as pp
from pathlib import Path
from copy import deepcopy
from pptx_parts import *

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--authored',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.resolve()in (a.base.resolve(),a.authored.resolve()):ap.error('Use a separate output file')
    cfg=json.loads(a.manifest.read_text());base=readzip(a.base);gen=readzip(a.authored);parts=dict(base);bs=ordered(base);gs=ordered(gen)
    if xml(base[PRES]).find('p:sldSz',NS).attrib!=xml(gen[PRES]).find('p:sldSz',NS).attrib:raise ValueError('Slide dimensions differ; author at the target canvas size')
    for source,key in ((a.base,'base_sha256'),(a.authored,'authored_sha256')):
        if key in cfg and cfg[key]!=sha(source.read_bytes()):raise ValueError(('Input hash mismatch',key))
    order=cfg['order'];ids=[x['id']for x in order];keys=[f"{x['source']}:{x['slide']}"for x in order]
    if len(ids)!=len(set(ids))or len(keys)!=len(set(keys)):raise ValueError('IDs and source selections must be unique; author intentional duplicates separately')
    if not order:raise ValueError('Output requires slides')
    # Avoid silently corrupting custom-show/section metadata when source slide IDs disappear.
    if xml(base[PRES]).find('p:custShowLst',NS)is not None or xml(base[PRES]).xpath('.//*[local-name()="sectionLst"]'):raise ValueError('Base has custom shows/sections; use task-specific metadata-preserving assembly')
    mp=import_parts(parts,gen);register_presentation_dependencies(parts,gen,mp)
    sourceparts={**{f'base:{i}':p for i,(_,p)in enumerate(bs,1)},**{f'authored:{i}':mp[p]for i,(_,p)in enumerate(gs,1)}}
    logical={x['id']:sourceparts[k]for x,k in zip(order,keys)};logical_entry={x['id']:x for x in order}
    dests=[logical[i]for i in ids];active=set(dests)
    redirects={sourceparts[k]:logical[v]for k,v in cfg.get('redirects',{}).items()}
    byowner={sourceparts[k]:{sourceparts[t]:logical[v]for t,v in changes.items()}for k,changes in cfg.get('owner_redirects',{}).items()}
    for path,raw in list(parts.items()):
        if not path.endswith('.rels'):continue
        oo=owner(path);rr=xml(raw);changed=False
        for r in rr:
            if r.get('TargetMode')=='External':continue
            t=r.get('Target');d=resolve(oo,t);nd=byowner.get(oo,{}).get(d,redirects.get(d,d))
            if nd!=d:r.set('Target',pp.relpath(nd,pp.dirname(oo)or'.'));changed=True
        if changed:parts[path]=dump(rr)
    # Add explicit links only to authored objects. Retained slide navigation uses redirects.
    link_checks=[]
    for spec in cfg.get('links',[]):
        sid=spec['owner'];part=logical[sid]
        if logical_entry[sid]['source']!='authored':raise ValueError('New links on retained slide bodies need a separately authorized edit workflow')
        root=xml(parts[part]);rr=rels(parts,part);nodes=[n for n in root.iter()if nonvisual(n)is not None and nonvisual(n).get('name')==spec['shape_name']]
        if len(nodes)!=1:raise ValueError(('Link shape is missing/ambiguous',sid,spec['shape_name']))
        node=nodes[0];target=logical[spec['target']];rid=add_rel(rr,part,target)
        mode=spec.get('mode','shape')
        if mode not in ('shape','text','both'):raise ValueError('Link mode must be shape/text/both')
        containers=[]
        if mode in ('shape','both'):containers.append(nonvisual(node))
        if mode in ('text','both'):
            for run in node.findall('.//a:r',NS):
                rp=run.find('a:rPr',NS)
                if rp is None:rp=E.Element('{'+A+'}rPr');run.insert(0,rp)
                containers.append(rp)
        if not containers:raise ValueError('No text runs available for text hyperlink')
        for container in containers:
            for h in container.findall('a:hlinkClick',NS):container.remove(h)
            E.SubElement(container,'{'+A+'}hlinkClick',attrib={'{'+R+'}id':rid,'action':'ppaction://hlinksldjump'})
        parts[part]=dump(root);parts[relpart(part)]=dump(rr);link_checks.append(spec)
    pres=xml(parts[PRES]);rr=rels(parts,PRES);sl=pres.find('p:sldIdLst',NS)
    for node in list(sl):sl.remove(node)
    nextid=max([int(s.get('id'))for s,_ in bs]+[255])+1
    for entry in order:
        node=deepcopy(bs[entry['slide']-1][0])if entry['source']=='base'else E.Element('{'+P+'}sldId',id=str(nextid))
        if entry['source']!='base':nextid+=1
        node.set('{'+R+'}id',add_rel(rr,PRES,logical[entry['id']]));sl.append(node)
    for r in list(rr):
        if r.get('Type')==SLIDE_REL and resolve(PRES,r.get('Target'))not in active:rr.remove(r)
    parts[PRES]=dump(pres);parts[relpart(PRES)]=dump(rr)
    # A surviving source slide must not retain a link to an omitted old slide.
    dangling=[]
    for part in dests:
        for r in rels(parts,part):
            if r.get('Type')==SLIDE_REL and r.get('TargetMode')!='External'and resolve(part,r.get('Target'))not in active:dangling.append((part,r.get('Target')))
    if dangling:raise ValueError(('Redirect links to removed slides explicitly',dangling))
    removed=prune(parts);parts,cm=canonicalize(parts,dests)
    if 'docProps/app.xml'in parts:
        app=xml(parts['docProps/app.xml'])
        for node in app:
            if E.QName(node).localname=='Slides':node.text=str(len(order))
        parts['docProps/app.xml']=dump(app)
    errors=relationship_issues(parts)
    if errors:raise ValueError(errors)
    preserved=[]
    for after,e in enumerate(order,1):
        if e['source']!='base':continue
        op=bs[e['slide']-1][1];np=cm[op]
        if base[op]!=parts[np]:raise ValueError(('Retained slide body changed',e))
        note_parts=[resolve(op,r.get('Target'))for r in rels(base,op)if r.get('Type')==R+'/notesSlide']
        if any(parts.get(p)!=base[p]for p in note_parts):raise ValueError(('Retained notes changed',e))
        preserved.append({'before':e['slide'],'after':after,'body_identical':True,'notes_identical':True})
    writezip(a.output,parts)
    report={'output_sha256':sha(a.output.read_bytes()),'base_sha256':sha(a.base.read_bytes()),'slide_count':len(order),'logical_to_physical':{x['id']:i for i,x in enumerate(order,1)},'preserved':preserved,'links':link_checks,'removed_unreachable_parts':removed}
    rp=a.output.with_suffix('.assembly.json');rp.write_text(json.dumps(report,indent=2));print(json.dumps({'slides':len(order),'retained':len(preserved),'output':str(a.output),'report':str(rp)}))
if __name__=='__main__':main()
