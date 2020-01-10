# Monoprice Mini Delta (MPMD) Auto Bed Calibration (P5)
This python script will automatically adjust the M666 XYZ and M665 LR values to calibrate bed leveling for a Monoprice Mini Delta 3D printer. It uses the G29 P5 method for an improved bed mesh.
## Overview

This tutorial is designed to be used in place of Step C5 in [Dennis Brown's great alignment/calibration tutorial](https://www.facebook.com/groups/mpminideltaowners/permalink/2058169440865198/).

I automated Dennis's G29 P5 Heatmap Spreadsheet for M666/M665 Calibration by updating Technoswiss's python script. Special thanks to them for all of their effort!

Python Script (auto_cal_p5.py)

Dennis's [Spreadsheet](https://docs.google.com/spreadsheets/d/1rTn4vu2924AA_z1WppvLk4r31JXvoI1YI_7iSye0v3k/copy) and [Original Instructions](https://www.facebook.com/groups/mpminideltaowners/permalink/2186865287995612/) <br/>
You should only need this for generating pretty heatmaps. I.E., there's no need to go through his Step C5 spreadsheet instructions if you're using this script.

**There is a comprehensive troubleshooting guide near the bottom of this post. I WILL NOT HELP YOU AT ALL unless you have gone through that section and provided ALL of the requested information in the Troubleshooting Form.** I get that there's a lot of content and that things are easy to overlook, but I can't help you unless I have a full picture of what's going on.

![Bed Leveling Heat Map](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/Before_After_new.jpg)<br/>
Image Source: https://www.facebook.com/groups/mpminideltaowners/permalink/2996644567017676/
## Features

1) Started with Technoswiss's G29 P2 v2 python script and included the most up-to-date bug fixes from it.

2) Updated to use Dennis Brown's G29 P5 Excel heatmap calculations.

3) Saves results after each iteration in text files (can be copy-pasted into Dennis's spreadsheet).

4) Works with all firmware versions.

5) Saves time iterating through the Excel procedure yourself and makes it easier to update values when you make any mods or change the bed temperature.

## Disclaimer

Use at your own risk. Backup everything and keep your finger on the after-market power-button (that I'm sure you installed) while the script runs. I'm not responsible if your printer decides to spontaneously combust or if you void your warranty. All disclaimers and prerequisites listed by Technoswiss on his original project still apply.


## Tested Firmware and Operating Systems

### Tested Firmware
Stock v37 <br/>
Stock v41 <br/>
Stock v43 <br/>
Stock v44 <br/>
Stock v45 <br/>
Marlin 8x (v1.2.2 and v1.3.3)<br/>
Marlin 16x (v1.2.2 and v1.3.3)<br/>


### Tested Operating Systems
Linux (mostly Octopi) <br/>
Windows 10 (batch file and command-line executable included) <br/>
The scripts should also work on Mac (using the same pyserial code that's confirmed in Technoswiss's scripts), but no one has reported back after installing all of the correct packages. <br/>

## Prerequisites

1) This script is intended to be used only **AFTER** you've gone through other calibration steps (namely Dennis's improved bed hold-down clips and having a more consistent bed surface). Do not run it unless you've made it that far in the [Calibration Roadmap](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/) I've put together.

2) You will need to be able to control your printer via USB. I use my Octopi (but not Octoprint) to run the script via terminal/command line (not to be confused with your print server terminal). <br/>
E.G., I don't have a monitor plugged into my [Octopi](https://octoprint.org/download/), so I do all of this using [Putty](https://www.raspberrypi.org/documentation/remote-access/ssh/windows.md). I'm able to enter "octopi" instead of the IP address to connect, but YMMV.

