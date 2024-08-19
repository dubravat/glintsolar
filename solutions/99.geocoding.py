"""
Was the initial idea to geocode by the "Property Address" field
"""

# imports
import requests
from requests.utils import requote_uri
from os.path import normpath, join, isfile

# file locations
PROJECT_DIR = normpath("D:/glintsolar/")
path_to_txt = join(PROJECT_DIR, "solutions/OS_DATA_HUB_API_KEY.txt")

if isfile(path_to_txt):
    file = open(file=path_to_txt, mode='r', encoding='utf-8')
    apiKey = str(file.read())


def os_places_geocoder(address: str = None) -> tuple or None:
    """
    Getting coordinates of addresses in the UK
    https://osdatahub.os.uk/docs/places/technicalSpecification
    :param address:
    :return:
    """
    global apiKey
    try:
        query = requote_uri(address)
    except Exception:
        query = ""
    maxresults = 1
    lr = 'EN'
    fq = 'COUNTRY_CODE:E'
    url = f"https://api.os.uk/search/places/v1/find?query={query}&maxresults={maxresults}&lr={lr}&fq={fq}&key={apiKey}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json().get("results")[0]
            dpa = result.get("DPA", None)
            if dpa:
                x = dpa.get("X_COORDINATE")
                y = dpa.get("Y_COORDINATE")
                return x, y
    except requests.exceptions.RequestException:
        return None


print(os_places_geocoder(""))
