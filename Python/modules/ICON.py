# Common code for ICON users at Illinois. Geometrical transformations, airglow code, etc.

import numpy as np
from pyglow import pyglow
from datetime import datetime, timedelta
from scipy import stats
import multiprocessing
from multiprocessing import Pool
import time
import math
from scipy import optimize


def wgs84constants():
    # http://en.wikipedia.org/wiki/World_Geodetic_System (Nov 10, 2014)
    a = 6378.137 # semi-major axis of earth [km]
    b = 6356.75231424518 # semi-minor axis of earth [km]
    e = np.sqrt(1-b**2/a**2) # eccentricity of earth
    return a,b,e



def ecef_to_wgs84(ecef_xyz):
    '''
    Convert from earth-centered earth-fixed (ECEF)
    coordinates (x,y,z) to WGS-84 latitude, longitude, and altitude.
    INPUTS:
       ecef_xyz - a length-3 array containing the X, Y, and Z locations in ECEF
                  coordinates in kilometers.

    OUTPUTS:
       latlonalt - a length-3 array containing the WGS-84 coordinates:
                   [latitude (degrees), longitude (degrees), altitude (km)]
                   Altitude is defined as the height above the reference
                   ellipsoid. Longitude is defined in [0,360).

    HISTORY:
       11-Jun-2006: Initial MATLAB template created by Jonathan J. Makela
       (jmakela@uiuc.edu)
       17-July-2006: Algorithm implemented by Dwayne P. Hagerman
       (dhagerm2@uiuc.ed)
       10-Nov-2014: Translated to Python by Brian J. Harding
       (bhardin2@illinois.edu)
       19-Jan-2015: Changed from iterative to closed-form implementation (BJH)
    '''
    
    
    a,b,e = wgs84constants()

    x = 1.0*ecef_xyz[0]
    y = 1.0*ecef_xyz[1]
    z = 1.0*ecef_xyz[2]
   
    lon = np.arctan2(y,x)
    # longitude is defined in [0,360) or [0,2*pi)
    if lon < 0.0:
        lon += 2*np.pi
     
    ep = np.sqrt((a**2-b**2)/b**2)
    p = np.sqrt(x**2 + y**2)
    th = np.arctan2(z*a,(p*b))

    lat = np.arctan2((z + ep**2 * b * np.sin(th)**3),(p - e**2 * a * np.cos(th)**3))

    N = a/np.sqrt(1 - e**2*np.sin(lat)**2)
    alt = p/np.cos(lat) - N
    lla = np.array([lat*180/np.pi, lon*180/np.pi, alt])

    return lla





def wgs84_to_ecef(latlonalt):
    '''
    Convert from WGS84 coordinates [latitude, longitude, altitude] to 
    earth-centered earth-fixed coordinates (ECEF) [x,y,z]
    
    INPUTS:
       latlonalt - a length-3 array containing the WGS-84 coordinates:
                   [latitude (degrees), longitude (degrees), altitude (km)]    

    OUTPUTS:
       ecef_xyz - a length-3 array containing the X, Y, and Z locations in ECEF
                  coordinates in kilometers.
                  
    HISTORY:
       11-Jun-2006: Initial MATLAB template created by Jonathan J. Makela
       (jmakela@uiuc.edu)
       17-July-2006: Algorithm implemented by Dwayne P. Hagerman
       (dhagerm2@uiuc.ed)
       10-Nov-2014: Translated to Python by Brian J. Harding
       (bhardin2@illinois.edu)    
    '''
    
    a,b,e = wgs84constants()
    
    lat = latlonalt[0]*np.pi/180.
    lon = latlonalt[1]*np.pi/180.
    alt = latlonalt[2]*1.0
    
    x = a * np.cos(lon) / np.sqrt(1 + (1-e**2) * np.tan(lat)**2) + alt*np.cos(lon)*np.cos(lat)
    y = a * np.sin(lon) / np.sqrt(1 + (1-e**2) * np.tan(lat)**2) + alt*np.sin(lon)*np.cos(lat)
    z = a * (1-e**2) * np.sin(lat) / np.sqrt(1 - e**2 * np.sin(lat)**2) + alt*np.sin(lat)
    
    return np.array([x,y,z])
  
  
  
  
    
