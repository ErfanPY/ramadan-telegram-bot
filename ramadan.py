import json
import requests
import datetime
import time
import pytz
import logging
from enum import Enum

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_now(timezone):
    TEH = pytz.timezone(timezone)
    now = datetime.datetime.now(TEH)
    now_text = str(now).split(' ')[-1].split('.')[0]
    
    return now_text

def delta(time1, time2, fix_hour):
    h1, m1, s1 = [int(i) for i in time1.split(":")]
    h2, m2, s2 = [int(i) for i in time2.split(":")]
    h, m, s = h2-h1, m2-m1, s2-s1
    
    if s < 0:
        s += 60
        m -= 1

    if m < 0:
        m += 60
        h -= 1

    if fix_hour and h < 0:
        h += 24

    return (h, m, s)


def calculate_reminder(city, do_next_day=False):
    azan, timezone = get_pray_zone_azan(city, do_next_day)
    
    if azan is None:
        return None, None, None

    azan += ":00"
    now  = get_now(timezone)
    
    rH, rM, rS = delta(now, azan, do_next_day)

    logging.debug(f"Now: {now} Azan is: {azan} >> {rH}:{rM}:{rS}")

    if rH < 0:
        # rH, rM, rS = calculate_reminder(city, True)
        rH += 24
    return rH, rM, rS

def get_pray_zone_azan(city_addr, do_next_day=None):

    lat_lng = get_lat_lng(city_addr)
    if lat_lng is None:
        return None, None

    azan_url = "https://api.pray.zone/v2/times/"
    
    if do_next_day:
        azan_url += "tomorrow.json"
    else:
        azan_url += "today.json"

    try:
        azan_resp = requests.get(azan_url, params={"latitude":lat_lng['lat'], "longitude":lat_lng['lng'], "elevation":"333", "school":7})
    except Exception as e:
        logging.error(f"Gettign prayer time Errored, {e}")
        return None, None
    azan_json = json.loads(azan_resp.content)

    if not azan_json['code'] == 200:
        logging.error("Gettign prayer time failed Not 200")
        return None, None

    Maghrib  = azan_json['results']['datetime'][0]['times']['Maghrib']
    timezone = azan_json['results']['location']['timezone']

    return Maghrib, timezone

def get_lat_lng(city_addr):
    key2 = "b6458d76cfc1440d827d43d9b9a5b2a0"
    url2 = "https://api.opencagedata.com/geocode/v1/json"

    try:
        location_resp = requests.get(url2, params={"q":city_addr, "key":key2})
    except Exception as e:
        logging.error(f"Getting city failed, {e}")
        return None

    json_data = json.loads(location_resp.content)
    # city = json_data['results'][0]['formatted']
    lat_lng = json_data['results'][0]['geometry']
    return lat_lng

    # key = "66752dc70ec2e4e9151abea6f6592233"
    # location_url = "http://api.positionstack.com/v1/forward"

    # try:
    #     location_resp = requests.get(location_url, params={"access_key":key, "query":city_addr})
    # except Exception as e:
    #     logging.error(f"Getting city failed, {e}")
    #     return None
    
    # location_json = json.loads(location_resp.content)
    # city = location_json['data'][0]['name']


if __name__ == "__main__":
    city = "بیرجند"
    print(calculate_reminder(city))
