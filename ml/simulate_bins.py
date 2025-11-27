import firebase_admin 
from firebase_admin import credentials,db 
import random
import time

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL': 'https://smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app/'})

bins = [
    {'id': 'bin_1', 'lat': 40.712776, 'lon': -74.005974},
    {'id': 'bin_2', 'lat': 34.052235, 'lon': -118.243683},
    {'id': 'bin_3', 'lat': 51.507351, 'lon': -0.127758},
    {'id': 'bin_4', 'lat': 48.856613, 'lon': 2.352222},
    {'id': 'bin_5', 'lat': 35.689487, 'lon': 139.691711},
    {'id': 'bin_6', 'lat': -33.868820, 'lon': 151.209290},
    {'id': 'bin_7', 'lat': 55.755825, 'lon': 37.617298},
    {'id': 'bin_8', 'lat': 52.520008, 'lon': 13.404954},
    {'id': 'bin_9', 'lat': 41.902782, 'lon': 12.496366},
    {'id': 'bin_10', 'lat': 19.432608, 'lon': -99.133209}
]

while True:
    for bin in bins:
        fill_level = random.randint(0, 100)
        bin_data = {
            'fill_level': fill_level,
            'latitude': bin['lat'],
            'longitude': bin['lon'],
            'timestamp': int(time.time())

        }
        db.reference(f'bins/{bin["id"]}').set(bin_data)
        print(f'Updated {bin["id"]} with fill level {fill_level}%')
    time.sleep(10)