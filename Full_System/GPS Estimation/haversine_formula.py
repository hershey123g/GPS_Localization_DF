from math import pi,sqrt,sin,cos,atan2

def haversine(pos1, pos2):
    lat1 = float(pos1['lat'])
    long1 = float(pos1['long'])
    lat2 = float(pos2['lat'])
    long2 = float(pos2['long'])

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c
    mi = 3956 * c
    return km
GPS_coord1 = {'lat':53.32055555555556 , 'long':-1.7297222222222221}
GPS_coord2 = {'lat':53.31861111111111, 'long':-1.6997222222222223}

print (haversine(GPS_coord1, GPS_coord2))


