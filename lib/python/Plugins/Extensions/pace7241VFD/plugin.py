#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd, eDVBVolumecontrol
from time import localtime, strftime, sleep
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
import os


try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 19:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	DisplayType = 19

config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.displayshow = ConfigSelection(default = "channel",
	choices = [
		("nothing", _("blank")),
		("channel number", _("channel number")),
		("channel", _("channel name")),
		("channel namenumber", _("channel number and name")),
		("time", _("time (with seconds)")),
		("timeHM", _("time (without seconds)")),
		("date", _("date")),
		("time_date", _("time and date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.stbshow = ConfigSelection(default = "time_date",
	choices = [
		("nothing", _("nothing")),
		("time", _("time (with seconds)")),
		("timeHM", _("time (without seconds)")),
		("date", _("date")),
		("time_date", _("time and date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.contrast = ConfigSlider(default = 6, limits = (0, 7))
config.plugins.vfdicon.stbcontrast = ConfigSlider(default = 0, limits = (0, 7))
config.plugins.vfdicon.ledbright = ConfigSlider(default = 6, limits = (0, 7))
config.plugins.vfdicon.stbledbright = ConfigSlider(default = 4, limits = (0, 7))
config.plugins.vfdicon.uppercase = ConfigYesNo(default = False)
config.plugins.vfdicon.textscroll = ConfigSelection(default = "1",
	choices = [
		("0", _("no")),
		("1", _("once")),
		("2", _("continuous"))
		])
config.plugins.vfdicon.textcenter = ConfigSelection(default = "0",
	choices = [
		("0", _("no")),
		("1", _("yes"))
		])
config.plugins.vfdicon.showicons = ConfigSelection(default = "all",
	choices = [
		("none", _("none")),
		("partial", _("partial")),
		("all", _("all"))
		])
config.plugins.vfdicon.powerledcolour = ConfigSelection(default = "2",
	choices = [
		("0", _("off")),
		("1", _("red")),
		("2", _("green")),
		("3", _("orange"))
		])
config.plugins.vfdicon.standbyledcolour = ConfigSelection(default = "1",
	choices = [
		("0", _("off")),
		("1", _("red")),
		("2", _("green")),
		("3", _("orange"))
		])
config.plugins.vfdicon.vfd_enable = ConfigYesNo(default = False)
config.plugins.vfdicon.extMenu = ConfigYesNo(default = True)

class ConfigVFDDisplay(Screen, ConfigListScreen):
	def __init__(self, session):
		self.icons_showicons = None
		try:
			self.adb_mod = open("/proc/stb/info/adb_variant").read().strip()
		except:
			pass

#		print('[pace7241VFD] ADB variant:', self.adb_mod)
#		if self.adb_mod == 'bsla' or self.adb_mod == 'bzzb':
			self.disp = 'vfd'
#		else:
#			self.disp = 'led'
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "SetupActions", "ColorActions"],
			{
				'left': self.keyLeft,
				'down': self.keyDown,
				'up': self.keyUp,
				'right': self.keyRight,
				"cancel": self.cancel,
				"ok": self.keySave,
				"green": self.keySave,
				"red": self.cancel,
			}, -2)
		self.cfglist = []
		ConfigListScreen.__init__(self, self.cfglist, session = session)
		self.setTitle(_("VFD display configuration"))
		self.createSetup()

	def createSetup(self):
		self.cfglist = []
		self.cfglist.append(getConfigListEntry(_("Show on display"), config.plugins.vfdicon.displayshow))
		self.cfglist.append(getConfigListEntry(_("Show on display in standby"), config.plugins.vfdicon.stbshow))
		if DisplayType == 18:
			self.cfglist.append(getConfigListEntry(_("Display brightness"), config.plugins.vfdicon.contrast))
			if self.disp == 'vfd':
				self.cfglist.append(getConfigListEntry(_("LED brightness"), config.plugins.vfdicon.ledbright))
			self.cfglist.append(getConfigListEntry(_("Standby brightness"), config.plugins.vfdicon.stbcontrast))
			if self.disp == 'vfd':
				self.cfglist.append(getConfigListEntry(_("Standby LED brightness"), config.plugins.vfdicon.stbledbright))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		if self.disp == 'vfd':
			self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
			self.cfglist.append(getConfigListEntry(_("Show icons"), config.plugins.vfdicon.showicons))
			self.icons_showicons = config.plugins.vfdicon.showicons.value
		if DisplayType == 18:
			self.cfglist.append(getConfigListEntry(_('Power LED colour'), config.plugins.vfdicon.powerledcolour))
			self.cfglist.append(getConfigListEntry(_('Standby LED colour'), config.plugins.vfdicon.standbyledcolour))
		if self.disp != 'vfd':
		        self.cfglist.append(getConfigListEntry(_('Enable VFD display'), config.plugins.vfdicon.vfd_enable))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if DisplayType == 18:
			if self["config"].getCurrent()[1] == config.plugins.vfdicon.stbcontrast:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.stbcontrast.value))
#			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.ledbright.value:
#				Console().ePopen("fp_control -led " + str(config.plugins.vfdicon.ledbright.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.stbledbright.value:
				b = str(config.plugins.vfdicon.stbledbright.value)
				Console().ePopen("fp_control -led " + b)
#			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.powerledcolour.value:
#				Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.powerledcolour.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyledcolour:
				Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.standbyledcolour.value))
			else:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
#				Console().ePopen("fp_control -led " + str(config.plugins.vfdicon.contrast.value))
				print("")
				b = str(config.plugins.vfdicon.ledbright.value)
				Console().ePopen("fp_control -led " + b)
				Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.powerledcolour.value))
		print("newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		b = str(config.plugins.vfdicon.ledbright.value)
		Console().ePopen("fp_control -led " + b)
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if DisplayType == 18:
			b = str(config.plugins.vfdicon.ledbright.value)
			Console().ePopen("fp_control -led " + b)
			print("[pace7241VFD] set brightness", config.plugins.vfdicon.contrast.value)
			Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
			Console().ePopen("fp_control -led " + str(config.plugins.vfdicon.ledbright.value))
			Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.powerledcolour.value))
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[pace7241VFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[pace7241VFD] set text centering", config.plugins.vfdicon.textcenter.value)
		main(self)
		ConfigListScreen.keySave(self)

	def keyLeft(self):
		self["config"].handleKey(KEY_LEFT)
		self.newConfig()

	def keyRight(self):
		self["config"].handleKey(KEY_RIGHT)
		self.newConfig()

	def keyDown(self):
		self['config'].instance.moveSelection(self['config'].instance.moveDown)
		self.newConfig()

	def keyUp(self):
		self['config'].instance.moveSelection(self['config'].instance.moveUp)
		self.newConfig()

def opencfg(session, **kwargs):
		session.open(ConfigVFDDisplay)
		evfd.getInstance().vfd_write_string( "VFD SETUP" )

def VFDdisplaymenu(menuid, **kwargs):
	if menuid == "system":
		return [(_("VFD display"), opencfg, "vfd_display", 44)]
	else:
		return []

class VFDIcons:
	def __init__(self, session):
		self.session = session
		self.onClose = []
		print('[pace7241VFD] Start')
		self.tuned = False
		self.play = False
		self.record = False
		self.timeshift = False
		self.standby = False
		self.usb = 0
		self.dolbyAvailable = False
		self.mp3Available = False
#		self.DTSAvailable = False

#		self.display = 'led'
#		try:
#			self.adb_model = open("/proc/stb/info/adb_variant").read().strip()
#		except:
#			pass
#		print('[pace7241VFD] ADB variant:', self.adb_model)
#		if self.adb_model == 'bsla' or self.adb_model == 'bzzb':
		self.display = 'vfd'

		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(60000, False) # start one minute timer
		if self.display == 'vfd':
			Console().ePopen("fp_control -i 22 0")
		b = str(config.plugins.vfdicon.ledbright.value)
		Console().ePopen("fp_control -led " + b)
		global DisplayType
		print('[pace7241VFD] Hardware displaytype:', DisplayType)
		print('[pace7241VFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 19:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged,
					iPlayableService.evSeekableStatusChanged: self.__evSeekableStatusChanged,
					iPlayableService.evTunedIn: self.__evTunedIn,
					iPlayableService.evTuneFailed: self.__evTuneFailed,
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call = False)
			session.nav.record_event.append(self.gotRecordEvent)
			if self.display == 'vfd':
				try:
					from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
					hotplugNotifier.append(self.hotplugCB)
				except:
					pass
		else:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evStart: self.writeName,
				})
		print('[pace7241VFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		evfd.getInstance().vfd_set_CENTER(False)
		if self.display == 'vfd':
			print("[pace7241VFD] Set text centering option")
			if config.plugins.vfdicon.textcenter.value == "1":
				evfd.getInstance().vfd_set_CENTER(True)
		print('[pace7241VFD] End initialisation')

	def __evStart(self):
		print('[pace7241VFD] __evStart')
		self.__evSeekableStatusChanged()

	def __evUpdatedEventInfo(self):
		print('[pace7241VFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[pace7241VFD] __evUpdatedInfo')
		self.writeName()
		if DisplayType == 19:
			self.checkAudioTracks()
			self.showCrypted()
			self.showDolby()
			self.showMP3()
			self.showTuned()
			self.showMute()

	def writeName(self):
		if (config.plugins.vfdicon.displayshow.value != "date" and config.plugins.vfdicon.displayshow.value != "day_date"
			and config.plugins.vfdicon.displayshow.value != "time_date" and config.plugins.vfdicon.displayshow.value != "time" and config.plugins.vfdicon.displayshow.value != "timeHM"):
			servicename = "            "
			if config.plugins.vfdicon.displayshow.value != "nothing":
				service = self.session.nav.getCurrentlyPlayingServiceOrGroup()
				if service:
					path = service.getPath()
					if path:
						self.play = True
						servicename = "Play"
						currPlay = self.session.nav.getCurrentService()
						if currPlay != None and self.mp3Available: # show the MP3 tag
							servicename = currPlay.info().getInfoString(iServiceInformation.sTagTitle) + " - " + currPlay.info().getInfoString(iServiceInformation.sTagArtist)
						else: # show the file name
							self.service = self.session.nav.getCurrentlyPlayingServiceReference()
							if not self.service is None:
								service = self.service.toCompareString()
								servicename = ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '')
					else:
						if config.plugins.vfdicon.displayshow.value == "channel number": #show the channel number
							servicename = str(service.getChannelNum())
							if len(servicename) == 1:
								servicename = '000' + servicename
							elif len(servicename) == 2:
								servicename = '00' + servicename
							elif len(servicename) == 3:
								servicename = '0' + servicename
						elif config.plugins.vfdicon.displayshow.value == "channel namenumber": #show the channel number & name
							servicename = str(service.getChannelNum()) + ' ' + ServiceReference(service).getServiceName()
						else:
							servicename = ServiceReference(service).getServiceName() #show the channel name
						self.play = False
			if config.plugins.vfdicon.uppercase.value == True:
				servicename = servicename.upper()
			servicename = servicename.replace('  ', ' ')
			evfd.getInstance().vfd_write_string(servicename[0:63])

	def showCrypted(self):
		if config.plugins.vfdicon.showicons.value != "none":
			service = self.session.nav.getCurrentService()
			if service:
				info = service.info()
				crypted = info.getInfo(iServiceInformation.sIsCrypted)
				if crypted == 1:
					Console().ePopen("fp_control -i 6 1") #padlock icon
				else:
					Console().ePopen("fp_control -i 6 0")

	def checkAudioTracks(self):
		self.dolbyAvailable = False
		self.mp3Available = False
		self.DTSAvailable = False
		if config.plugins.vfdicon.showicons.value != "none":
			service = self.session.nav.getCurrentService()
			if service:
				audio = service.audioTracks()
				if audio:
					n = audio.getNumberOfTracks()
					for x in range(n):
						i = audio.getTrackInfo(x)
						description = i.getDescription()
						if description.find("AC3") != -1:
							self.dolbyAvailable = True
						if description.find("MP3") != -1:
							self.mp3Available = True
