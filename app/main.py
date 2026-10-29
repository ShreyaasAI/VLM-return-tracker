import hashlib, joblib, os, uuid
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from psycopg.rows import dict_row
from routers.ai import decide, look
from models.risk import C, F, risk_score
from schema.db import con

app = FastAPI()
os.makedirs('uploads', exist_ok=True)
MODEL = joblib.load('risk_model.joblib') if os.path.exists('risk_model.joblib') else None

def anomaly(row):
    if MODEL is None:
        return 0  # shortcut: no trained model yet, run risk.py
    return int(risk_score(MODEL['pipe'], pd.DataFrame([row])[F + C])[0] > MODEL['thr'])

@app.post('/returns')
async def create(customer_id: str = Form(...), complaint: str = Form(...),
                 days_since_purchase: int = Form(...), price: float = Form(...),
                 image: UploadFile = File(...)):
    data = await image.read()
    if not (image.content_type or '').startswith('image/') or len(data) > 5_000_000:
        raise HTTPException(400, 'image only, max 5MB')
    h = hashlib.sha256(data).hexdigest()
    path = 'uploads/' + uuid.uuid4().hex + '.jpg'
    open(path, 'wb').write(data)
    dup = con.execute('SELECT 1 FROM returns WHERE image_hash=%s', (h,)).fetchone()
    n = con.execute('SELECT COUNT(*) FROM returns WHERE customer_id=%s', (customer_id,)).fetchone()[0]
    row = dict(days_since_purchase=days_since_purchase, price=price, customer_returns=n)
    v = look(path)
    case = dict(**row, complaints=complaint, **v, anomaly=anomaly({**row, **v}), duplicate=int(dup is not None))
    d = decide(case)
    rec = dict(**case, customer_id=customer_id, image_path=path, image_hash=h, **d,
               status='new' if d['route'] == 'human' else 'auto_approved')
    con.execute('INSERT INTO returns(' + ','.join(rec) + ') VALUES(' + ','.join(['%s'] * len(rec)) + ')', list(rec.values()))
    return rec

@app.get('/returns')
def list_returns():
    with con.cursor(row_factory=dict_row) as c:
        return c.execute('SELECT * FROM returns ORDER BY id DESC').fetchall()

@app.post('/returns/{rid}/resolve')
def resolve(rid: int, status: str):
    if status not in ('approved', 'rejected'):
        raise HTTPException(400, 'bad status')
    con.execute('UPDATE returns SET status=%s WHERE id=%s', (status, rid))
    return {'ok': True}