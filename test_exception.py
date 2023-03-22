import os
import board
import time
import busio
import adafruit_tca9548a
import adafruit_drv2605
import adafruit_vl53l0x
from math import floor
from adafruit_rplidar import RPLidar
import vlc

# Initialize the I2C and TCA
i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)

# Initialize the Motors
lMotor1 = adafruit_drv2605.DRV2605(tca[6])
lMotor2 = adafruit_drv2605.DRV2605(tca[5])
rMotor1 = adafruit_drv2605.DRV2605(tca[7])
rMotor2 = adafruit_drv2605.DRV2605(tca[4])

# Initialize the TOF Sensors
tof1 = adafruit_vl53l0x.VL53L0X(tca[0])
tof2 = adafruit_vl53l0x.VL53L0X(tca[1])

# Initialize the Lidar
# NOTE: Sometimes this throws an error. Try unplugging the lidar and put it in a different USB port.
lidar = RPLidar(None, '/dev/ttyUSB0',timeout=3) # '/dev/ttyUSB0' is the port name

# Declare Variables
scan_count = 0 # Number of scans done
scan_data = [0]*360 # Array with the data from the lidar scan
max_distance = 0 # To find the max distance in a scan
min_distance = 2743 # 9 feet, To find the min distance in a scan
direction = 0 # To find direction of hazard
last_dir = 0 # Set last_dir
min_angle = 0 # To find the angle where the min distance is
max_angle = 0 # To find the anlge where the max distance is
cond = 6 # To set the condition
run = True # Tells walker to run or not
play = False # Tells whether to play audio or not
print('Press Ctrl-C to stop')

# Function to tell which motors to vibrate and at what intensity
def Motors(effect_id):
    global direction
    global temp_dir
    
    # Set the effect IDs for each motor
    lMotor1.sequence[0] = adafruit_drv2605.Effect(effect_id)
    lMotor2.sequence[0] = adafruit_drv2605.Effect(effect_id)
    rMotor1.sequence[0] = adafruit_drv2605.Effect(effect_id)
    rMotor2.sequence[0] = adafruit_drv2605.Effect(effect_id)

    # The effect_ids are run twice so that it runs the whole time before the lidar updates
    lMotor1.sequence[1] = adafruit_drv2605.Effect(effect_id)
    lMotor2.sequence[1] = adafruit_drv2605.Effect(effect_id)
    rMotor1.sequence[1] = adafruit_drv2605.Effect(effect_id)
    rMotor2.sequence[1] = adafruit_drv2605.Effect(effect_id)
    
    # Test if direction variable has changed
    if last_dir != direction:
        play = True
    else:
        play = False
    
    # Left Side Detection
    if direction == 1:
        lMotor1.play()
        lMotor2.play()
        if play:
            player = vlc.MediaPlayer("/home/raspberrypi/Desktop/Walker Sounds/ObstacleLeft.wav")
            player.play()
            
    # Center Detection
    elif direction == 2:
        lMotor1.play()
        lMotor2.play()
        rMotor1.play()
        rMotor2.play()
        if play:
            player = vlc.MediaPlayer("/home/raspberrypi/Desktop/Walker Sounds/ObstacleCenter.wav")
            player.play()
            
    # Right Side Detection
    elif direction == 3:
        rMotor1.play()
        rMotor2.play()
        if play:
            player = vlc.MediaPlayer("/home/raspberrypi/Desktop/Walker Sounds/ObstacleRight.wav")
            player.play()
            
    # TOF Detection
    elif direction == 4:
        lMotor1.play()
        lMotor2.play()
        rMotor1.play()
        rMotor2.play()
        if play:
            player = vlc.MediaPlayer("/home/raspberrypi/Desktop/Walker Sounds/TOFAlarm.mp3")
            player.play()
            
