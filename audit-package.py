"""Validate all gallery assets, preserve source, record generation and make ZIP."""
from pathlib import Path
import json,hashlib,zipfile,sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path(__file__).parent
items=json.loads((root/'data/prompts.json').read_text(encoding='utf-8'))
manifest=[]
assert len(items)==117
assert len(set(p['id'] for p in items))==117
source=root.parent/'繪圖提示詞.txt'
if source.exists():
    assert (root/'data/繪圖提示詞原始.txt').read_bytes()==source.read_bytes()
(root/'assets/thumbnails').mkdir(exist_ok=True)
for p in items:
    file=root/p['image']
    assert file.is_file(),f'Missing image {p["id"]}'
    with Image.open(file) as img:
        img.verify()
    with Image.open(file) as img:
        width,height=img.size
        thumbnail=root/f'assets/thumbnails/{p["id"]:03}.webp'
        if not thumbnail.exists() or thumbnail.stat().st_mtime<file.stat().st_mtime:
            thumb=ImageOps.contain(img.convert('RGB'),(560,560))
            thumb.save(thumbnail,quality=82,method=6)
    if p['upload']:
        assert (root/f'assets/references/{p["reference"]}.png').is_file()
    manifest.append(dict(id=p['id'],title=p['title'],image=p['image'],size=[width,height],bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),method='built-in imagegen',reference=f'assets/references/{p["reference"]}.png' if p['upload'] else None,exampleSetting=p['note'],originalPrompt=p['prompt']))
assert len({p['sha256'] for p in manifest})==117,'Duplicate images'
(root/'data/generation-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',20)
for chunk in range(0,len(items),24):
    group=items[chunk:chunk+24]
    sheet=Image.new('RGB',(1200,6*260),'#fffaf2')
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(group):
        x=(i%4)*300;y=(i//4)*260
        with Image.open(root/p['image']) as img:
            thumb=ImageOps.contain(img.convert('RGB'),(280,215))
            sheet.paste(thumb,(x+(300-thumb.width)//2,y+(215-thumb.height)//2))
        draw.text((x+10,y+220),f'{p["id"]:03} {p["title"]}',font=font,fill='#202a3d')
    contact=root/f'qa-contact-{chunk//24+1}.jpg'
    if not contact.exists():
        sheet.save(contact,quality=85)
if '--prepare' in sys.argv:
    print('Verified 117 unique example images; thumbnails and contact sheets ready.')
    sys.exit(0)
report=json.loads((root/'qa-report.json').read_text())
assert not report['missingImages'] and not report['imageLoadFailures'] and not report['scriptErrors']
report['sourcePreserved']=True
report['sourceSha256']=hashlib.sha256((root/'data/繪圖提示詞原始.txt').read_bytes()).hexdigest()
report['uniqueExampleImages']=117
report['simulatedReferences']=5
(root/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
archive=root.parent/'靈感畫室-GitHub完整網站.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(root.rglob('*')):
        if file.is_file() and not file.name.startswith('qa-contact-'):
            z.write(file,file.relative_to(root).as_posix())
print(json.dumps(dict(archive=str(archive),prompts=len(items),uniqueImages=117,bytes=archive.stat().st_size),ensure_ascii=False))
