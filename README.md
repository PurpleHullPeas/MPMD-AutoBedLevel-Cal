# Monoprice Mini Delta P5 Endstop Script

This tutorial is designed to be used in place of Step C5 in Dennis Brown's great alignment/calibration tutorial.

I automated Dennis's G29 P5 Heatmap Spreadsheet for M666/M665 Calibration by updating Technoswiss's python script. Special thanks to them for all of their effort!

Python Script (auto_cal_p5.py): https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal

Dennis's [Spreadsheet](https://docs.google.com/spreadsheets/d/1rTn4vu2924AA_z1WppvLk4r31JXvoI1YI_7iSye0v3k/copy) and [Original Instructions](https://www.facebook.com/groups/mpminideltaowners/permalink/2186865287995612/)
You should only need this for generating pretty heatmaps. I.E., there's no need to go through his instructions if you're using this script.

![enter image description here](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/Before_After.jpg)
## Features

1) Started with Technoswiss's G29 P2 v2 python script and included the most up-to-date bug fixes from it.

2) Updated to use Dennis Brown's G29 P5 Excel heatmap calculations.

3) Saves results after each iteration in text files (can be copy-pasted into Dennis's spreadsheet).

4) Works with all firmware versions.

5) Saves time iterating through the Excel procedure yourself and makes it easier to update values when you make any mods or change the bed temperature.

# Disclaimer

Use at your own risk. Backup everything and keep your finger on the after-market power-button (that I'm sure you installed) while the script runs. I'm not responsible if your printer decides to spontaneously combust or if you void your warranty. All disclaimers and prerequisites listed by Technoswiss on his original project still apply.


# Tested Firmware and Operating Systems

## Tested Firmware
Stock v37 <br/>
Stock v41 <br/>
Stock v43 <br/>
Stock v44 <br/>
Marlin 8x <br/>
Marlin 16x <br/>


## Tested Operating Systems
Linux (mostly Octopi) <br/>
Windows 10 (batch file and command-line executable included) <br/>
The scripts should also work on Mac, but no one has reported back after installing all of the correct packages. <br/>

# Prerequisites

1) This script is intended to be used only **AFTER** you've gone through other calibration steps (namely Dennis's improved bed hold-down clips and having a more consistent bed surface). Do not run it unless you've made it that far in the [Calibration Roadmap](bit.ly/mpmdfaq) I've put together. If you're having trouble accessing this document, your adblocker may be blocking link shorteners.

2) You will need to be able to control your printer via USB. I use my Octopi (but not Octoprint) to run the script via terminal/command line (not to be confused with your print server terminal). <br/>
E.G., I don't have a monitor plugged into my Octopi, so I do all of this using [Putty](https://www.raspberrypi.org/documentation/remote-access/ssh/windows.md). I'm able to enter "octopi" instead of the IP address to connect, but YMMV.

3) Unless you're using the Windows executable, Python3 is required, with additional updates/packages.
**Octopi Installation:** (some unnecessary commands included to help noobs) <br/>
sudo apt-get install python3-serial <br/>
sudo apt-get install python3-scipy <br/>
sudo apt-get install python-serial <br/>
git clone https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal.git <br/>
cd MPMD-AutoBedLevel-Cal <br/>
git fetch <br/>
git pull <br/>
**Windows Installation:** <br/>
I recently released a command-line executable that can be used instead of the python script, as well as a batch file to make running it more straightforward: auto_cal_p5_v0.bat and auto_cal_p5_v0.exe (you will need both files in the same directory). <br/>
[Visual C++ Redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=48145) may be required whether you use the executable or the Python script. <br/>
If you prefer to use Python, you will need the additional packages included with [WinPython](http://winpython.github.io/). <br/>
**Mac/OSX Installation (not tested):** <br/>
Download [Python for Mac](https://www.python.org/downloads/mac-osx/) <br/>
[Install pyserial](https://stackoverflow.com/questions/31228787/install-pyserial-mac-os-10-10) <br/>
Install [scipy and related packages](https://www.scipy.org/install.html) <br/>

4) The points that the nozzle probes need to be consistent. I.E., if you're using tape, a sticker, PEI, glass, mirror, etc., you need to make sure the nozzle taps that for every probe point. If using tape, make sure it covers the entire build surface without overlapping. Whatever build surface you choose, make sure you remove the stock sticker before application because you want everything as flat as possible. If you typically use glue/hairspray on your bed, I recommend cleaning it off beforehand. The script will most definitely not work if the effector is colliding with a bed clip before the nozzle can probe the bed.

5) Dennis wrote the spreadsheet assuming you have his hold-down clips installed (see previously linked tutorial). This is not an optional step. You should also tune your belts if you haven't done so recently.


# INSTRUCTIONS:
**DO NOT FORGET TO COMPLETE THE REMAINING STEPS AFTER RUNNING THE PROGRAM! UPDATING YOUR M666, M665, and using G29 P5 (stock firmware) is crucial!**

1) Power cycle your printer to clear out any temporary settings.

2) Make sure the nozzle is clean and then turn the nozzle heat off.

