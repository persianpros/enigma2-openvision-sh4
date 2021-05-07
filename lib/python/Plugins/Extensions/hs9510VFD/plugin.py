#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference
from Components.ServiceList import ServiceList
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd
from time import localtime, strftime, sleep
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Components.SystemInfo import BoxInfo


try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 7:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if BoxInfo.getItem("model") == "octagon1008":
		DisplayType = 7
	else:
		DisplayType = None

config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.displayshow = ConfigSelection(default="channel",
	choices=[
		("nothing", _("blank")),
		("channel number", _("channel number")),
		("channel", _("channel name")),
		("channel namenumber", _("channel number and name")),
		("date", _("date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.stbshow = ConfigSelection(default="time",
	choices=[
		("nothing", _("nothing")),
		("time", _("time")),
		("date", _("date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.contrast = ConfigSlider(default=4, limits=(0, 7))
config.plugins.vfdicon.stbcontrast = ConfigSlider(default=2, limits=(0, 7))
config.plugins.vfdicon.uppercase = ConfigYesNo(default=True)
config.plugins.vfdicon.textscroll = ConfigSelection(default="1",
	choices=[
		("0", _("no")),
		("1", _("once")),
		("2", _("continuous"))
		])
config.plugins.vfdicon.textcenter = ConfigSelection(default="0",
	choices=[
		("0", _("no")),
		("1", _("yes"))
		])
config.plugins.vfdicon.showicons = ConfigSelection(default="all",
	choices=[
		("none", _("none")),
		("partial", _("partial")),
		("all", _("all"))
		])
config.plugins.vfdicon.standbyredledon = ConfigSlider(default=0, limits=(0, 7))
#config.plugins.vfdicon.dstandbyredledon = ConfigSlider(default=7, limits=(0, 7))
config.plugins.vfdicon.recredledon = ConfigSlider(default=2, limits=(0, 7))
config.plugins.vfdicon.extMenu = ConfigYesNo(default=True)


class ConfigVFDDisplay(Screen, ConfigListScreen):
	def __init__(self, session):
		self.icons_showicons = None
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
		ConfigListScreen.__init__(self, self.cfglist, session=session)
		self.setTitle(_("VFD display configuration"))
		self.createSetup()

	def createSetup(self):
		self.cfglist = []
		self.cfglist.append(getConfigListEntry(_("Show on VFD display"), config.plugins.vfdicon.displayshow))
		self.cfglist.append(getConfigListEntry(_("Show on VFD display in standby"), config.plugins.vfdicon.stbshow))
		if DisplayType == 7:
			self.cfglist.append(getConfigListEntry(_("VFD brightness"), config.plugins.vfdicon.contrast))
			self.cfglist.append(getConfigListEntry(_("Standby brightness"), config.plugins.vfdicon.stbcontrast))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
		self.cfglist.append(getConfigListEntry(_("Show icons"), config.plugins.vfdicon.showicons))
		self.icons_showicons = config.plugins.vfdicon.showicons.value
		self.cfglist.append(getConfigListEntry(_('Standby LED brightness'), config.plugins.vfdicon.standbyredledon))
#		self.cfglist.append(getConfigListEntry(_('Deepstandby LED brightness'), config.plugins.vfdicon.dstandbyredledon))
		self.cfglist.append(getConfigListEntry(_('Rec LED brightness'), config.plugins.vfdicon.recredledon))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if DisplayType == 7:
			if self["config"].getCurrent()[1] == config.plugins.vfdicon.stbcontrast:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.stbcontrast.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyredledon:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredledon.value))
#			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.dstandbyredledon:
#				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.dstandbyredledon.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.recredledon:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredledon.value))
			else:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
				print("")
				Console().ePopen("fp_control -l 0 0")
		print("[hs9510VFD] newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		Console().ePopen("fp_control -l 0 0")
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if DisplayType == 7:
			Console().ePopen("fp_control -l 0 0")
			print("[hs9510VFD] set brightness", config.plugins.vfdicon.contrast.value)
			Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs9510VFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[hs9510VFD] set text centering", config.plugins.vfdicon.textcenter.value)
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
		evfd.getInstance().vfd_write_string("VFD SETUP")


def VFDdisplaymenu(menuid, **kwargs):
	if menuid == "system":
		return [(_("VFD display"), opencfg, "vfd_display", 44)]
	else:
		return []


class VFDIcons:
	def __init__(self, session):
		self.session = session
		self.onClose = []
		print('[hs9510VFD] Start')
		self.tuned = False
		self.play = False
		self.record = False
		self.timeshift = False
		self.standby = False
		self.usb = 0
		self.dolbyAvailable = False
		self.mp3Available = False
		self.DTSAvailable = False
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(60000, False) # start one minute timer
		Console().ePopen("fp_control -i 29 0")
		Console().ePopen("fp_control -l 0 0")
		global DisplayType
		print('[hs9510VFD] Hardware displaytype:', DisplayType)
		print('[hs9510VFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 7:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged,
					iPlayableService.evSeekableStatusChanged: self.__evSeekableStatusChanged,
					iPlayableService.evTunedIn: self.__evTunedIn,
					iPlayableService.evTuneFailed: self.__evTuneFailed,
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call=False)
			session.nav.record_event.append(self.gotRecordEvent)
			try:
				from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
				hotplugNotifier.append(self.hotplugCB)
			except:
				pass
			self.dir = None
			self.mount = None
			self.firstmount = -1
			global hddUsed
			hddUsed = -1
			self.SetMount()
			if self.mount:
				self.firstmount = self.mount
			if self.standby == False:
				self.displayHddUsed()
		else:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evStart: self.writeName,
				})
		print('[hs9510VFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs9510VFD] Set text centering option")
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print('[hs9510VFD] End initialisation')

	def __evStart(self):
		print('[hs9510VFD] __evStart')
		self.__evSeekableStatusChanged()

	def __evUpdatedEventInfo(self):
		print('[hs9510VFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[hs9510VFD] __evUpdatedInfo')
		self.checkAudioTracks()
		self.writeName()
		self.showDTS()
		if DisplayType == 7:
			self.showCrypted()
			self.showDolby()
			self.showTuned()

	def writeName(self):
		if config.plugins.vfdicon.displayshow.value != "date" and config.plugins.vfdicon.displayshow.value != "day_date":
			servicename = "        "
			if config.plugins.vfdicon.displayshow.value != "nothing":
				service = self.session.nav.getCurrentlyPlayingServiceOrGroup()
				if service:
					path = service.getPath()
					if path:
						self.play = True
						servicename = "PLAY"
						currPlay = self.session.nav.getCurrentService()
						if currPlay != None and self.mp3Available: # show the MP3 tag
							servicename = currPlay.info().getInfoString(iServiceInformation.sTagTitle) + " - " + currPlay.info().getInfoString(iServiceInformation.sTagArtist)
							Console().ePopen("fp_control -i 4 1 -i 3 0") #AUDIO icon on, DVB, VIDEO off
						else: # show the file name
							self.service = self.session.nav.getCurrentlyPlayingServiceReference()
							if not self.service is None:
								service = self.service.toCompareString()
								servicename = ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
								Console().ePopen("fp_control -i 3 1 -i 4 0") #VIDEO icon on, DVB, AUDIO off
						Console().ePopen("fp_control -i 19 1") #play
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
						Console().ePopen("fp_control -i 19 0") #play
						self.play = False
						#evaluate radio or tv
						if config.plugins.vfdicon.showicons.value == "all":
							if config.servicelist.lastmode.value == 'tv':
								Console().ePopen("fp_control -i 3 1 -i 4 0") #DVB, VIDEO icon on, AUDIO off
							else:
								Console().ePopen("fp_control -i 4 1 -i 3 0") #DVB, AUDIO icon on, VIDEO off
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
					Console().ePopen("fp_control -i 18 1") #Euro icon
				else:
					Console().ePopen("fp_control -i 18 0")

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
						if description.find("DTS") != -1:
							self.DTSAvailable = True

	def showDolby(self):
		if self.dolbyAvailable:
			Console().ePopen("fp_control -i 1 1") #Dolby
		else:
			Console().ePopen("fp_control -i 1 0")

	def showDTS(self):
		if self.DTSAvailable:
			Console().ePopen("fp_control -i 2 1") #DTS
		else:
			Console().ePopen("fp_control -i 2 0")

	def showTuned(self):
		if config.plugins.vfdicon.showicons.value == "all":
			if self.tuned == True:
				service = self.session.nav.getCurrentService()
				if service is not None and self.play == False:
					info = service.info()
					Console().ePopen("fp_control -i 8 1") #DVB on
			else:
				Console().ePopen("fp_control -i 8 0")

	def showTimer(self):
		if config.plugins.vfdicon.showicons.value == "all":
			# check if timers are set
			next_rec_time = -1
			next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
			if next_rec_time > 0:
				Console().ePopen("fp_control -i 11 1") #Timer
			else:
				Console().ePopen("fp_control -i 11 0")

	def timerEvent(self):
		self.showTimer() #update timer icon
#		if (self.record == True and config.plugins.vfdicon.recredledon.value != 0):
		if self.record == True:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredledon.value))
 		if self.standby == False:
			if self.record == False and self.timeshift == False:
				disptype = config.plugins.vfdicon.displayshow.value
		else:
			disptype = config.plugins.vfdicon.stbshow.value
			self.writeDate(disptype)

	def __evVideoSizeChanged(self):
		if config.plugins.vfdicon.showicons.value != "none":
			service = self.session.nav.getCurrentService()
			if service:
				info = service.info()
				aspect = info.getInfo(iServiceInformation.sAspect)
				if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
					Console().ePopen("fp_control -i 16 0")
				else:
					Console().ePopen("fp_control -i 16 1") #set 16:9 icon

	def __evSeekableStatusChanged(self):
		if config.plugins.vfdicon.showicons.value == "all":
			service = self.session.nav.getCurrentService()
			if service:
				if self.play == False:
					ts = service and service.timeshift()
#					if ts and ts.isTimeshiftEnabled() > 0:
					if ts and ts.isTimeshiftActive() > 0:
						self.timeshift = True
						Console().ePopen("fp_control -i 10 1") #Time
					else:
						self.timeshift = False
						Console().ePopen("fp_control -i 10 0") #Time icon off

	def gotRecordEvent(self, service, event):
		if config.plugins.vfdicon.showicons.value != 'none':
			if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
				recs = self.session.nav.getRecordings()
				nrecs = len(recs)
				if nrecs > 1: #two or more recordings active
					self.record = True
					Console().ePopen("fp_control -i 24 1 -i 13 1 -i 14 1") #REC, 1+2 on
				elif nrecs > 0: #one recording active
					self.record = True
					Console().ePopen("fp_control -i 24 1 -i 13 1 -i 14 0") #REC, 1 on, 2 off
				else: # no recording active
					Console().ePopen("fp_control -i 24 0 -i 13 0 -i 14 0 -l 0 0") #REC, 1, 2 & LED off
					self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)
			self.showTimer() #update timer icon

	def writeDate(self, disp):
		tm = localtime()
		if disp == "day_date":
			date = strftime("%a", tm)[0:2] + strftime(" %d-%m", tm)
			Console().ePopen("fp_control -i 27 0 -i 28 0") # colons off
		elif disp == "date":
			date = strftime("%d-%m-", tm) + strftime("%y", tm)[0:2]
			Console().ePopen("fp_control -i 27 0 -i 28 0") # colons off
		else:
			date = strftime("%H%M%S", tm)
			Console().ePopen("fp_control -i 27 1 -i 28 1") # colons on
		evfd.getInstance().vfd_write_string(date[0:8])

	def __evTunedIn(self):
		self.tuned = True
		Console().ePopen("fp_control -i 8 0") #DVB off

	def __evTuneFailed(self):
		self.tuned = False

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		Console().ePopen("fp_control -i 27 0 -i 28 0") # colons off
		evfd.getInstance().vfd_write_string("       ")
		self.timer.stop() # stop one second timer
		self.timer.start(60000, False) # start one minute timer
		if DisplayType == 7:
			evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.contrast.value)
			print("[hs9510VFD] set brightness", config.plugins.vfdicon.contrast.value)
			self.timerEvent()
			Console().ePopen("fp_control -l 0 0") # LED off
			if config.plugins.vfdicon.showicons.value == "all":
				global hddUsed
				hddUsed = -1 #force hdd display
				self.displayHddUsed()
				if self.usb == 1:
					Console().ePopen("fp_control -i 17 1") #USB
				else:
					Console().ePopen("fp_control -i 17 0")
			print("[hs9510VFD] set icons on Leave Standby")

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 7:
			Console().ePopen("fp_control -i 29 0") #clear all VFD icons
#			Console().ePopen("fp_control -i 36 1") #Standby
			if config.plugins.vfdicon.stbshow.value == "nothing":
				evfd.getInstance().vfd_set_light(0)
			else:
				evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.stbcontrast.value)
			print("[hs9510VFD] set standby brightness", config.plugins.vfdicon.stbcontrast.value)
			if config.plugins.vfdicon.standbyredledon.value:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredledon.value)) #Red LED on
		if config.plugins.vfdicon.stbshow.value == "time":
			self.timer.stop() # stop minute timer
			self.timer.start(999, False) # start one second timer
		if config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "time":
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_clear_string()
		self.standby = True
		print("[hs9510VFD] set display & icons on Enter Standby")

	def hotplugCB(self, dev, media_state):
		if config.plugins.vfdicon.showicons.value == "all":
			if dev.__contains__('sda') or dev.__contains__('sdb') or dev.__contains__('sdc'):
