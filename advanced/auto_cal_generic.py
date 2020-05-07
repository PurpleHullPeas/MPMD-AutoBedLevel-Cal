#!/usr/bin/python

# Updated version of the original script
#
# This script is kind of a sandbox right now.
# https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal

from serial import Serial, SerialException, PARITY_ODD, PARITY_NONE
import sys
import argparse
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
# User Input Function
# -----------------------------------------------------------------------------
#https://gist.github.com/garrettdreyfus/8153571
def yes_or_no(question):
    while "the answer is invalid":
        try:
            reply = str(raw_input(question+' (y/n): ')).lower().strip()
        except:
            reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


# -----------------------------------------------------------------------------
# Carbon Paper Function
# -----------------------------------------------------------------------------

# mpmd_carbon_marlin.gcode
# https://drive.google.com/open?id=1ti26of-TKoAjkr2QLdoFnVoZAiNE0M7G 
def draw_carbon_paper_dots(port, hotend_temp):
    #Setup Probe Points
    number_rows = 18
    x_list = [None]*number_rows
    y_list = [None]*number_rows
    #
    x_list[0] = 0.0
    y_list[0] = 0.0
    #
    x_list[1] = 0.0
    y_list[1] = 50.0
    #
    x_list[2] = 0.0
    y_list[2] = 45.0
    #
    x_list[3] = 0.0
    y_list[3] = 0.0
    #
    x_list[4] = -0.0
    y_list[4] = -50.0
    #
    x_list[5] = -43.301
    y_list[5] = -25.0
    #
    x_list[6] = 0.0
    y_list[6] = 0.0
    #
    x_list[7] = 43.301
    y_list[7] = 25.0
    #
    x_list[8] = 43.301
    y_list[8] = -25.0
    #
    x_list[9] = 0.0
    y_list[9] = 0.0
    #
    x_list[10] = -43.301
    y_list[10] = 25.0
    #
    x_list[11] = 50.0
    y_list[11] = 0.0
    #
    x_list[12] = 0.0
    y_list[12] = 0.0
    #
    x_list[13] = -50.0
    y_list[13] = 0.0
    #
    x_list[14] = -25.0
    y_list[14] = -43.301
    #
    x_list[15] = 25.0
    y_list[15] = 43.301
    #
    x_list[16] = 25.0
    y_list[16] = -43.301
    #
    x_list[17] = -25.0
    y_list[17] = 43.301

    # Send Gcode Commands
    if hotend_temp >= 0: # warm up the hot end for better carbon imprint
        port.write('M109 S{0}\n'.format(str(hotend_temp)).encode())
    port.write(('M851 D0 R10 F2000\n').encode())
    port.write(('G28\n').encode()) # Home
    port.write(('G90\n').encode()) # Absolute Positioning
    port.write(('G0 Z10 F5000\n').encode())
    for ii in range(len(x_list)): 
        #print('{0}: Sending G0 X{1} Y{2}\n'.format(ii, x_list[ii], y_list[ii]))
        port.write(('G0 X{0} Y{1}\n'.format(x_list[ii], y_list[ii])).encode()) # Move to desired position
        port.write(('G30\n').encode()) # Probe
        tmp = get_points(port) # Clear data from buffer
        port.write(('G0 Z10\n').encode()) # Move effector up
        
    port.write(('G28\n').encode()) # Home

    # Exit
    return

    

# -----------------------------------------------------------------------------
# Autoleveling Functions
# -----------------------------------------------------------------------------
    
