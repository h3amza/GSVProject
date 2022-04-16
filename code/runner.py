"""
Module executes the point generation process for a region.

Given a region name and center coordinates, the code will fetch all panorama
related info for all points 15 meters apart that are within a mile radius of
the region center.

After generating a CSV file with panorama info, the program will then download
images for each unique panorama of the left and right side of the street.
"""


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Region import *
from Panorama import *

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
#options.add_argument("--headless") # run in background
driver = webdriver.Chrome('../miscellaneous/chromedriver')

# define region and run all functions
region = Region("DowntownLA",34.041842, -118.244583)
region.level_routes()
region.get_routes(driver)
region.get_segments()
region.populate_routes()
region.write_region()
driver.close()


# open newly generated file for region
with open("../data/DowntownLA-points.csv","r") as file:
    data = file.readlines()
data = [i.split(",") for i in data]

# for each panorama point, create panorama object and download 2 images for it
for point in data:
    #Panorama(region,panoIS,date,lat,lng,direction)
    p = Panorama(point[0],point[5],point[6],point[7],point[8],point[4])
    p.download()
