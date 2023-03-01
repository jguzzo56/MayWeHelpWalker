import os
import board
import time
import busio
import adafruit_drv2605
import adafruit_tca9548a
import adafruit_vl53l0x
from math import floor
from adafruit_rplidar import RPLidar

i2c=busio.I2C(board.SCL, board.SDA)
tca=adafruit_tca9548a.TCA9548A(i2c)

# Initialize the motors
lMotor1 = adafruit_drv2605.DRV2605(tca[6])
lMotor2 = adafruit_drv2605.DRV2605(tca[5])
rMotor1 = adafruit_drv2605.DRV2605(tca[7])
rMotor2 = adafruit_drv2605.DRV2605(tca[4])

# Initialize the Time of Flight sensors
tof1 = adafruit_vl53l0x.VL53L0X(tca[0])
#tof2 = adafruit_vl53l0x.VL53L0X(tca[1])

# Set the port name of the Lidar
PORT_NAME = '/dev/ttyUSB0'
#baudrate=9600

# Initialize the Lidar
lidar = RPLidar(None, PORT_NAME,timeout=3)

# Declare Variables
scan_count = 0 # Number of scans done
scan_data = [0]*360 # Array with the data from the lidar scan
max_distance = 0 # To find the max distance in a scan
min_distance = 2743 # 9 feet, To find the min distance in a scan
direction = 0 # To find direction of hazard
max_angle = 0 # To find the angle where the max distance is
min_angle = 0 # To find the angle where the min distance is
cond = 6 # To set the condition

# Notify the user to press Ctrl-C to pass a KeyboardInterrupt Exception to stop the walker
print('Press Ctrl-C to stop')

# Function to tell which motors to vibrate and at what intensity
def Motors(direction, effect_id):
    
    # Set the effect IDs for each motor
    lMotor1.sequence[0] = adafruit_drv2605.Effect(effect_id)
    lMotor2.sequence[0] = adafruit_drv2605.Effect(effect_id)
    rMotor1.sequence[0] = adafruit_drv2605.Effect(effect_id)
    rMotor2.sequence[0] = adafruit_drv2605.Effect(effect_id)

    # The effect_ids are run twice so that it runs the whole time before the lidar updates again
    lMotor1.sequence[1] = adafruit_drv2605.Effect(effect_id)
    lMotor2.sequence[1] = adafruit_drv2605.Effect(effect_id)
    rMotor1.sequence[1] = adafruit_drv2605.Effect(effect_id)
    rMotor2.sequence[1] = adafruit_drv2605.Effect(effect_id)
    
    # Left Side Detection
    if direction == 1:
        lMotor1.play()
        lMotor2.play()
        
    # Center Detection
    elif direction == 2 or direction == 0:
        lMotor1.play()
        lMotor2.play()
        rMotor1.play()
        rMotor2.play()
    
    # Right Side Detection
    elif direction == 3:
        rMotor1.play()
        rMotor2.play()

