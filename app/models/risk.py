from attr import has
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import RandomForestClassifier, IsolationForest, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import OneClassSVM


F = ["days_since_purchase","price","customer_return"]
C = ["defect", "severity"]
MODELS  = {
    "isolation_forest": lambda:IsolationForest(random_state=0),
    "lof": lambda:LocalOutlierFactor(novelty=True),
    "one_class_svm": lambda: OneClassSVM(nu=0.1),
    "elliptic":lambda:EllipticEnvelope(random_state=0),
    "lr": lambda:LogisticRegression(max_iter=1000, penalty='l1',class_weight='balanced'),
    "rf": lambda:RandomForestClassifier(n_estimators=200, class_weight='balanced',random_state=0),
    "gboost": lambda:GradientBoostingClassifier(n_estimators=200,learning_rate=0.2, random_state=0)
}

def pipe(name):
    pre = ColumnTransformer([('num',StandardScaler(),F), ('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),C)])
    return Pipeline([('preprocess',pre),('model',MODELS[name()])])

def risk_score(pipe,x):
    if hasattr(pipe,'predict_proba'):
        return pipe.predict_proba(x)[:,1]
    return -pipe.score_samples(x)

