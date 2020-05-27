# auto_cal_generic.py

If you're trying to tackle advanced calibration, then it is assumed that you have already gone through the steps outlined in the [Calibration Roadmap](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/). If not, then do not act surprised when things do not work well for you. I will add some extra reminders here, but this page is not comprehensive. Also, this page isn't for the basic "I don't know how to connect to USB, why bed not level?" types of questions. Go back to [MPMD 101](https://docs.google.com/document/d/1LHomAxmgSWEggiCM1p6B0vZCIcJPIFTe0OqnozhtZxc/edit) and/or the [P5 script tutorial](https://youtu.be/kyznWfPQgBk) if you need that level of help.

## Mandatory Troubleshooting Form

Much like the P5 tutorial, **I WILL NOT HELP YOU AT ALL UNLESS YOU FILL OUT THE [TROUBLESHOOTING FORM](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/blob/master/advanced/troubleshooting_form.md)**. As a matter of fact, you are on the advanced tutorial page now, so things get a little hairier, anyways. Things are not quite as cut-and-dry here, so you may have to do your own experimentation.

## Recommended Hardware Upgrades: 

1. General [cleaning, lubrication](https://youtu.be/2vuTZncnQYM), [belt tuning](https://youtu.be/gTtEJum10Ss), part inspection, making sure no nuts are loose, [recalibrating the bed clips](https://youtu.be/2eko2PRa6y8), etc.

2. You absolutely must do something to address/calibrate the precision/consistency/activation of the bed leveling switches. I.E., you need to ensure that the bed switches activate at the same distance every time the bed is probed, regardless of where the bed is probed. You also need to know what that probe distance is. I highly recommend using [well-tested bed hold-down clips](https://youtu.be/RSZ5xZf63Xo). 

3. The bed surface needs to be completely consistent so that the nozzle probes the exact same surface height for every point. Yes, a height difference the thickness of tape or a sticker makes a huge difference.

4. The bed should preferably be a perfectly flat glass plate or a mirror. I recommend either a [thermal pad](https://youtu.be/5neI6RTg0IE) or a [budget glue-down solution](https://youtu.be/qceoahMSJIU). Other glass mounting solutions might introduce problems, as is explained in the video descriptions of the previous links. If your bed is not perfectly flat (e.g. WhamBam), then you may have to do additional work to get good results (explained later). Some people add PEI or a flexplate on top of glass to get a surface that is simultaneously flat and convenient.

5. The bed may need to be [shimmed square to the rails](https://youtu.be/2kGcRpWrSE8). This is a quality control issue in that some MPMDs desperately need it while others aren't too bad (I have personally checked 3 MPMDs for this). If yours needs it, this will have a huge impact on bed leveling.

6. [Physically adjusting all arms to be the same length](https://youtu.be/GYoeg-HAw0I) can also help the delta kinematics behave more predictably. If you are trying to achieve perfect dimensional accuracy, this adjustment becomes much more important. It may also positively impact bed leveling. Once again, this is a quality control issue in that some printers may come from the factory better or worse than others.

Note: Any time you mess with the hardware, you should recalibrate your machine.

## Firmware Requirements

The previously mentioned hardware upgrades will help, regardless of the firmware version used.

1. Stock Firmware (not recommended) - you are very limited on what you can do with stock firmware. The only new feature versus the [P5 tutorial](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal) is the addition of the P2 calibration option.

2. Marlin4MPMD 1.3.3 by mcheah - This firmware is no longer supported, but the script should also work with it. Note that a few things like the tower rotation flag (explained in the P5 tutorial) and G33 works differently compared to aegean-odyssey's MPMD Marlin 1.X.X.

3. MPMD Marlin 1.1.X by aegean-odyssey - By default, the script will turn off the probe compensation routine unless you remove that part of the Python code yourself. It uses a more current G33 routine and for this firmware option, the script's tower flag is used to control the G33 T parameter. (explained more later) .

## Delta Calibration Gcode Parameters

Since this is an advanced tutorial, I will try to cover the delta calibration parameters you can control via the firmware. Now that you have done your best to align the hardware to the best of your abilities, it is time to adjust the calibration parameters to achieve accurate delta kinematics (printhead movement, bed leveling, dimensional accuracy, etc.).

### M92 XYZ Steps per mm
This is already covered in detail on [this page](https://www.thingiverse.com/thing:3892011). Note that Marlin may default the M92 XYZ 1/16 values to 114.29 instead of 114.28. If you care, try both to see which one gives you better vertical dimensional accuracy. Do this first, because it will absolutely affect your other calibration parameters.

### In Progress
