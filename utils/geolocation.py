# backend/utils/geolocation.py

import math
from decimal import Decimal

def haversine(lat1, lon1, lat2, lon2, unit='km'):
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees) using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of the first point.
        lat2, lon2: Latitude and longitude of the second point.
        unit (str): Unit for the result ('km', 'miles', 'm'). Defaults to 'km'.

    Returns:
        float: Distance between the two points in the specified unit,
               or float('inf') if input coordinates are invalid/missing.
    """
    try:
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, map(Decimal, [lat1, lon1, lat2, lon2]))
    except (TypeError, ValueError, InvalidOperation):
         # Handle cases where lat/lon might be None or invalid Decimal
        return float('inf')


    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in different units
    if unit == 'miles':
        r = 3956
    elif unit == 'm':
        r = 6371000
    else: # Default to kilometers
        r = 6371

    distance = c * r
    return distance