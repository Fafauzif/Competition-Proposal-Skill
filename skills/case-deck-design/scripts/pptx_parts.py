"""Small OOXML package utilities; never render or re-author untouched slide bytes."""
from pathlib import Path
from copy import deepcopy
import hashlib,posixpath as pp,zipfile
from lxml import etree as E

P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
C='http://schemas.openxmlformats.org/drawingml/2006/chart'
NS={'p':P,'a':A,'r':R,'rel':PKG,'ct':CT,'c':C}
PRES='ppt/presentation.xml'
SLIDE_REL=R+'/slide'
EMU_PER_PIXEL=9525

def xml(raw):return E.fromstring(raw,E.XMLParser(resolve_entities=False,no_network=True))
def dump(root):return E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def readzip(path):
    with zipfile.ZipFile(path)as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP member names')
        if any(n.startswith('/')or '..'in n.split('/')for n in names):raise ValueError('Unsafe package member path')
        return {n:z.read(n)for n in names if not n.endswith('/')}
def writezip(path,parts):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,b in parts.items():z.writestr(n,b)
def relpart(part):return pp.join(pp.dirname(part),'_rels',pp.basename(part)+'.rels')if part else '_rels/.rels'
def owner(rp):
    if rp=='_rels/.rels':return ''
    directory,name=rp.rsplit('/_rels/',1);return pp.join(directory,name[:-5])
def resolve(part,target):
    target=target.split('#',1)[0]
    return pp.normpath(target.lstrip('/')if target.startswith('/')else pp.join(pp.dirname(part),target))
def rels(parts,part):return xml(parts[relpart(part)])if relpart(part)in parts else E.Element('{'+PKG+'}Relationships',nsmap={None:PKG})
def ordered(parts):
    root=xml(parts[PRES]);rr={r.get('Id'):r for r in rels(parts,PRES)}
    return [(deepcopy(s),resolve(PRES,rr[s.get('{'+R+'}id')].get('Target')))for s in root.findall('p:sldIdLst/p:sldId',NS)]
def text(node):return ''.join(node.xpath('.//a:t/text()',namespaces=NS))
def nonvisual(shape):
    for tag in ('nvSpPr','nvCxnSpPr','nvGrpSpPr','nvPicPr','nvGraphicFramePr'):
        nv=shape.find('p:'+tag+'/p:cNvPr',NS)
        if nv is not None:return nv
    return None
def transform(shape):
    for path in ('p:spPr/a:xfrm','p:grpSpPr/a:xfrm','p:xfrm'):
        x=shape.find(path,NS)
        if x is not None:return x
    return None
def frame(shape):
    xf=transform(shape)
    if xf is None:return None
    off,ext=xf.find('a:off',NS),xf.find('a:ext',NS)
    if off is None or ext is None:return None
    return {'x':int(off.get('x'))/EMU_PER_PIXEL,'y':int(off.get('y'))/EMU_PER_PIXEL,'w':int(ext.get('cx'))/EMU_PER_PIXEL,'h':int(ext.get('cy'))/EMU_PER_PIXEL,'rotation_degrees':int(xf.get('rot','0'))/60000}
def add_rel(root,part,target,kind=SLIDE_REL,external=False):
    dest=target if external else pp.relpath(target,pp.dirname(part)or'.')
    for r in root:
        if r.get('Type')==kind and r.get('Target')==dest and (r.get('TargetMode')=='External')==external:return r.get('Id')
    used={r.get('Id')for r in root};i=1
    while 'rCase'+str(i)in used:i+=1
    attrs={'Id':'rCase'+str(i),'Type':kind,'Target':dest}
    if external:attrs['TargetMode']='External'
    E.SubElement(root,'{'+PKG+'}Relationship',**attrs);return attrs['Id']
def relationship_issues(parts):
    issues=[]
    for path,raw in parts.items():
        if not path.endswith('.rels'):continue
        o=owner(path);ids=set()
        for r in xml(raw):
            rid=r.get('Id')
            if rid in ids:issues.append({'kind':'duplicate_relationship_id','owner':o,'id':rid})
            ids.add(rid)
            if r.get('TargetMode')!='External'and resolve(o,r.get('Target',''))not in parts:issues.append({'kind':'missing_target','owner':o,'target':r.get('Target')})
    return issues
def import_parts(parts,incoming):
    mapping={}
    for path in incoming:
        if not path.startswith('ppt/')or path in (PRES,relpart(PRES))or path.endswith('.rels'):continue
        directory,name=pp.split(path);i=1;new=pp.join(directory,'case_'+name)
        while new in parts or new in mapping.values():i+=1;new=pp.join(directory,f'case{i}_'+name)
        mapping[path]=new
    for old,new in mapping.items():
        parts[new]=incoming[old]
        if relpart(old)not in incoming:continue
        rr=rels(incoming,old)
        for r in rr:
            if r.get('TargetMode')=='External':continue
            t=r.get('Target');dest=resolve(old,t)
            if dest!=PRES and dest not in mapping:raise ValueError(('Unmapped imported dependency',old,dest))
            mapped=PRES if dest==PRES else mapping[dest]
            fragment='#'+t.split('#',1)[1]if '#'in t else ''
            r.set('Target',pp.relpath(mapped,pp.dirname(new))+fragment)
        parts[relpart(new)]=dump(rr)
    ct=xml(parts['[Content_Types].xml']);gct=xml(incoming['[Content_Types].xml'])
    defaults={e.get('Extension'):e.get('ContentType')for e in ct.findall('ct:Default',NS)}
    gd={e.get('Extension'):e.get('ContentType')for e in gct.findall('ct:Default',NS)}
    overrides={e.get('PartName').lstrip('/'):e.get('ContentType')for e in gct.findall('ct:Override',NS)}
    for ext,typ in gd.items():
        if ext not in defaults:E.SubElement(ct,'{'+CT+'}Default',Extension=ext,ContentType=typ);defaults[ext]=typ
    for old,new in mapping.items():
        ext=old.rsplit('.',1)[-1];typ=overrides.get(old,gd.get(ext))
        if not typ:raise ValueError(('Missing imported content type',old))
        if old in overrides or defaults.get(ext)!=typ:E.SubElement(ct,'{'+CT+'}Override',PartName='/'+new,ContentType=typ)
    parts['[Content_Types].xml']=dump(ct)
    return mapping