#						if description.find("DTS") != -1:
#							self.DTSAvailable = True

	def showDolby(self):
		if self.dolbyAvailable:
			Console().ePopen("fp_control -i 7 1") #Dolby
		else:
			Console().ePopen("fp_control -i 7 0")

	def showMP3(self):
		if self.mp3Available:
			Console().ePopen("fp_control -i 11 1") #MP3
		else:
			Console().ePopen("fp_control -i 11 0")

	def showTuned(self):
		if config.plugins.vfdicon.showicons.value == "all":
			if self.tuned == True:
				service = self.session.nav.getCurrentService()
				if service is not None and self.play == False:
					info = service.info()
					TPdata = info and info.getInfoObject(iServiceInformation.sTransponderData)
#					tunerType = TPdata.get("tuner_type")
#					if tunerType == "DVB-S":
					feinfo = service.frontendInfo()
					FEdata = feinfo and feinfo.getAll(True)
					tunerNumber = FEdata and FEdata.get("tuner_number")
					print("[pace7241VFD] Set tuner number icon ", tunerNumber)
					if tunerNumber == 0:
						Console().ePopen("fp_control -i 9 1 -i 10 0") #Tu1 on, Tu2 off
					else:
						Console().ePopen("fp_control -i 9 0 -i 10 1") #Tu1 off, Tu2 on