3) Unless you're using the Windows executable, Python3 is required, with additional updates/packages. <br/><br/>
**Octopi Installation:** (some unnecessary commands included to help noobs) <br/>
sudo apt-get install python3-serial <br/>
sudo apt-get install python3-scipy <br/>
sudo apt-get install python-serial <br/>
git clone https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal.git <br/>
cd MPMD-AutoBedLevel-Cal <br/>
git fetch <br/>
git pull <br/><br/>
**Windows Installation:** <br/>
I recently released a command-line executable that can be used instead of the python script, as well as a batch file to make running it more straightforward: auto_cal_p5_v0.bat and auto_cal_p5_v0.exe (you will need both files in the same directory). <br/>
The [Visual C++ Redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=48145) may be required whether you use the executable or the Python script. <br/>
If you prefer to use Python, you will need the additional packages included with [WinPython](http://winpython.github.io/). <br/><br/>
**Mac/OSX Installation** (not tested): <br/>
Download [Python for Mac](https://www.python.org/downloads/mac-osx/) <br/>
Install [pyserial](https://stackoverflow.com/questions/31228787/install-pyserial-mac-os-10-10) <br/>
Install [scipy and related packages](https://www.scipy.org/install.html) <br/>

4) The points that the nozzle probes need to be consistent. I.E., if you're using tape, a sticker, PEI, glass, mirror, etc., you need to make sure the nozzle taps that for every probe point. If using tape, make sure it covers the entire build surface without overlapping. Whatever build surface you choose, make sure you remove the stock sticker before application because you want everything as flat as possible. If you typically use glue/hairspray on your bed, I recommend cleaning it off beforehand. The script will most definitely not work if the effector is colliding with a bed clip or other obstructions before the nozzle can probe the bed. In my experience, trying to use glass retainer/holding clips causes problems and should be avoided (read my recommendations in the calibration guide).

5) Dennis wrote the spreadsheet assuming you have his hold-down clips installed (see previously linked tutorial). This is not an optional step. You should also tune your belts if you haven't done so recently.


## Instructions

**DO NOT FORGET TO COMPLETE THE REMAINING STEPS AFTER RUNNING THE PROGRAM! UPDATING YOUR M666, M665, using G29 P5 (stock firmware), and having the correct M92 is crucial!** <br/>

1) Power cycle your printer to clear out any temporary settings.

2) Make sure the nozzle is clean and then turn the nozzle heat off.

3) Heat your bed up to your desired printing temperature and clean it. Let it sit for a while so that all parts get fully heated. Later when you run the script, you want to set the "-bt 60" parameter to whatever your desired bed temperature is.

4) If you're currently connected to the printer via Octoprint, Pronterface, Repetier, Cura, Simply3D, or some other service, click the Disconnect button now.

5) Run the Python script with your port connection, starting R and L values from Dennis's previous alignment tutorial step, the appropriate step/mm for your firmware, and your desired bed temperature. Standby with your finger on the power button, ready to abort, just in case weird things start happening. Don't forget to complete the remaining steps here after running the program. <br/> <br/>
The following examples are provided for Octopi, using Dennis's default M665 L/R values, stock firmware, and a bed temperature of 60 C. Additional details for Windows will be covered later. <br/><br/>
**Stock Firmware <=V41, V45** <br/>
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 57.14 -bt 60 <br/> <br/>
**Stock V43 & V44** <br/>
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 114.28 -bt 60 <br/> <br/>
**Firmware Flag and Tower Flag Notes** <br/>
Because of differences in how stock firmware and Marlin4MPMD treats tower orientation and G29, you will need to set the firmware flag (-ff) and tower flag (-tf) appropriately. <br/>
-Stock Firmware: -ff 0 -tf 0 <br/>
-Marlin4MPMD 1.3.3 (Default): -ff 1 -tf 1 <br/>
-Marlin4MPMD 1.3.3 (M665 X-120 Y-120 Z-120): -ff 1 -tf 2 <br/>
-Older Marlin4MPMD Versions (Default): -ff 1 -tf 0 <br/>
-Other Configurations: You can try all three tower flags (0, 1, or 2) one at a time until one works. The script will stop due to an error in a few passes if you guessed the wrong configuration. <br/> <br/>
**Windows Executable Notes** <br/>
For Windows, you can can instead use the executable/batch file (see uploaded screenshots). You will need both the auto_cal_p5_v0.bat and auto_cal_p5_v0.exe files in the same folder for this to work. **Don't forget to complete the remaining steps here after running the program.** <br/>

6) The calibration values should now be set to whatever was calculated on the last pass. The outputs for each pass should be stored in files named auto_cal_p5_pass#.txt. You can paste the contents of this file into [Dennis's Spreadsheet](https://docs.google.com/spreadsheets/d/1rTn4vu2924AA_z1WppvLk4r31JXvoI1YI_7iSye0v3k/copy) to check your heatmap. If you've run the script multiple times, sort the files by date to make sure you're using the most recent text file. <br/>
Note: I'm using [Samba](https://www.raspberrypi.org/magpi/samba-file-server/) to copy files between Windows and Linux.

