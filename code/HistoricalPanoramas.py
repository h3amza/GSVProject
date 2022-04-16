"""
Module uses a stored panorama to find IDs and date of older panoramas using Google
Maps website. At the moment the API does not have functionality to fetch older
panoramas for a location and this is the only way to do it.

For each panorama stored for a region, go to Google Maps in Street View mode. Then
click the timemachine button, if present, then use JS script to fetch the total
number of historical panoramas. Iterate through them one by one and fetch the
date and panorama ID for those panoramas.

TODO: Pipeline to server to join with relevant panoramas.
TODO: Incorporate within Panorama class as set of functions.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import JavascriptException
import time
import pandas as pd


# Selenium driver connection
options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome('../miscellaneous/chromedriver',options=options)


def fetch_panorama(panoID,lat,lng):
    """
    Fetch the ID and date of old panoramas given the location of a current panorama.

    This works by first finding X number of buttons for X historical panoramas. Then
    find the list view object in the site that holds the buttons for historical panoramas
    and click on them one by one. fetch_info is called for each index of historical
    panorama.

    Parameter panoID: ID of latest panorama for location
    Parameters lat,lng: Location of panorama
    """

    # go to street view link for current panorama
    link = "https://www.google.com/maps?q="+str(lat)+","+str(lng)+"&layer=c&cbll="+str(lat)+","+str(lng)+"&cbp=11,90,0,0,0"
    driver.get(link)
    time.sleep(5) # give time to load completely
    try: # click on timeline button on site if exists
        driver.execute_script('document.getElementsByClassName("b4tYeb-icon noprint")[0].click()')
    except JavascriptException:
        print("no older panos") # some locations do not have old panoramas
        return

    # execute JS code in browser to fetch count of buttons for historical panoramas
    js_code = "var x = document.getElementsByClassName('T6Hn3d')[0].childNodes[7].getElementsByTagName('li');"
    js_code+="return x.length"
    pano_count = driver.execute_script(js_code)

    for index in range(pano_count):
        info = fetch_info(index) # fetch information for each old panorama
        print(panoID,lat,lng,info[0],info[1])


def fetch_info(index):
    """
    Fetch the ID and date of an old panorama given an index value.

    Click on panorama button then click on window to load the panorama. Then store
    the date and ID of panorama from JS objects.

    Parameter index: which button in list to press to fetch current historical panorama.
    """

    js_code="var x = document.getElementsByClassName('T6Hn3d')[0].childNodes[7].getElementsByTagName('li');"
    js_code+="x["+str(index)+"].getElementsByClassName('NKAWqe')[0].click()" # click on button
    driver.execute_script(js_code)
    time.sleep(1)
    driver.execute_script("document.getElementsByClassName('eWNdlf-AHe6Kc-JUCs7e')[0].click()") # expand panorama
    time.sleep(2)

    # now date and panorama ID of historical panorama should be stored
    date = driver.find_elements_by_class_name("kXDede")[1].get_attribute("innerText")
    date = date.replace("Currently shown: ","")
    src = driver.find_elements_by_class_name("eWNdlf-AHe6Kc-JUCs7e")[0].get_attribute("src")
    src = src[src.index("panoid")+7:-7]
    return(date,src)


# read points file and only select important attributes into rows list
columns = ['region', 'streetID', 'lat','lng','direction','panoID','pano_date','pano_lat','pano_lng']
df = pd.read_csv("../data/DowntownLA-points.csv",header=None,names=columns)
rows = list(zip(df.panoID,df.pano_lat,df.pano_lng,df.pano_date,df.direction))

# testing on just the first row
fetch_panorama(rows[0][0],rows[0][1],rows[0][2])

driver.close()