def ven_to_ecef(latlonalt, ven):
    '''
    Convert a direction vector (e.g., velocity) in local vertical-east-north (VEN) 
    coordinates, defined at the location given in WGS84 coordinates 
    [latitude, longitude, altitude], to a vector in earth-centered earth-fixed 
    (ECEF) coordinates [x,y,z].
    
    INPUTS:
        latlonalt - a length-3 array containing the WGS-84 coordinates of the location:
                   [latitude (degrees), longitude (degrees), altitude (km)]
        ven - the local direction vector [vertical, east, north] which will be converted to 
             ECEF coordinates.
    OUTPUTS:
        xyz - the direction vector in ECEF coordinates [x,y,z]
        
    HISTORY:
       10-Nov-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
       02-Sep-2015: Changed from numerical to analytical solution (BJH)
    '''
                
    # Convert to float values, in case they are integers
    latlonalt = np.array([float(x) for x in latlonalt])

    # Construct rotation matrix to take ECEF to VEN
    latr = latlonalt[0]*np.pi/180.
    lonr = latlonalt[1]*np.pi/180.
    M = np.array([[ np.cos(latr)*np.cos(lonr),   np.cos(latr)*np.sin(lonr),  np.sin(latr)],
                  [-np.sin(lonr),                np.cos(lonr),               0],
                  [-np.sin(latr)*np.cos(lonr),  -np.sin(latr)*np.sin(lonr),  np.cos(latr)]
                  ])
    
    # Perform rotation
    ecef = np.linalg.solve(M,ven)

    return ecef




def ecef_to_ven(latlonalt, ecef):
    '''
    Convert a direction vector (e.g., velocity) in earth-centered earth-fixed (ECEF) 
    coordinates [dx,dy,dz], defined at the location given in WGS84 coordinates
    [latitude, longitude, altitude], to a vector in local vertical-east-north (VEN)
    coordinates.
    
    INPUTS:
        latlonalt - a length-3 array containing the WGS-84 coordinates of the location:
                   [latitude (degrees), longitude (degrees), altitude (km)]
        ecef - the direction vector [dx,dy,dz] which will be converted to 
               VEN coordinates.
       
    OUTPUTS:
        ven - the direction vector in [vertical, east, north] coordinates.
        
    HISTORY:
       06-Jan-2015: Written by Brian J. Harding (bhardin2@illinois.edu)
       02-Sep-2015: Changed from numerical to analytical solution (BJH)
    '''
                
    # Convert to float values, in case they are integers
    latlonalt = np.array([float(x) for x in latlonalt])
    
    # Construct rotation matrix to take ECEF to VEN
    latr = latlonalt[0]*np.pi/180.
    lonr = latlonalt[1]*np.pi/180.
    M = np.array([[ np.cos(latr)*np.cos(lonr),   np.cos(latr)*np.sin(lonr),  np.sin(latr)],
                  [-np.sin(lonr),                np.cos(lonr),               0],
                  [-np.sin(latr)*np.cos(lonr),  -np.sin(latr)*np.sin(lonr),  np.cos(latr)]
                  ])
    
    # Perform rotation
    ven = M.dot(ecef)
        
    return ven




def ecef_to_azze(latlonalt, ecef):
    '''
    Convert a direction vector (e.g., velocity) in earth-centered earth-fixed (ECEF)
    coordinates [dx,dy,dz],  defined at the location given in WGS84 coordinates 
    [latitude, longitude, altitude], to the azimuth and zenith angles of the 
    direction vector. This function is similar to ecef_to_ven.
    
    INPUTS:
        latlonalt - a length-3 array containing the WGS-84 coordinates of the location:
                   [latitude (degrees), longitude (degrees), altitude (km)]
        ecef - the direction vector [dx,dy,dz] which will be converted to 
               azimuth and zenith angles.
       
    OUTPUTS:
        az,ze - the azimuth (degrees East from North) and zenith (degrees down
                from Vertical) angles of the direction vector.
        
    HISTORY:
       24-Feb-2015: Written by Brian J. Harding (bhardin2@illinois.edu)
    '''
    
    # First convert to VEN
    ven = ecef_to_ven(latlonalt, ecef)
    
    # Then convert VEN to az, ze
    ze = np.arccos(ven[0])*180.0/np.pi
    az = np.arctan2(ven[1],ven[2])*180.0/np.pi
    
    return az,ze
    
    
    
  