7) [MARLIN ONLY] If you are using [Marlin4MPMD](https://github.com/mcheah/Marlin4MPMD/wiki/Calibration) firmware, now would be a good time to re-run the 7x7 mesh while the bed is still hot (details given below). After that, you may or may not need to revisit your z-offset via M851.  <br/>
;At this point, you've already run the script and the bed should still be heated. <br/>
;Delete your old M666 XYZ and M665 RL lines from your Start Gcode. <br/>
;Send the following commands via terminal: <br/>
M665 S120 <br/>
G29 <br/>
;Wait for the G29 to finish running. <br/>
M500 <br/>
;You can now use G29 P0 in your Start Gcode if you wish<br/>

7) [STOCK FIRMWARE ONLY] Stock firmware doesn't save M665 R with M500 due to a bug, so for the purposes of keeping things simple for this tutorial, I'm just going to suggest you save your M665/M666 values in your Start Gcode. If there are already lines in your Start Gcode with M665/M666, replace those with your new values. If you followed the prerequisites, the proper M92 values should also be set there ([if not, fix that now](https://bit.ly/mpmd101)). Change your G29 line to **G29 P5** Z0.28. You may need to change 0.28 to whatever z-offset value works best for your machine (see [MPMD 101](https://bit.ly/mpmd101)). It has also come to my attention recently that, if you have not already, you should add [M665 S120](https://www.reddit.com/r/mpminidelta/comments/cr7rie/pimples_after_calibration_fixed_by_reducing/) to your Start Gcode.


## Troubleshooting

**1) Python versions and/or dependency errors.** <br/>
E.G., "python3: command not found", "ModuleNotFoundError: No module named 'numpy'", etc. <br/>
Try replacing "python3 auto_cal_p5.py" with "python auto_cal_p5_v0.py". This will both reduce the number of dependencies required to run the script and handle any issues where your OS may have assigned "python" to Python 3.X instead of "python3". You will still need to install pyserial for this to work.

**2) Serial Ports?** <br/>
The provided examples work for Octopi if you only have one serial device plugged into the rPi. Otherwise, you will need to replace "-p /dev/ttyACM0" with your appropriate serial port, because **it will most likely not be the same as the provided examples.** <br/>
**Windows Example:** "-p COM3" <br/>
**Mac Example:** "-p /dev/tty.SOMETHING" (need to replace SOMETHING with your actual value) <br/>
If you're unsure of what your port name is, try seeing what it's called when you connect to the printer via Octoprint, Pronterface, Repetier, or some other service. Otherwise, try Googling, "how to find serial port name on my operating system".

**3) I had to abort because the nozzle started probing outside of the build area and/or the machine started making weird/bad noises.** <br/>
Two possibilities come to mind: <br/>
**a) Hardware/setup issue.** Go back and read through the PREREQUISITES section. Also, please fill out the troubleshooting form at the bottom of this section (including a photo of your bed setup) so we can identify potential issues. It also probably wouldn't hurt to check the lubrication on your moving parts (guide rods, carriage arm joints, etc.). <br/>
**b) Bad M665 values.** The examples provided use Dennis's starting values and may not be applicable for your machine (although, they do seem to work for most). You can adjust these by replacing "-r 63.5 -l 123.0" with your desired R/L values. Ideally, you have calculated these values from the Carbon Paper Step C4 in Dennis's tutorial. If not, replace these numbers with whatever you've been using to print successfully. For example, the stock values would be "-r 61.70 -l 120.80".<br/>

**4) I reach the maximum number of runs and/or my results suck.**
Make sure you have Dennis Brown's custom hold-down clips installed. That step is not optional. Without the clips, the 5x5 probe mesh will make the bed wobble everywhere, preventing you from obtaining consistent results. Also, make sure you're using G29 P5 in your Start Gcode. For some reason, people keep skipping that step in the instructions. After that, you can further improve your results by removing the stock Buildtak and installing 120 mm borosilicate glass w/ a 0.5 mm thermal pad and/or PEI. If you have a bad/stuck/obstructed endstop switch, damaged belts, poorly-lubricated parts, or other major hardware issues, the script will fail to provide usable results.

**5) My nozzle is going too high or low on the first layer (possibly even grinding into the plate).** <br/>
Multiple possibilities come to mind. <br/>
a) Did you remember to complete the remaining steps that come AFTER running the script/program? For some reason, most recent questions have been related to skipping the steps (for Marlin4MPMD or Stock firmware) pertaining to G29.<br/>
b) Search the [Calibration Roadmap and FAQ](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/) for the word "erratic." There are a lot of possible causes for this behavior.<br/>
c) Z-Offset problem <br/>
As long as most of your points are <= 0.14 in the spreadsheet, you'll probably be okay. Keep in mind that the spreadsheet values represent measurements BEFORE G29 makes any compensations. A high "Initial Layer Height", finely-tuned z-offset (see: [MPMD 101](https://bit.ly/mpmd101), and/or the tips within the [Calibration Roadmap and FAQ](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/)) can help compensate for any remaining issues. Tuning the z-offset should come AFTER adjusting the Initial Layer Height.

