REM Replace these inputs with those for your machine/setup.
REM Do not add any spaces or quotes.

REM Enter your com port exactly as it appears in Pronterface/Repetier/Cura/etc.
SET com_name=COM3

REM Preheat the bed before running the script.
REM Also enter your bed temperature here to ensure it stays heated
SET bed_temp=50

REM Fill in these M665 R and L values with your results from
SET M665_R=63.5
SET M665_L=123.0

REM Firmware Versions <=41, 45: Use 57.14
REM Firmware Version 43, 44: Use 114.28
SET steps_mm=57.14

REM If using Marlin, set to 1
SET firmware_flag=0

REM If using Marlin 1.3.3, also set this to 1
SET tower_flag=0

REM Don't mess with anything below here unless you know what you're doing
REM
SET x0=0.0
SET y0=0.0
SET z0=0.0
REM
%~dp0auto_cal_p5_v0.exe -p %com_name% -ff %firmware_flag% -tf %tower_flag% -r %M665_R% -l %M665_L% -s %steps_mm% -bt %bed_temp% -x %x0% -y %y0% -z %z0%
REM
cmd /k