def get_current_values(port, firmFlag, calibration_pattern):
    # Replacing G29 P5 with manual probe points for cross-firmware compatibility
    # G28 ; home
    # G1 Z15 F6000; go to safe distance
    # Start Loop
    #     G1 X## Y##; go to specified location
    #     G30 ;probe bed for z values
    #     G30 ;probe bed again for z values
    # End Loop
    # G28 ; return home
    
    # Initialize Lists
    number_rows = 21
    if calibration_pattern == 5: 
        number_rows = 21
    elif abs(calibration_pattern) == 2: 
        number_rows = 4
    else: 
        number_rows = 4+12
    x_list = [None]*number_rows
    y_list = [None]*number_rows
    z1_list = [None]*number_rows
    z2_list = [None]*number_rows
    z_avg_list = [None]*number_rows
    dtap_list = [None]*number_rows
    dz_list = [None]*number_rows
    
    # Select the proper calibration pattern
    if calibration_pattern == 5: 
        # Assign X Coordinates (G29 P5)
        x_list[0] = -25.0
        x_list[1] = 0.0
        x_list[2] = 25.0
        x_list[3] = 50.0
        x_list[4] = 25.0
        x_list[5] = 0.0
        x_list[6] = -25.0
        x_list[7] = -50.0
        x_list[8] = -50.0
        x_list[9] = -25.0
        x_list[10] = 0.0
        x_list[11] = 25.0
        x_list[12] = 50.0
        x_list[13] = 50.0
        x_list[14] = 25.0
        x_list[15] = 0.0
        x_list[16] = -25.0
        x_list[17] = -50.0
        x_list[18] = -25.0
        x_list[19] = 0.0
        x_list[20] = 25.0
        
        # Assign Y Coordinates (G29 P5)
        y_list[0] = -50.0
        y_list[1] = -50.0
        y_list[2] = -50.0
        y_list[3] = -25.0
        y_list[4] = -25.0
        y_list[5] = -25.0
        y_list[6] = -25.0
        y_list[7] = -25.0
        y_list[8] = 0.0
        y_list[9] = 0.0
        y_list[10] = 0.0
        y_list[11] = 0.0
        y_list[12] = 0.0
        y_list[13] = 25.0
        y_list[14] = 25.0
        y_list[15] = 25.0
        y_list[16] = 25.0
        y_list[17] = 25.0
        y_list[18] = 50.0
        y_list[19] = 50.0
        y_list[20] = 50.0

    elif abs(calibration_pattern) == 2:  
        # G29 P2

        # Experimental, choose 50 or 25 mm radius
        radius = 50.0
        if calibration_pattern == -2: 
            radius = 25.0

        # Tower 3/Z/E
        theta = 90.0
        x_tmp, y_tmp = rect(radius, theta)
        x_list[0] = x_tmp # 0.0
        y_list[0] = y_tmp # 50.0
        #
        # Tower 1/X/N
        theta = -150.0
        x_tmp, y_tmp = rect(radius, theta)
        x_list[1] = x_tmp # -43.3
        y_list[1] = y_tmp # -25.0
        #
        # Tower 2/Y/W
        theta = -30.0
        x_tmp, y_tmp = rect(radius, theta)
        x_list[2] = x_tmp # 43.3
        y_list[2] = y_tmp # -25.0
        #
        # Center
        x_list[3] = 0.0
        y_list[3] = 0.0

    else:  

        #Experimental pattern
        # E.G. 2550 => 25 mm radius for towers, 50 mm radius for outer ring.
        inner_radius = math.trunc(calibration_pattern/100.0)
        outer_radius = abs(calibration_pattern - 100.0*inner_radius)
        print('inner radius {0}, outer radius {1}\n'.format(inner_radius, outer_radius))
        #inner_radius = 25.0
        #outer_radius = 50.0
        #
        # Tower 3/Z/E
        theta = 90.0
        x_tmp, y_tmp = rect(inner_radius, theta)
        x_list[0] = x_tmp
        y_list[0] = y_tmp
        #
        # Tower 1/X/N
        theta = -150.0
        x_tmp, y_tmp = rect(inner_radius, theta)
        x_list[1] = x_tmp
        y_list[1] = y_tmp
        #
        # Tower 2/Y/W
        theta = -30.0
        x_tmp, y_tmp = rect(inner_radius, theta)
        x_list[2] = x_tmp
        y_list[2] = y_tmp
        #
        # Center
        x_list[3] = 0.0
        y_list[3] = 0.0

        # insert code for experiment
        theta = 0.0 # Start at 0 degrees
        dtheta = 15.0 # increment by 15 degrees
        for ii in range(4, len(x_list)):
            x_tmp, y_tmp = rect(outer_radius, theta)
            x_list[ii] = x_tmp
            y_list[ii] = y_tmp
            theta = theta + dtheta

    # Send Gcodes
    port.write(('G28\n').encode()) # Home
    
    if firmFlag == 1: 
        # Marlin
        port.write(('G1 Z15 F6000\n').encode()) # Move to safe distance
    else:
        # Stock Firmware
        if calibration_pattern == 5:
            port.write(('G29 P5 V4\n').encode())
        else: 
            port.write(('G29 P2 V4\n').encode())

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

