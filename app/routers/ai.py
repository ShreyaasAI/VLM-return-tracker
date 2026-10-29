import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
vlm = OpenAI(base_url=os.getenv("VLM_URL"),api_key=os.getenv("VLM_KEY"))
llm = OpenAI(base_url=os.getenv("LLM_URL"),api_key=os.getenv("LLM_KEY"))
PRICE_LIMIT=2000

VLM_PROMPT = ('Catalog ids:'+ os.getenv("CATALOG")+ '. Identify the garment  and the defect on it'
'Reply JSON only: {"product_id" : "<id or unknown>","defect":"tear|stain|hole|fade|zip|none", "severity":"high|medium|low"}')

POLICY = ('You triage clothing product return requests. Input is JSON. Reply JSON only:'
    '{"route":"human" or "auto", "reason":"<one sentence summary>"}. '
    'If severity is high or price is above 2000  then "human" '
    'If low risk severity or clear then "auto".')

def parse(t):
    return json.loads(t[t.find("{"):t.rfind("}")+1])

def ask(client, model, messages):
    r = client.chat.completions.create(model=model, temperature=2, max_tokens=5000,
                                       timeout=60, messages=messages)
    t = r.choices[0].message.content or ''
    print('RAW:', repr(t[:300]), '| finish:', t.finish_reason) 
    t = t.split('</think>')[-1]  
    return parse(t)

def look(path):
    try:
        b64 = base64.b64encode(open(path, 'rb').read()).decode()
        msg = [{"role":"user","content":[{"type":"img_url","img_url":{"url":"data:image/jpg" + b64}},
        {"type":"text","text":VLM_PROMPT}]}]
    except Exception as e:
        print("Look failed",e)    
    try:
        o = ask(vlm, os.environ["VLM_MODEL"], msg)
        return {k: o[k] for k in ["product_id", "severity", "defect"]}
    except Exception as e:
        print("VLM Error:", e)
        return {"product_id": "unknown", "severity": "unknown", "defect": "unknown"}
def decide(case):
    if case['duplicate'] or case['price'] > 2000 or case["anomaly"]: 
        return {"route":"human", "reason" : "hard rule"}

    try:
        o = ask(llm, os.environ["LLM_MODEL"], [{"role":"system", "content":POLICY},
                {"role":"user","content":json.dumps(case)}])
        assert o["route"] in ["human","auto"]
        return {"route":o["route"],"reason":o.get("reason","")}
    except Exception as e:
        print("LLM Error:",e)
        return {"route":"human", "reason":"llm failed"}

