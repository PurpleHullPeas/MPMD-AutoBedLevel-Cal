#!/usr/bin/python

# Updated version of the original script

# Original Project Found here:
# https://github.com/TechnoSwiss/MPMD-AutoBedLevel-Cal
# This version was made to be compatible with Dennis Brown's G29 P5 Spreadsheet:
# https://www.facebook.com/groups/mpminideltaowners/permalink/2186865287995612/
# G29 P5 V4 Converted to manual probes for cross-firmware compatibility:
# https://github.com/mcheah/Marlin4MPMD/wiki/Calibration#user-content-m665m666-delta-parameter-calibrations
#
# Full Instructions: https://www.facebook.com/groups/mpminideltaowners/permalink/2574670629215074/
#
# REQUIRES SERIAL
#
# sudo apt-get install python-serial
#
# Stock Firmware <=V41, V45 at 60 degrees C w/ Dennis's Defaults:
# python auto_cal_p5_v0.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 57.14 -bt 60
#
# Stock V43 & V44 at 60 degrees C w/ Dennis's Defaults:
# python auto_cal_p5_v0.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 114.28 -bt 60
#
# For Marlin, use the appropriate line for your stock firmware and replace "-ff 0" with "-ff 1"

from serial import Serial, SerialException, PARITY_ODD, PARITY_NONE
import sys
import argparse
import json
import math
import os

# -----------------------------------------------------------------------------
# Get Serial Connection
# -----------------------------------------------------------------------------

def establish_serial_connection(port, speed=115200, timeout=10, writeTimeout=10000):
    # Hack for USB connection
    # There must be a way to do it cleaner, but I can't seem to find it
    try:
        temp = Serial(port, speed, timeout=timeout, writeTimeout=writeTimeout, parity=PARITY_ODD)
        if sys.platform == 'win32':
            temp.close()
        conn = Serial(port, speed, timeout=timeout, writeTimeout=writeTimeout, parity=PARITY_NONE)
        conn.setRTS(False)#needed on mac
        if sys.platform != 'win32':
            temp.close()
        return conn
    except SerialException as e:
        print ("Could not connect to {0} at baudrate {1}\nSerial error: {2}".format(port, str(speed), e))
        return None
    except IOError as e:
        print ("Could not connect to {0} at baudrate {1}\nIO error: {2}".format(port, str(speed), e))
        return None

def get_points(port):
    while True:
        out = port.readline().decode()
        if 'Bed ' in out:
            break

    return out.split(' ')

# -----------------------------------------------------------------------------
# Generic Math Functions
# -----------------------------------------------------------------------------

def polar(x, y):
    """returns r, theta(degrees)
    """
    r = (x ** 2 + y ** 2) ** .5
    if y == 0:
        theta = 180 if x < 0 else 0
    elif x == 0:
        theta = 90 if y > 0 else 270
    else:
        theta = math.degrees(math.atan2(float(y), float(x)))
    return r, theta
    
