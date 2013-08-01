::
:: Utility for copying MH scripts to Blenders addon folder
:: Usage:
:: 
::     copy2blender path\to\addons\folder

echo Copy files to %1

rem Mhx importer already bundled with Blender
rem copy .\tools\blender26x\mhx_importer\*.py %1

mkdir %1\makeclothes
del %1\makeclothes\*.* /q
mkdir %1\makeclothes\__pycache__
del %1\makeclothes\__pycache__\*.* /q
copy .\tools\blender26x\makeclothes\*.py %1\makeclothes

mkdir %1\makeclothes\targets
del %1\makeclothes\targets\*.* /q
copy .\tools\blender26x\makeclothes\targets\*.target %1\makeclothes\targets

mkdir %1\maketarget
del %1\maketarget\*.* /q
mkdir %1\maketarget\__pycache__
del %1\maketarget\__pycache__\*.* /q
copy .\tools\blender26x\maketarget\*.py %1\maketarget

mkdir %1\maketarget\data
del %1\maketarget\data\*.* /q
copy .\tools\blender26x\maketarget\data\*.obj %1\maketarget\data
copy .\tools\blender26x\maketarget\data\*.mhclo %1\maketarget\data

mkdir %1\mh_mocap_tool
del %1\mh_mocap_tool\*.* /q
mkdir %1\mh_mocap_tool\__pycache__
del %1\mh_mocap_tool\__pycache__\*.* /q
copy .\tools\blender26x\mh_mocap_tool\*.py %1\mh_mocap_tool
copy .\tools\blender26x\mh_mocap_tool\*.json %1\mh_mocap_tool

mkdir %1\mh_mocap_tool\target_rigs
del %1\mh_mocap_tool\target_rigs\*.* /q
copy .\tools\blender26x\mh_mocap_tool\target_rigs\*.trg %1\mh_mocap_tool\target_rigs

mkdir %1\mh_mocap_tool\source_rigs
del %1\mh_mocap_tool\source_rigs\*.* /q
copy .\tools\blender26x\mh_mocap_tool\source_rigs\*.src %1\mh_mocap_tool\source_rigs

echo All files copied