3) Heat your bed up to your desired printing temperature and clean it. Let it sit for a while so that all parts get fully heated. Later when you run the script, you want to set the "-bt 60" parameter to whatever your desired bed temperature is.

4) If you're currently connected to the printer via Octoprint, Pronterface, Repetier, Cura, Simply3D, or some other service, click the Disconnect button now.

5) Run the Python script with your port connection, starting R and L values from Dennis's previous alignment tutorial step, the appropriate step/mm for your firmware, and your desired bed temperature. Standby with your finger on the power button, ready to abort, just in case weird things start happening. Don't forget to complete the remaining steps here after running the program.
 The following examples are provided for Octopi, using Dennis's default M665 L/R values, stock firmware, and a bed temperature of 60 C. Additional details for Windows will be covered later.
**Stock Firmware <=V41, V45**
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 57.14 -bt 60
**Stock V43 & V44**
python3 auto_cal_p5.py -p /dev/ttyACM0 -ff 0 -tf 0 -r 63.5 -l 123.0 -s 114.28 -bt 60
**Firmware Flag and Tower Flag Notes**
Because of differences in how stock firmware and Marlin4MPMD treats tower orientation and G29, you will need to set the firmware flag (-ff) and tower flag (-tf) appropriately.
-Stock Firmware: -ff 0 -tf 0
-Marlin4MPMD 1.3.3 (Default): -ff 1 -tf 1
-Marlin4MPMD 1.3.3 (M665 X-120 Y-120 Z-120): -ff 1 -tf 2
-Older Marlin4MPMD Versions (Default): -ff 1 -tf 0
-Other Configurations: You can try all three tower flags (0, 1, or 2) one at a time until one works. The script will stop due to an error in a few passes if you guessed the wrong configuration.
**Windows Executable Notes**
For Windows, you can can instead use the executable/batch file (see uploaded screenshots). You will need both the auto_cal_p5_v0.bat and auto_cal_p5_v0.exe files in the same folder for this to work. **Don't forget to complete the remaining steps here after running the program.**

6) The calibration values should now be set to whatever was calculated on the last pass. The outputs for each pass should be stored in files named auto_cal_p5_pass#.txt. You can paste the contents of this file into Dennis's spreadsheet to check your heatmap.
Note: I'm using [Samba](https://www.raspberrypi.org/magpi/samba-file-server/) to copy files between Windows and Linux.



7) [MARLIN ONLY] If you are using Marlin firmware, now would be a good time to re-run G29 P2 V4 while the bed is still hot. After that, you may want to revisit your z-offset. Unless you plan on re-running the full 7x7 G29 mesh before every print via your start gcode, you'll want to save your new mesh and calibration values with M500. You can find more information on this (as well as alternate/additional calibration methods) in the [Marlin4MPMD Wiki](https://github.com/mcheah/Marlin4MPMD/wiki/Calibration).

8) Stock firmware doesn't save M665 R with M500, so for the purposes of keeping things simple for this tutorial, I'm just going to suggest you save your M665/M666/M92 values in your starting gcode. If there are already lines in your Start Gcode with M665/M666/M92, replace those with your new values. For stock firmware, change your G29 line to G29 P5 Z0.28 (or whatever your offset is). Marlin4MPMD has other ways of handling G29 and EEPROM which you can read about in its wiki.


# TROUBLESHOOTING

**1) Python versions and/or dependency errors.** E.G., "python3: command not found", "ModuleNotFoundError: No module named 'numpy'", etc.
Try replacing "python3 auto_cal_p5.py" with "python auto_cal_p5_v0.py". This will both reduce the number of dependencies required to run the script and handle any issues where your OS may have assigned "python" to Python 3.X instead of "python3". You will still need to install pyserial for this to work.

**2) Serial Ports?**
The provided examples work for Octopi if you only have one serial device plugged into the rPi. Otherwise, you will need to replace "-p /dev/ttyACM0" with your appropriate serial port.
**Windows Example:** "-p COM3"
**Mac Example:** "-p /dev/tty.SOMETHING" (need to replace SOMETHING with your actual value)
If you're unsure of what your port name is, try seeing what it's called when you connect to the printer via Octoprint, Pronterface, Repetier, or some other service. Otherwise, try Googling, "how to find serial port name on my operating system".

