#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import time
import re
from enigma import getBoxType, getBoxBrand
from Components.SystemInfo import SystemInfo
import socket
import fcntl
import struct
from Components.Console import Console
from Tools.Directories import fileExists


def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', ifname[:15])
	info = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])


def getIfConfig(ifname):
	ifreq = {'ifname': ifname}
	infos = {}
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos['addr'] = 0x8915 # SIOCGIFADDR
	infos['brdaddr'] = 0x8919 # SIOCGIFBRDADDR
	infos['hwaddr'] = 0x8927 # SIOCSIFHWADDR
	infos['netmask'] = 0x891b # SIOCGIFNETMASK
	try:
		for k, v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	return ifreq


def getIfTransferredData(ifname):
	print("[About] Read /proc/net/dev")
	f = open('/proc/net/dev', 'r')
	for line in f:
		if ifname in line:
			data = line.split('%s:' % ifname)[1].split()
			rx_bytes, tx_bytes = (data[0], data[8])
			return rx_bytes, tx_bytes


def getVersionString():
	return getImageVersionString()


def getImageVersionString():
	try:
		if os.path.isfile('/var/lib/opkg/status'):
			print("[About] Read /var/lib/opkg/status")
			st = os.stat('/var/lib/opkg/status')
		tm = time.localtime(st.st_mtime)
		if tm.tm_year >= 2018:
			return time.strftime("%Y-%m-%d %H:%M:%S", tm)
	except:
		print("[About] Read /var/lib/opkg/status failed.")
	return _("unavailable")

# WW -placeholder for BC purposes, commented out for the moment in the Screen


def getFlashDateString():
	return _("unknown")


def getBuildDateString():
	try:
		if os.path.isfile('/etc/version'):
			print("[About] Read /etc/version")
			version = open("/etc/version", "r").read()
			return "%s-%s-%s" % (version[:4], version[4:6], version[6:8])
	except:
		print("[About] Read /etc/version failed.")
	return _("unknown")


def getUpdateDateString():
	try:
		if fileExists("/proc/openvision/compiledate"):
			print("[About] Read /proc/openvision/compiledate")
			build = open("/proc/openvision/compiledate", "r").read().strip()
		elif fileExists("/etc/openvision/compiledate"):
			print("[About] Read /etc/openvision/compiledate")
			build = open("/etc/openvision/compiledate", "r").read().strip()
		if build.isdigit():
			return "%s-%s-%s" % (build[:4], build[4:6], build[6:])
	except:
		print("[About] Read compiledate failed")
	return _("unknown")


def getEnigmaVersionString():
	import enigma
	enigma_version = enigma.getEnigmaVersionString()
	if '-(no branch)' in enigma_version:
		enigma_version = enigma_version[:-12]
	return enigma_version


def getGStreamerVersionString():
	from glob import glob
	if os.path.isfile('/usr/lib/pkgconfig/gstreamer-1.0.pc'):
		print("[About] Read /usr/lib/pkgconfig/gstreamer-1.0.pc")
		gstversion = [x.split("Version:") for x in open(glob("/usr/lib/pkgconfig/gstreamer-1.0.pc")[0], "r") if x.startswith("Version:")][0]
		if os.path.isfile('/usr/lib/libeplayer3.so'):
			return "GStreamer " + ("%s" % gstversion[1].replace("\n", "")) + " + eplayer3"
		else:
			return "GStreamer " + ("%s" % gstversion[1].replace("\n", ""))
	else:
		return _("eplayer3")


def getFFmpegVersionString():
	try:
		from glob import glob
		print("[About] Read /var/lib/opkg/info/ffmpeg.control")
		ffmpeg = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/ffmpeg.control")[0], "r") if x.startswith("Version:")][0]
		version = ffmpeg[1].split("-")[0].replace("\n", "")
		return "%s" % version.split("+")[0]
	except:
		print("[About] Read /var/lib/opkg/info/ffmpeg.control failed.")
		return _("Not Installed")


def getKernelVersionString():
	try:
		print("[About] Read /proc/version")
		return open("/proc/version", "r").read().split(' ', 4)[2].split('-', 2)[0]
	except:
		print("[About] Read /proc/version failed.")
		return _("unknown")


