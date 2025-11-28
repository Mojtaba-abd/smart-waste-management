import firebase_admin
from firebase_admin import credentials, db
import random
import time

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app/"
    },
)
db.reference("bins").delete()

baghdad_bins = []

# Area 1 (e.g., Karrada / central-east)
for i in range(1, 11):
    baghdad_bins.append(
        {
            "id": f"bin{i}",
            "lat": round(random.uniform(33.350, 33.370), 6),
            "lon": round(random.uniform(44.360, 44.380), 6),
        }
    )

# Area 2 (e.g., Al-Rusafa / central-west)
for i in range(11, 21):
    baghdad_bins.append(
        {
            "id": f"bin{i}",
            "lat": round(random.uniform(33.310, 33.330), 6),
            "lon": round(random.uniform(44.360, 44.380), 6),
        }
    )

# Area 3 (e.g., Dora / south)
for i in range(21, 31):
    baghdad_bins.append(
        {
            "id": f"bin{i}",
            "lat": round(random.uniform(33.280, 33.300), 6),
            "lon": round(random.uniform(44.350, 44.370), 6),
        }
    )
while True:
    for bin in baghdad_bins:
        fill_level = random.randint(0, 100)
        bin_data = {
            "fill_level": fill_level,
            "latitude": bin["lat"],
            "longitude": bin["lon"],
            "timestamp": int(time.time()),
        }
        db.reference(f'bins/{bin["id"]}').set(bin_data)
        print(f'Updated {bin["id"]} with fill level {fill_level}%')
    time.sleep(10)
