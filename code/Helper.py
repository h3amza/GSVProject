"""
Module contains static functions used in the project.

If there is a function not pertinent to a particular class, it is defined here.
"""

from math import asin,cos,pi,sin,atan2,degrees,radians,sqrt


RADIUS_EARTH = 6371.01 # earth's radius in kilometers
EPSILON = 0.000001 # threshold parameter for distance calculation

def direction(lat1,lng1,lat2,lng2):
    """
    Returns the direction from point A to B in degrees (0-360)

    Parameters lat1,lng1: coordinates of point A
    Parameters lat2,lng2: coordinates of point B
    Formula derived from https://www.movable-type.co.uk/scripts/latlong.html
    """
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lng_diff = radians(lng2 - lng1)
    x = sin(lng_diff) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1)* cos(lat2) * cos(lng_diff))
    initial_bearing = atan2(x, y)
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return(compass_bearing)

def interpolate(lat1,lng1,lat2,lng2):
    """
    Returns coordinates between points A and B in a straight line, 15 meters apart.

    Parameters lat1,lng1: coordinates of point A
    Parameters lat2,lng2: coordinates of point B
    """
    segments = []
    distance = haversine(lat1,lng1,lat2,lng2)*1000 # get distance in meters
    split = int(distance/15) # how many unique points need to be generated
    for i in range(split): # find x and y coordinates for each point
        x = lat1 + (lat2-lat1) * (i/split)
        y = lng1 + (lng2-lng1) * (i/split)
        segments.append((x,y)) # generate list of points --> [(x1,y1),(x2,y2),...]
    return segments

def haversine(lat1,lng1,lat2,lng2):
    """
    Returns haversine distance between 2 points A and B in kilometers.

    Parameters lat1,lng1: coordinates of point A
    Parameters lat2,lng2: coordinates of point B
    Formula derived from https://www.movable-type.co.uk/scripts/latlong.html
    """
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    delta_lng = lng2 - lng1
    delta_lat = lat2 - lat1
    a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lng/2)**2
    c = 2 * asin(sqrt(a))
    return c * RADIUS_EARTH


def radial_distance(lat,lng,bearing, dist):
    """
    Returns a spatial coordinate some degrees and distance away from point A.

    Parameters lat,lng: coordinates of point A
    Parameter bearing: direction in degrees
    Parameter dist: distance in miles
    Formula derived from https://www.movable-type.co.uk/scripts/latlong.html
    """
    radian_lat1 = radians(lat)
    radian_lng1 = radians(lng)
    radian_bearing = radians(bearing)
    norm_distance = dist / RADIUS_EARTH # normalize linear distance to radian angle
    radian_lat = asin( sin(radian_lat1) * cos(norm_distance) + cos(radian_lat1) * sin(norm_distance) * cos(radian_bearing) )
    if cos(radian_lat) == 0 or abs(cos(radian_lat)) < EPSILON: # endpoint a pole
        radian_lng=radian_lng1
    else:
        radian_lng = ( (radian_lng1 - asin( sin(radian_bearing)* sin(norm_distance) / cos(radian_lat) ) + pi ) % (2*pi) ) - pi
    lat = degrees(radian_lat)
    lng = degrees(radian_lng)
    return (lat, lng)
