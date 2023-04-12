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

drv1=adafruit_drv2605.DRV2605(tca[4])
drv2=adafruit_drv2605.DRV2605(tca[5])
drv3=adafruit_drv2605.DRV2605(tca[6])
drv4=adafruit_drv2605.DRV2605(tca[7])

effect_id = 15

drv1.sequence[0] = adafruit_drv2605.Effect(effect_id)
drv2.sequence[0] = adafruit_drv2605.Effect(effect_id)
drv3.sequence[0] = adafruit_drv2605.Effect(effect_id)
drv4.sequence[0] = adafruit_drv2605.Effect(effect_id)

drv1.play()
drv2.play()
drv3.play()
drv4.play()