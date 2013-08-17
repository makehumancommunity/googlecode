::
:: Utility for copying MH scripts to Blenders addon folder
:: Usage:
:: 
::     copy2blender path\to\addons\folder

echo Copy files to %1

rem Mhx importer already bundled with Blender
rem copy .\tools\blender\mhx_importer\*.py %1

mkdir %1\makeclothes
del %1\makeclothes\*.* /q
mkdir %1\makeclothes\__pycache__
del %1\makeclothes\__pycache__\*.* /q
copy .\tools\blender\makeclothes\*.py %1\makeclothes

mkdir %1\makeclothes\targets
del %1\makeclothes\targets\*.* /q
copy .\tools\blender\makeclothes\targets\*.target %1\makeclothes\targets

mkdir %1\maketarget
del %1\maketarget\*.* /q
mkdir %1\maketarget\__pycache__
del %1\maketarget\__pycache__\*.* /q
copy .\tools\blender\maketarget\*.py %1\maketarget

mkdir %1\maketarget\data
del %1\maketarget\data\*.* /q
copy .\tools\blender\maketarget\data\*.obj %1\maketarget\data
copy .\tools\blender\maketarget\data\*.mhclo %1\maketarget\data

mkdir %1\makewalk
del %1\makewalk\*.* /q
mkdir %1\makewalk\__pycache__
del %1\makewalk\__pycache__\*.* /q
copy .\tools\blender\makewalk\*.py %1\makewalk
copy .\tools\blender\makewalk\*.json %1\makewalk

mkdir %1\makewalk\target_rigs
del %1\makewalk\target_rigs\*.* /q
copy .\tools\blender\makewalk\target_rigs\*.trg %1\makewalk\target_rigs
copy .\tools\blender\makewalk\target_rigs\*.json %1\makewalk\target_rigs

mkdir %1\makewalk\source_rigs
del %1\makewalk\source_rigs\*.* /q
copy .\tools\blender\makewalk\source_rigs\*.src %1\makewalk\source_rigs
copy .\tools\blender\makewalk\source_rigs\*.json %1\makewalk\source_rigs

echo All files copied