def calculate_contour_experimental(dz_list, tower_flag, calibration_pattern):

    # Rotate the towers according to M665 X Y Z
    TX, TY, TZ, xtower, ytower, ztower = rotate_tower_values(dz_list[1], dz_list[2], dz_list[0], dz_list[1], dz_list[2], dz_list[0], tower_flag)

    # Center Value = Center Point
    BowlCenter = dz_list[0]

    # Outer Ring
    BowlOR = 0.0
    if abs(calibration_pattern) == 2: 
        # Simple 4 point pattern
        BowlOR = (TX + TY + TZ) / 3.0
    else: 
        # Experimental Outer Ring
        npts = len(dz_list) - 4
        OR_list = [None]*npts
        for ii in range(4, len(dz_list)):
            OR_list[ii-4] = dz_list[ii]
        BowlOR = float(median(OR_list))

    # Return Results
    return TX, TY, TZ, xtower, ytower, ztower, BowlCenter, BowlOR

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
    
def calculate_contour_p5(x_list, y_list, dz_list, tower_flag):
    
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
                                    (x1, y2, z12),
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

    # Rotate the towers according to M665 X Y Z
    TX, TY, TZ, xtower, ytower, ztower = rotate_tower_values(TN, TW, TE, ntower, wtower, etower, tower_flag)

    # Return Results
    return TX, TY, TZ, xtower, ytower, ztower, BowlCenter, BowlOR
    

# Rotate the towers according to M665 X Y Z
def rotate_tower_values(TN, TW, TE, ntower, wtower, etower, tower_flag): 
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
    return TX, TY, TZ, xtower, ytower, ztower

    
def determine_high_tower(xtower, ytower, ztower, TX, TY, TZ, iHighTower):
    # Determine the highest tower
    if iHighTower == -1:
        if xtower > ytower and xtower > ztower: 
            # X Tower
            iHighTower = 0
        elif ytower > xtower and ytower > ztower: 
            # Y Tower
            iHighTower = 1
        elif ztower > xtower and ztower > ytower: 
            # Z Tower
            iHighTower = 2

    # Calculate High Tower Parameter
    THigh = 0.0
    if iHighTower == 0:
        THigh = TX
    elif iHighTower == 1:
        THigh = TY
    else:
        THigh = TZ

    return iHighTower, THigh

def determine_error(TX, TY, TZ, THigh, BowlCenter, BowlOR):
    z_error = float("{0:.4f}".format(TZ - THigh))
    x_error = float("{0:.4f}".format(TX - THigh))
    y_error = float("{0:.4f}".format(TY - THigh))
    c_error = float("{0:.4f}".format(BowlCenter - BowlOR))
    print('Z-Error: ' + str(z_error) + ' X-Error: ' + str(x_error) + ' Y-Error: ' + str(y_error) + ' C-Error: ' + str(c_error) + '\n')

    return z_error, x_error, y_error, c_error
    

def calibrate(port, z_error, x_error, y_error, c_error, trial_x, trial_y, trial_z, l_value, r_value, Lratio, iHighTower, max_runs, runs):
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
        
    new_l = float("{0:.4f}".format(Lratio*(new_r-r_value) + l_value))

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
    