def getCPUBenchmark():
	try:
		cpucount = 0
		print("[About] Read /proc/cpuinfo")
		for line in open("/proc/cpuinfo").readlines():
			line = [x.strip() for x in line.strip().split(":")]
			if line[0] == "processor":
				cpucount += 1

		if not fileExists("/tmp/dhry.txt"):
			cmdbenchmark = "dhry > /tmp/dhry.txt"
			Console().ePopen(cmdbenchmark)
		if fileExists("/tmp/dhry.txt"):
			print("[About] Read /tmp/dhry.txt")
			cpubench = os.popen("cat /tmp/dhry.txt | grep 'Open Vision DMIPS' | sed 's|[^0-9]*||'").read().strip()
			benchmarkstatus = os.popen("cat /tmp/dhry.txt | grep 'Open Vision CPU status' | cut -f2 -d':'").read().strip()

		if cpucount > 1:
			cpumaxbench = int(cpubench) * int(cpucount)
			return "%s DMIPS per core\n%s DMIPS for all (%s) cores (%s)" % (cpubench, cpumaxbench, cpucount, benchmarkstatus)
		else:
			return "%s DMIPS (%s)" % (cpubench, benchmarkstatus)
	except:
		print("[About] Read /tmp/dhry.txt failed.")
		return _("unknown")


def getCPUSerial():
	print("[About] Read /proc/cpuinfo")
	with open('/proc/cpuinfo', 'r') as f:
		for line in f:
			if line[0:6] == 'Serial':
				return line[10:26]
		return "0000000000000000"


