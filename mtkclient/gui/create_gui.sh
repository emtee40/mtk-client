#!/bin/sh
pyside6-uic main_gui.ui -o main_gui.py
pyside6-uic erasepart_gui.ui -o erasepart_gui.py
pyside6-uic readpart_gui.ui -o readpart_gui.py
pyside6-uic writepart_gui.ui -o writepart_gui.py
pyside6-uic readfull_gui.ui -o readfull_gui.py
pyside6-uic writefull_gui.ui -o writefull_gui.py