def azze_to_ecef(latlonalt, az, ze):
    '''
    Convert a line of sight in (az,ze) coordinates, defined at the 
    location given in WGS84 coordinates [latitude, longitude, altitude],
    to a unit vector in earth-centered earth-fixed (ECEF) coordinates [x,y,z]. This
    function is very similiar to ven_to_ecef.
    
    INPUTS:
        latlonalt - a length-3 array containing the WGS-84 coordinates of the location:
                   [latitude (degrees), longitude (degrees), altitude (km)]
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith
       
    OUTPUTS:
        xyz - the unit direction vector in ECEF coordinates [x,y,z]
        
    HISTORY:
       15-May-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
    '''
    zer = ze*np.pi/180.
    azr = az*np.pi/180.    
    
    # First convert az,ze to VEN
    ven = np.zeros(3)
    ven[0] = np.cos(zer)
    ven[1] = np.sin(zer)*np.sin(azr)
    ven[2] = np.sin(zer)*np.cos(azr)
    # Then run ven_to_ecef
    return ven_to_ecef(latlonalt, ven)
    
    
    


def project_line_of_sight(satlatlonalt, az, ze, step_size = 1., total_distance = 4000.):
    '''
    Starting at the satellite, step along a line of sight, and return an array of 
    equally-spaced points at intervals along this line of sight, in WGS84 latitude,
    longitude, and altitude coordinates.
    
    INPUTS:
        satlatlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the satellite
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith
        
    OPTIONAL INPUTS:
        step_size - spacing between points in the returned array (km).
        total_distance - length of the projected line (km).
        
    OUTPUTS:
        xyz - array of size 3xN, where N is floor(total_distance/step_size). Contains
              the ECEF coordinates of every point along the line of sight, in step_size
              intervals.
        latlonalt - array of size 3xN, where each column contains the latitude, longitude
                    and altitude corresponding to the column of xyz, in WGS84 coordinates
    
    HISTORY:
        10-Nov-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
    '''
    
    # Convert to radians
    zer = ze*np.pi/180.
    azr = az*np.pi/180.

    # Create unit vector describing the look direction in Vertical-East-North (VEN) coordinates
    lookven = np.array([np.cos(zer), np.sin(zer)*np.sin(azr), np.sin(zer)*np.cos(azr)])
    # Convert satellite location to ecef
    satxyz = wgs84_to_ecef(satlatlonalt)
    # Convert look direction to ecef. This is a unit vector.
    lookxyz = ven_to_ecef(satlatlonalt, lookven)

    # Step along this line of sight
    step_sizes = np.arange(0,total_distance,step_size)
    N = len(step_sizes)
    xyz = np.zeros((3,N))
    latlonalt = np.zeros((3,N))
    for i in range(N):
        xyzi = satxyz + step_sizes[i]*lookxyz
        xyz[:,i] = xyzi
        latlonalt[:,i] = ecef_to_wgs84(xyzi)  
        
    return xyz, latlonalt
 
 
    
    
def tangent_point(satlatlonalt, az, ze, tol=1e-7):
    '''
    Find the location (lat, lon, alt) of the tangent point of a ray from the satellite.
    Current implementation finds the minimum altitude along the line of sight by using
    a numerical method with a precision of about 0.1 m. The vertical
    precision is much better than the horizontal precision.
    
    INPUTS:
        satlatlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the satellite
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith
        
    OPTIONAL INPUTS:
        tol - km, stopping criterion for the solver. Stop when the solution is not moving
              by more than a horizontal distance of tol.
        
    OUTPUTS:
        latlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the tangent location.
    
    HISTORY:
        10-Dec-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
        02-Sep-2015: Use scipy.optimize to do minimization instead of my own implementation.
    '''
    
    # Convert to radians
    zer = ze*np.pi/180.
    azr = az*np.pi/180.

    # Create unit vector describing the look direction in Vertical-East-North (VEN) coordinates
    lookven = np.array([np.cos(zer), np.sin(zer)*np.sin(azr), np.sin(zer)*np.cos(azr)])
    # Convert satellite location to ecef
    satxyz = wgs84_to_ecef(satlatlonalt)
    # Convert look direction to ecef. This is a unit vector.
    lookxyz = ven_to_ecef(satlatlonalt, lookven)

    # Find the step size which minimizes the altitude. This problem is convex,
    # so it's easy. Define a function which will be minimized.
    def altitude(step_size):
        xyzi = satxyz + step_size*lookxyz
        latlonalt = ecef_to_wgs84(xyzi)
        return latlonalt[2]

    # Throw an error if there doesn't appear to be a tangent altitude.
    # (i.e., if the slope is positive, which would happen if the line
    # of sight is looking upward instead of downward)
    if altitude(1.) >= altitude(0.):
        raise Exception('No Tangent Altitude: Altitude not decreasing along line of sight')

    # Perform minimization using scipy minimization function (golden section search)
    #res = optimize.minimize_scalar(altitude, method='golden', tol=tol)
    res = optimize.minimize_scalar(altitude, method='golden', options={'xtol':tol})
    s = res.x

    # Determine tangent location from step size
    xyzi = satxyz + s*lookxyz
    latlonalt = ecef_to_wgs84(xyzi)
    return latlonalt




