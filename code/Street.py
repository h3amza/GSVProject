"""
Module defines Street class. Each Street object contains its end points, A and B,
as well as points that are 15 meters apart between A and B.
"""
from Helper import *
from Point import *

class Street():
    """
    Class representing a street with two end points.

    Attribute ID: Unique identifier for records

    Attribute points: List of spatial coordinates 15 meters apart in a street.

    Attribute A: First end point of street.

    Attribute B: Second end point of street.

    Attribute direction: bearing from A to B. Helps in accessing panorama in the
    precise direction. (90 degrees left, 90 degrees right)
    """

    def __init__(self,ID,A,B):
        """
        Initialize Street object with name and center lat lng.

        Parameter ID: UID for Street object
        Parameters A,B: end points of object
        """
        self.ID = ID
        self.points = []
        self.A = A
        self.B = B
        self.direction = 0

    def populate_points(self):
        """
        Estimate direction using Helper module's direction function. Then find
        all points that are 15 meters apart using Helper module's interpolate
        function. Store those in points list.
        """
        self.direction = direction(self.A[0],self.A[1],self.B[0],self.B[1])
        self.points = interpolate(self.A[0],self.A[1],self.B[0],self.B[1])
