import json
import os
import sys
import mlflow
from routers.ai import look

path = sys.argv[1] if len(sys.argv)>1 else 'data/test.jsonl'

mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_experiment('vlm-eval')

rows = [json.load(l) for l in open(path)]
out = [(look(r['image']), r['answer']) for r in rows]
n = len(rows)
with mlflow.start_run(run_name = os.environ["VLM_MODEL"] + ' ' + os.path.basename(path)):
    mlflow.log_params({"vlm_model":os.environ["VLM_MODEL"],"test_file":path})
    mlflow.log_metric('product_acc', sum(p['product_id'] == a['product_id'] for p, a in out) / n)
    mlflow.log_metric('defect_acc', sum(p["defect"]==a["defect"] for p,a in out)/n )
    mlflow.log_metric('unknown_rate', sum(p['product_id'] == 'unknown' for p, _ in out) / n)