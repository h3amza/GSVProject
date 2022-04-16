"""
Module defines the Point class. A point is a spatial coordinate with a StreetView API
panorama information attached to it.

The direction attribute of a point object ensures that when metadata is collected
for a panorama, it is when you are looking precisely to your left or right at a 90
degree angle from your direction. Direction attribute will offset if street is at
an angle for a point.
"""
import urllib, os, json
import urllib.request
import time

key = "&key=" + "XXXX"

class Point():
    """
    A class representing a spatial coordinate point.

    Attribute ID: UID for each point.

    Attribute region: Name of region point belongs to.

    Attribute streetID: UID for street point belongs to.

    Attribute lat,lng: Coordinates of point.

    Attribute direction: bearing from end point A to B of street of point.

    Attribute panoramaID: UID for panorama from API.

    Attribute panorama_date: Date panorama for this point was recorded.

    Attribute panorama_lat,panorama_lng: Precise coordinates of panorama stored
    for this point location.
    """

    def __init__(self,ID,region,streetID,lat,lng,direction):
        """
        Initialize Street object with information coming from point's street.

        Parameter ID: UID for point
        Parameter streetID: UID for point's street
        Parameters lat,lng: coordinates for point
        Parameter direction: direction of street in degrees
        """
        self.ID = ID
        self.region = region
        self.streetID = streetID
        self.lat = lat
        self.lng = lng
        self.direction = direction
        self.panoramaID = 0
        self.panorama_date = 0
        self.panorama_lat = 0
        self.panorama_lng = 0
        self.populatePanoramaInfo()

    def strForm(self):
        """
        Write object as comma separated attributes.
        """
        return str(self.region)+","+str(self.streetID)+","+str(self.lat)+","+str(self.lng)+ \
        ","+str(self.direction)+","+str(self.panoramaID)+","+str(self.panorama_date)+ \
        ","+str(self.panorama_lat)+","+str(self.panorama_lng)

    def populatePanoramaInfo(self):
        """
        Call StreetView API for point given direction and API key.

        The API is called to extract the metadata for a panorama stored for this
        point location. Panorama ID, date, lat,lng values are stored.
        """
        base = r"https://maps.googleapis.com/maps/api/streetview"
        size = r"?size=1200x800&fov=80&location="
        end = str(self.lat) + "," + str(self.lng) + "&heading=" + str(self.direction) + key
        while True:
            try: # request StreetView API for metadata
                response = urllib.request.urlopen(base + r"/metadata" + size + end) # API call
                json_raw = response.read().decode('utf-8')
                json_data = json.loads(json_raw)
                if json_data['status'] != 'ZERO_RESULTS' and 'date' in json_data:
                    #print(json_data['pano_id'])
                    lcn = json_data['location']
                    self.panoramaID = json_data['pano_id']
                    self.panorama_date = json_data['date'] # important for project
                    self.panorama_lat = lcn['lat']
                    self.panorama_lng = lcn['lng']
                break
            except IOError: # possible connection error, retry in 5 seconds
                print("ERROR")
                time.sleep(5)
                continue
