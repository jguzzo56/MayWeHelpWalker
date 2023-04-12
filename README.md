# MayWeHelpWalker

Repository for the May We Help visually impaired walker

WalkerCode.py is the main program for the walker. 
MotorVibrationsTests.py is to test different motor vibrations and strenghts.
TestAudio.py is to test different audio files.

Launcher.bash is a bash script to run the WalkerCode.py file on startup.
A small change to the Pi's system is needed in order for it to work. In a terminal window, type:
sudo crontab -e

Scroll all the way to the bottom of the file, and add the following line:
@reboot bash /home/raspberrypi/Desktop/Spring2023/Launcher.bash >home/raspberrypi/logs/cronlog 2>&1

Save the file. When the Raspberry Pi boots up, the WalkerCode.py file should run.

To see a log of the WalkerCode.py's output when it runs on startup, type in a terminal window:
cd logs
cat cronlog
