#!/usr/bin/python3.6

"""Launcher script for the PythonSCA GUI.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

SCA² (C) 2012 Mark Rosenfelder aka Zompist (markrose@zompist.com)
Python re-code (C) 2015-2017 Andreas Kübrich aka Schyrsivochter (andreas.kuebrich@kuebrich.de)"""

import scaguioo
scaguioo.PythonSCA(1).MainLoop()