#				if media_state == "add" or media_state == "change":
				if media_state == "add":
					Console().ePopen("fp_control -i 17 1")
					self.usb = 1
					self.displayHddUsedOff() # signal hot plug
					self.mount = None # force remount
					self.SetMount() # determine mount
					if self.firstmount == -1 and self.mount:
						self.firstmount = self.mount
					self.displayHddUsed() # and display icon
				if media_state == "remove":
					Console().ePopen("fp_control -i 17 0")
					self.usb = 0
					if self.firstmount != -1:
						self.mount = self.firstmount
					else:
						self.mount = None
#					if not self.mount:
						self.displayHddUsedOff()

	def SetMount(self):
		dir = config.usage.instantrec_path.value[:-1]
		if dir == "<default":
			dir = config.usage.default_path.value[:-1]
		if not self.mount or self.dir != dir:
			if not self.mount:
				self.dir = dir
#				print("[VFD-Icons] SetMount", dir)
				self.mount = self.FindMountDir(dir)
			if not self.mount:
				self.mount = self.FindMountDir('/autofs/sdc1')
			if not self.mount:
				self.mount = self.FindMountDir('/autofs/sdb1')
			if not self.mount:
				self.mount = self.FindMountDir('/autofs/sda1')
			if not self.mount:
				self.mount = self.FindMountDir('/media/hdd')
			if not self.mount:
				self.mount = self.FindMountDir('/hdd')

	def FindMountDir(self, dir):
		mounts = open("/proc/mounts", 'r')
		for line in mounts:
			result = line.strip().split()
			if result[1].startswith(dir):
				mounts.close()
				return result[1]
		mounts.close()
		return None

	def FindMountDev(self, dev):
		mounts = open("/proc/mounts", 'r')
		for line in mounts:
			result = line.strip().split()
			if result[0].startswith(dev):
				mounts.close()
				return result[1]
		mounts.close()
		return None

	def displayHddUsed(self):
		global hddUsed
		if config.plugins.vfdicon.showicons.value == "all":
			if self.mount == None:
				self.displayHddUsedOff() #HDD display off
			else:
				Console().ePopen("fp_control -i 6 1") #HDD on
				print("[hs9510VFD] HDD mount point:", self.mount)
		else:
			self.displayHddUsedOff()

	def displayHddUsedOff(self): #switch off hdd icon
		Console().ePopen("fp_control -i 6 0")


VFDIconsInstance = None


def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	global hddUsed
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 7:
		if config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date" or config.plugins.vfdicon.displayshow.value == "time":
			sleep(1)
			VFDIconsInstance.timerEvent()
		else:
			if config.plugins.vfdicon.showicons.value == "none":
				Console().ePopen("fp_control -i 29 0")
			else:
				hddUsed = -1
				VFDIconsInstance.displayHddUsed()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()


def Plugins(**kwargs):
	l = [PluginDescriptor(
		name=_("hs9510VFD"),
		description=_("VFD display configuration"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=VFDdisplaymenu),
		PluginDescriptor(
		name=_("hs9510VFD"),
		description=_("VFD icons for Fortis HS9510"),
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name=_("hs9510VFD"),
			description=_("VFD display configuration for Fortis HS9510"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=opencfg))
	return l
