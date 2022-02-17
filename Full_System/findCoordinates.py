import numpy as np
import math
R = 6371 # radius of the earth

def get_cartesian(lat,lon):
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R *np.sin(lat)
    return x,y,z

def get_latlon(x,y,z):
	lat = np.degrees(np.arcsin(z/R))
	lon = np.degrees(np.arctan2(y, x))
	return lat,lon

def distance(x1 , y1, z1, x2 , y2, z2): 
	return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2) * 1.0) 