def output_M421(port, trial_x, trial_y, trial_z, l_value, r_value, aaa, bbb, ccc, ddd, eee, fff, iHighTower): 
    number_rows = 7
    M421_Data = [None]*number_rows
    new_line_str = "\r\n" # Octopi = "\r\n", Windows = "\n"
    
    # Send Bed Mesh Command
    port.write(('M421 ;\n').encode())
    
    # Clear port data until we reach M421
    while True:
        out = port.readline().decode()
        #print("{0}\n".format(out))
        if 'Grid spacing' in out:
            break
            
    # Create the file
    directory_location = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_name = "M421_data.txt"
    output_path_name = os.path.join(directory_location + os.sep, file_name)
    file_object  = open(str(output_path_name), "w")
    
    # Output current pass values
    file_object.write("M666 X{0:.2f} Y{1:.2f} Z{2:.2f}".format(float(trial_x), float(trial_y), float(trial_z))) 
    file_object.write(new_line_str) 
    file_object.write("M665 L{0:.4f} R{1:.4f} A{2:.4f} B{3:.4f} C{4:.4f} D{5:.4f} E{6:.4f} F{7:.4f}".format(float(l_value), float(r_value), float(aaa), float(bbb), float(ccc), float(ddd), float(eee), float(fff))) 
    file_object.write(new_line_str) 
    file_object.write(new_line_str) 
            
    # Write Data to the text file
    file_object.write(out) 
    for ii in range(len(M421_Data)): 
        out = port.readline().decode()
        file_object.write(out) 
    
def output_pass_text(runs, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, x_list, y_list, z1_list, z2_list): 

    new_line_str = "\r\n" # Octopi = "\r\n", Windows = "\n"

    # Get the pass number corresponding to Dennis's spreadsheet
    pass_num = int(runs-1)
    
    # Create the file
    directory_location = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_name = "auto_cal_p5_pass{0}.txt".format(str(pass_num))
    output_path_name = os.path.join(directory_location + os.sep, file_name)
    file_object  = open(str(output_path_name), "w")
    
    # Output current pass values
    file_object.write("M666 X{0:.2f} Y{1:.2f} Z{2:.2f}".format(float(trial_x), float(trial_y), float(trial_z))) 
    file_object.write(new_line_str) 
    file_object.write("M665 L{0:.4f} R{1:.4f}".format(float(l_value), float(r_value))) 
    file_object.write(new_line_str) 
    file_object.write(new_line_str) 
    
    # Highest Tower Value
    if int(iHighTower) == 0:
        file_object.write("Highest Tower: X" + new_line_str) 
    elif int(iHighTower) == 1:
        file_object.write("Highest Tower: Y" + new_line_str) 
    else: 
        file_object.write("Highest Tower: Z" + new_line_str) 
    
    # Output Grid Points
    file_object.write(new_line_str) 
    file_object.write(new_line_str) 
    file_object.write("< 01:02:03 PM: G29 Auto Bed Leveling" + new_line_str) 
    for ii in range(len(x_list)):
        file_object.write("< 01:02:03 PM: Bed X: {0:.3f} Y: {1:.3f} Z: {2:.3f}{3}".format(float(x_list[ii]), float(y_list[ii]), float(z1_list[ii]), new_line_str)) 
        file_object.write("< 01:02:03 PM: Bed X: {0:.3f} Y: {1:.3f} Z: {2:.3f}{3}".format(float(x_list[ii]), float(y_list[ii]), float(z2_list[ii]), new_line_str)) 
    
    # Close file stream
    file_object.close() 
    
    return


