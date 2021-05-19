from os import R_OK, access, listdir, walk
from os.path import isdir, isfile, join as pathjoin
from re import findall
from subprocess import PIPE, Popen

from enigma import Misc_Options, eDVBCIInterfaces, eDVBResourceManager, eGetEnigmaDebugLvl

from Tools.Directories import SCOPE_SKIN, fileCheck, fileExists, fileHas, fileReadLine, fileReadLines, pathExists, resolveFilename

MODULE_NAME = __name__.split(".")[-1]
ENIGMA_KERNEL_MODULE = "openvision.ko"
PROC_PATH = "/proc/openvision"

SystemInfo = {}


class BoxInformation:  # To maintain data integrity class variables should not be accessed from outside of this class!
	def __init__(self):
		self.enigmaList = []
		self.enigmaInfo = {}
		self.immutableList = []
		self.boxInfo = {}
		self.procList = [file for file in listdir(PROC_PATH) if isfile(pathjoin(PROC_PATH, file))] if isdir(PROC_PATH) else []
		lines = fileReadLines("/etc/enigma.conf", source=MODULE_NAME)
		if lines:
			for line in lines:
				if line.startswith("#") or line.strip() == "":
					continue
				if "=" in line:
					item, value = [x.strip() for x in line.split("=", 1)]
					if item:
						self.enigmaList.append(item)
						self.enigmaInfo[item] = self.processValue(value)
			print("[SystemInfo] Enigma config override file available and data loaded into BoxInfo.")
		for dirpath, dirnames, filenames in walk("/lib/modules"):
			if ENIGMA_KERNEL_MODULE in filenames:
				modulePath = pathjoin(dirpath, ENIGMA_KERNEL_MODULE)
				self.boxInfo["enigmamodule"] = modulePath
				self.immutableList.append("enigmamodule")
				break
		# As the /proc values are static we can save time by using cached
		# values loaded here.  If the values become dynamic this code
		# should be disabled and the dynamic code below enabled.
		if self.procList:
			for item in self.procList:
				self.boxInfo[item] = self.processValue(fileReadLine(pathjoin(PROC_PATH, item), source=MODULE_NAME))
				self.immutableList.append(item)
			print("[SystemInfo] Enigma kernel module available and data loaded into BoxInfo.")
		else:
			process = Popen(("/sbin/modinfo", "-d", modulePath), stdout=PIPE, stderr=PIPE)
			stdout, stderr = process.communicate()
			if process.returncode == 0:
				for line in stdout.split("\n"):
					if "=" in line:
						item, value = line.split("=", 1)
						if item:
							self.procList.append(item)
							self.boxInfo[item] = self.processValue(value)
							self.immutableList.append(item)
				print("[SystemInfo] Enigma kernel module not available but modinfo data loaded into BoxInfo!")
			else:
				print("[SystemInfo] Error: Unable to load Enigma kernel module data!  (Error %d: %s)" % (process.returncode, stderr.strip()))
		self.enigmaList = sorted(self.enigmaList)
		self.procList = sorted(self.procList)

	def processValue(self, value):
		if value is None:
			pass
		elif value.startswith("\"") or value.startswith("'") and value.endswith(value[0]):
			value = value[1:-1]
		elif value.startswith("(") and value.endswith(")"):
			data = []
			for item in [x.strip() for x in value[1:-1].split(",")]:
				data.append(self.processValue(item))
			value = tuple(data)
		elif value.startswith("[") and value.endswith("]"):
			data = []
			for item in [x.strip() for x in value[1:-1].split(",")]:
				data.append(self.processValue(item))
			value = list(data)
		elif value.upper() == "NONE":
			value = None
		elif value.upper() in ("FALSE", "NO", "OFF", "DISABLED"):
			value = False
		elif value.upper() in ("TRUE", "YES", "ON", "ENABLED"):
			value = True
		elif value.isdigit() or (value[0:1] == "-" and value[1:].isdigit()):
			value = int(value)
		elif value.startswith("0x") or value.startswith("0X"):
			value = int(value, 16)
		elif value.startswith("0o") or value.startswith("0O"):
			value = int(value, 8)
		elif value.startswith("0b") or value.startswith("0B"):
			value = int(value, 2)
		else:
			try:
				value = float(value)
			except ValueError:
				pass
		return value

	def getEnigmaList(self):
		return self.enigmaList

	def getProcList(self):
		return self.procList

	def getItemsList(self):
		return sorted(list(self.boxInfo.keys()))

	def getItem(self, item, default=None):
		if item in self.enigmaList:
			value = self.enigmaInfo[item]
		# As the /proc values are static we can save time by uusing cached
		# values loaded above.  If the values become dynamic this code
		# should be enabled.
		# elif item in self.procList:
		# 	value = self.processValue(fileReadLine(pathjoin(PROC_PATH, item), source=MODULE_NAME))
		elif item in self.boxInfo:
			value = self.boxInfo[item]
		elif item in SystemInfo:
			value = BoxInfo.getItem(item]
		else:
			value = default
		return value

	def setItem(self, item, value, immutable=False):
		if item in self.immutableList or item in self.procList:
			print("[BoxInfo] Error: Item '%s' is immutable and can not be %s!" % (item, "changed" if item in self.boxInfo else "added"))
			return False
		if immutable:
			self.immutableList.append(item)
		self.boxInfo[item] = value
		BoxInfo.getItem(item] = value
		return True

	def deleteItem(self, item):
		if item in self.immutableListor or item in self.procList:
			print("[BoxInfo] Error: Item '%s' is immutable and can not be deleted!" % item)
		elif item in self.boxInfo:
			del self.boxInfo[item]
			return True
		return False


