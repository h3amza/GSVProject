"""
Module defines a Region class. Each Region object at the end of execution will
contain information about each accessible panorama from Maps API within a mile
radius from the center of the region.

This is analogous to walking down several streets in real life and storing metadata
about photographs you take every 15 meters. At every interval, you turn 90 degrees
to your left and store photograph (panorama) metadata, then you turn 90 degrees to
your right and do the same. This way, you have access to panaromas of both sides
of a street as you walk down it in a straight line.
"""


from Helper import *
from Street import *
import re
import time
import ast

class Region():
    """
    A class representing a region with a center point coordinate.

    Points are generated 0.25, 0.5, 0.75, and 1 mile away from the center and
    all routes are recorded between points and center. This ends up giving all
    coordinates 15 meters around the center in a 1 mile radius, for which we
    can call Maps API to get information about panoramas on the left and right
    of each point.

    Attribute region_name: Unique identifier for records

    Attribute center: Tuple for region center coordinates

    Attribute routes: All possible routes between center and destination points

    Attribute destinations: Coordinates of points spread around center within
    a mile radius.

    Attribute intersections: Temporary list of potential intersections in all
    routes.

    Attribute segments: List of tuples (lat,lng) of all intersection segments
    in all routes.


    Attribute streets: List of all points that are 15 meters apart in all routes.
    """

    def __init__(self,name,lat,lng):
        """
        Initialize Region object with name and center lat lng.

        Parameter name: name of region
        Parameters lat,lng: coordinates of region center
        """
        self.region_name = name
        self.center = (lat,lng)
        self.routes = []
        self.destinations = []
        self.intersections = []
        self.segments = []
        self.streets = []

    def level_routes(self):
        """
        Generate destination coordinates that are some radius away from center.

        For each distance value, generate 90 destinations around the center and
        append to destinations list. Destinations are generated in complete circle
        using 360/90 = 4 as the multiplier for each range value.
        """
        radii = [0.25]#,0.5,0.75,1.0] # distance in miles
        for r in radii:
            for i in range(0,4): # generate 90 destinations
                self.destinations.append(radial_distance(self.center[0],self.center[1],i*4,r))

    def get_routes(self,driver):
        """
        Functions uses Selenium webdriver to access Google Maps link to extract
        the route between acenter and a destination.

        The link using center and destination coordinates is first constructed
        and loaded. After 3 seconds (time for page to load on slow speed internet)
        extract the HTML and look for the pattern that matches coordinates like
        [null,null,33.453,-121.23522]. These are potential intersections in the route
        between center and destination.

        Parameters driver: Selenium Chrome driver
        """
        for i in self.destinations:
            placeholder = "https://www.google.com/maps/dir/"+str(self.center[0])+","+str(self.center[1])+"/"
            site = placeholder+str(i[0])+","+str(i[1])+"/data=!3m1!4b1!4m2!4m1!3e0"
            driver.get(site) # selenium web driver
            time.sleep(3) # allow time for website to load completely
            source = driver.page_source # get HTML
            matches = (re.findall('\[null,null,-?\d+\.?\d+,-?\d+\.?\d+]',source)) # look for pattern
            for i in range(len(matches)): # remove the null part from the matched value
                matches[i]=matches[i].replace("null,null,","")
            self.intersections.append(matches)

    def get_segments(self):
        """
        Generate a list of intersection segments from the intersections list.

        The set of coordinates fetched from Maps page always have this pattern:
        coordinates that are always repeated twice, are part of the actual route
        (corner 1, then corner2 etc.). The first repeated coordinate is always
        the origin in the route.
        """
        print(self.intersections)
        for route in self.intersections:
            doubles = []
            for i in range(len(route)-1):
                if route[i] == route[i+1]: # if a duplicate is found, then it is an intersection
                    pair = ast.literal_eval(route[i]) # string literal to list
                    doubles.append([round(pair[0],6),round(pair[1],6)]) # round off decimals
            source = doubles[0] # starting element in doubles is always the origin in the route
            starting_indices = [] # since the origin can differ a few 100th of a lat/lng value, compare
                                    # only upto the first 3 decimal points
            starting_indices = [i for i in range(len(doubles)) if (round(doubles[i][0],3) == round(source[0],3)) and (round(doubles[i][1],3) == round(source[1],3))]
            starting_indices.append(len(doubles)+1) # this is a list of indices of origins in doubles
            indices = list(zip(starting_indices,starting_indices[1:])) # stagger indices [1,2,3] --> [(1,2),(2,3)]
            for i in indices:
                minilist = doubles[i[0]:i[1]] # grab an intersection
                l = list(zip(minilist,minilist[1:])) # convert into segment
                l = [i for i in l if i[0]!=i[1]] # make sure that a segment is not a dud, (lat1,lng1) to (lat1,lng1)
                self.segments.append(l)

    def populate_routes(self):
        """
        Generate all points between intersection segments that are 15 meters apart.

        The spatial coordinates are stored in a list with a unique street ID to
        be used later for matching streetwise panoramas. Street objects also store
        the coordinates to the end points of a street for referencing later.
        """
        streets = []
        print(self.segments)
        for segment in self.segments: # store unique coordinate points of intersections
            for point in segment:
                if point not in streets:
                    streets.append(point)
        for i in range(len(streets)): # create street object for each spatial point
            streetID = i
            A = streets[i][0]
            B = streets[i][1]
            self.streets.append(Street(streetID,A,B))
        for i in self.streets:
            i.populate_points() # fills street object.points with interpolated points

    def write_region(self):
        """
        Write every single point's information to a csv file.

        For every spatial coordinate in street's points, a Point object is created
        which is queried against the Static Maps API to find information about
        the panorama for that coordinate. All this information is then added to a
        csv file.
        """
        points_list = []
        panoramas_list = []
        pointCounter = 0 # unique identifier for Point ID
        for i in self.streets: # for each street, get direction between ends
            streetID = i.ID
            A = i.A
            B = i.B
            direction = i.direction
            region = self.region_name
            for j in i.points: # for each point in street, get panorama information
                pt = Point(pointCounter,region,streetID,j[0],j[1],direction)
                if (pt.panorama_lat,pt.panorama_lng) in panoramas_list:
                    continue # rare but if already have panorama, skip
                else:
                    points_list.append(pt)
                    panoramas_list.append((pt.panorama_lat,pt.panorama_lng))
                    pointCounter +=1
        f = open("../data/"+self.region_name+"-points.csv","w")
        for p in points_list:
            print(p.strForm(),file=f)
        f.close()