def run_calibration(port, firmFlag, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, max_runs, max_error, bed_temp, hotend_temp, tower_flag, Lratio, calibration_pattern, runs=0):
    runs += 1

    if runs > max_runs:
        sys.exit("Too many calibration attempts")
    print('\nCalibration pass {1}, run {2} out of {0}'.format(str(max_runs), str(runs-1), str(runs)))
    
    # Make sure the bed doesn't go cold
    if bed_temp >= 0: 
        port.write('M140 S{0}\n'.format(str(bed_temp)).encode())

    # Make sure the hotend doesn't go cold
    if hotend_temp >= 0: 
        port.write('M109 S{0}\n'.format(str(hotend_temp)).encode())
    
    # Read G30 or G29 probe values
    x_list, y_list, z1_list, z2_list, z_avg_list, dtap_list, dz_list = get_current_values(port, firmFlag, calibration_pattern)
    
    if calibration_pattern == 5: 
        # Generate the P5 contour map
        TX, TY, TZ, xtower, ytower, ztower, BowlCenter, BowlOR = calculate_contour_p5(x_list, y_list, dz_list, tower_flag)
    else: 
        # Either P2 or Experimental Calibration
        TX, TY, TZ, xtower, ytower, ztower, BowlCenter, BowlOR = calculate_contour_experimental(dz_list, tower_flag, calibration_pattern)

    # Determine the highest tower
    iHighTower, THigh = determine_high_tower(xtower, ytower, ztower, TX, TY, TZ, iHighTower)
    
    # Output current pass results
    if calibration_pattern == 5: 
        output_pass_text(runs, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, x_list, y_list, z1_list, z2_list)
    
    #print('DEBUGGING')
    
    # Calculate Error
    z_error, x_error, y_error, c_error = determine_error(TX, TY, TZ, THigh, BowlCenter, BowlOR)
    
    if abs(max([z_error, x_error, y_error, c_error], key=abs)) > max_error and runs > 1:
        sys.exit("Calibration error on non-first run exceeds set limit")

    calibrated, new_z, new_x, new_y, new_l, new_r = calibrate(port, z_error, x_error, y_error, c_error, trial_x, trial_y, trial_z, l_value, r_value, Lratio, iHighTower, max_runs, runs)
    
    if calibrated:
        print ("Calibration complete")
    else:
        calibrated, new_z, new_x, new_y, new_l, new_r, iHighTower = run_calibration(port, firmFlag, new_x, new_y, new_z, new_l, new_r, iHighTower, max_runs, max_error, bed_temp, hotend_temp, tower_flag, Lratio, calibration_pattern, runs)

    return calibrated, new_z, new_x, new_y, new_l, new_r, iHighTower

# -----------------------------------------------------------------------------
# Main Entry Function
# -----------------------------------------------------------------------------
    
