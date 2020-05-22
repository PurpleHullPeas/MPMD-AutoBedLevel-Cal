This is a work in progress.

##Recommended Hardware Upgrades: 

Any time you mess with the hardware, 

1. General cleaning, lubrication, belt tuning, part inspection, making sure no nuts are loose, recalinrating the bed clips, etc.

2. You absolutely must do something to address/calibrate the Precision/Consistency/Activation of the bed leveling switches. I.E., you need to ensure that the bed switches activate at the same distance every time the bed is probed, regardless of where the bed is probed. You also need to know what that probe distance is. I highly recommend using well-tested bed hold-down clips. 

3. The bed surface needs to be completely consistent so that the nozzle probes the exact same surface height for every point. Yes, a height difference the thickness of tape or a sticker makes a huge difference.

4. The bed should preferably be a perfectly flat glass plate or a mirror. I recommend either a thermal pad or a budget glue-down solution. Other mounting solutions may introduce problems, as is explained in the video descriptions of the previous links. If your bed is not perfectly flat (e.g. WhamBam), then you may have to do additional work to get good results.

5. The bed may need to be shimmed square to the rails. This is a quality control issue in that some MPMDs desperately need it while others aren't too bad (I have personally checked 3 MPMDs for this).

6. Physically adjusting all arms to be the same length can also help the delta kinematics behave more predicatably. If you are trying to achieve perfect dimensional accuracy, this adjustment becomes much more important. It may also positively impact bed leveling. 

##M92 XYZ Steps per mm
This is already covered in detail on [this page](https://www.thingiverse.com/thing:3892011). Note that Marlin may default the M92 XYZ 1/16 values to 114.29 instead of 114.28. If you care, try both to see which one gives you better vertical dimensional accuracy.
