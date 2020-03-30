pip install pynput
pip install -U wxPython
pip install pyinstaller

pyinstaller ^
    --onefile ^
    --noconsole ^
    --icon=.\pygrinder_icon.ico ^
    --distpath ../ ^
PyGrinder.py