# Process the data to determine minimum distance and minimum angle of the scan_data
def process_data(data):
    global max_distance
    global max_angle
    global direction
    global cond
    global last_dir
    
    # Set temp_dir to current direction
    last_dir = direction
    
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
            if distance < 304.8 and (angle > 270 or angle < 90):
                # Set new max and min if necessary
                temp_max = max_distance
                max_distance = max(distance, max_distance)
                temp_min = min_distance
                min_distance = min(distance, min_distance)
            
                # Update the angle variables if a change in the max/min distance was detected
                if max_distance != temp_max:
                    max_angle = angle
                if min_distance != temp_min:
                    min_angle = angle
            if distance > 304.8 and distance < 914.4 and (angle > 300 or angle < 60):
                # Set new max and min if necessary
                temp_max = max_distance
                max_distance = max(distance, max_distance)
                temp_min = min_distance
                min_distance = min(distance, min_distance)
            
                # Update the angle variables if a change in the max/min distance was detected
                if max_distance != temp_max:
                    max_angle = angle
                if min_distance != temp_min:
                    min_angle = angle
            elif distance > 914.4 and distance < 1828.8 and (angle > 330 or angle < 30):
                # Set new max and min if necessary
                temp_max = max_distance
                max_distance = max(distance, max_distance)
                temp_min = min_distance
                min_distance = min(distance, min_distance)
            
                # Update the angle variables if a change in the max/min distance was detected
                if max_distance != temp_max:
                    max_angle = angle
                if min_distance != temp_min:
                    min_angle = angle
            
    # Closest distance (Less than 1 foot)
    if min_distance < 304.8 and min_distance > 0:
        cond = 3
            
        # Set direction based on the angle
        # 90 degress to 270 degrees is jumped because it is the area that is covered
        if (min_angle > 270 and min_angle < 330):
            direction = 1 # Left
        elif (min_angle > 330 and min_angle < 359) or (min_angle >= 0 and min_angle < 30):
            direction = 2 # Middle
        elif (min_angle > 30 and min_angle < 90):
            direction = 3 # Right
        else:
            direction = 5
           
    # Medium distance (1 foot to 3 feet)
    elif min_distance < 914.4 and min_distance > 304.8:
        cond = 4
            
        # Set direction based on the angle
        if (min_angle > 300 and min_angle < 340):
            direction = 1 # Left
        elif (min_angle > 340 and min_angle < 359) or (min_angle >= 0 and min_angle < 20):
            direction = 2 # Middle
        elif (min_angle > 20 and min_angle < 60):
            direction = 3 # Right
        else:
            direction = 5
                
    # Longest distance (3 feet to 6 feet)
    elif min_distance < 1828.8 and min_distance > 914.4:
        cond = 5
            
        # Set direction based on the angle
        if (min_angle > 330 and min_angle < 355):
            direction = 1 # Left
        elif (min_angle > 355 and min_angle < 359) or (min_angle >= 0 and min_angle < 5):
            direction = 2 # Middle
        elif (min_angle > 5 and min_angle < 30):
            direction = 3 # Right
        else:
            direction = 5
            
    # Test if max_distance is greater than 11 feet (Dropoff)
    elif max_distance > 3350:
        cond = 7
        
        # Set direction based on the angle
        if (max_angle > 330 and max_angle < 355):
            direction = 1 # Left
        elif (max_angle > 355 and max_angle < 359) or (max_angle >= 0 and max_angle < 5):
            direction = 2 # Middle
        elif (max_angle > 5 and max_angle < 30):
            direction = 3 # Right
        else:
            direction = 5
    return cond, direction, min_distance, min_angle
            
def troubleshoot(cond,direction,min_distance,min_angle):
    
    # Information on Conditions
    if cond == 1:
        print("Tof, greater than 1.8 feet: Condition = 1")
    elif cond == 2:
        print("Tof, between 1.8 feet and 1.3 feet: Condition = 2")
    elif cond == 3:
        print("Lidar, Less than 1 foot: Condition = 3")
    elif cond == 4:
        print("Lidar, 1 to 3 feet: Condition = 4")
    elif cond == 5:
        print("Lidar, 3 to 6 feet: Condition = 5")
    elif cond == 6:
        print("Condition Wasn't Updated")
    elif cond == 7:
        print("Lidar, Greater than 11 feet: Condition = 7")
    else:
        print("Condition is out of the range 1-6")
        
    # Direction Information
    if direction == 1:
        print("Left")
    elif direction == 2:
        print("Middle")
    elif direction == 3:
        print("Right")
    elif direction == 4:
        print("TOF, Below")
    elif direction == 5:
        print("Min Angle is outside of the range we are looking at")
    elif direction == 0:
        print("Direction Wasn't Updated")
    else:
        print("Direction is outside of the range 0-5")
        
    # Min Angle and Min Distance Information
    print("Minimum Distance Detected = " + str(min_distance) + " mm")
    print("Angle At Minimum Distance = " + str(min_angle) + " degrees")
    
    # Max Angle and Max Distance Information
    print("Maximum Distance Detected = " + str(max_distance) + " mm")
    print("Angle At Maximum Distance = " + str(max_angle) + " degrees")
    
    # Notify a new scan starting. Helps to show where a scan starts and finishes
    print("-------------- Break in Scan --------------")
    
def run_walker():
    global run
    global scan_count
    global scan_data
    global cond
    global direction
    while run:
        try:
            # This is the for loop that is making the whole thing run over and over
            for scan in lidar.iter_scans():
                scan_count = scan_count + 1
                for (_, angle, distance) in scan:
                    #print('dist - ' +str(distance) + ' ang - ' +str(floor(angle)))
                    scan_data[min([359, floor(angle)])] = distance
                    if scan_count == 5:                     
                        cond = 6
                        scan_count = 0
                            
                        # Call the function to process the scan
                        [cond, direction, min_distance, min_angle] = process_data(scan_data)
                            
                        # Process time of flight sensors
                        if tof1.range > 550 or tof2.range > 550:
                            cond = 1
                            direction = 4
                            Motors(52)
                            print(str(tof1.range))
                                
                        elif tof1.range > 400 or tof2.range > 400:
                            cond = 2
                            direction = 4
                            Motors(53)
                            print(str(tof1.range))
                                         
                        # Conditions         
                        if cond == 3:
                            # effect_id 16 is a 1 second alert at 100% strength
                            Motors(16)
                        elif cond == 4:
                            # effect_id 49 is a buzz at 60% strength
                            Motors(49)
                        elif cond == 5:
                            # effect_id 51 is a buzz at 20% strength
                            Motors(51)
                        elif cond == 7:
                            Motors(47)
                        
                        # Call the troubleshooting function
                        troubleshoot(cond,direction,min_distance,min_angle)
                        
                        # Reset scan_data
                        scan_data = [0]*360
                            
        except Exception as e:
            print(e)
            print("Error. Restarting Walker")
            run_walker()
            
        except KeyboardInterrupt:
            print("Stopped")
            run = False

# Call the function to run the walker
run_walker()

# Stop the lidar after the walker is done running
lidar.stop()
lidar.disconnect()