BoxInfo = BoxInformation()

from Tools.Multiboot import getMultibootStartupDevice, getMultibootslots  # This import needs to be here to avoid a SystemInfo load loop!

# Parse the boot commandline.
cmdline = fileReadLine("/proc/cmdline", source=MODULE_NAME)
cmdline = {k: v.strip('"') for k, v in findall(r'(\S+)=(".*?"|\S+)', cmdline)}


def getNumVideoDecoders():
	numVideoDecoders = 0
	while fileExists("/dev/dvb/adapter0/video%d" % numVideoDecoders, "f"):
		numVideoDecoders += 1
	return numVideoDecoders


def countFrontpanelLEDs():
	numLeds = fileExists("/proc/stb/fp/led_set_pattern") and 1 or 0
	while fileExists("/proc/stb/fp/led%d_pattern" % numLeds):
		numLeds += 1
	return numLeds


def hassoftcaminstalled():
	from Tools.camcontrol import CamControl
	return len(CamControl("softcam").getList()) > 1


def getBootdevice():
	dev = ("root" in cmdline and cmdline["root"].startswith("/dev/")) and cmdline["root"][5:]
	while dev and not fileExists("/sys/block/%s" % dev):
		dev = dev[:-1]
	return dev


def getRCFile(ext):
	filename = resolveFilename(SCOPE_SKIN, pathjoin("rc_models", "%s.%s" % (BoxInfo.getItem("rcname"), ext)))
	if not isfile(filename):
		filename = resolveFilename(SCOPE_SKIN, pathjoin("rc_models", "spark.%s" % ext))
	return filename


def getModuleLayout():
	modulePath = BoxInfo.getItem("enigmamodule")
	if modulePath:
		process = Popen(("/sbin/modprobe", "--dump-modversions", modulePath), stdout=PIPE, stderr=PIPE)
		stdout, stderr = process.communicate()
		if process.returncode == 0:
			for detail in stdout.split("\n"):
				if "module_layout" in detail:
					return detail.split("\t")[0]
	return None


model = BoxInfo.getItem("model")
brand = BoxInfo.getItem("brand")
displaytype = BoxInfo.getItem("displaytype")

BoxInfo.setItem("DebugLevel", eGetEnigmaDebugLvl())
BoxInfo.setItem("InDebugMode", eGetEnigmaDebugLvl() >= 4)
BoxInfo.setItem("ModuleLayout", getModuleLayout(), immutable=True)

# Remote control related data.
#
BoxInfo.setItem("RCImage", getRCFile("png"))
BoxInfo.setItem("RCMapping", getRCFile("xml"))
BoxInfo.setItem("RemoteEnable", False)
BoxInfo.setItem("RemoteRepeat", 300)
BoxInfo.setItem("RemoteDelay", 700)

