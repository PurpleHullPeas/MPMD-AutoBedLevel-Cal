https://github.com/PurpleHullPeas/MPMD-AutoBedLevel-Cal

No more hand-holding in the advanced folder. 
You are still encouraged to report legitimate script errors/bugs.
If your question consists of "why is my bed still not level", 
then please go away and read the full calibration guide.

This is an experimental script. I don't know whether or not 
it will work better for you.
I also don't know if it will work with aegean-odyssey's firmware.

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
5:      Stock or Marlin4MPMD - G29 P5 pattern. Same as the p5_v0 script.
2:      Stock or Marlin4MPMD - G29 P2 pattern - 1 center point, 3 tower points (50 mm radius)
-2:     Marlin4MPMD - 1 center point, 3 tower points (25 mm radius)
2550:   Marlin4MPMD - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (50 mm radius)
2537.5: Marlin4MPMD - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (37.5 mm radius)
2525:   Marlin4MPMD - 1 center point, 3 tower points (25 mm radius), 12 outer ring points (25 mm radius)
????.?:   Marlin4MPMD - 1 center point, first two digits inner radius, remaining digits outer radius

Which pattern should you use? Whatever works best for you. This script is experimental.

Generally, for stock firmware, 5 works best with a properly setup bed.

For Marlin4MPMD, I'm thinking one of the last options will probably work best, 
since they align with the 7x7 matrix.

2 or -2 are the fastest because of fewer probe points. 
This is basically like Marlin G33 R50 or G33 R25, 
except it also calculates R and (optionally) L (see Lratio).
It also might be okay for all of the people trying to take hardware shortcuts. 
That being said, don't whine if your results stink.

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