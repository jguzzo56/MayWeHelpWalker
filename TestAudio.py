import pygame
import time
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play

play(AudioSegment.from_mp3('/home/raspberrypi/Desktop/Walker Sounds/ObstacleLeft.wav'))

#playsound('/home/raspberrypi/Desktop/Walker Sounds/TOFAlarm.mp3')

#pygame.mixer.init()
#pygame.mixer.music.load('/home/raspberrypi/Desktop/Walker Sounds/TOFAlarm.mp3')
#pygame.mixer.music.play()
#time.sleep(3) #It doesn't work without this
#pygame.mixer.music.stop()