def earth_curvature(lat):
    '''
    The radius of curvature of the Earth at the location specified. This is 
    different from the radius of Earth at that point. WGS84 Earth is assumed.
    INPUTS:
        lat -- TYPE:float, UNITS:deg. Latitude of point on surface.
    OUTPUTS:
        r   -- TYPE:float, UNITS:km.  Radius of curvature of Earth.
    '''
    ecef = wgs84_to_ecef([lat, 0., 0.])
    z = ecef[2]
    a,b,_ = wgs84constants()
    t = np.arcsin(z/b)
    r = (b**2 * np.cos(t)**2 + a**2 * np.sin(t)**2)**(1.5)/(a*b)
    return r





def distance_to_shell(satlatlonalt, az, ze, shell_altitude, intersection='first', tol=1e-5):
    '''
    Along the line of sight, find the distance from the satellite to the
    first intersection with the shell at a given altitude. If no intersection
    exists, return np.nan. If the satellite is below this shell, return np.nan.
    
    INPUTS:
        satlatlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the satellite
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith
        shell_altitude - the altitude of the shell in km.
        
    OPTIONAL INPUTS:
        intersection - str, 'first' or 'second'. In general there are two intersections of the 
                       ray with the shell. This argument specifies which will be returned.
        tol - km, stopping criterion for the solver. Stop when the solution is not changing
              by more than  tol.
        
    OUTPUTS:
        d - distance in km. If no intersection exists, d is nan.
    
    HISTORY:
        10-Dec-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
        31-Mar-2015: Included "intersection" parameter.
    '''
    maxiters = 1e4 # Just in case, so it doesn't hang forever

    # Convert to radians
    zer = ze*np.pi/180.
    azr = az*np.pi/180.

    # Create unit vector describing the look direction in Vertical-East-North (VEN) coordinates
    lookven = np.array([np.cos(zer), np.sin(zer)*np.sin(azr), np.sin(zer)*np.cos(azr)])
    # Convert satellite location to ecef
    satxyz = wgs84_to_ecef(satlatlonalt)
    # Convert look direction to ecef. This is a unit vector.
    lookxyz = ven_to_ecef(satlatlonalt, lookven)
    
    # First find the tangent altitude
    tanglatlonalt = tangent_point(satlatlonalt, az, ze)
    tangent_altitude = tanglatlonalt[2]
    
    # If there's no intersection, return nan.
    if shell_altitude <= tangent_altitude or shell_altitude > satlatlonalt[2]:
        return np.nan

    # Find the step size which results in an altitude equal to the shell altitude
    def my_func(step_size): # We want this function value to be zero
        xyzi = satxyz + step_size*lookxyz
        latlonalt = ecef_to_wgs84(xyzi)
        return latlonalt[2] - shell_altitude 
    
    # We need different initializations for the 'first' and 'second' intersections.
    if intersection=='first':
        # Find two values which straddle the solution.
        # (0) Satellite location (distance of zero)
        # (1) Tangent location (we need to calculate this distance)
        # (0)
        s0 = 0.
        f0 = my_func(s0)
        # (1)
        tangxyz = wgs84_to_ecef(tanglatlonalt)
        s1 = np.linalg.norm(tangxyz - satxyz) # distance from satellite to tangent point
        f1 = my_func(s1)
    elif intersection=='second':
        # Find two values which straddle the solution.
        # (0) Tangent location (we need to calculate this distance)
        # (1) A distance past the tangent location by a large amount
        # (0)
        tangxyz = wgs84_to_ecef(tanglatlonalt)
        s0 = np.linalg.norm(tangxyz - satxyz) # distance from satellite to tangent point
        f0 = my_func(s0)    
        # (1) Twice again as far should do it, but we'll do three times to be safe
        s1 = 3*s0
        f1 = my_func(s1)
    else:
        raise Exception('Unrecognized argument: intersection="%s". Try "first" or "second"' % intersection)
    
    # Check if straddle points are indeed straddle points
    if np.sign(f0)==np.sign(f1):
        raise Exception('Something went horribly wrong')

    # Straddle points found. Use bisection to converge to the answer.
    iters = 0
    while(abs(s0-s1) > tol):
        iters += 1
        if iters > maxiters:
            raise Exception('Bisection method failed: Maximum iterations reached')

        sn = (s0+s1)/2
        fn = my_func(sn)
        if np.sign(fn)==np.sign(f0):
            s0 = sn
            f0 = fn
        else:
            s1 = sn
            f1 = fn
    return sn




