import pandas as pd
import requests
import streamlit as st

API = 'http://localhost:8000'
st.title('Returns')
df = pd.DataFrame(requests.get(API+"/returns").json())
t1,t2,t3 = st.tabs(["Most Returned", "Review Queue", "Submit Test"])

with t1:
    if df.empty:
        st.info("No Returns yet")
    else:
        st.bar_chart(df.product_id.value_counts())
        st.bar_chart(df.defect.value_counts())
        p = st.selectbox("Product",['all']+sorted(df.product_id.unique()))
        d=df if p=='all' else df[df.product_id ==p]
        st.dataframe(d[['created','product_id','defect','severity','complaint','route','status']])

with t2:
    if not df.empty:
        for r in df[(df.route=='human')&(df.status=='new')].to_dict('records'):
            st.image(r['image_path'], width=200)
            st.write(r['product_id'],r['defect'],'|', r['complaint'],'|',r['reason'])
            a,b = st.columns(2)
            for col, s in (a,'approved'),(b,'rejected'):
                if col.button(s,key=s+ str(r['id'])):
                    requests.post(API + "/returns/" +str(r['id']) +"/resolve", params={"status": s})
                    st.rerun()

    else:
        st.write("NO rreturns")
with t3:
    f = st.file_uploader('Photo', type=['jpg', 'jpeg', 'png'])
    cust = st.text_input('Customer id', 'c1')
    comp = st.text_input('Complaint')
    days = st.number_input('Days since purchase', 0, 365, 5)
    price = st.number_input('Price', 0.0, 100000.0, 999.0)
    if f and st.button('Submit'):
        r = requests.post(API + '/returns', data=dict(customer_id=cust, complaint=comp, days_since_purchase=days, price=price),
                          files={'image': (f.name, f.getvalue(), f.type)})
        
        st.json(r.json())
        st.write("Hello")
