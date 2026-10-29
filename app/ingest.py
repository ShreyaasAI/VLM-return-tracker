import json 
import random
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
random.seed(0)
CLOTHES = Path('../catalogs/clothes')
FABRICS = Path('../catalogs/fabrics/fabrics')
DEFECT_MAP = {"defect free":"none","horizontal":"tear","hole":"hole","lines":"lining","stain":"stain","vertical":"tear"}
SCALES = {"low":0.07, "med": 0.15, "high":0.22}
EXT = {".jpg", ".png",".jpeg", ".webp"}

def images(folder):
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in EXT)



def load(p,max_side=768):
    im = Image.open(p).convert('RGB')
    im.thumbnail(size=(max_side,max_side))
    return im

def split(files,test_fact=0.25):
    files = files[:]; random.shuffle(files)
    k= max(1,int(len(files)*test_fact))
    return files[k:], files[:k] #train , test

    
def composite(garment,fabric,scale):
    g = garment.copy()
    w,h = g.size
    s = int(w*scale)
    mask = Image.new('L', (s,s),0)
    ImageDraw.Draw(mask).ellipse([0, 0, s, s], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(s//8))

    x = random.randint(w//4, max(w//4, 3*w//4-s))
    y = random.randint(h//4, max(h//4, 3*h//4-s))
    g.paste(fabric.resize((s,s)), (x,y), mask)
    return g
clothes = {c.name.lower():split(images(c)) for c in sorted(CLOTHES.iterdir()) if c.is_dir() }
fabrics ={}
for f in sorted(FABRICS.iterdir()):
    if f.is_dir():
        key = f.name.lower()
        if key not in DEFECT_MAP:
            raise SystemExit("Fabric folder is unknown"+f.name+"-> add it to DEFECT MAP")
        fabrics[key]=split(images(f))

def build(part, n_comp):  # part 0 = train, 1 = test
    name = ('train', 'test')[part]
    out = Path('data') / name
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for cat, parts in clothes.items():
        for i, p in enumerate(parts[part]):
            g = load(p)
            variants = [(g, 'none', 'low')]  # clean garment
            for _ in range(n_comp):
                key = random.choice(list(fabrics))
                sev = random.choice(list(SCALES))
                im = composite(g, load(random.choice(fabrics[key][part])), SCALES[sev] * random.uniform(0.8, 1.2))
                d = DEFECT_MAP[key]
                variants.append((im, d, 'low' if d == 'none' else sev))
            for j, (im, d, sev) in enumerate(variants):
                f = out / (cat + '_' + str(i) + '_' + str(j) + '.jpg')
                im.save(f, quality=90)
                rows.append({'image': str(f), 'answer': {'product_id': cat, 'defect': d, 'severity': sev}})
    random.shuffle(rows)
    with open('data/' + name + '.jsonl', 'w') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    return len(rows)

print('train rows', build(0, 1), '| test rows', build(1, 1))
print('CATALOG=' + ','.join(clothes))  # paste into your env



        