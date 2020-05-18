https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal

No more hand-holding in the advanced folder. 
You are still encouraged to report legitimate script errors/bugs.
If your question consists of "why is my bed still not level", 
then please go away and read the full calibration guide.

This is an experimental script. I don't know whether or not 
it will work better for you.
It is also still being tested on aegean-odyssey's firmware.

IMPORTANT: THIS SCRIPT WORKS DIFFERENTLY DEPENDING ON YOUR FIRMWARE!
Stock Firmware:
    Firmware Flag (-ff) = 0
    Tower Flag (-tf) = 0
    Calibration Pattern (-patt) = 2 or 5 only
Marlin4MPMD 1.3.3 Firmware by mcheah:
    Firmware Flag (-ff) = 1
    Tower Flag (-tf) = See main page instructions, but probably 1
    Calibration Pattern (-patt) = Anything except for the "G33" patterns
aegean-odyssey's MPMD Marlin 1.1.X Bugfix: 
    Firmware Flag (-ff) = 2
    Tower Flag (-tf) = Controls whether or not to include tower rotations, instead.
    Calibration Pattern (-patt) = 33 or 330-340 are also options.

Do not ask for a batch file or executable. 
Use Python, or go back to the basic-to-intermediate stuff.
I have a WinPython screenshot in the basic instructions 
and Octopi examples to copy-paste for Python help.

Known Issues: 
If for some reason you've made it this far and you're 
relying on the stock built-in WiFi (not Octopi), 
you might have trouble running the carbon paper test. 
Just print the gcode file instead. 
https://drive.google.com/open?id=1ti26of-TKoAjkr2QLdoFnVoZAiNE0M7G 

This script is for people going deep into the weeds.
If you try to use the options in here as a shortcut, 
that is on you.

What is new here (from the older p5 scripts)?

----------

More autoleveling options (-patt)
5:      Stock or Marlin - G29 P5 pattern. Same as the p5_v0 script.
2:      Stock or Marlin - G29 P2 pattern - 1 center point, 3 tower points (50 mm radius)
-2:     Marlin - 1 center point, 3 tower points (25 mm radius)
2550:   Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (50 mm radius)
2537.5: Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (37.5 mm radius)
2525:   Marlin - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (25 mm radius)
????.?:   Marlin - 1 center point, first two digits inner radius, remaining digits outer radius
33: Odyssey Marlin Only - Uses G33 except with automatic M665 L adjustment
330-340: Odyssey Marlin Only - Uses G33 except with automatic M665 L adjustment.
         Last digit is for G33_P parameter.
         https://marlinfw.org/docs/gcode/G033.html

Which pattern should you use? Whatever works best for you. This script is experimental.

Stock Firmware
5 works best with a properly setup bed. Follow ALL of the instructions on the main GitHub page.
2 might work better if you still have the stock sticker or you skipped other steps.
    No promises. Don't whine if it does not work well for you.

Marlin4MPMD 1.3.3
-2 worked best on my machine.
The 2550/2537.5/2525/etc. patterns were designed around this firmware.

aegean-odyssey MPMD Marlin 1.1.X
2 worked best for me, but the 330-340 options are interesting.

----------

Lratio (-ratio)
Dennis Brown determined that an experimental ratio of 1.5 works well for adjusting 
M665 L simultaneously as M665 R changes to maintain previously calibrated dimensional accuracy.
new_l = Lratio*(new_r-r_value) + l_value
You can change this if you want. 
Setting it to 0.0 will keep M665 L at your starting value.

----------

M665 ABCDEF (Marlin4MPMD only)
arguments: aaa, bbb, ccc, ddd, eee, fff
Details: https://github.com/mcheah/Marlin4MPMD/wiki/Calibration
You can set these values via script argument, 
but no special math is done with them.
I.E., this is purely a trial-and-error process.

----------

Hotend/Nozzle Temperature
-ht
Setting this to 100 degrees C may help with 
the carbon paper imprint. 
Setting it too high may cause oozing filament to
interfere with calibration.

----------

After-script prompts? 
I've added a prompt for running the carbon paper test 
upon script completion. This was so that I could more quickly 
test dimensional accuracy via trial-and-error.

----------

I am not going to cover the other inputs, because the 
p5 script guide already adequately does that.
