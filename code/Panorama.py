"""
Module defines a Panorama class. The Street View API is called for the precise
left and right directions for a panorama (90 and 270 degrees) to store flat
images.
"""

import urllib.request
key = "&key=" + "XXXX"

class Panorama():
    """
    A class representing a panorama object.
    The panorama objects are created by reading in the region-points.csv file.

    Attribute region: Region name for storage purposes.

    Attribute ID: Panorama ID.

    Attribute date: Panorama date.

    Attribute lat,lng: Coordinates of panorama.

    Attribute direction: bearing from end point A to B of street where panorama is
    situated. Helps offset for a flat image.
    """
    def __init__(self,region,id,date,lat,lng,direction):
        """
        Initialize Panorama object with information coming from panorama Point.

        Parameters region: Name of panorama's region
        Parameters ID: UID for Street object
        Parameters date: date of panorama from file
        Parameters lat,lng: string lat,lng values from file
        Parameters direction: string panorama direction from  file
        """
        self.region = region
        self.ID = id
        self.date = date
        self.lat = float(lat)
        self.lng = float(lng)
        self.direction = float(direction)

    def download(self):
        """
        Call Street View API to store panorama screenshot.

        2 images are stored per panorama, at 90 and 270 degrees after offset from
        panorama's street direction. Ensures that flat images are taken of the left
        and right for each point.
        """
        # API call is similar to one for point but without the metadata attachement
        base = r"https://maps.googleapis.com/maps/api/streetview"
        size = r"?size=1200x800&fov=80&location="
        # generate and store image for bearing 90 degrees (right)
        end = str(self.lat) + "," + str(self.lng) + "&heading=" + str(self.direction+90) + key
        urllib.request.urlretrieve(base + size + end,"../images/"+self.region+"/"+self.ID+"-90"+".jpg")
        # generate and store image for bearing 270 degrees (left)
        end = str(self.lat) + "," + str(self.lng) + "&heading=" + str(self.direction+270) + key
        urllib.request.urlretrieve(base + size + end,"../images/"+self.region+"/"+self.ID+"-270"+".jpg")
