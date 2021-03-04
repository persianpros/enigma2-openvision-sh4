#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from Tools.Directories import resolveFilename, SCOPE_CONFIG, fileExists
from enigma import evfd

PERCENTAGE_START = 0
PERCENTAGE_END = 100

profile_start = time.time()

profile_data = {}
total_time = 1
profile_file = None

try:
	profile_old = open(resolveFilename(SCOPE_CONFIG, "profile"), "r").readlines()

	t = None
	for line in profile_old:
		(t, id) = line[:-1].split('\t')
		t = float(t)
		total_time = t
		profile_data[id] = t
except:
	print("[Profile] no profile data available")

try:
	profile_file = open(resolveFilename(SCOPE_CONFIG, "profile"), "w")
except IOError:
	print("[Profile] WARNING: couldn't open profile file!")


def profile(id):
	now = time.time() - profile_start
	if profile_file:
		profile_file.write("%7.3f\t%s\n" % (now, id))

		if id in profile_data:
			t = profile_data[id]
			if total_time:
				perc = t * (PERCENTAGE_END - PERCENTAGE_START) / total_time + PERCENTAGE_START
			else:
				perc = PERCENTAGE_START
			try:
				if fileExists("/proc/progress"):
					try:
#						print("[Profile] Write to /proc/progress")
						open("/proc/progress", "w").write("%d \n" % perc)
					except:
#						print("[Profile] Write to /proc/progress failed.")
				elif (perc > 1) and (perc < 98):
					value = 1
					if fileExists("/proc/stb/lcd/symbol_circle"):
#						print("[Profile] Write to /proc/stb/lcd/symbol_circle")
						open("/proc/stb/lcd/symbol_circle", "w").write("%1d \n" % value)
					if perc > 20:
						evfd.getInstance().vfd_write_string("-%02d-" % perc)
				elif perc > 98:
					value = 0
					if fileExists("/proc/stb/lcd/symbol_circle"):
#						print("[Profile] Write to /proc/stb/lcd/symbol_circle")
						open("/proc/stb/lcd/symbol_circle", "w").write("%1d \n" % value)
			except IOError:
				pass


def profile_final():
	global profile_file
	if profile_file is not None:
		profile_file.close()
		profile_file = None
