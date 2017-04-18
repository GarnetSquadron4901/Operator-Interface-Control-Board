py -3.5 UpdateAllPip.py
py -3.5 -m pip install --upgrade --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix 
py -3.5-32 UpdateAllPip.py
py -3.5-32 -m pip install --upgrade --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix 
py -3.5 cx_setup.py bdist_msi
py -3.5-32 cx_setup.py bdist_msi
pause
