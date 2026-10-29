import os, psycopg
con = psycopg.connect(os.environ['DATABASE_URL'], autocommit=True)
con.execute('''CREATE TABLE IF NOT EXISTS returns(
  id SERIAL PRIMARY KEY, created TIMESTAMPTZ DEFAULT now(),
  customer_id TEXT, complaint TEXT, image_path TEXT, image_hash TEXT,
  product_id TEXT, defect TEXT, severity TEXT,
  days_since_purchase INT, price REAL, customer_returns INT,
  anomaly INT, duplicate INT, route TEXT, reason TEXT, status TEXT)''')