def distance_to_tangent_point(satlatlonalt, az, ze):
    '''
    Along the line of sight, find the distance from the satellite to the
    tangent point.
    
    INPUTS:
        satlatlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the satellite
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith
        
    OUTPUTS:
        d - distance in km.
    
    HISTORY:
        07-Jan-2014: Written by Brian J. Harding (bhardin2@illinois.edu)
    '''
    tanglatlonalt = tangent_point(satlatlonalt, az, ze)
    tangxyz = wgs84_to_ecef(tanglatlonalt)
    satxyz  = wgs84_to_ecef(satlatlonalt)
    d = np.linalg.norm(tangxyz - satxyz)
    return d



def azze_to_lla(satlatlonalt, az, ze, ht, tol=1e-6):
    '''
    Find the location (lat, lon, alt) where the requested look direction (az, ze) from the requested location
    intersects the specified altitude
    
    INPUTS:
        satlatlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the satellite
        az - direction of line of sight. degrees east of north.
        ze - direction of line of sight. degrees down from zenith.
        ht - altitude to calculate the intersection point for.
        
    OPTIONAL INPUTS:
        tol - km, stopping criterion for the solver. Stop when the solution is not moving
              by more than a horizontal distance of tol.
        
    OUTPUTS:
        latlonalt - array [latitude (deg), longitude (deg), altitude (km)] of the tangent location
    
    HISTORY:
        22-Jan-2015: Written by Jonathan J. Makela (jmakela@illinois.edu) based on ICON.tangent_point
    '''
    maxiters = 1e4 # Just in case, so it doesn't hang forever

    # Convert to radians
    zer = ze*np.pi/180.
    azr = az*np.pi/180.

    # Create unit vector describing the look direction in Vertical-East-North (VEN) coordinates
    lookven = np.array([np.cos(zer), np.sin(zer)*np.sin(azr), np.sin(zer)*np.cos(azr)])
    # Convert satellite location to ecef
    satxyz = wgs84_to_ecef(satlatlonalt)
    # Convert look direction to ecef. This is a unit vector.
    lookxyz = ven_to_ecef(satlatlonalt, lookven)

    # Find the step size which minimizes the altitude. This problem is convex,
    # so it's easy.
    def altitude(step_size):
        xyzi = satxyz + step_size*lookxyz
        latlonalt = ecef_to_wgs84(xyzi)
        return latlonalt[2]
    
    # Or, find the step size for which the slope is zero.
    # Define function to calculate the slope numerically
    def slope(step_size):
        numerical_step = 1e-4 # km
        alt1 = altitude(step_size - numerical_step/2)
        alt2 = altitude(step_size + numerical_step/2)
        return (alt2-alt1)/numerical_step

    # Find two values which straddle the solution.
    s0 = 0. # start at the satellite
    s1 = 1. # iterate on the next value until we've straddled the solution
    f0 = slope(s0)
    f1 = slope(s1)
        
    if (f0 > 0) & (satlatlonalt[2] > ht):
        raise Exception('Ray path will not intersect desired altitude')
        
    if (f0 < 0) & (satlatlonalt[2] < ht):
        raise Exception('Ray path will not intersect desired altitude')

    M = 2 # multiplier for line search to find straddle points
    iters = 0
    while(np.sign(f0)==np.sign(ht-altitude(s1))):
        iters += 1
        if iters > maxiters:
            raise Exception('Initial line search failed: Maximum iterations reached')
        s0 = s1
        s1 = s1 * M

    # Straddle points found. Use bisection to converge to the answer.
    iters = 0
    while(abs(s0-s1) > tol):

        iters += 1
        if iters > maxiters:
            raise Exception('Bisection method failed: Maximum iterations reached')

        # The next step
        sn = (s0+s1)/2
                
        # Figure out what side of the desired altitude this new step is    
        if(f0 < 0):
            if altitude(sn) < ht:
                s1 = sn
            else:
                s0 = sn
        else:
            if altitude(sn) < ht:
                s0 = sn
            else:
                s1 = sn

    xyzi = satxyz + sn*lookxyz
    latlonalt = ecef_to_wgs84(xyzi)
    return latlonalt