def register_presentation_dependencies(parts,incoming,mapping):
    root=xml(parts[PRES]);gen=xml(incoming[PRES]);rr=rels(parts,PRES);gr={r.get('Id'):r for r in rels(incoming,PRES)}
    for tag in ('sldMasterIdLst','notesMasterIdLst','embeddedFontLst'):
        inc=gen.find('p:'+tag,NS)
        if inc is None:continue
        dest=root.find('p:'+tag,NS)
        if dest is None:
            dest=E.Element('{'+P+'}'+tag)
            # Presentation child order follows CT_Presentation.
            order=['sldMasterIdLst','notesMasterIdLst','handoutMasterIdLst','sldIdLst','sldSz','notesSz','smartTags','embeddedFontLst','custShowLst','photoAlbum','custDataLst','kinsoku','defaultTextStyle','modifyVerifier','extLst']
            before=next((e for e in root if E.QName(e).localname in order and order.index(E.QName(e).localname)>order.index(tag)),None)
            root.insert(root.index(before)if before is not None else len(root),dest)
        used={int(e.get('id'))for e in dest if e.get('id')}
        for item in inc:
            copy=deepcopy(item)
            for node in copy.iter():
                rid=node.get('{'+R+'}id')
                if rid:
                    rel=gr[rid];target=mapping[resolve(PRES,rel.get('Target'))]
                    node.set('{'+R+'}id',add_rel(rr,PRES,target,rel.get('Type')))
            if copy.get('id'):
                n=max(used|{2147483647})+1;copy.set('id',str(n));used.add(n)
            dest.append(copy)
    # Table styles are presentation-wide, unlike per-slide layouts and themes.
    gstyle=next((resolve(PRES,r.get('Target'))for r in gr.values()if r.get('Type')==R+'/tableStyles'),None)
    if gstyle:
        target=next((resolve(PRES,r.get('Target'))for r in rr if r.get('Type')==R+'/tableStyles'),None)
        if target is None:add_rel(rr,PRES,mapping[gstyle],R+'/tableStyles')
        else:
            existing=xml(parts[target]);inc=xml(incoming[gstyle]);known={s.get('styleId'):s for s in existing};changed=False
            for style in inc:
                ident=style.get('styleId')
                if ident in known:
                    if E.tostring(known[ident],method='c14n')!=E.tostring(style,method='c14n'):raise ValueError(('Conflicting table style IDs require task-specific remapping',ident))
                else:existing.append(deepcopy(style));changed=True
            if changed:parts[target]=dump(existing)
    parts[PRES]=dump(root);parts[relpart(PRES)]=dump(rr)
def prune(parts):
    seen={'[Content_Types].xml'};queue=['']
    while queue:
        o=queue.pop();rp=relpart(o)
        if rp not in parts:continue
        seen.add(rp)
        for r in xml(parts[rp]):
            if r.get('TargetMode')=='External':continue
            target=resolve(o,r.get('Target'))
            if target not in parts:raise ValueError(('Broken relationship',o,target))
            if target not in seen:seen.add(target);queue.append(target)
    removed=set(parts)-seen
    for p in removed:del parts[p]
    ct=xml(parts['[Content_Types].xml'])
    for e in list(ct):
        if e.get('PartName')and e.get('PartName').lstrip('/')not in parts:ct.remove(e)
    parts['[Content_Types].xml']=dump(ct)
    return sorted(removed)
def canonicalize(parts,slide_paths):
    mapping={p:f'ppt/slides/slide{i}.xml'for i,p in enumerate(slide_paths,1)}
    mapping.update({relpart(p):relpart(n)for p,n in list(mapping.items())if relpart(p)in parts})
    names=[mapping.get(p,p)for p in parts]
    if len(names)!=len(set(names)):raise ValueError('Part collision during canonical slide numbering')
    out={}
    for old,raw in parts.items():
        new=mapping.get(old,old)
        if old.endswith('.rels'):
            oo,no=owner(old),owner(new);rr=xml(raw);changed=False
            for r in rr:
                if r.get('TargetMode')=='External':continue
                t=r.get('Target');dest=resolve(oo,t);nd=mapping.get(dest,dest)
                if nd!=dest or oo!=no:
                    frag='#'+t.split('#',1)[1]if '#'in t else ''
                    r.set('Target',pp.relpath(nd,pp.dirname(no)or'.')+frag);changed=True
            if changed:raw=dump(rr)
        out[new]=raw
    ct=xml(out['[Content_Types].xml'])
    for e in ct:
        n=e.get('PartName','').lstrip('/')
        if n in mapping:e.set('PartName','/'+mapping[n])
    out['[Content_Types].xml']=dump(ct)
    return out,mapping
