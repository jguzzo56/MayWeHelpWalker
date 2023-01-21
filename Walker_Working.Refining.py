#May We Help Walker

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

#drv1=adafruit_drv2605.DRV2605(tca[4])
drv2=adafruit_drv2605.DRV2605(tca[7])
#drv3=adafruit_drv2605.DRV2605(tca[6])
#drv4=adafruit_drv2605.DRV2605(tca[7])
tof1 = adafruit_vl53l0x.VL53L0X(tca[0])
tof2 = adafruit_vl53l0x.VL53L0X(tca[1])

# Setup the RPLidar
#python -m serial.tools.miniterm
#use this command on the command line to determine port name 
PORT_NAME = '/dev/ttyUSB0'
#baudrate=9600
lidar = RPLidar(None, PORT_NAME,timeout=3)

#health = lidar.get_health()
#print(health)
#lidar.stop()
# used to scale data to fit on the screen
max_distance = 0
scanCount = 0
print('Press Ctrl-C to stop')
def MotorsAndToF():
    effect_id = 1

    print("Playing effect #{0}".format(effect_id))
    print('Range: {}mm'.format(tof1.range))
    print('Range: {}mm'.format(tof2.range))
    drv2.sequence[0] = adafruit_drv2605.Effect(effect_id)  # Set the effect on slot 0.
        # You can assign effects to up to 8 different slots to combine
        # them in interesting ways. Index the sequence property with a
        # slot number 0 to 7.
        # Optionally, you can assign a pause to a slot. E.g.
        # drv.sequence[1] = adafruit_drv2605.Pause(0.5)  # Pause for half a second
    drv2.play()  # play the effect
    # time.sleep(2)  # for 0.5 seconds // time seems to kill lidar - found github comments that agree
    drv2.stop()  # and then stop (if it's still running)
     
def Motors(onoff,effect_id):
    # 0 off, 1 on
    #effect_id = 7

    drv2.sequence[0] = adafruit_drv2605.Effect(effect_id)  # Set the effect on slot 0.
        # You can assign effects to up to 8 different slots to combine
        # them in interesting ways. Index the sequence property with a
        # slot number 0 to 7.
        # Optionally, you can assign a pause to a slot. E.g.
        # drv.sequence[1] = adafruit_drv2605.Pause(0.5)  # Pause for half a second
    if onoff == 1:
        drv2.play()  # play the effect
        # time.sleep(2)  # for 0.5 seconds // time seems to kill lidar - found github comments that agree
    else:
        drv2.stop()  # and then stop (if it's still running)      

def process_data(data, sensorstatus):
    global detect_distance
    x=1
    for angle in range(360):
        distance = data[angle]
     #   print(str(distance))
        if distance < 304.8 and distance > 0:
            if (angle > 330 and angle < 359) or (angle >= 0 and angle < 30):
                if sensorstatus > 3: sensorstatus = 3
                #print('1C ' + str(distance))
            elif (angle > 270 and angle < 330):
                if sensorstatus > 4: sensorstatus = 4
            elif (angle > 30 and angle < 90):
                if sensorstatus > 5: sensorstatus = 5
           
        elif distance < 914.4 and distance > 0:
            if (angle > 340 and angle < 359) or (angle >= 0 and angle < 20):
                if sensorstatus > 6: sensorstatus = 6
            elif (angle > 300 and angle < 340):
                if sensorstatus > 7: sensorstatus = 7
            elif (angle > 20 and angle < 60):
                if sensorstatus > 8: sensorstatus = 8
            
        elif distance < 1828.8 and distance > 0:
            if (angle > 355 and angle < 359) or (angle >= 0 and angle < 5):
                if sensorstatus > 9: sensorstatus = 9
            elif (angle > 330 and angle < 355):
                if sensorstatus > 10: sensorstatus = 10
            elif (angle > 5 and angle < 30):
                if sensorstatus > 11: sensorstatus = 11
     
    return sensorstatus
                #print('ICU ' +str(distance) +' - angle - ' + str(angle) + ' ScanCount - ' +str(scanCount))
    
scan_data = [0]*360
cond = 12 # Condition value indicates the highest priority sensor

while True:
    try:
        try:
             print(lidar.info)
             for scan in lidar.iter_scans():
                 scanCount = scanCount + 1
                 for (_, angle, distance) in scan:
               #      print('dist - ' +str(distance) + ' ang - ' +str(floor(angle)))
                     scan_data[min([359, floor(angle)])] = distance
                 if scanCount == 5:                     
                     cond = 12
                     scanCount = 0
                     
                     cond = process_data(scan_data, cond)
                     if tof1.range > 13 / 0.0254 or tof2.range > 13 / 0.0254:
                         cond = 1
                     elif tof1.range < 5 / 0.0254 or tof2.range < 5 / 0.0254:
                         cond = 2
                    # print(str(tof2.range))
                     print(str(cond))
                     if cond != 1:
                        Motors(0,1)
                     if cond == 1:
                        Motors(1,118)
                     if cond == 2:
                        Motors(1,119)
                     if cond <= 5:
                        Motors(1,118)
                     elif cond <= 8:
                        Motors(1,121)
                     elif cond <= 11:
                        Motors(1,122)
                     else:
                        Motors(0,3)
                     
                     scan_data = [0]*360 
        except KeyboardInterrupt:
             print('Stopping.')
    except Exception:
       print (scanCount)
       lidar.stop()
lidar.stop()
lidar.disconnect()
