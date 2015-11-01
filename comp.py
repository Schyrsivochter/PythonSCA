import py_compile as pyc, os, sys

scaPath = os.path.dirname(__file__)

pyc.compile(scaPath + "\\sca.py", scaPath + "\\WD\\sca.pyc")
pyc.compile(scaPath + "\\scaguioo.py", scaPath + "\\WD\\scaguioo.pyc")
