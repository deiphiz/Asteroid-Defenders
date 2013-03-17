import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"includes": ["pygame._view"], "include_files":["gamelib"]}
executable_options = {"icon":"icon.ico"}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "EPIC SPACE SHOOTER",
        version = "1.0",
        description = "Shoot bad guys and shit!",
        options = {"build_exe": build_exe_options, "cx_Freeze.Executable":executable_options},
        executables = [Executable("spaceShooter.pyw", base=base)])