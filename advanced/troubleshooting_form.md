### Troubleshooting Form/Questionnaire 

![Budget Bed Leveling](https://cdn.thingiverse.com/assets/1c/90/56/76/f5/featured_preview_81224952_10157946633951407_1884648180813922304_o.jpg)

I promise that I am not trying to brush you off. Delta calibration, especially on the Monoprice Mini Delta, can be complicated. Everything affects everything and there are numerous pitfalls that could be preventing you from obtaining a good first layer. Every single item/question here exists because it has tripped up someone else in the past. <br/>

The various scripts and other M665/M666 calibration methods are basically just dumb mathematical equations that take bed probe readings and tweak values to try to make the probe values read closer to the same numbers. It is usually not smart enough to tell you if something wrong with your hardware is interfering.

As stated in the main tutorial, once I have directed you to this page, **I will not help you until you make an honest attempt to fill out this questionnaire**. This form also sort of doubles as a checklist for the steps contained within the [full calibration guide](https://www.reddit.com/r/mpminidelta/comments/bzm1s2/updated_mpmd_calibration_guide_and_faq/). It is my recommendation to try to go through those, step-by-step, without skipping steps. Note that many of the questions have links embedded within them to help you better understand what is being asked. Some of the video links are long, but they almost always include a summary/abbreviation in the video description. <br/>

Do your best to fill this out, even if you just write "I do not understand." Even if you do not think it is relevant. Do not skip the bed photo. I'm usually pretty good about helping as long as you make an honest attempt to answer the questions. <br/>

**Computer Used:** Octopi/Windows7/Windows10/Mac/etc. <br/>
**[Firmware Version](https://www.mpminidelta.com/firmware/firmware_version_check) Shipped with Printer/Mainboard:** Stock v[37/38/39/40/41/42/43/44/45] <br/>
**Are you now using Marlin firmware?** Yes/No? copy-paste the firmware.bin filename and list the version of Marlin <br/>
**Build Plate Surface:** Glass/Mirror, PEI, WhamBam, Terrible Stock Sticker, Tape, etc. (also include how you decided to attach the bed to the printer) <br/>
**Did you remove the stock build surface sticker prior to installing the surface above?** Yes/No, Why? <br/>
**List any mods between the heated build plate and printer base that cannot be seen in your photo:** N/A <br/>
**Did you make sure that the bed heater wires are tucked away completely in the base hole?:** Yes/No <br/>
**Do you have [Dennis's Hold-Down Clips](https://www.youtube.com/watch?v=RSZ5xZf63Xo) Installed?** Yes/No <br/>
**Did you [calibrate Dennis's Hold-Down Clips](https://www.youtube.com/watch?v=2eko2PRa6y8) with an Index Card with the bed heated to printing temperature?** Yes/No <br/>
**Have you [tuned the belts](https://www.youtube.com/watch?v=gTtEJum10Ss) recently?** Yes/No <br/>
**Have you [lubricated moving parts](https://www.youtube.com/watch?v=2vuTZncnQYM) recently?** Yes/No <br/>
**Have you [shimmed the bed square to the rails](https://www.youtube.com/watch?v=2kGcRpWrSE8) (not always necessary)?** Yes/No <br/>
**Have you [ensured all arms are the same length](https://youtu.be/GYoeg-HAw0I) (very rarely necessary)?** Yes/No <br/>
**Is there any "play" in the carriage bearings and/or arm screws/nuts?** Yes/No/What <br/>
**Is your effector [colliding with a bed clip](https://youtu.be/tC87r8OVIII) (or something else)** Yes/No (See 8-second Video) <br/>
**Does the nozzle appear to be sliding across the surface at any probe point?** Yes/No <br/>
**Did you clean the filament off of the tip of the nozzle?** Yes/No <br/>
**Is the nozzle tapping only the primary print surface throughout the entire calibration process? I.E., it is not tapping outside of the glass/flexplate/tape/etc.** Yes/No <br/>
**Are the arms and/or effector getting stuck at the top near the wires and/or Bowden Tube ([Helpful Video](https://www.facebook.com/GrantSGarrison/videos/3705044122847715/))?** Yes/No <br/>
**Have you (optional) rotated any towers (swapping wires and/or M665 XYZ)?** Yes/No - Explain <br/>
**List any other mods that may affect bed leveling:** N/A <br/>
**What method did you use to calibrate M665/M666?:** auto_cal_p5.py, auto_cal_p5_v0.py, auto_cal_generic.py, auto_cal_p5_v0.bat, Dennis's spreadsheet, G33, MPMD Marlin 1.1.X's AUTO_CALIBRATE.GCODE, other (explain), etc.  <br/>
**Did you preheat the bed and/or nozzle prior to software calibration?:** Yes/No, what temperatures?  <br/>
**Terminal Command Used and/or Batch File Screenshot:** E.G., python3 auto_cal_p5.py [insert inputs here] <br/>
**Successful?** Yes/No/Partial <br/>
**Terminal Error:** Screenshot preferred. If applicable, copy and paste any script errors here <br/>
**If not successful, were you able to run "python auto_cal_p5_v0.py [INPUTS]"?** Yes/No - If no, paste that error as well. If N/A, try running this alternate script using "python" instead of "python3". <br/>
**Did you try any of Marlin's advanced post-processing options?** G29 C1, parabolic fit, least squares fit, manual mesh adjustment, etc.</br>
**Comments:** E.G., Here's how/why it sucks. <br/>
**Photos/Video:** Include a photo (mandatory) of your bed setup and/or a video of your printer while the script runs. A screenshot of your heatmap could also be helpful, but do not skip posting an actual photo of your bed setup. <br/>
**Start Gcode:** Copy-Paste your entire Start Gcode from your slicer. <br/>
**M503:** Send M503 over USB and Copy-Paste Your Output <br/>
