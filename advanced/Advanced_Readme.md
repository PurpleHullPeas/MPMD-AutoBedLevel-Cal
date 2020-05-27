# Advanced Calibration (auto_cal_generic.py)

If you're trying to tackle advanced calibration, then it is assumed that you have already gone through the steps outlined in the [Calibration Roadmap](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/). If not, then do not act surprised when things do not work well for you. I will add some extra reminders here, but this page is not comprehensive. Also, this page isn't for the basic "I don't know how to connect to USB, why bed not level?" types of questions. Go back to [MPMD 101](https://docs.google.com/document/d/1LHomAxmgSWEggiCM1p6B0vZCIcJPIFTe0OqnozhtZxc/edit) and/or the [P5 script tutorial](https://youtu.be/kyznWfPQgBk) if you need that level of help.

## Mandatory Troubleshooting Form

Much like the P5 tutorial, **I WILL NOT HELP YOU AT ALL UNLESS YOU FILL OUT THE [TROUBLESHOOTING FORM](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal/blob/master/advanced/troubleshooting_form.md)**. As a matter of fact, you are on the advanced tutorial page now, so things get a little hairier, anyways. Things are not quite as cut-and-dry here, so you may have to do your own experimentation.

## Recommended Hardware Upgrades/Alignments: 

1. General [cleaning, lubrication](https://youtu.be/2vuTZncnQYM), [belt tuning](https://youtu.be/gTtEJum10Ss), part inspection, making sure no nuts are loose, [recalibrating the bed clips](https://youtu.be/2eko2PRa6y8), etc.

2. You absolutely must do something to address/calibrate the precision/consistency/activation of the bed leveling switches. I.E., you need to ensure that the bed switches activate at the same distance every time the bed is probed, regardless of where the bed is probed. You also need to know what that probe distance is. I highly recommend using [well-tested bed hold-down clips](https://youtu.be/RSZ5xZf63Xo). 

3. The bed surface needs to be completely consistent so that the nozzle probes the exact same surface height for every point. Yes, a height difference the thickness of tape or a sticker makes a huge difference.

4. The bed should preferably be a perfectly flat glass plate or a mirror. I recommend either a [thermal pad](https://youtu.be/5neI6RTg0IE) or a [budget glue-down solution](https://youtu.be/qceoahMSJIU). Other glass mounting solutions might introduce problems, as is explained in the video descriptions of the previous links. If your bed is not perfectly flat (e.g. WhamBam), then you may have to do additional work to get good results (explained later). Some people add PEI or a flexplate on top of glass to get a surface that is simultaneously flat and convenient.

5. The bed may need to be [shimmed square to the rails](https://youtu.be/2kGcRpWrSE8). This is a quality control issue in that some MPMDs desperately need it while others aren't too bad (I have personally checked 3 MPMDs for this). If yours needs it, this will have a huge impact on bed leveling. Delta math assumes that the bed is square to the rails.

6. [Physically adjusting all arms to be the same length](https://youtu.be/GYoeg-HAw0I) can also help the delta kinematics behave more predictably. If you are trying to achieve perfect dimensional accuracy, this adjustment becomes much more important. It may also positively impact bed leveling. Once again, this is a quality control issue in that some printers may come from the factory better or worse than others. Delta math usually (unless using the advanced offset options) assumes that all arms are the same length.

Note: Any time you mess with the hardware, you should recalibrate your machine.

## Firmware Options

The previously mentioned hardware upgrades will help, regardless of the firmware version used.

1. [Stock Firmware](https://www.mpminidelta.com/firmware/motion_controller) (not recommended) - you are very limited on what you can do with stock firmware. The only new feature versus the [P5 tutorial](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal) is the addition of the P2 calibration option. Most of the advanced calibration parameters referenced on this page (e.g. M665 ABCDEFXYZ) do not exist on stock firmware.

2. [Marlin4MPMD 1.3.3](https://github.com/mcheah/Marlin4MPMD) by mcheah - This firmware is no longer supported, but the script should also work with it. Note that a few things like the tower rotation flag (explained in the P5 tutorial) and G33 works differently compared to aegean-odyssey's MPMD Marlin 1.X.X.

3. [MPMD Marlin 1.1.X](https://github.com/aegean-odyssey/mpmd_marlin_1.1.x) by aegean-odyssey - By default, the script will turn off the probe compensation routine unless you remove that part of the Python code yourself. It uses a more current G33 routine and for this firmware option, the script's tower flag is used to control the G33 T parameter. (explained more later) .

## Calibration Script Inputs and Delta Calibration Gcode Parameters

Since this is an advanced tutorial, I will try to cover the delta calibration parameters you can control via the firmware. Now that you have done your best to align the hardware to the best of your abilities, it is time to adjust the calibration parameters to achieve accurate delta kinematics (printhead movement, bed leveling, dimensional accuracy, etc.). The command-line script argument will be put in parenthesis.

M666 and M665 help define the delta geometry that help calculate the delta kinematics (i.e. tells the printer how to move). 
Because of the complexity and nonlinearity of the equations, "everything affects everything" is a safe assumption, which is why it can take an iterative trial-and-error process in order to properly set delta kinematics parameters. Put another way, if you want to fix both bed leveling AND dimensional accuracy, the process gets more complicated.

### M92 XYZ Motor Steps per mm (-s)
This is already covered in detail on [this page](https://www.thingiverse.com/thing:3892011). Note that Marlin may default the M92 XYZ 1/16 values to 114.29 instead of 114.28. If you care, try both to see which one gives you better vertical dimensional accuracy. Do this first, because it will absolutely affect your other calibration parameters.

### M666 XYZ Delta Endstop Adjustments (-x) (-y) (-z)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M666.html)

In theory, M666 XYZ is used to adjust the positions of the home sensors (at the top of the printer) via software. It has the most direct impact on bed leveling, but can also mess with dimensional accuracy. Adjusting only M666 without also adjusting M665 can sometimes results in a bowl, dome, or dip-shaped movement where the probed height of the center of the bed is significantly different (higher or lower) from the outer edges. If this is your first time running the script, you should keep all of these values at 0.0. Nonzero values in this field can optionally be used later for various trial-and-error solutions.

I do not want to provide a photo of tower locations, because this may vary depending on what hardware and/or firmware tweaks you have performed. You can figure out which tower is which by homing (G28) and then moving the printhead to these positions: 
Tower X = G1 X-43.3 Y-25 Z10
Tower Y = G1 X43.3 Y-25 Z10
Tower Z = G1 X0 Y50 Z10

### M665 L Diagonal Rod Length (-l) and ratio (-Lratio)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html) 
[Visual Representation/Math](https://reprap.org/wiki/Delta_geometry) 
M665 L defines the length of the arms. It has the most direct impact on dimensional accuracy, but can also affect bed leveling. Many guides (and G33) leave this as a manual-user-entry trial-and-error input, but Dennis Brown in the Facebook group derived a simple equation, via experimentation, which can help maintain previously calibrated dimensional accuracy as you continue to adjust M666 XYZ and M665 R simultaneously.
L_new = L_old + Lratio*(R_new-R_old)
Lratio ~ 1.5 for most stock MPMDs, but may vary if your arm lengths are drastically different.
Your starting LR values should ideally come from the carbon paper step or [basic dimensional accuracy tutorial](https://youtu.be/Sscz8CBmmok).

### M665 R Delta Radius (-r)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html) 
[Visual Representation/Math](https://reprap.org/wiki/Delta_geometry) 
M665 R has a direct impact on dimensional accuracy and reducing the bowl/dome shape (previously discussed under M666 XYZ). If you are using Dennis's previously-mentioned M665 L equation, then you can use M665 R to do a lot of your initial dimensional accuracy tweaks. Otherwise, most generic delta calibrations use M665 R just to reduce the dome/bowl movement while letting the user manually change M665 L for dimensional accuracy via trial-and-error.

### M665 H Delta Height (-hhh)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html) 
For all practical purposes, the height is handled when G29 is used to create your bed mesh and/or in your Start Gcode. However, I included this since it appears that the newer G33 routine in later versions of Marlin (not mcheah's version) may be affected somewhat by this when it comes to avoiding "delta calibration error." You are probably okay leaving this at its default value.

### M665 S Segments Per Second (-sss)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html) 
[Reddit Discussion](https://www.reddit.com/r/mpminidelta/comments/cr7rie/pimples_after_calibration_fixed_by_reducing/) 
This probably will not affect your calibration results, but I added it to the script so that I wouldn't have to enter it over terminal. It can have a large impact on print quality for certain prints under certain circumstances. 

### M665 V Delta Calibration Radius (-vvv)
Only applicable to MPMD Marlin 1.X.X. Controls the calibration radius for the up-to-date version of G33. Use this instead of the B parameter mentioned on the [Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html). If trying to use G33, you may have to change this for the calibration to succeed. E.G., default is 50, but 40 or 30 may work better.

### M665 XYZ Tower Offset Angles (-xxx) (-yyy) (-zzz)
[Marlin Reference Page](https://marlinfw.org/docs/gcode/M665.html) 
[Marlin4MPMD 1.3.3 Reference Page](https://github.com/mcheah/Marlin4MPMD/wiki/Calibration)
[G33](https://marlinfw.org/docs/gcode/G033.html) in MPMD Marlin 1.X.X has an option for automatically adjusting this. Basically applies an angular offset to the towers. I haven't needed to use this, but feel free to experiment.

### M665 ABCDEF Advanced Offset Parameters (-aaa) (-bbb) (-ccc) (-ddd) (-eee) (-fff)
[Marlin4MPMD 1.3.3 Reference Page](https://github.com/mcheah/Marlin4MPMD/wiki/Calibration)
These are highly experimental values that were made specifically for Marlin4MPMD and later imported into MPMD Marlin 1.X.X. These are the parameters you will need to adjust to fix dimensional accuracy issues specific to a tower. Zek Negus in the Facebook Group does his final dimensional accuracy tweaks only with the diagonal rod length offsets (ABC); however, I have had luck fixing things just by adjusting the delta radii offsets (DEF). Because of the experimental trial-and-error nature of these adjustments, I would recommend getting M666 XYZ and M665 LR adjusted for the best average dimensional accuracy and bed leveling possible before proceeding here.

### Serial Port (-p)
This is the serial port the printer is connected to on your computer. This will be the same thing that you see in Pronterface, Octoprint, Repetier, or whatever program you normally use to send commands over USB. 
E.G.
/dev/ttyACM0
COM3
/dev/tty.SOMETHING

### Hotend and Bed Temperature (-ht) (-bt)
You can set the hotend and bed temperature as script arguments so that the firmware will not automatically shut them down while the script is running. I highly recommend setting the bed temperature to your usual print temperature prior to calibration. A hotend temperature of 100 C can make the carbon paper test come out more clearly. I would not push the hotend temperature too high because oozing filament could impact calibration values.

### Firmware Flag (-ff)
0 = Stock Firmware
1 = Marlin4MPMD 1.2.2 or 1.3.3
2 = MPMD Marlin 1.X.X

### Tower Flag (-tf)
0 = Stock Firmware.
Marlin4MPMD 1.3.3: Read the discussion on the [P5 tutorial](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal).
MPMD Marlin 1.X.X: G33 T option - 0 (do not rotate towers) or 1 (rotate towers M665 XYZ).

### Calibration Pattern (-patt)
You can experiment to find whichever pattern works the best for you. For stock firmware, P5 is well-tested/known to be the best when you follow all of the instructions on the [P5 tutorial](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal).

5:      Stock or Marlin - G29 P5 pattern. Same as the p5_v0 script.
2:      Stock or Marlin - G29 P2 pattern - 1 center point, 3 tower points (50 mm radius)
-2:     Marlin - 1 center point, 3 tower points (25 mm radius)
2550:   Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (50 mm radius)
2537.5: Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (37.5 mm radius)
2525:   Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (25 mm radius)
????.?: Marlin - 1 center point, first two digits inner radius, remaining digits outer radius
33: Odyssey Marlin Only - Uses G33 except with automatic M665 L adjustment
330-340: Odyssey Marlin Only - Uses G33 except with automatic M665 L adjustment.
         Last digit is for G33_P parameter.
         https://marlinfw.org/docs/gcode/G033.html

Which pattern should you use? Whatever works best for you. This script is experimental.

Stock Firmware
5 works best with a properly setup bed. Follow ALL of the instructions on the [P5 tutorial](https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal).
2 might work better if you still have the stock sticker or you skipped other steps. No promises. Don't whine if it does not work well for you.

Marlin4MPMD 1.3.3
-2 worked best on my machine.
The 2550/2537.5/2525/etc. patterns were designed around this firmware.

aegean-odyssey MPMD Marlin 1.1.X
2 worked best for me, but the 330-340 options are interesting.
