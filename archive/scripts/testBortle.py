import requests

def get_lat_lon(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json"}
    r = requests.get(url, params=params)
    data = r.json()
    return float(data[0]["lat"]), float(data[0]["lon"])


def get_light_pollution(lat, lon):
    # Example VIIRS query (you may need proper dataset access)
    url = f"https://www.lightpollutionmap.info/QueryRaster/?ql=wa_2015&qt=point&lat={lat}&lon={lon}"
    r = requests.get(url)
    return r.json()


#lat, lon = get_lat_lon("Utah")
data = get_light_pollution(40, 0)

print(data)
