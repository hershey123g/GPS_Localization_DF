import numpy as np
import math
R = 6371 # radius of the earth

def get_cartesian(lat=None,lon=None):
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
    	return math.sqrt(math.pow(x2 - x1, 2) +
                math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2) * 1.0) 

#Given GPS coordinates of Master Drone as lat, lon, alt
#Given vector from master drone to slave drone vx vy vz
lat = 53.32055555555556
lon = -1.7297222222222221
alt = 5

vx = 1.414
vy = 1
vz = 1

#Find cartesian coordinates (Mx,My,Mz) of Master drone using lat, lon
Mx,My,Mz = get_cartesian(lat,lon)
print ("Cartesian coordinates of master drone",Mx,My,Mz)

#Find cartesian coordinates of slave drone using vector transformation
Sx = Mx+vx
Sy = My+vy
Sz = Mz+vz
print ("Cartesian coordinates of slave drone" , Sx,Sy,Sz)

#check distance between cartesian coordinates of master and drone
print ("Distance between cartesian coordinates of master and drone", distance(Mx,My,Mz,Sx,Sy,Sz))


#Find latitude, longitude of slave drone using cartesian coordinates(Sx,Sy,Sz) 
slave_lat, slave_lon = get_latlon(Sx,Sy,Sz)

print ("Latitude and Longitude of slave drone", slave_lat, slave_lon)