#					elif tunerType == "DVB-C":
#						print("[pace7241VFD] Set TER icon")
#						Console().ePopen("fp_control -i 26 1 -i 2 0 -i 44 0 -i 45 0 -i 29 0") #TER on, SAT, Tu1, Tu2 off
				else:
					print("[pace7241VFD] No TER or SAT icon")
					Console().ePopen("fp_control -i 9 0 -i 10 0") #Tu1, Tu2 off
			else:
				                              # HD, Timeshift,Dolby,MP3,    Tu1    Tu2 off
				Console().ePopen("fp_control  -i 4 0 -i 2 0 -i 7 0 -i 11 0 -i 9 0 -i 10 0")

	def showMute(self):
		if config.plugins.vfdicon.showicons.value != "none":
			self.isMuted = eDVBVolumecontrol.getInstance().isMuted()
			if self.isMuted:
				Console().ePopen("fp_control -i 8 1") #Mute
			else:
				Console().ePopen("fp_control -i 8 0")

	def showTimer(self):
		if config.plugins.vfdicon.showicons.value == "all":
			# check if timers are set
			next_rec_time = -1
			next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
			if self.display == 'vfd':
				if next_rec_time > 0:
					Console().ePopen("fp_control -i 3 1") #Timer icon
				else:
					Console().ePopen("fp_control -i 3 0")
			else:
				if next_rec_time > 0:
					Console().ePopen("fp_control -l 2 1") #Timer LED
				else:
					Console().ePopen("fp_control -l 2 0")

	def timerEvent(self):
		self.showTimer() #update timer icon
 		if self.standby == False:
			if self.display == 'vfd':
				self.showMute() #update mute icon
				if config.plugins.vfdicon.showicons.value == "all":
					if (self.record == True or self.timeshift == True): # if recording or timeshifting, display a rotating disc
						Console().ePopen("fp_control  -i 23 1")
		if self.record == False and self.timeshift == False:
			if self.standby == False:
				if self.display == 'vfd' and  config.plugins.vfdicon.showicons.value == "all":
					Console().ePopen("fp_control  -i 23 0")
				disptype = config.plugins.vfdicon.displayshow.value
			else:
				disptype = config.plugins.vfdicon.stbshow.value
			self.writeDate(disptype)

	def __evVideoSizeChanged(self):
		if config.plugins.vfdicon.showicons.value != "none":
			service = self.session.nav.getCurrentService()
			if service:
				info = service.info()
				height = info.getInfo(iServiceInformation.sVideoHeight)
				if height > 576: #set HD icon
					Console().ePopen("fp_control -i 4 1")
				else:
					Console().ePopen("fp_control -i 4 0")

	def __evSeekableStatusChanged(self):
		if config.plugins.vfdicon.showicons.value == "all" and self.display == 'vfd':
			if not os.path.exists('/proc/stb/lcd/symbol/timeshift'):
				service = self.session.nav.getCurrentService()
				if service:
					if self.play == False:
						ts = service and service.timeshift()