BoxInfo.getItem("CommonInterface") = eDVBCIInterfaces.getInstance().getNumOfSlots()
BoxInfo.getItem("CommonInterfaceCIDelay") = fileCheck("/proc/stb/tsmux/rmx_delay")
for cislot in range(0, BoxInfo.getItem("CommonInterface")):
	BoxInfo.getItem("CI%dSupportsHighBitrates" % cislot] = fileCheck("/proc/stb/tsmux/ci%d_tsclk" % cislot)
	BoxInfo.getItem("CI%dRelevantPidsRoutingSupport" % cislot] = fileCheck("/proc/stb/tsmux/ci%d_relevant_pids_routing" % cislot)
BoxInfo.getItem("HasSoftcamInstalled") = hassoftcaminstalled()
BoxInfo.getItem("NumVideoDecoders") = getNumVideoDecoders()
BoxInfo.getItem("Udev") = not fileExists("/dev/.devfsd")
BoxInfo.getItem("PIPAvailable") = BoxInfo.getItem("NumVideoDecoders") > 1
BoxInfo.getItem("CanMeasureFrontendInputPower") = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()
BoxInfo.getItem("12V_Output") = Misc_Options.getInstance().detected_12V_output()
BoxInfo.getItem("ZapMode") = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
BoxInfo.getItem("NumFrontpanelLEDs") = countFrontpanelLEDs()
BoxInfo.getItem("FrontpanelDisplay") = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
BoxInfo.getItem("LCDsymbol_circle_recording") = fileCheck("/proc/stb/lcd/symbol_circle") or fileCheck("/proc/stb/lcd/symbol_recording")
BoxInfo.getItem("LCDsymbol_timeshift") = fileCheck("/proc/stb/lcd/symbol_timeshift")
BoxInfo.getItem("LCDshow_symbols") = fileCheck("/proc/stb/lcd/show_symbols")
BoxInfo.getItem("LCDsymbol_hdd") = fileCheck("/proc/stb/lcd/symbol_hdd")
BoxInfo.getItem("FrontpanelDisplayGrayscale") = fileExists("/dev/dbox/oled0")
BoxInfo.getItem("DeepstandbySupport") = model not in ("adb_box", "hl101", "vip1_v1")
BoxInfo.getItem("Fan") = fileCheck("/proc/stb/fp/fan")
BoxInfo.getItem("FanPWM") = BoxInfo.getItem("Fan") and fileCheck("/proc/stb/fp/fan_pwm")
BoxInfo.getItem("PowerLED") = fileCheck("/proc/stb/power/powerled")
BoxInfo.getItem("PowerLED2") = fileCheck("/proc/stb/power/powerled2")
BoxInfo.getItem("StandbyLED") = fileCheck("/proc/stb/power/standbyled")
BoxInfo.getItem("SuspendLED") = fileCheck("/proc/stb/power/suspendled")
BoxInfo.getItem("Display") = BoxInfo.getItem("FrontpanelDisplay") or BoxInfo.getItem("StandbyLED")
BoxInfo.getItem("LedPowerColor") = fileCheck("/proc/stb/fp/ledpowercolor")
BoxInfo.getItem("LedStandbyColor") = fileCheck("/proc/stb/fp/ledstandbycolor")
BoxInfo.getItem("LedSuspendColor") = fileCheck("/proc/stb/fp/ledsuspendledcolor")
BoxInfo.getItem("WakeOnLAN") = fileCheck("/proc/stb/power/wol") or fileCheck("/proc/stb/fp/wol")
BoxInfo.getItem("HasExternalPIP") = fileCheck("/proc/stb/vmpeg/1/external")
BoxInfo.getItem("VideoDestinationConfigurable") = fileExists("/proc/stb/vmpeg/0/dst_left")
BoxInfo.getItem("hasPIPVisibleProc") = fileCheck("/proc/stb/vmpeg/1/visible")
BoxInfo.getItem("MaxPIPSize") = (540, 432)
BoxInfo.getItem("VFD_scroll_repeats") = fileCheck("/proc/stb/lcd/scroll_repeats")
BoxInfo.getItem("VFD_scroll_delay") = fileCheck("/proc/stb/lcd/scroll_delay")
BoxInfo.getItem("VFD_initial_scroll_delay") = fileCheck("/proc/stb/lcd/initial_scroll_delay")
BoxInfo.getItem("VFD_final_scroll_delay") = fileCheck("/proc/stb/lcd/final_scroll_delay")
BoxInfo.getItem("3DMode") = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
BoxInfo.getItem("3DZNorm") = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
BoxInfo.getItem("Blindscan_t2_available") = False
BoxInfo.getItem("HasFullHDSkinSupport") = BoxInfo.getItem("fhdskin")
BoxInfo.getItem("HasBypassEdidChecking") = fileCheck("/proc/stb/hdmi/bypass_edid_checking")
BoxInfo.getItem("HasColorspace") = fileCheck("/proc/stb/video/hdmi_colorspace")
BoxInfo.getItem("HasColorspaceSimple") = BoxInfo.getItem("HasColorspace")
BoxInfo.getItem("HasMultichannelPCM") = fileCheck("/proc/stb/audio/multichannel_pcm")
BoxInfo.getItem("HasMMC") = "root" in cmdline and cmdline["root").startswith("/dev/mmcblk")
BoxInfo.getItem("HasTranscoding") = BoxInfo.getItem("transcoding") or BoxInfo.getItem("multitranscoding") or pathExists("/proc/stb/encoder/0") or fileCheck("/dev/bcm_enc0")
BoxInfo.getItem("HasH265Encoder") = fileHas("/proc/stb/encoder/0/vcodec_choices", "h265")
BoxInfo.getItem("CanNotDoSimultaneousTranscodeAndPIP") = True
BoxInfo.getItem("HasColordepth") = fileCheck("/proc/stb/video/hdmi_colordepth")
BoxInfo.getItem("Has24hz") = fileCheck("/proc/stb/video/videomode_24hz")
BoxInfo.getItem("HasHDMIpreemphasis") = fileCheck("/proc/stb/hdmi/preemphasis")
BoxInfo.getItem("HasColorimetry") = fileCheck("/proc/stb/video/hdmi_colorimetry")
BoxInfo.getItem("HasHdrType") = fileCheck("/proc/stb/video/hdmi_hdrtype")
BoxInfo.getItem("HasHDMI") = BoxInfo.getItem("hdmi")
BoxInfo.getItem("HasHDMI-CEC") = BoxInfo.getItem("HasHDMI") and (fileExists("/proc/stb/cec/send") or fileExists("/proc/stb/hdmi/cec"))
BoxInfo.getItem("HasYPbPr") = BoxInfo.getItem("yuv")
BoxInfo.getItem("HasScart") = BoxInfo.getItem("scart")
BoxInfo.getItem("HasSVideo") = BoxInfo.getItem("svideo")
BoxInfo.getItem("HasComposite") = BoxInfo.getItem("rca")
BoxInfo.getItem("HasAutoVolume") = fileExists("/proc/stb/audio/avl_choices") or fileCheck("/proc/stb/audio/avl")
BoxInfo.getItem("HasAutoVolumeLevel") = fileExists("/proc/stb/audio/autovolumelevel_choices") or fileCheck("/proc/stb/audio/autovolumelevel")
BoxInfo.getItem("Has3DSurround") = fileExists("/proc/stb/audio/3d_surround_choices") or fileCheck("/proc/stb/audio/3d_surround")
BoxInfo.getItem("Has3DSpeaker") = fileExists("/proc/stb/audio/3d_surround_speaker_position_choices") or fileCheck("/proc/stb/audio/3d_surround_speaker_position")
BoxInfo.getItem("Has3DSurroundSpeaker") = fileExists("/proc/stb/audio/3dsurround_choices") or fileCheck("/proc/stb/audio/3dsurround")
BoxInfo.getItem("Has3DSurroundSoftLimiter") = fileExists("/proc/stb/audio/3dsurround_softlimiter_choices") or fileCheck("/proc/stb/audio/3dsurround_softlimiter")
BoxInfo.getItem("HasOfflineDecoding") = True
BoxInfo.getItem("MultibootStartupDevice") = getMultibootStartupDevice()
BoxInfo.getItem("canMode12") = False
BoxInfo.getItem("canMultiBoot") = False
BoxInfo.getItem("canFlashWithOfgwrite") = True
BoxInfo.getItem("HDRSupport") = fileExists("/proc/stb/hdmi/hlg_support_choices") or fileCheck("/proc/stb/hdmi/hlg_support")
BoxInfo.getItem("CanDownmixAC3") = fileHas("/proc/stb/audio/ac3_choices", "downmix")
BoxInfo.getItem("CanDownmixDTS") = fileHas("/proc/stb/audio/dts_choices", "downmix")
BoxInfo.getItem("CanDownmixAAC") = fileHas("/proc/stb/audio/aac_choices", "downmix")
BoxInfo.getItem("HDMIAudioSource") = fileCheck("/proc/stb/hdmi/audio_source")
BoxInfo.getItem("BootDevice") = getBootdevice()
BoxInfo.getItem("FbcTunerPowerAlwaysOn") = False
BoxInfo.getItem("HasPhysicalLoopthrough") = ["Vuplus DVB-S NIM(AVL2108)", "GIGA DVB-S2 NIM (Internal)")
BoxInfo.getItem("SmallFlash") = fileExists("/etc/openvision/smallflash")
BoxInfo.getItem("MiddleFlash") = fileExists("/etc/openvision/middleflash") and not fileExists("/etc/openvision/smallflash")
BoxInfo.getItem("HaveCISSL") = fileCheck("/etc/ssl/certs/customer.pem") and fileCheck("/etc/ssl/certs/device.pem")
BoxInfo.getItem("CanChangeOsdAlpha") = access("/proc/stb/video/alpha", R_OK) and True or False
BoxInfo.getItem("ScalerSharpness") = fileExists("/proc/stb/vmpeg/0/pep_scaler_sharpness")
BoxInfo.getItem("OScamInstalled") = fileExists("/usr/bin/oscam") or fileExists("/usr/bin/oscam-emu") or fileExists("/usr/bin/oscam-smod")
BoxInfo.getItem("OScamIsActive") = BoxInfo.getItem("OScamInstalled") and fileExists("/tmp/.oscam/oscam.version")
BoxInfo.getItem("NCamInstalled") = fileExists("/usr/bin/ncam")
BoxInfo.getItem("NCamIsActive") = BoxInfo.getItem("NCamInstalled") and fileExists("/tmp/.ncam/ncam.version")
BoxInfo.getItem("OpenVisionModule") = fileCheck("/proc/openvision/distro")
BoxInfo.getItem("7segment") = displaytype == "7segment" or "7seg" in displaytype
BoxInfo.getItem("CanAC3plusTranscode") = fileExists("/proc/stb/audio/ac3plus_choices")
BoxInfo.getItem("CanDTSHD") = fileExists("/proc/stb/audio/dtshd_choices")
BoxInfo.getItem("CanWMAPRO") = fileExists("/proc/stb/audio/wmapro")
BoxInfo.getItem("CanDownmixAACPlus") = fileExists("/proc/stb/audio/aacplus_choices")
BoxInfo.getItem("CanAACTranscode") = fileExists("/proc/stb/audio/aac_transcode_choices")
BoxInfo.getItem("ConfigDisplay") = BoxInfo.getItem("FrontpanelDisplay") and displaytype != "7segment" and "7seg" not in displaytype
BoxInfo.getItem("VFDSymbol") = BoxInfo.getItem("vfdsymbol")
BoxInfo.getItem("CanBTAudio") = fileCheck("/proc/stb/audio/btaudio")
BoxInfo.getItem("CanBTAudioDelay") = fileCheck("/proc/stb/audio/btaudio_delay")
BoxInfo.getItem("SeekStatePlay") = False
BoxInfo.getItem("StatePlayPause") = False
BoxInfo.getItem("StandbyState") = False
BoxInfo.getItem("HasH9SD") = False
BoxInfo.getItem("HasSDnomount") = False
BoxInfo.getItem("canBackupEMC") = False
BoxInfo.getItem("CanSyncMode") = fileExists("/proc/stb/video/sync_mode_choices")
BoxInfo.getItem("RFmodSupport") = model == "spark7162"
BoxInfo.getItem("LCDSupport") = False
BoxInfo.getItem("LEDSupport") = False