def rect(r, theta):
    """theta in degrees

    returns tuple; (float, float); (x,y)
    """
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x,y

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def median(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n//2]
    else:
            return sum(sorted(lst)[n//2-1:n//2+1])/2.0
    
def linear_interp(x0, x1, z0, z1, xq):
    # https://en.wikipedia.org/wiki/Linear_interpolation
    x0 = float(x0)
    x1 = float(x1)
    z0 = float(z0)
    z1 = float(z1)
    xq = float(xq)
    zq = z0 + (xq-x0)*(z1-z0)/(x1-x0)
    return zq
    
# https://stackoverflow.com/questions/8661537/how-to-perform-bilinear-interpolation-in-python
def bilinear_interpolation(x, y, points):
    '''Interpolate (x,y) from values associated with four points.

    The four points are a list of four triplets:  (x, y, value).
    The four points can be in any order.  They should form a rectangle.

        >>> bilinear_interpolation(12, 5.5,
        ...                        [(10, 4, 100),
        ...                         (20, 4, 200),
        ...                         (10, 6, 150),
        ...                         (20, 6, 300)])
        165.0

    '''
    # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation

    points = sorted(points)               # order points by x, then by y
    (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

    if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        raise ValueError('points do not form a rectangle')
    if not x1 <= x <= x2 or not y1 <= y <= y2:
        raise ValueError('(x, y) not within the rectangle')

    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)

# -----------------------------------------------------------------------------
# Autoleveling Functions
# -----------------------------------------------------------------------------
    
def get_current_values(port, firmFlag):
    # Replacing G29 P5 with manual probe points for cross-firmware compatibility
    # G28 ; home
    # G1 Z15 F6000; go to safe distance
    # Start Loop
    #     G1 X## Y##; go to specified location
    #     G30 ;probe bed for z values
    #     G30 ;probe bed again for z values
    # End Loop
    # G28 ; return home
    
    # Initialize G29 P5 V4 Table
    number_cols = 7 
    number_rows = 21
    x_list = [None]*number_rows
    y_list = [None]*number_rows
    z1_list = [None]*number_rows
    z2_list = [None]*number_rows
    z_avg_list = [None]*number_rows
    dtap_list = [None]*number_rows
    dz_list = [None]*number_rows
    dz_test = [None]*number_rows
    
    # Define Table Indices
    ix = 0
    iy = 1
    iz1 = 2
    iz2 = 3
    izavg = 4 
    idtap = 5
    idz = 6
    
    # Assign X Coordinates (G29 P5)
    x_list[0] = -25
    x_list[1] = 0
    x_list[2] = 25
    x_list[3] = 50
    x_list[4] = 25
    x_list[5] = 0
    x_list[6] = -25
    x_list[7] = -50
    x_list[8] = -50
    x_list[9] = -25
    x_list[10] = 0
    x_list[11] = 25
    x_list[12] = 50
    x_list[13] = 50
    x_list[14] = 25
    x_list[15] = 0
    x_list[16] = -25
    x_list[17] = -50
    x_list[18] = -25
    x_list[19] = 0
    x_list[20] = 25
    
    # Assign Y Coordinates (G29 P5)
    y_list[0] = -50
    y_list[1] = -50
    y_list[2] = -50
    y_list[3] = -25
    y_list[4] = -25
    y_list[5] = -25
    y_list[6] = -25
    y_list[7] = -25
    y_list[8] = 0
    y_list[9] = 0
    y_list[10] = 0
    y_list[11] = 0
    y_list[12] = 0
    y_list[13] = 25
    y_list[14] = 25
    y_list[15] = 25
    y_list[16] = 25
    y_list[17] = 25
    y_list[18] = 50
    y_list[19] = 50
    y_list[20] = 50

    # Send Gcodes
    port.write(('G28\n').encode()) # Home
    
    if firmFlag == 1: 
        # Marlin
        port.write(('G1 Z15 F6000\n').encode()) # Move to safe distance
    else:
        # Stock Firmware
        port.write(('G29 P5 V4\n').encode())

        while True:
            out = port.readline().decode()
            #print("{0}\n".format(out))
            if 'G29 Auto Bed Leveling' in out:
                break
        
    # Loop through all 
    for ii in range(len(x_list)):
        
        if firmFlag == 1: 
            # Marlin
            
            # Move to desired position
            port.write(('G1 X{0} Y{1}\n'.format(x_list[ii], y_list[ii])).encode()) 
            #print('Sending G1 X{0} Y{1}\n'.format(x_list[ii], y_list[ii]))
            
            # Probe Z values
            port.write(('G30\n').encode())
            z_axis_1 = get_points(port)
            port.write(('G30\n').encode())
            z_axis_2 = get_points(port)
        else:
            # Stock Firmware
            z_axis_1 = get_points(port)
            z_axis_2 = get_points(port)
        
        # Populate most of the table values
        z1_list[ii] = float(z_axis_1[6])
        z2_list[ii] = float(z_axis_2[6])
        z_avg_list[ii] = float("{0:.4f}".format((z1_list[ii] + z2_list[ii]) / 2.0))
        dtap_list[ii] = z2_list[ii] - z1_list[ii]
        #print('Received: X:{0} X:{1} Y:{2} Y:{3} Z1:{4} Z2:{5}\n\n'.format(str(x_list[ii]), str(z_axis_1[2]), str(y_list[ii]), str(z_axis_1[4]), z1_list[ii], z2_list[ii]))
    
    # Find the Median Reference
    z_med = median(z_avg_list)
    
    # Calculate z diff
    for ii in range(len(x_list)):
        dz_list[ii] = z_avg_list[ii] - z_med
        
    # Empty out remaining lines for stock firmware
    if firmFlag == 0: 
        for ii in range(6):
            out = port.readline().decode()
    
    return x_list, y_list, z1_list, z2_list, z_avg_list, dtap_list, dz_list

def gridval2idx(x, y, xStart, yStart, dx, dy):
    ix = int(round(abs(x-xStart)/dx))
    iy = int(round(abs(y-yStart)/dy))
    irow = iy
    icol = ix
    return irow, icol
    
def findProbePoints(ii, idprobe, n):
    # Inputs: 
    #     ii = irow or icol of unknown point
    #     idprobe = probe indices increment, 3 for G29 P5
    #     n = number of rows or columns, 13 for G29 P5
    # Outputs:
    #     ip1 = known probe point location 1
    #     ip2 = known probe point location 2
    #     ip3 = known probe point location 3,
    #           only used if irow == icol and not an edge point
    
    r = ii%idprobe # Remainder
    if (r == 0): 
        if (ii == 0):
            # First row/column
            ip1 = 0
            ip2 = ip1+idprobe
            ip3 = -1
        elif (ii == n-1):
            # Last row/column
            ip2 = n-1
            ip1 = ip2-idprobe
            ip3 = -1
        else:  
            # Interior row/column that is aligned 
            # vertically/horizontally with a probe point
            ip1 = ii-idprobe
            ip2 = ii
            ip3 = ii+idprobe
    else: 
        # All other interior points
        ip1 = ii-r
        ip2 = ip1+idprobe
        ip3 = -1
    
    return ip1, ip2, ip3
    
def calculate_contour(x_list, y_list, dz_list, runs, xhigh, yhigh, zhigh, tower_flag):
    
    # Dennis's G29 P5 Heatmap
    # [ ],[?] = outside of circular bed area
    # [-] = unknown bed heatmap values
    # [P] = known probe points from G29 P5, used to calculate corner
    # [?] = fake corner probe points used for bilinear interpolation
    #
    #     icol=0   1   2   3   4   5   6   7   8   9  10  11  12
    # irow=0  [?] [ ] [ ] [P] [-] [-] [P] [-] [-] [P] [ ] [ ] [?]  Y=50 = yStart
    #      1  [ ] [ ] [-] [-] [-] [-] [-] [-] [-] [-] [-] [ ] [ ]
    #      2  [ ] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [ ]
    #      3  [P] [-] [-] [P] [-] [-] [P] [-] [-] [P] [-] [-] [P]  Y=25
    #      4  [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-]
    #      5  [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-]
    #      6  [P] [-] [-] [P] [-] [-] [P] [-] [-] [P] [-] [-] [P]  Y=0
    #      7  [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-]
    #      8  [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-]
    #      9  [P] [-] [-] [P] [-] [-] [P] [-] [-] [P] [-] [-] [P]  Y=-25
    #      10 [ ] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [-] [ ]
    #      11 [ ] [ ] [-] [-] [-] [-] [-] [-] [-] [-] [-] [ ] [ ]
    #      12 [?] [ ] [ ] [P] [-] [-] [P] [-] [-] [P] [ ] [ ] [?]  Y=-50 = yEnd
    #        X=-50       X=-25        X=0         X=25        X=50
    #       xStart         |<--------->|   |<->|              xEnd
    #                          dprobe        dx
    
    # Matching Dennis's spreadsheet, going from top to bottom and left to right
    n = 13 # Number of rows/columns
    xmin = -50.0
    xmax = 50.0
    xStart = xmin
    xEnd = xmax
    ymin = -50.0
    ymax = 50.0
    yStart = ymax
    yEnd = ymin
    dprobe = 25.0 # Distance between known probe points

    # Correlate increasing/decreasing x/y with increasing/decreasing icol/irow
    xsign = float(round((xEnd-xStart)/abs(xEnd-xStart)))
    ysign = float(round((yEnd-yStart)/abs(yEnd-yStart)))
    
    # Define some paramters for the contour
    grid_length = abs(xEnd-xStart) # Grid Diameter
    idprobe = int(round(grid_length/dprobe)) - 1 # probe point index increment
    dx = dprobe/float(idprobe) # Distance Between adjacent heatmap points
    dy = dx # Distance Between adjacent heatmap points
    
    # Initialize the n by n grid
    heatmap = [[[] for i in range(n)] for i in range(n)]
    for ii in range(len(x_list)):
        irow, icol = gridval2idx(x_list[ii], y_list[ii], xStart, yStart, dx, dy)
        #print("{0} {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}".format(irow, icol, x_list[ii], y_list[ii], xStart, yStart, dx, dy))
        heatmap[irow][icol] = float(dz_list[ii])
    
    # Extrapolate off the bed to make the grid square
    # E.G., Top Left Corner
    # Solve for [?] to make interpolation for [-] points easier
    # [?] [ ] [ ] [P]
    # [ ] [ ] [-] [-]
    # [ ] [-] [-] [-]
    # [P] [-] [-] [P]
    extrapFlag = 0 # 0 = Weighted Average, 1 = Linear Extrapolation
    zvals = [0.0, 0.0, 0.0]
    dd = math.sqrt(dprobe*dprobe + dprobe*dprobe) # Diagonal distance from [?] to known point
    d_test = math.sqrt(dx*dx+dy*dy)
    #
    # Weighted Average Values
    dnorm = dprobe+dprobe+dd # Normalizing factor
    w = [0.0, 0.0, 0.0]
    w[0] = (dprobe + 0.5*(dd-dprobe)) / dnorm # Assign more weight to closer points
    w[1] = w[0] # Same distance
    w[2] = 1.0 - w[0] - w[1] # Assign less weight to the diagonal point
    #
    # Extrapolation Values
    # Step 1: Define the midpoint between the 3 known points
    #         radial distance, d2 = ddhalf = 0.5*dd
    #         z-value, z2 = average of three known probe points
    # Step 2: Draw a straight line from the known diagonal probe point to the corner
    # Step 3: Create the equation of the line from the two known points
    #   Point 1: The known diagonal probe point
    #            d1 = 0.0 # Treat it as origin
    #            z1 =  zvals[2] # Known diagonal probe point
    # Use the formulas for the equation of a straight line given two points
    # d = distance from the origin
    # m = slope = (z2-z1)/(d2-d1)
    # b = intercept = z2 = known diagonal probe point z-value, since it is at d=0
    # z_corner = m*dd + b
    ddhalf = 0.5*dd
    d1 = 0.0
    d2 = ddhalf
    #
    # Top Left Corner
    irow, icol = gridval2idx(xStart, yStart, xStart, yStart, dx, dy)
    #print("{0} {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}".format(irow, icol, x_list[ii], y_list[ii], xStart, yStart, dx, dy))
    zvals[0] = heatmap[irow+idprobe][icol]
    zvals[1] = heatmap[irow][icol+idprobe]
    zvals[2] = heatmap[irow+idprobe][icol+idprobe]
    if extrapFlag == 0: 
        heatmap[irow][icol] = w[0]*zvals[0] + w[1]*zvals[1] + w[2]*zvals[2]
    elif extrapFlag == 1:
        z1 = zvals[2]
        z2 = mean(zvals)
        m = (z2 - z1) / (d2 - d1)
        b = zvals[2]
        heatmap[irow][icol] = m*dd + b
    #
    # Top Right Corner
    irow, icol = gridval2idx(xEnd, yStart, xStart, yStart, dx, dy)
    #print("{0} {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}".format(irow, icol, x_list[ii], y_list[ii], xStart, yStart, dx, dy))
    zvals[0] = heatmap[irow+idprobe][icol]
    zvals[1] = heatmap[irow][icol-idprobe]
    zvals[2] = heatmap[irow+idprobe][icol-idprobe]
    if extrapFlag == 0: 
        heatmap[irow][icol] = w[0]*zvals[0] + w[1]*zvals[1] + w[2]*zvals[2]
    elif extrapFlag == 1: 
        z1 = zvals[2]
        z2 = mean(zvals)
        m = (z2 - z1) / (d2 - d1)
        b = zvals[2]
        heatmap[irow][icol] = m*dd + b
    #
    # Bottom Right Corner
    irow, icol = gridval2idx(xEnd, yEnd, xStart, yStart, dx, dy)
    #print("{0} {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}".format(irow, icol, x_list[ii], y_list[ii], xStart, yStart, dx, dy))
    zvals[0] = heatmap[irow-idprobe][icol]
    zvals[1] = heatmap[irow][icol-idprobe]
    zvals[2] = heatmap[irow-idprobe][icol-idprobe]
    test_y = linear_interp(0.0, dd, zvals[0], zvals[1], d_test)
    if extrapFlag == 0: 
        heatmap[irow][icol] = w[0]*zvals[0] + w[1]*zvals[1] + w[2]*zvals[2]
    elif extrapFlag == 1: 
        z1 = zvals[2]
        z2 = mean(zvals)
        m = (z2 - z1) / (d2 - d1)
        b = zvals[2]
        heatmap[irow][icol] = m*dd + b
    #
    # Bottom Left Corner
    irow, icol = gridval2idx(xStart, yEnd, xStart, yStart, dx, dy)
    #print("{0} {1} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}".format(irow, icol, x_list[ii], y_list[ii], xStart, yStart, dx, dy))
    zvals[0] = heatmap[irow-idprobe][icol]
    zvals[1] = heatmap[irow][icol+idprobe]
    zvals[2] = heatmap[irow-idprobe][icol+idprobe]
    test_x = linear_interp(0.0, dd, zvals[0], zvals[1], d_test)
    if extrapFlag == 0: 
        heatmap[irow][icol] = w[0]*zvals[0] + w[1]*zvals[1] + w[2]*zvals[2]
    elif extrapFlag == 1: 
        z1 = zvals[2]
        z2 = mean(zvals)
        m = (z2 - z1) / (d2 - d1)
        b = zvals[2]
        heatmap[irow][icol] = m*dd + b
        
    # Populate all interior points using interpolation
    for irow in range(n): 
        # Define known probe points, y
        iy1, iy2, iy3 = findProbePoints(irow, idprobe, n)
        y1 = yStart + ysign*float(iy1)*dy
        y2 = yStart + ysign*float(iy2)*dy
        y3 = yStart + ysign*float(iy3)*dy
        for icol in range(n): 
            # Define known probe points, x
            ix1, ix2, ix3 = findProbePoints(icol, idprobe, n)
            x1 = xStart + xsign*float(ix1)*dx
            x2 = xStart + xsign*float(ix2)*dx
            x3 = xStart + xsign*float(ix3)*dx
            
            # Only interpolate on unknown points
            if ((irow%idprobe != 0) or (icol%idprobe != 0)): 
                xq = xStart + xsign*float(icol)*dx
                yq = yStart + ysign*float(irow)*dy
                
                if (irow%idprobe == 0): # Linear Interpolation - Horizontal
                    zq = linear_interp(x1, x2, heatmap[irow][ix1], heatmap[irow][ix2], xq)
                elif (icol%idprobe == 0): # Linear Interpolation - Vertical
                    zq = linear_interp(y1, y2, heatmap[iy1][icol], heatmap[iy2][icol], yq)
                else: # Bilinear Interpolation
                
                    z11 = heatmap[iy1][ix1]
                    z12 = heatmap[iy2][ix1]
                    z21 = heatmap[iy1][ix2]
                    z22 = heatmap[iy2][ix2]
                    probe_points = [(x1, y1, z11),
                                    (x1, y2, z22),
                                    (x2, y1, z21),
                                    (x2, y2, z22)]
                    zq_tmp = bilinear_interpolation(xq, yq, probe_points)
                    zq = zq_tmp
                    
                    # Handle cases that align with the point
                    if (irow%idprobe == 0 or icol%idprobe == 0) and (irow > 0) and (irow < n-1): 
                    
                        # THIS IS BACKUP CODE THAT DID NOT PERFORM WELL DURING TESTING
                        # THIS IS NO LONGER BEING USED
                        
                        if (irow%idprobe == 0): 
                            # x3 = same, y3 = new
                            ix3 = ix1
                            x3 = x1
                        elif (icol%idprobe == 0): 
                            # x3 = new, y3 = same
                            iy3 = iy1
                            y3 = y1
                            
                        # Redo bilinear interpolation
                        z33 = heatmap[iy3][ix3]
                        z32 = heatmap[iy2][ix3]
                        z23 = heatmap[iy3][ix2]
                        z22 = heatmap[iy2][ix2]
                        probe_points = [(x2, y2, z22),
                                       (x2, y3, z23),
                                       (x3, y2, z32),
                                       (x3, y3, z33)]
                        zq_tmp = bilinear_interpolation(xq, yq, probe_points)
                        
                        # Take the average of the bilinear interpolation on both sides
                        zq = 0.5*(zq+zq_tmp)
                    
                    
                # Assign new heatmap value
                heatmap[irow][icol] = zq
                #print("xq = {0}, yq = {1}".format(str(xq),str(yq)))
                #print("x1 = {0}, y1 = {1}".format(str(x1),str(y1)))
                #print("x2 = {0}, y2 = {1}".format(str(x2),str(y2)))
                #print("x3 = {0}, y3 = {1}".format(str(x3),str(y3)))
                #print("\n")
                #print("{0} {1} {2} {3} {4} {5} {6} {7}\n".format(str(irow), str(icol), str(zq), str(zq_tmp), str(z11), str(z12), str(z21), str(z22)))
    

    # North Tilt (opposite of LCD)
    x0 = xmin
    y0 = ymin/2.0
    irow, icol = gridval2idx(x0, y0, xStart, yStart, dx, dy)
    ntower = heatmap[irow][icol]
    TN_list = [None]*5
    TN_list[0] = heatmap[irow][icol]
    TN_list[1] = heatmap[irow-1][icol]
    TN_list[2] = heatmap[irow][icol+1]
    TN_list[3] = heatmap[irow+1][icol+1]
    TN_list[3] = test_x #DEBUGGING
    TN_list[4] = heatmap[irow-1][icol+1]
    #print("TN Values\n")
    #print(*TN_list, sep='\n\n')
    #print("\n")
    TN = float(mean(TN_list))
    
    # West Tilt (left of LCD)
    x0 = xmax
    y0 = ymin/2
    irow, icol = gridval2idx(x0, y0, xStart, yStart, dx, dy)
    wtower = heatmap[irow][icol]
    TW_list = [None]*5
    TW_list[0] = heatmap[irow][icol]
    TW_list[1] = heatmap[irow-1][icol]
    TW_list[2] = heatmap[irow-1][icol-1]
    TW_list[3] = heatmap[irow][icol-1]
    TW_list[4] = heatmap[irow+1][icol-1]
    TW_list[4] = test_y #DEBUGGING
    #print("TW Values\n")
    #print(*TW_list, sep='\n\n')
    #print("\n")
    TW = float(mean(TW_list))
    
    # East Tilt (right of LCD)
    x0 = 0.0
    y0 = ymax
    irow, icol = gridval2idx(x0, y0, xStart, yStart, dx, dy)
    etower = heatmap[irow][icol]
    TE_list = [None]*6
    TE_list[0] = heatmap[irow][icol]
    TE_list[1] = heatmap[irow][icol+1]
    TE_list[2] = heatmap[irow][icol-1]
    TE_list[3] = heatmap[irow+1][icol]
    TE_list[4] = heatmap[irow+1][icol+1]
    TE_list[5] = heatmap[irow+1][icol-1]
    #print("TE Values\n")
    #print(*TE_list, sep='\n\n')
    #print("\n")
    TE = float(mean(TE_list))
    
    # Bowl Stats - Center
    x0 = 0.0
    y0 = 0.0
    irow, icol = gridval2idx(x0, y0, xStart, yStart, dx, dy)
    BC_list = [None]*9
    BC_list[0] = heatmap[irow-1][icol]
    BC_list[1] = heatmap[irow-1][icol+1]
    BC_list[2] = heatmap[irow-1][icol-1]
    BC_list[3] = heatmap[irow][icol]
    BC_list[4] = heatmap[irow][icol+1]
    BC_list[5] = heatmap[irow][icol-1]
    BC_list[6] = heatmap[irow+1][icol]
    BC_list[7] = heatmap[irow+1][icol+1]
    BC_list[8] = heatmap[irow+1][icol-1]
    #print("Bowl Center: \n")
    #print(*BC_list, sep='\n\n')
    #print("\n")
    BowlCenter = float(mean(BC_list))
    
    # Bowl Stats - Outside Ring
    OR_list = [None]*12
    # Left
    irow, icol = gridval2idx(xmin, 0.0, xStart, yStart, dx, dy)
    OR_list[0]  = heatmap[irow-idprobe][icol]
    OR_list[1]  = heatmap[irow][icol]
    OR_list[2]  = heatmap[irow+idprobe][icol]
    # Right
    irow, icol = gridval2idx(xmax, 0.0, xStart, yStart, dx, dy)
    OR_list[3]  = heatmap[irow-idprobe][icol]
    OR_list[4]  = heatmap[irow][icol]
    OR_list[5]  = heatmap[irow+idprobe][icol]
    # Top
    irow, icol = gridval2idx(0.0, ymax, xStart, yStart, dx, dy)
    OR_list[6]  = heatmap[irow][icol-idprobe]
    OR_list[7]  = heatmap[irow][icol]
    OR_list[8]  = heatmap[irow][icol+idprobe]
    # Bottom
    irow, icol = gridval2idx(0.0, ymin, xStart, yStart, dx, dy)
    OR_list[9]  = heatmap[irow][icol-idprobe]
    OR_list[10]  = heatmap[irow][icol]
    OR_list[11]  = heatmap[irow][icol+idprobe]
    #
    BowlOR = float(median(OR_list))
    #print("Outer Ring Values: \n")
    #print(*OR_list, sep='\n\n')
    #print("\n")
    #print("BowlOR = {0:.4f}".format(BowlOR))
    
    # Assign Towers to the current Tower X/Y/Z configuration (default is stock)
    TX = TN
    xtower = ntower
    TY = TW
    ytower = wtower
    TZ = TE
    ztower = etower
    if tower_flag == 1: 
        TX = TE
        xtower = etower
        TY = TN
        ytower = ntower
        TZ = TW
        ztower = wtower
    elif tower_flag == 2: 
        TX = TW
        xtower = wtower
        TY = TE
        ytower = etower
        TZ = TN
        ztower = ntower
    
    # Define Pass # according to the spreadsheet
    pass_num = runs - 1
    
    if pass_num == 0:
        # Check X Tower
        if xtower > ytower and xtower > ztower:
            xhigh[1] = 1
            
        # Check Y Tower
        if ytower > xtower and ytower > ztower:
            yhigh[1] = 1
            
        # Check Z Tower
        if ztower > xtower and ztower > ytower:
            zhigh[1] = 1
            
        # Save Values
        xhigh[0] = xhigh[1]
        yhigh[0] = yhigh[1]
        zhigh[0] = zhigh[1]
    else: 
        xhigh[1] = 0
        yhigh[1] = 0
        zhigh[1] = 0

    # Calculate High Parameter
    iHighTower = -1
    if xhigh[0] == 1:
        THigh = TX
        iHighTower = 0
    elif yhigh[0] == 1:
        THigh = TY
        iHighTower = 1
    else:
        THigh = TZ
        iHighTower = 2

    # Return Results
    return TX, TY, TZ, THigh, BowlCenter, BowlOR, xhigh, yhigh, zhigh, iHighTower
    
    
def determine_error(TX, TY, TZ, THigh, BowlCenter, BowlOR):
    z_error = float("{0:.4f}".format(TZ - THigh))
    x_error = float("{0:.4f}".format(TX - THigh))
    y_error = float("{0:.4f}".format(TY - THigh))
    c_error = float("{0:.4f}".format(BowlCenter - BowlOR))
    print('Z-Error: ' + str(z_error) + ' X-Error: ' + str(x_error) + ' Y-Error: ' + str(y_error) + ' C-Error: ' + str(c_error) + '\n')

    return z_error, x_error, y_error, c_error
    

def calibrate(port, z_error, x_error, y_error, c_error, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, max_runs, runs):
    calibrated = True
    if abs(z_error) >= 0.02:
        if iHighTower == 2:
            new_z = float("{0:.4f}".format(0.0))
        else:
            new_z = float("{0:.4f}".format(z_error + trial_z))
        calibrated = False
    else:
        new_z = trial_z

    if abs(x_error) >= 0.02:
        if iHighTower == 0:
            new_x = float("{0:.4f}".format(0.0))
        else:
            new_x = float("{0:.4f}".format(x_error + trial_x))
        calibrated = False
    else:
        new_x = trial_x

    if abs(y_error) >= 0.02:
        if iHighTower == 1:
            new_y = float("{0:.4f}".format(0.0))
        else:
            new_y = float("{0:.4f}".format(y_error + trial_y))
        calibrated = False
    else:
        new_y = trial_y

    if abs(c_error) >= 0.02:
        new_r = float("{0:.4f}".format(r_value - 4.0*c_error))
        calibrated = False
    else:
        new_r = r_value
        
    new_l = float("{0:.4f}".format(1.5*(new_r-r_value) + l_value))

    # making sure I am sending the lowest adjustment value
    #diff = 100
    #for i in [new_z, new_x ,new_y]:
    #    if abs(0-i) < diff:
    #        diff = 0-i
    #new_z += diff
    #new_x += diff
    #new_y += diff

    if calibrated:
        print ("Final values\nM666 Z{0} X{1} Y{2} \nM665 L{3} R{4}".format(str(new_z),str(new_x),str(new_y),str(new_l),str(new_r)))
    else:
        set_M_values(port, new_z, new_x, new_y, new_l, new_r)

    return calibrated, new_z, new_x, new_y, new_l, new_r

def set_M_values(port, z, x, y, l, r):

    print ("Setting values M666 X{0} Y{1} Z{2}, M665 L{3} R{4}".format(str(x),str(y),str(z),str(l),str(r)))

    port.write(('M666 X{0} Y{1} Z{2}\n'.format(str(x), str(y), str(z))).encode())
    out = port.readline().decode()
    port.write(('M665 L{0} R{1}\n'.format(str(l),str(r))).encode())
    out = port.readline().decode()
    
def output_pass_text(runs, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, x_list, y_list, z1_list, z2_list): 

    # Get the pass number corresponding to Dennis's spreadsheet
    pass_num = int(runs-1)
    
    # Create the file
    directory_location = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_name = "auto_cal_p5_pass{0}.txt".format(str(pass_num))
    output_path_name = os.path.join(directory_location + os.sep, file_name)
    file_object  = open(str(output_path_name), "w")
    
    # Output current pass values
    file_object.write("M666 X{0:.2f} Y{1:.2f} Z{2:.2f}\r\n".format(float(trial_x), float(trial_y), float(trial_z))) 
    file_object.write("M665 L{0:.4f} R{1:.4f}\r\n".format(float(l_value), float(r_value))) 
    file_object.write("\r\n") 
    
    # Highest Tower Value
    if int(iHighTower) == 0:
        file_object.write("Highest Tower: X\r\n") 
    elif int(iHighTower) == 1:
        file_object.write("Highest Tower: Y\r\n") 
    else: 
        file_object.write("Highest Tower: Z\r\n") 
    
    # Output Grid Points
    file_object.write("\r\n") 
    file_object.write("\r\n") 
    file_object.write("< 01:02:03 PM: G29 Auto Bed Leveling\r\n") 
    for ii in range(len(x_list)):
        file_object.write("< 01:02:03 PM: Bed X: {0:.3f} Y: {1:.3f} Z: {2:.3f}\r\n".format(float(x_list[ii]), float(y_list[ii]), float(z1_list[ii]))) 
        file_object.write("< 01:02:03 PM: Bed X: {0:.3f} Y: {1:.3f} Z: {2:.3f}\r\n".format(float(x_list[ii]), float(y_list[ii]), float(z2_list[ii]))) 
    
    # Close file stream
    file_object.close() 
    
    return


def run_calibration(port, firmFlag, trial_x, trial_y, trial_z, l_value, r_value, xhigh, yhigh, zhigh, max_runs, max_error, bed_temp, tower_flag, runs=0):
    runs += 1

    if runs > max_runs:
        sys.exit("Too many calibration attempts")
    print('\nCalibration pass {1}, run {2} out of {0}'.format(str(max_runs), str(runs-1), str(runs)))
    
    # Make sure the bed doesn't go cold
    if bed_temp >= 0: 
        port.write('M140 S{0}\n'.format(str(bed_temp)).encode())
    
    # Read G30 values and calculate values in columns B through H
    x_list, y_list, z1_list, z2_list, z_avg_list, dtap_list, dz_list = get_current_values(port, firmFlag)
    
    # Generate the P5 contour map
    TX, TY, TZ, THigh, BowlCenter, BowlOR, xhigh, yhigh, zhigh, iHighTower = calculate_contour(x_list, y_list, dz_list, runs, xhigh, yhigh, zhigh, tower_flag)
    
    # Output current pass results
    output_pass_text(runs, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, x_list, y_list, z1_list, z2_list)
    
    # Output Debugging Info
    #file_object  = open("debug_pass{0:d}.csv".format(int(runs-1)), "w")
    #file_object.write("X,Y,Z1,Z2,Z avg,Tap diff,Z diff,TX,TY,TZ,THigh,BowlCenter,BowlOR\r\n") 
    #z_med = median(z_avg_list)
    #for ii in range(len(x_list)):
    #    dz_list[ii] = z_avg_list[ii] - z_med
    #    file_object.write("{0:.4f},{1:.4f},{2:.4f},{3:.4f},".format(float(x_list[ii]),float(y_list[ii]),float(z1_list[ii]),float(z2_list[ii])))
    #    file_object.write("{0:.4f},{1:.4f},{2:.4f},".format(float(z_avg_list[ii]),float(dtap_list[ii]),float(dz_list[ii])))
    #    file_object.write("{0:.4f},{1:.4f},{2:.4f},{3:.4f},{4:.4f},{5:.4f}\r\n".format(float(TX),float(TY),float(TZ),float(THigh),float(BowlCenter),float(BowlOR)))
    #file_object.close() 
    
    # Calculate Error
    z_error, x_error, y_error, c_error = determine_error(TX, TY, TZ, THigh, BowlCenter, BowlOR)
    
    if abs(max([z_error, x_error, y_error, c_error], key=abs)) > max_error and runs > 1:
        sys.exit("Calibration error on non-first run exceeds set limit")

    calibrated, new_z, new_x, new_y, new_l, new_r = calibrate(port, z_error, x_error, y_error, c_error, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, max_runs, runs)
    
    if calibrated:
        print ("Calibration complete")
    else:
        calibrated, new_z, new_x, new_y, new_l, new_r, xhigh, yhigh, zhigh = run_calibration(port, firmFlag, new_x, new_y, new_z, new_l, new_r, xhigh, yhigh, zhigh, max_runs, max_error, bed_temp, tower_flag, runs)

    return calibrated, new_z, new_x, new_y, new_l, new_r, xhigh, yhigh, zhigh

# -----------------------------------------------------------------------------
# Main Entry Function
# -----------------------------------------------------------------------------
    
def main():
    # Default values
    max_runs = 14
    max_error = 1

    x0 = 0.0
    y0 = 0.0
    z0 = 0.0
    trial_z = x0
    trial_x = y0
    trial_y = z0
    r_value = 63.5
    step_mm = 57.14
    l_value = 123.0
    xhigh = [0]*2
    yhigh = [0]*2
    zhigh = [0]*2
    bed_temp = -1
    firmFlag = 0
    tower_flag = 0
    port_error = 'error'

    parser = argparse.ArgumentParser(description='Auto-Bed Cal. for Monoprice Mini Delta')
    parser.add_argument('-p','--port',default=port_error,help='Serial port',required=False)
    parser.add_argument('-x','--x0',type=float,default=x0,help='Starting x-value')
    parser.add_argument('-y','--y0',type=float,default=y0,help='Starting y-value')
    parser.add_argument('-z','--z0',type=float,default=z0,help='Starting z-value')
    parser.add_argument('-r','--r-value',type=float,default=r_value,help='Starting r-value')
    parser.add_argument('-l','--l-value',type=float,default=l_value,help='Starting l-value')
    parser.add_argument('-s','--step-mm',type=float,default=step_mm,help='Set steps-/mm')
    parser.add_argument('-me','--max-error',type=float,default=max_error,help='Maximum acceptable calibration error on non-first run')
    parser.add_argument('-mr','--max-runs',type=int,default=max_runs,help='Maximum attempts to calibrate printer')
    parser.add_argument('-bt','--bed-temp',type=int,default=bed_temp,help='Bed Temperature')
    parser.add_argument('-ff','--firmFlag',type=int,default=firmFlag,help='Firmware Flag (0 = Stock; 1 = Marlin)')
    parser.add_argument('-tf','--tower_flag',type=int,default=tower_flag,help='Tower Flag (0 = Stock and old Marlin; 1 = Marlin 1.3.3, 2 = experimental)')
    parser.add_argument('-f','--file',type=str,dest='file',default=None,
        help='File with settings, will be updated with latest settings at the end of the run')
    args = parser.parse_args()

    port = establish_serial_connection(args.port)        

    if args.file:
        try:
            with open(args.file) as data_file:
                settings = json.load(data_file)
            tower_flag = int(settings.get('tower_flag', tower_flag))
            firmFlag = int(settings.get('firmFlag', firmFlag))
            bed_temp = int(settings.get('bed_temp', bed_temp))
            max_runs = int(settings.get('max_runs', max_runs))
            max_error = float(settings.get('max_error', max_error))
            trial_z = float(settings.get('z', trial_z))
            trial_x = float(settings.get('x', trial_x))
            trial_y = float(settings.get('y', trial_y))
            r_value = float(settings.get('r', r_value))
            l_value = float(settings.get('l', l_value))
            step_mm = float(settings.get('step', step_mm))

        except:
            tower_flag = args.tower_flag
            firmFlag = args.firmFlag
            bed_temp = args.bed_temp
            max_error = args.max_error
            max_runs = args.max_runs
            trial_z = args.z0
            trial_x = args.x0
            trial_y = args.y0
            r_value = args.r_value
            step_mm = args.step_mm
            max_runs = args.max_runs
            l_value = args.l_value
            pass
    else: 
        tower_flag = args.tower_flag
        firmFlag = args.firmFlag
        bed_temp = args.bed_temp
        max_error = args.max_error
        max_runs = args.max_runs
        trial_z = args.z0
        trial_x = args.x0
        trial_y = args.y0
        r_value = args.r_value
        step_mm = args.step_mm
        max_runs = args.max_runs
        l_value = args.l_value
        
    if args.port == port_error:
        print ('auto_cal_p5_v0.py: error: the following arguments are required: -p/--port\n')
        
    elif port:
    
        # Firmware
        if firmFlag == 0:
            print("Using Monoprice/Malyan Firmware\n")
        elif firmFlag == 1:
            print("Using Marlin Firmware\n")
            
        # Tower Setup
        if tower_flag == 0:
            print("Tower Rotation Setup 0\n")
        elif tower_flag == 1:
            print("Tower Rotation Setup 1\n")
        elif tower_flag == 2:
            print("Tower Rotation Setup 2\n")
    
        #Set Bed Temperature
        if bed_temp >= 0:
            print ('Setting bed temperature to {0} C\n'.format(str(bed_temp)))
            port.write('M140 S{0}\n'.format(str(bed_temp)).encode())
            out = port.readline().decode()
            
        # Set the proper step/mm
        print ('Setting up M92 X{0} Y{0} Z{0}\n'.format(str(step_mm)))
        port.write(('M92 X{0} Y{0} Z{0}\n'.format(str(step_mm))).encode())
        out = port.readline().decode()
        
        print ('Setting up M665 L{0} R{1}\n'.format(str(l_value),str(r_value)))
        port.write(('M665 L{0}\n'.format(str(l_value))).encode())
        out = port.readline().decode()

        if firmFlag == 1:
            print ('Setting up M206 X0 Y0 Z0\n')
            port.write('M206 X0 Y0 Z0\n'.encode())
            out = port.readline().decode()
        
            print ('Clearing mesh with M421 C\n')
            port.write('M421 C\n'.encode())
            out = port.readline().decode()

        set_M_values(port, trial_z, trial_x, trial_y, l_value, r_value)

        print ('\nStarting calibration')

        calibrated, new_z, new_x, new_y, new_l, new_r, xhigh, yhigh, zhigh = run_calibration(port, firmFlag, trial_x, trial_y, trial_z, l_value, r_value, xhigh, yhigh, zhigh, max_runs, args.max_error, bed_temp, tower_flag)

        port.close()

        if calibrated:
            if firmFlag == 1:
                print ('Run mesh bed leveling before printing: G29\n')
            if args.file:
                data = {'z':new_z, 'x':new_x, 'y':new_y, 'r':new_r, 'l': new_l, 'step':step_mm, 'max_runs':max_runs, 'max_error':max_error, 'bed_temp':bed_temp}
                with open(args.file, "w") as text_file:
                    text_file.write(json.dumps(data))
    
    else: 
        print ('There was an unknown error with the port.\n')
        
    # This next line does not work in Python2. 
    # Uncomment it when making the executable.
    #input("Press Enter to continue...")

if __name__ == '__main__':
    main()
