#!/bin/sh
pyside2-uic main_gui.ui -o main_gui.py
pyside2-uic erasepart_gui.ui -o erasepart_gui.py
pyside2-uic readpart_gui.ui -o readpart_gui.py
pyside2-uic writepart_gui.ui -o writepart_gui.py
pyside2-uic readfull_gui.ui -o readfull_gui.py
pyside2-uic writefull_gui.ui -o writefull_gui.py
