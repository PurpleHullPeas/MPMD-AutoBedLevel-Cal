IF YOU'RE UNFAMILIAR WITH DENNIS BROWN'S MPMD TUTORIAL IN THE FACEBOOK GROUP, DO NOT USE THIS SCRIPT! GO BACK AND USE TECHNOSWISS'S ORIGINAL SCRIPTS INSTEAD!

https://www.facebook.com/groups/mpminideltaowners/permalink/2574670629215074/

I automated Dennis's G29 P5 Heatmap Spreadsheet for M666/M665 Calibration (Step C5 in his pinned alignment/calibration tutorial) by updating Technoswiss's python script. Special thanks to them for all of their effort!
Dennis's Spreadsheet+Instructions: https://www.facebook.com/groups/mpminideltaowners/permalink/2186865287995612/
Python Script (auto_cal_p5.py): https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal

-----------------------------------------------------------------------------------

BETA TESTERS NEEDED!!!!!!!!
Scroll to the bottom for more info!

-----------------------------------------------------------------------------------

DISCLAIMER: 

Use at your own risk. Backup everything and keep your finger on the after-market power-button (that I'm sure you installed) while the script runs. I'm not responsible if your printer decides to spontaneously combust or if you void your warranty. All disclaimers and prerequisites listed by Technoswiss on GitHub still apply.

Tested Firmware:
Stock v41
Stock v43
Stock v44
Marlin x8

-----------------------------------------------------------------------------------

PREREQUISITES:

1) Everything will work better if you start with this tutorial and work your way up to Step C5. 
https://www.facebook.com/groups/mpminideltaowners/permalink/2058169440865198/

2) You will need to be able to control your printer via USB. I use my Octopi (but not Octoprint) to run the script via terminal/command line (not to be confused with your print server terminal).
E.G., I don't have a monitor plugged into my Octopi, so I do all of this using Putty. I'm able to enter "octopi" instead of the IP address to connect, but YMMV.
https://www.raspberrypi.org/documentation/remote-access/ssh/windows.md

3) Python3 is required, with additional updates/packages. 

Octopi Installation
sudo apt-get update
sudo apt-get install python3-serial
sudo apt-get install python3-scipy

Windows Installation (not tested):
http://winpython.github.io/

Mac/OSX Installation (not tested):
Download Python for Mac - https://www.python.org/downloads/mac-osx/
Install pyserial - https://stackoverflow.com/questions/31228787/install-pyserial-mac-os-10-10
Install scipy and related packages - https://www.scipy.org/install.html

4) The points that the nozzle probes need to be consistent. I.E., if you're using tape, a sticker, PEI, glass, mirror, etc., you need to make sure the nozzle taps that for every probe point. If using tape, make sure it covers the entire build surface without overlapping. Whatever build surface you choose, make sure you remove the stock sticker before application because you want everything as flat as possible. Dennis wrote the spreadsheet assuming you have his hold-down clips installed (see previously linked tutorial).

INSTRUCTIONS:

1) Power cycle your printer to clear out any temporary settings. 

2) Make sure the nozzle is clean and then turn the nozzle heat off.

3) Heat your bed up to your desired printing temperature and clean it. Let it sit for a while so that all parts get fully heated. Later when you run the script, you want to set the "-bt 60" parameter to whatever your desired bed temperature is.

4) If you're currently connected to the printer via Octoprint or some other service, click the Disconnect button now.

5) Run the Python script with your port connection, starting R and L values from Dennis's previous alignment tutorial step, the appropriate step/mm for your firmware, and your desired bed temperature. As this is a new script, standby with your finger on the power button just in case.

Examples for Linux after you've changed directories into the same path as the script (Bed Temperature = 60):

Stock Firmware <=V41, V45 at 60 degrees C w/ Dennis's Defaults:
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -r 63.5 -l 123.0 -s 57.14 -bt 60

Stock V43 & V44 at 60 degrees C w/ Dennis's Defaults:
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -r 63.5 -l 123.0 -s 114.28 -bt 60

For Marlin, use the appropriate line for your stock firmware and replace "-ff 0" with "-ff 1"

6) The calibration values should now be set to whatever was calculated on the last pass. The outputs for each pass should be stored in files named auto_cal_p5_pass#.txt. You can paste the contents of this file into Dennis's spreadsheet to check your heatmap.
Note: I'm using Samba to copy files between Windows and Linux.
https://www.raspberrypi.org/magpi/samba-file-server/

7) Stock firmware seems buggy on saving with M500, so write your final values down somewhere and possibly store them in your starting gcode. If you're on Marlin and have an SD card inserted, you can use M500.

-----------------------------------------------------------------------------------

BETA TESTING NOTES

Debugging/Testing Notes:

1) Most thoroughly tested with x8 Marlin. Also tested with stock v41. Should work with any firmware version as long as you use the correct inputs (see examples).
Reports:
Stock v43 and v44 successfully tested by other users

2) This is my first time coding in Python. The code is messy, but it appears to work.

3) My instructions aren't super detailed. If someone wants to do a better job, I'll gladly update my post.

4) My default interpolation method for heatmap points is python's griddata; therefore, your results will be slightly different than if you run Dennis's spreadsheet manually. I talked some things through with Dennis and feel confident that this is the right decision.

PLEASE FILL OUT THIS FORM WITH TROUBLESHOOTING NOTES:

If you decide to run the script, please leave a comment with the information below.

Computer Used: Octopi/Windows7/Windows10/Mac/etc.
Firmware Version: Stock v[37/38/39/40/41/42/43/44/45] or Marlin [x8/x16]
Build Plate Surface - Glass/Mirror/PEI/Stock/Tape/etc. (also include if you use binder clips, printed clips, thermal pad, etc.)
Do you have Dennis's Hold-Down Clips Installed? Yes/No
Do you have Dennis's Top Bed Switch Mod Installed?  Yes/No
Terminal Command Used: E.G., python3 auto_cal_p5.py [insert inputs here]
Successful? Yes/No/Partial
Terminal Error: N/A [If applicable, copy and paste any script errors here]
If not successful, are you able to run one of TechnoSwiss's other scripts? Yes/No/NA
Comments: E.G., Here's how/why it sucks.

FEATURES:

1) Started with Technoswiss's G29 P2 v2 python script and included the most up-to-date bug fixes from it.

2) Updated to use Dennis Brown's G29 P5 Excel heatmap calculations.

3) Saves results after each iteration in text files (can be copy-pasted into Dennis's spreadsheet).

4) Intended to work with all firmware versions, but not yet tested/confirmed.

5) Saves time iterating through the Excel procedure yourself and makes it easier to update values when you make any mods or change the bed temperature.
