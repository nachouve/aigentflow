import json
import requests

CITY = "Santiago de Compostela"
URL2 = f"http://api.openweathermap.org/geo/1.0/direct?q='Santiago de Compostela'&limit=3&appid={API_KEY}"
response = requests.get(URL2)

resp_json = json.loads(response.text)
# TODO Extract the latitude and longitude from the response
# pprint(kk[0])
# {'country': 'ES',
#  'lat': 42.8827376,
#  'lon': -8.538168217203808,
#  'name': 'Santiago de Compostela',
#  'state': 'Galicia'}

URL = f"http://api.openweathermap.org/data/2.5/forecast?lat=42.88273&lon=-8.538168217203808&appid={API_KEY}&units=metric"
response = requests.get(URL)
response.text
resp_json = json.loads(response.text)

for item in resp_json.get("list"):
    #print(item)
    print(item.get("dt_txt", ""), item.get("weather",[])[0].get("description"), item.get("main", "").get("temp") )
    if 'rain' in str(item):
        print(f"\t RAIN: {item.get('rain', []).get('3h', 'ERROR')} mm")
        #pprint(item)
        #break