def main():

    # Default values
    port_default = 'error'
    x0 = 0.0
    y0 = 0.0
    z0 = 0.0
    step_mm = 57.14
    r_value = 63.5
    l_value = 123.0
    Lratio = 1.5
    aaa = 0.0
    bbb = 0.0
    ccc = 0.0
    ddd = 0.0
    eee = 0.0
    fff = 0.0
    bed_temp = -1
    hotend_temp = -1
    firmFlag = 0
    tower_flag = 0
    calibration_pattern = 2

    # Other Initializations
    max_runs = 14
    max_error = 1
    port_error = 'error'
    
    # Initialize trial values
    trial_z = x0
    trial_x = y0
    trial_y = z0
    
    # Set iHighTower if initializing at non-zero M666 XYZ
    iHighTower = -1 # x=0, y=1, z=2
    test_tmp = abs(trial_z) + abs(trial_x) + abs(trial_y)
    if (test_tmp > 0.0001) and (iHighTower < 0): 
        if (trial_x > trial_y) and (trial_x > trial_z): 
            iHighTower = 0 #X
        elif (trial_y > trial_x) and (trial_y > trial_z): 
            iHighTower = 1 #Y
        elif (trial_y > trial_x) and (trial_y > trial_z): 
            iHighTower = 2 #Z
        else: 
            iHighTower = -1 # Calculate later
            
    # Parse command line inputs
    parser = argparse.ArgumentParser(description='Auto-Bed Cal. for Monoprice Mini Delta')
    parser.add_argument('-p','--port',default=port_default,help='Serial port',required=False)
    parser.add_argument('-x','--x0',type=float,default=x0,help='Starting M666 X-value')
    parser.add_argument('-y','--y0',type=float,default=y0,help='Starting M666 Y-value')
    parser.add_argument('-z','--z0',type=float,default=z0,help='Starting M666 Z-value')
    parser.add_argument('-r','--r_value',type=float,default=r_value,help='Starting M665 R-value')
    parser.add_argument('-l','--l_value',type=float,default=l_value,help='Starting M665 L-value')
    parser.add_argument('-s','--step_mm',type=float,default=step_mm,help='Set steps-/mm M92 XYZ')
    parser.add_argument('-me','--max_error',type=float,default=max_error,help='Maximum acceptable calibration error on non-first run')
    parser.add_argument('-mr','--max_runs',type=int,default=max_runs,help='Maximum attempts to calibrate printer')
    parser.add_argument('-bt','--bed_temp',type=int,default=bed_temp,help='Bed Temperature')
    parser.add_argument('-ht','--hotend_temp',type=int,default=hotend_temp,help='Hotend Temperature')
    parser.add_argument('-ff','--firmFlag',type=int,default=firmFlag,help='Firmware Flag (0 = Stock; 1 = Marlin)')
    parser.add_argument('-tf','--tower_flag',type=int,default=tower_flag,help='Tower Flag (0 = Stock and old Marlin4MPMD; 1 = Marlin4MPMD 1.3.3, 2 = experimental)')
    parser.add_argument('-patt','--calibration_pattern',type=int,default=calibration_pattern,help='Calibration Pattern (2 = Stock G29 P2 Pattern, 5 = Stock G29 P5 Pattern, -2 = P2 Pattern at 25 mm radius, 2550 = Experimental for Marlin4MPMD, 2537.5 = Experimental for Marlin4MPMD')
    parser.add_argument('-ratio','--Lratio',type=float,default=Lratio,help='Experimental M665 L adjustment ratio')
    parser.add_argument('-aaa','--aaa',type=float,default=aaa,help='Trial M665 A-value (Marlin4MPMD Only)')
    parser.add_argument('-bbb','--bbb',type=float,default=bbb,help='Trial M665 B-value (Marlin4MPMD Only)')
    parser.add_argument('-ccc','--ccc',type=float,default=ccc,help='Trial M665 C-value (Marlin4MPMD Only)')
    parser.add_argument('-ddd','--ddd',type=float,default=ddd,help='Trial M665 D-value (Marlin4MPMD Only)')
    parser.add_argument('-eee','--eee',type=float,default=eee,help='Trial M665 E-value (Marlin4MPMD Only)')
    parser.add_argument('-fff','--fff',type=float,default=fff,help='Trial M665 F-value (Marlin4MPMD Only)')
    args = parser.parse_args()

    port = establish_serial_connection(args.port)        
    tower_flag = args.tower_flag
    firmFlag = args.firmFlag
    bed_temp = args.bed_temp
    hotend_temp = args.hotend_temp
    max_error = args.max_error
    max_runs = args.max_runs
    trial_z = args.z0
    trial_x = args.x0
    trial_y = args.y0
    r_value = args.r_value
    step_mm = args.step_mm
    max_runs = args.max_runs
    l_value = args.l_value
    aaa = args.aaa
    bbb = args.bbb
    ccc = args.ccc
    ddd = args.ddd
    eee = args.eee
    fff = args.fff
    Lratio = args.Lratio
    calibration_pattern = args.calibration_pattern
        
    if args.port == port_error:
        print ('auto_cal_generic.py: error: the following arguments are required: -p/--port\n')
        
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
        else: 
            tower_flag = 0
    
        # Set Bed Temperature
        if bed_temp >= 0:
            print ('Setting bed temperature to {0} C\n'.format(str(bed_temp)))
            port.write('M140 S{0}\n'.format(str(bed_temp)).encode())
            out = port.readline().decode()

        # Set Hotend Temperature
        if hotend_temp >= 0:
            print ('Setting hotend temperature to {0} C\n'.format(str(hotend_temp)))
            port.write('M109 S{0}\n'.format(str(hotend_temp)).encode())
            out = port.readline().decode()
            
        # Set the proper step/mm
        print ('Setting up M92 X{0} Y{0} Z{0}\n'.format(str(step_mm)))
        port.write(('M92 X{0} Y{0} Z{0}\n'.format(str(step_mm))).encode())
        out = port.readline().decode()
        
        print ('Setting up M665 L{0} R{1}\n'.format(str(l_value),str(r_value)))
        port.write(('M665 L{0} R{1}\n'.format(str(l_value),str(r_value))).encode())
        out = port.readline().decode()

        if firmFlag == 1:
            print ('Setting up M206 X0 Y0 Z0\n')
            port.write('M206 X0 Y0 Z0 ;\n'.encode())
            out = port.readline().decode()
        
            print ('Clearing mesh with M421 C\n')
            port.write('M421 C\n'.encode())
            out = port.readline().decode()

            test_tmp = abs(aaa) + abs(bbb) + abs(ccc) + abs(ddd) + abs(eee) + abs(fff)
            if firmFlag == 1:
                print ('Setting Trial M665 ABCDEF Values\n')
                print ('M665 A{0} B{1} C{2} D{3} E{4} F{5} ;\n'.format(str(aaa), str(bbb), str(ccc), str(ddd), str(eee), str(fff)))
                try:
                    port.write(('M665 A{0} B{1} C{2} D{3} E{4} F{5} ;\n'.format(str(aaa), str(bbb), str(ccc), str(ddd), str(eee), str(fff))).encode())
                    out = port.readline().decode()
                except:
                    print ('Failed at Setting M665 ABCDEF Values\n')

        set_M_values(port, trial_z, trial_x, trial_y, l_value, r_value)

        print ('\nStarting calibration')

        calibrated = False
        calibrated, new_z, new_x, new_y, new_l, new_r, iHighTower = run_calibration(port, firmFlag, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, max_runs, args.max_error, bed_temp, hotend_temp, tower_flag, Lratio, calibration_pattern)

        # Post Calibration Actions/Logging
        if calibrated:
              
            port.write(('G28 ;\n').encode()) # Home
            
            if calibration_pattern != 5: 
                if yes_or_no('Generate G29 P5 Heatmap Data for final pass? '):
                    calibration_pattern = 5
                    x_list, y_list, z1_list, z2_list, z_avg_list, dtap_list, dz_list = get_current_values(port, firmFlag, calibration_pattern)
                    output_pass_text(10000, trial_x, trial_y, trial_z, l_value, r_value, iHighTower, x_list, y_list, z1_list, z2_list)
                    port.write(('G28 ;\n').encode()) # Home
            
            if yes_or_no('Run carbon paper test now? '): 
                draw_carbon_paper_dots(port, hotend_temp)
                
            if firmFlag == 1:
                print ('On Marlin4MPMD 1.3.3, you need to re-run G29. ')
                if yes_or_no('Run G29 and output M421 data now? '):
                    port.write(('G29 ;\n').encode()) # Mesh Leveling
                    port.write(('G28 ;\n').encode()) # Home
                    output_M421(port, trial_x, trial_y, trial_z, l_value, r_value, aaa, bbb, ccc, ddd, eee, fff, iHighTower)
            
            if yes_or_no('Save with M500? '): 
                port.write(('M500 ;\n').encode()) # Save to memory
                
        # Close the com port
        port.close()

    else: 
        print ('There was an unknown error with the port.\n')
        
    # This next line does not work in Python2. 
    # Uncomment it when making the executable.
    #input("Press Enter to continue...")

if __name__ == '__main__':
    main()