def getCPUInfoString():
	try:
		cpu_count = 0
		cpu_speed = 0
		processor = ""
		print("[About] Read /proc/cpuinfo")
		for line in open("/proc/cpuinfo").readlines():
			line = [x.strip() for x in line.strip().split(":")]
			if not processor and line[0] in ("system type", "model name", "Processor"):
				processor = line[1].split()[0]
			elif not cpu_speed and line[0] == "cpu MHz":
				cpu_speed = "%1.0f" % float(line[1])
			elif line[0] == "processor":
				cpu_count += 1

		if processor.startswith("ARM") and os.path.isfile("/proc/stb/info/chipset"):
			print("[About] Read /proc/stb/info/chipset")
			processor = "%s (%s)" % (open("/proc/stb/info/chipset").readline().strip().upper(), processor)

		if not cpu_speed:
			try:
				print("[About] Read /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
				cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
			except:
				print("[About] Read /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq failed.")
				cpu_speed = "-"

		temperature = None
		if os.path.isfile('/proc/stb/fp/temp_sensor_avs'):
			print("[About] Read /proc/stb/fp/temp_sensor_avs")
			temperature = open("/proc/stb/fp/temp_sensor_avs").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/power/avs'):
			print("[About] Read /proc/stb/power/avs")
			temperature = open("/proc/stb/power/avs").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/fp/temp_sensor'):
			print("[About] Read /proc/stb/fp/temp_sensor")
			temperature = open("/proc/stb/fp/temp_sensor").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/sensors/temp0/value'):
			print("[About] Read /proc/stb/sensors/temp0/value")
			temperature = open("/proc/stb/sensors/temp0/value").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/sensors/temp/value'):
			print("[About] Read /proc/stb/sensors/temp/value")
			temperature = open("/proc/stb/sensors/temp/value").readline().replace('\n', '')
		elif os.path.isfile("/sys/devices/virtual/thermal/thermal_zone0/temp"):
			try:
				print("[About] Read /sys/devices/virtual/thermal/thermal_zone0/temp")
				temperature = int(open("/sys/devices/virtual/thermal/thermal_zone0/temp").read().strip()) / 1000
			except:
				print("[About] Read /sys/devices/virtual/thermal/thermal_zone0/temp failed.")
		elif os.path.isfile("/sys/class/thermal/thermal_zone0/temp"):
			try:
				print("[About] Read /sys/class/thermal/thermal_zone0/temp")
				temperature = int(open("/sys/class/thermal/thermal_zone0/temp").read().strip()) / 1000
			except:
				print("[About] Read /sys/class/thermal/thermal_zone0/temp failed.")
		if temperature:
			degree = u"\u00B0"
			if not isinstance(degree, str):
				degree = degree.encode("UTF-8", errors="ignore")
			return "%s %s MHz (%s) %s%sC" % (processor, cpu_speed, ngettext("%d core", "%d cores", cpu_count) % cpu_count, temperature, degree)
		return "%s %s MHz (%s)" % (processor, cpu_speed, ngettext("%d core", "%d cores", cpu_count) % cpu_count)
	except:
		print("[About] Read temperature failed.")
		return _("undefined")


def getChipSetString():
	try:
		print("[About] Read /proc/stb/info/chipset")
		chipset = open("/proc/stb/info/chipset", "r").read()
		return str(chipset.lower().replace('\n', ''))
	except IOError:
		print("[About] Read /proc/stb/info/chipset failed.")
		return _("undefined")


def getCPUBrand():
	return _("STMicroelectronics")


def getCPUArch():
	return _("SH4")


def getFlashType():
	if SystemInfo["SmallFlash"]:
		return _("Small - Tiny image")
	elif SystemInfo["MiddleFlash"]:
		return _("Middle - Lite image")
	else:
		return _("Enough - Vision image")


def getDVBAPI():
	return _("Old - SH4")


def getVisionModule():
	if SystemInfo["OpenVisionModule"]:
		return _("Loaded")
	else:
		print("[About] No Open Vision module! hard multiboot?")
		return _("Unknown!")


def getDriverInstalledDate():
	from glob import glob
	try:
		print("[About] Read /var/lib/opkg/info/dvb-modules.control")
		driver = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/*dvb-modules*.control")[0], "r") if x.startswith("Version:")][0]
		return "%s-%s-%s" % (driver[:4], driver[4:6], driver[6:])
	except:
		print("[About] Read /var/lib/opkg/info/dvb-modules.control failed.")
		return _("unknown")


def getPythonVersionString():
	try:
		try:
			import commands
		except:
			import subprocess as commands
		status, output = commands.getstatusoutput("python -V")
		return output.split(' ')[1]
	except:
		print("[About] Get python version failed.")
		return _("unknown")


def GetIPsFromNetworkInterfaces():
	import socket
	import fcntl
	import struct
	import array
	import sys
	is_64bits = sys.maxsize > 2**32
	struct_size = 40 if is_64bits else 32
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	max_possible = 8 # initial value
	while True:
		_bytes = max_possible * struct_size
		names = array.array('B')
		for i in range(0, _bytes):
			names.append(0)
		outbytes = struct.unpack('iL', fcntl.ioctl(
			s.fileno(),
			0x8912,  # SIOCGIFCONF
			struct.pack('iL', _bytes, names.buffer_info()[0])
		))[0]
		if outbytes == _bytes:
			max_possible *= 2
		else:
			break
	namestr = names.tostring()
	ifaces = []
	for i in range(0, outbytes, struct_size):
		iface_name = bytes.decode(namestr[i:i + 16]).split('\0', 1)[0].encode('ascii')
		if iface_name != 'lo':
			iface_addr = socket.inet_ntoa(namestr[i + 20:i + 24])
			ifaces.append((iface_name, iface_addr))
	return ifaces


def getBoxUptime():
	try:
		time = ''
		print("[About] Read /proc/uptime")
		f = open("/proc/uptime", "r")
		secs = int(f.readline().split('.')[0])
		f.close()
		if secs > 86400:
			days = secs / 86400
			secs = secs % 86400
			time = ngettext("%d day", "%d days", days) % days + " "
		h = secs / 3600
		m = (secs % 3600) / 60
		time += ngettext("%d hour", "%d hours", h) % h + " "
		time += ngettext("%d minute", "%d minutes", m) % m
		return "%s" % time
	except:
		print("[About] Read /proc/uptime failed.")
		return '-'


# For modules that do "from About import about"
about = sys.modules[__name__]