**3) I had to abort because the nozzle started probing outside of the build area and/or the machine started making weird/bad noises.** Two possibilities come to mind:
**a) Hardware/setup issue.** Go back and read through the PREREQUISITES section. Also, please fill out the troubleshooting form at the bottom of this section (including a photo of your bed setup) so we can identify potential issues. It also probably wouldn't hurt to check the lubrication on your moving parts (guide rods, carriage arm joints, etc.).
**b) Bad M665 values.** The examples provided use Dennis's starting values and may not be applicable for your machine (although, they do seem to work for most). You can adjust these by replacing "-r 63.5 -l 123.0" with your desired R/L values. Ideally, you have calculated these values from the Carbon Paper Step C4 in Dennis's tutorial. If not, replace these numbers with whatever you've been using to print successfully.
How to find my current M665 values? First, check your Start Gcode in your slicer. If they aren't there, power cycle your machine and then send M503 via Octoprint/Pronterface/Repetier/etc.

**4) I reach the maximum number of runs and/or my results suck.**
Make sure you have Dennis Brown's custom hold-down clips installed. That step is not optional. Without the clips, the 5x5 probe mesh will make the bed wobble everywhere, preventing you from obtaining consistent results. Also, make sure you're using G29 P5 in your Start Gcode. For some reason, people keep skipping that step in the instructions. After that, you can further improve your results by removing the stock Buildtak and installing 120 mm borosilicate glass w/ a 0.5 mm thermal pad and/or PEI.

**5) My nozzle is going too high or low on the first layer (possibly even grinding into the plate).** Multiple possibilities come to mind.
a) A common cause of this is not using the proper M92 X/Y/Z values for your firmware (see Dennis's pinned tutorial in the Announcements). However, if you successfully ran the script, I doubt you made this mistake. Other possible causes are covered in the [Calibration Roadmap and FAQ](bit.ly/mpmdfaq)
b) More than a couple of users who flashed Marlin4MPMD firmware have forgotten to run the steps that come AFTER running the script. Make sure you get your new bed mesh by sending G29, save all of your results by issuing M500, and then remove any conflicting lines from your start gcode. This is just one way of doing it.
c) Z-Offset problem
As long as most of your points are <= 0.14 in the spreadsheet, you'll probably be okay. A high "Initial Layer Height" and finely-tuned z-offset (see: [MPMD 101](bit.ly/mpmd101) and/or the [Calibration Roadmap and FAQ](bit.ly/mpmdfaq)) can help compensate for any remaining issues. Tuning the z-offset should come AFTER adjusting the Initial Layer Height.

**6) "Calibration error on non-first run exceeds set limit."**
This error usually occurs for one of two reasons:
**a) Hardware problem.** Go back and read Troubleshooting point 3b.
**b) Wrong tower flag.** the -tf option tells the script how to account for any software tinkering of tower locations via Marlin4MPMD 1.3.3 and/or M665 X/Y/Z adjustments (not to be confused with M666). You can try each tower flag (0, 1 and 2) until you find one that works.

**7) Other Issues.** At this point, many users (both in this thread and elsewhere) have successfully run this script for all configurations of printer firmware on Octopi. Mac has not been as thoroughly-tested. If you're still having issues, please fill out the troubleshooting form at the bottom of this section, and post it via one of the following channels:
a) File an issue on this Stack Overflow page.
b) Respond to [my original thread on Facebook](https://www.facebook.com/groups/mpminideltaowners/permalink/2574670629215074/). 
c) Ask the question on [Reddit](https://www.reddit.com/r/mpminidelta/) and tag me /u/PurpleHullPeas 

## Troubleshooting Form

**Computer Used:** Octopi/Windows7/Windows10/Mac/etc.
**Firmware Version:** Stock v[37/38/39/40/41/42/43/44/45] or Marlin [8x/16x]
**Build Plate Surface: ** Glass/Mirror/PEI/Stock/Tape/etc. (also include if you use binder clips, printed clips, thermal pad, etc.)
**Do you have Dennis's Hold-Down Clips Installed?** Yes/No
**Do you have Dennis's Top Bed Switch Mod Installed?** Yes/No
**Terminal Command Used:** E.G., python3 auto_cal_p5.py [insert inputs here]
**Successful?** Yes/No/Partial
**Terminal Error:** N/A [If applicable, copy and paste any script errors here]
If not successful, are you able to run one of TechnoSwiss's other scripts? Yes/No/NA
**Comments:** E.G., Here's how/why it sucks.
**Photo/Video:** Assuming the script at least tried to run, including a photo of your bed setup and/or a video of your printer while the script runs would be helpful in identifying potential issues. A screenshot 
**Start Gcode:** Copy-Paste your Start Gcode
**M503:** Copy-Paste Your M503 Output

# Features

You can export the current file by clicking **Export to disk** in the menu. You can choose to export the file as plain Markdown, as HTML using a Handlebars template or as a PDF.


# Windows Batch File Help

## Step 1

![Windows Batch File Step 1](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step1.jpg)
## Step 2
![Windows Batch File Step 2](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step2.jpg)
## Step 3
![Windows Batch File Step 3](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step3.jpg)
## Step 4
![Windows Batch File Step 4](https://raw.githubusercontent.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/master/WindowsBat_Step4.jpg)