**6) "Calibration error on non-first run exceeds set limit."** <br/>
This error usually occurs for one of two reasons: <br/>
**a) Hardware problem.** Go back and read Troubleshooting point 3. <br/>
**b) Wrong tower flag.** the -tf option tells the script how to account for any software tinkering of tower locations via Marlin4MPMD 1.3.3 and/or M665 X/Y/Z adjustments (not to be confused with M666). You can try each tower flag (0, 1 and 2) until you find one that works.

**7) Windows Batch/Executable Errors** I've had a few other people report to me that they were able to run the batch file, so I know it works for more than just me. For example, one common issue is when users try clicking the executable instead of the batch file (read the instructions again). When doing that, a command window containing only the following information will appear: <br/> 
"Could not connect to error at baudrate 115200<br/> 
Serial error: could not open port 'error': FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)
auto_cal_p5_v0.py: error: the following arguments are required: -p/--port<br/> 
Press Enter to continue..."<br/> 

**8) Other Issues.** At this point, many users have successfully run this script for all configurations of printer firmware on Octopi. Mac has not been as thoroughly-tested. If you're still having issues, please fill out the troubleshooting form at the bottom of this section and post it via one of the following channels: <br/>
a) File an issue on this GitHub page. <br/>
b) Respond to [my original thread on Facebook](https://www.facebook.com/groups/mpminideltaowners/permalink/2574670629215074/). Note: If I don't respond, maybe make a new post. Facebook can be buggy sometimes. <br/> 
c) Ask the question on [Reddit](https://www.reddit.com/r/mpminidelta/) and tag me /u/PurpleHullPeas <br/>

### Troubleshooting Form/Questionnaire 

Do your best to fill this out, even if you just write "I don't understand." Even if you don't think it's relevant. Do not skip the bed photo. </br>
**Computer Used:** Octopi/Windows7/Windows10/Mac/etc. <br/>
**[Firmware Version](https://www.mpminidelta.com/firmware/firmware_version_check) Shipped with Printer/Mainboard:** Stock v[37/38/39/40/41/42/43/44/45] <br/>
**Are you now using Marlin4MPMD firmware?** copy-paste the firmware.bin filename and list the version of Marlin4MPMD <br/>
**Build Plate Surface:** Glass/Mirror, PEI, WhamBam, Terrible Stock Sticker, Tape, etc. (also include how you decided to attach the bed to the printer) <br/>
**List any mods between the heated build plate and printer base that cannot be seen in your photo:** N/A <br/>
**Do you have [Dennis's Hold-Down Clips](https://www.youtube.com/watch?v=RSZ5xZf63Xo) Installed?** Yes/No <br/>
**Did you [calibrate Dennis's Hold-Down Clips](https://www.youtube.com/watch?v=2eko2PRa6y8) with an Index Card?** Yes/No <br/>
**Have you [tuned the belts](https://www.youtube.com/watch?v=gTtEJum10Ss) recently?** Yes/No <br/>
**Have you [lubricated moving parts](https://www.youtube.com/watch?v=2vuTZncnQYM) recently?** Yes/No <br/>
**Have you [shimmed the bed square to the rails](https://www.youtube.com/watch?v=2kGcRpWrSE8) (not always necessary)?** Yes/No <br/>
**Is your effector [colliding with a bed clip](https://www.facebook.com/zoe.yiasemides/videos/1693764524100934/) (or something else)** Yes/No (See Video) <br/>
**Have you (optional) rotated any towers (swapping wires and/or M665 XYZ)?** Yes/No - Explain <br/>
**List any other mods that may affect bed leveling:** N/A <br/>
**Terminal Command Used and/or Batch File Screenshot:** E.G., python3 auto_cal_p5.py [insert inputs here] <br/>
**Successful?** Yes/No/Partial <br/>
**Terminal Error:** Screenshot preferred. If applicable, copy and paste any script errors here <br/>
**If not successful, were you able to run "python auto_cal_p5_v0.py [INPUTS]"?** Yes/No - If no, paste that error as well. If N/A, try running this alternate script using "python" instead of "python3". <br/>
**Comments:** E.G., Here's how/why it sucks. <br/>
**Photos/Video:** Include a photo (mandatory) of your bed setup and/or a video of your printer while the script runs. A screenshot of your heatmap could also be helpful, but do not skip posting an actual photo of your bed setup. <br/>
**Start Gcode:** Copy-Paste your Start Gcode. <br/>
**M503:** Copy-Paste Your M503 Output <br/>


## Windows Batch File Help

### Step 0
Follow the previous instructions until it is time to run the script/program.
### Step 1
![Windows Batch File Step 1](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step1.jpg)
### Step 2
![Windows Batch File Step 2](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step2.jpg)
### Step 3
![Windows Batch File Step 3](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step3.jpg)
### Step 4
![Windows Batch File Step 4](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step4.jpg)
### Step 5
Go back and finish the remaining steps in the instructions.