#						if ts and ts.isTimeshiftEnabled() > 0:
						if ts and ts.isTimeshiftActive() > 0:
							self.timeshift = True
							Console().ePopen("fp_control -i 2 1") #Time shift
						else:
							self.timeshift = False
							Console().ePopen("fp_control -i 2 0") #Time shift icon off

	def gotRecordEvent(self, service, event):
		if config.plugins.vfdicon.showicons.value != 'none':
			if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
				recs = self.session.nav.getRecordings()
				nrecs = len(recs)
				if nrecs > 0: #recording active
					self.record = True
					Console().ePopen("fp_control -l 2 1") #REC LED on
				else: # no recording active
					Console().ePopen("fp_control -l 2 0") #REC LED off
					self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)
			self.showTimer() #update timer icon

	def writeDate(self, disp): #TODO: replace with case
		if disp == "date" or disp == "day_date" or disp == "time" or disp == "timeHM" or disp == "time_date" or disp == "nothing":
			tm = localtime()
			if disp == "day_date":
				date = strftime("%a", tm)[0:2] + strftime(" %d-%m-%y", tm)
			elif disp == "date":
				date = strftime("%d-%m-%y", tm) 
			elif disp == "time_date":
				date = strftime("%d-%m %H:%M", tm) 
			elif disp == "timeHM":
				date = strftime("    %H:%M", tm)
			elif disp == "time":
				date = strftime("    %H:%M:%S", tm)
			elif disp == "nothing":
				date = ("            ")
			evfd.getInstance().vfd_write_string(date[0:12])

	def __evTunedIn(self):
		self.tuned = True

	def __evTuneFailed(self):
		self.tuned = False

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		self.timer.stop() # stop one second timer
		evfd.getInstance().vfd_write_string("               ")
		self.timer.start(60000, False) # start one minute timer
		print("[pace7241VFD] minute timer started")
		if DisplayType == 19:
			evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.contrast.value)
			if self.display == 'vfd':
				Console().ePopen("fp_control -led " + str(config.plugins.vfdicon.ledbright.value))
			print("[pace7241VFD] set brightness", config.plugins.vfdicon.contrast.value)
			self.timerEvent()
			b = str(config.plugins.vfdicon.powerledcolour)
			Console().ePopen("fp_control -l 1 " + b)  #Power LED

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 19:
			print("[pace7241VFD] set display & icons on Enter Standby")
			if config.plugins.vfdicon.stbshow.value == "nothing":
				evfd.getInstance().vfd_set_light(0)
			else:
				evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.stbcontrast.value)
				if self.display == 'vfd':
					Console().ePopen("fp_control -led " + str(config.plugins.vfdicon.stbledbright.value))
			print("[pace7241VFD] set standby brightness", config.plugins.vfdicon.stbcontrast.value)
			if config.plugins.vfdicon.standbyledcolour.value:
				Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.standbyledcolour.value)) #Power LED
			else:
				Console().ePopen("fp_control -l 1 0") #Power LED red
		if (config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.timer.stop() # stop minute timer
			self.timer.start(999, False) # start one second timer
			print("[pace7241VFD] second timer started")
		if (config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "timeHM" or config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_clear_string()
		self.standby = True

	def hotplugCB(self, dev, media_state):
		if config.plugins.vfdicon.showicons.value == "all":
			if dev.__contains__('sda') or dev.__contains__('sdb') or dev.__contains__('sdc'):
#				if media_state == "add" or media_state == "change":
				if media_state == "add":
					Console().ePopen("fp_control -i 5 1")
					self.usb = 1
				if media_state == "remove":
					Console().ePopen("fp_control -i 5 0")
					self.usb = 0

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	global hddUsed
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 18:
		if (config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date"
			or config.plugins.vfdicon.displayshow.value == "time" or config.plugins.vfdicon.displayshow.value == "time_date"):
			sleep(1)
			VFDIconsInstance.timerEvent()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name = _("pace7241VFD"),
		description = _("Front panel display configuration"),
		where = PluginDescriptor.WHERE_MENU,
		fnc = VFDdisplaymenu),
		PluginDescriptor(
		name = _("pace7241VFD"),
		description = _("VFD icons for Pace HDS-7241"),
		where = PluginDescriptor.WHERE_SESSIONSTART,
		fnc = main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name = _("pace7241VFD"),
			description = _("Front panel display configuration for Pace HDS-7241"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			fnc = opencfg))
	return l
