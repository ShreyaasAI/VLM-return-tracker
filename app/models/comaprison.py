from risk import *
import mlflow
import mlflow.sklearn
from app.schema.db import con

from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
def compare():
    
    col = F+C
    row = con.execute("SELECT"+",".join(col)+", status FROM returns WHERE status IN ('approved','rejected')").fetchall()
    if not row:
        print("No data risk/compare")
        return 
    df =pd.DataFrame(row, columns=col+['status'])
    y =(df.status=='rejected').astype(int)
    if len(df)<40 or y.nunique()<2:
        raise SystemExit("Need 40+ human approved rows with both approved and rejected. Use the review queue")
    x_tr, x_tes, y_tr, y_tes = train_test_split(df[col],y,stratify=y, test_size=0.3, random_state=0)
    mlflow.set_tracking_uri("sqlite://mlflow.db")
    mlflow.set_experiment("return-risk")
    best = (-1,None,None)
    for name in MODELS: 
        with mlflow.start_run(run_name=name):
            build = pipe(name)
            supervised = hasattr(build,'predict_proba')            
            if supervised:
                build.fit(x_tr,y_tr)
            else:
                build.fit(x_tr[y_tr==0])

        auc = roc_auc_score(y_tes, risk_score(build, x_tes))       
        acc = accuracy_score(y_tes, build.predict(x_tes)) 
        f1 = f1_score(y_tes, build.predict(x_tes))     
        mlflow.log_params(({'model': name, 'supervised': supervised, 'train_rows': len(x_tr), 'cats': ','.join(C) or 'none'}))
        mlflow.log_metrics({'auc': auc, 'accuracy': acc, 'f1_score': f1})
        mlflow.sklearn.log_model(build, "model")
        if auc > best[0]:
            best = (auc, name, build)
    auc,name,build = best
    thr = float(np.quantile(risk_score(build, x_tr),0.9))
    joblib.dump({'pipe':build, 'risky_threshold':thr},"risk_model.joblib") 
    print("best model:",name, "auc", round(auc,3), "threshold",(thr,3))


if __name__ =='__main__':
    compare()
        