# Process the data to determine minimum distance and minimum angle of the scan_data
def process_data(data):
    global max_distance
    global min_distance
    global direction
    global max_angle
    global min_angle
    global cond
    
    # Reset the min distance and min angle variables
    min_distance = 2743
    min_angle = 0
    
    # Reset the max distance and max angle variables
    max_distance = 0
    max_angle = 0
    
    # Loop to find the minimum distance and the corresponding angle as well as the maximum distance with its corresponding angle
    for angle in range(360):
        distance = data[angle]
        if distance > 0:
            temp_max = max_distance
            max_distance = max(distance, max_distance)
            temp_min = min_distance
            min_distance = min(distance, min_distance)
            
            if max_distance != temp_max:
                max_angle = angle
            # Update the angle variables if a change in the max/min distance was detected
            if min_distance != temp_min:
                min_angle = angle
            
            
    # Closest distance (Less than 1 foot)
    if min_distance < 304.8 and min_distance > 0:
        cond = 3
            
        # Set direction based on the angle
        # 90 degress to 270 degrees is jumped because it is the area that is covered
        if (min_angle > 330 and min_angle < 359) or (min_angle >= 0 and min_angle < 30):
            direction = 2 # Middle
        elif (min_angle > 270 and min_angle < 330):
            direction = 1 # Left
        elif (min_angle > 30 and min_angle < 90):
            direction = 3 # Right
           
    # Medium distance (1 foot to 3 feet)
    elif min_distance < 914.4 and min_distance > 304.8:
        cond = 4
            
        # Set direction based on the angle
        if (min_angle > 340 and min_angle < 359) or (min_angle >= 0 and min_angle < 20):
            direction = 2 # Middle
        elif (min_angle > 300 and min_angle < 340):
            direction = 1 # Left
        elif (min_angle > 20 and min_angle < 60):
            direction = 3 # Right
                
    # Longest distance (3 feet to 6 feet)
    elif min_distance < 1828.8 and min_distance > 914.4:
        cond = 5
            
        # Set direction based on the angle
        if (min_angle > 355 and min_angle < 359) or (min_angle >= 0 and min_angle < 5):
            direction = 2 # Middle
        elif (min_angle > 330 and min_angle < 355):
            direction = 1 # Left
        elif (min_angle > 5 and min_angle < 30):
            direction = 3 # Right
            
try:            
    for scan in lidar.iter_scans():
        scan_count = scan_count + 1
        for (_, angle, distance) in scan:
            #print('dist - ' +str(distance) + ' ang - ' +str(floor(angle)))
            scan_data[min([359, floor(angle)])] = distance
            if scan_count == 5:                     
                cond = 6
                scan_count = 0
                
                # Call the function to process the scan
                process_data(scan_data)
                
                # Process time of flight sensors
                if tof1.range > 550 or tof1.range > 550:
                    cond = 1
                    Motors(0,52)
                    print(str(tof1.range))
                elif tof1.range > 400 or tof1.range > 400:
                    cond = 2
                    Motors(0,53)
                    print(str(tof1.range))
                             
                # Conditions         
                if cond == 3:
                    # effect_id 16 is a 1 second alert at 100% strength
                    Motors(direction,16)
                    print("condition 3")
                elif cond == 4:
                    # effect_id 49 is a buzz at 60% strength
                    Motors(direction,49)
                    print("condition 4")
                elif cond == 5:
                    # effect_id 51 is a buzz at 20% strength
                    Motors(direction,51)
                    print("condition 5")
                elif cond > 5:
                    #Motors(0,1)
                    print("condition > 5")
                else:
                    #Motors(0,3)
                    print("off")
                
                # Reset scan_data
                scan_data = [0]*360
                
                # Troubleshooting Information
                if cond == 1:
                    print("Tof, greater than 1.8 feet: Condition = 1")
                if cond == 2:
                    print("Tof, between 1.8 feet and 1.3 feet: Condition = 2")
                if cond == 3:
                    print("Lidar, Less than 1 foot: Condition = 3")
                if cond == 4:
                    print("Lidar, 1 to 3 feet: Condition = 4")
                if cond == 5:
                    print("Lidar, 3 to 6 feet: Condition = 5")
                    
                if direction == 1:
                    print("Left")
                if direction == 2:
                    print("Middle")
                if direction == 3:
                    print("Right")
                if direction == 0:
                    print("Direction Wasn't Updated")
                    
                print("Minimum Distance Detected = " + str(min_distance) + " mm")
                print("Angle At Minimum Distance = " + str(min_angle) + " degrees")
                print("Maximum Distance Detected = " + str(max_distance) + " mm")
                print("Angle At Maximum Distance = " + str(max_angle) + " degrees")
                
                print("-------------- Break in Scan --------------")
                
except KeyboardInterrupt:
    lidar.stop()
    lidar.disconnect()
    print("Stopped")