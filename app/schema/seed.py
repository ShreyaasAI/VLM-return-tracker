
import glob, random, time, requests
COMPLAINTS = ['too small', 'torn at seam', 'stain on front', 'zip broke', 'color faded after wash']
files = glob.glob('data/test/*.jpg')
for f in random.sample(files, min(100, len(files))):  # random: sorted order would be one category only
    r = requests.post('http://localhost:8000/returns',
        data=dict(customer_id='c' + str(random.randint(1, 30)), complaint=random.choice(COMPLAINTS),
                  days_since_purchase=random.randint(1, 40), price=random.choice([499, 999, 1999, 2999])),
        files={'image': open(f, 'rb')})
    print(r.status_code, f)
    time.sleep(5) 