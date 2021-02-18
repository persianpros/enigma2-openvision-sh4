#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd, getBoxType
from time import localtime, strftime, sleep
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen


model = getBoxType()

try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 9:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if model in ("hs7810a", "hs7819", "hs7119"):
		DisplayType = 9
	else:
		DisplayType = None

config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.displayshow = ConfigSelection(default="channel number",
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
if model in ("hs7810a", "hs7819"):
	config.plugins.vfdicon.logoled = ConfigSlider(default=4, limits=(0, 7))
config.plugins.vfdicon.standbyredled = ConfigSlider(default=3, limits=(0, 7))
config.plugins.vfdicon.dstandbyredled = ConfigSlider(default=7, limits=(0, 7))
config.plugins.vfdicon.recredled = ConfigSlider(default=2, limits=(0, 7))
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
		self.setTitle(_("LED display configuration"))
		self.createSetup()

	def createSetup(self):
		self.cfglist = []
		self.cfglist.append(getConfigListEntry(_("Show on LED display"), config.plugins.vfdicon.displayshow))
		self.cfglist.append(getConfigListEntry(_("Show on LED display in standby"), config.plugins.vfdicon.stbshow))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
		if model in ("hs7810a", "hs7819"):
			self.cfglist.append(getConfigListEntry(_('Logo brightness'), config.plugins.vfdicon.logoled))
		self.cfglist.append(getConfigListEntry(_('Standby LED brightness'), config.plugins.vfdicon.standbyredled))
		self.cfglist.append(getConfigListEntry(_('Rec LED brightness'), config.plugins.vfdicon.recredled))
		self.cfglist.append(getConfigListEntry(_('Deepstandby LED brightness'), config.plugins.vfdicon.dstandbyredled))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyredled:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value))
		elif self["config"].getCurrent()[1] == config.plugins.vfdicon.dstandbyredled:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.dstandbyredled.value))
		elif self["config"].getCurrent()[1] == config.plugins.vfdicon.recredled:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredled.value))
		elif model in ("hs7810a", "hs7819") and (self["config"].getCurrent()[1] == config.plugins.vfdicon.logoled):
			Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.logoled.value))
		print("[hs7810aVFD] newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		Console().ePopen("fp_control -l 0 0") # red LED off
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs7810aVFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[hs7810aVFD] set text centering", config.plugins.vfdicon.textcenter.value)
		if model in ("hs7810a", "hs7819"):
			Console().ePopen("fp_control -l 0 0 -l 1 " + str(config.plugins.vfdicon.logoled.value)) # red LED off, logo on
		else:
			Console().ePopen("fp_control -l 0 0") # red LED off
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
		evfd.getInstance().vfd_write_string( "LED SETUP" )

def VFDdisplaymenu(menuid, **kwargs):
	if menuid == "system":
		return [(_("LED display"), opencfg, "vfd_display", 44)]
	else:
		return []

class VFDIcons:
	def __init__(self, session):
		self.session = session
		self.onClose = []
		print('[hs7810aVFD] Start')
		self.record = False
		self.standby = False
		self.dolbyAvailable = False
		self.mp3Available = False
		self.DTSAvailable = False
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(60000, False) # start one minute timer
		if model in ("hs7810a", "hs7819"):
			Console().ePopen("fp_control -l 0 0 -l 1 " + str(config.plugins.vfdicon.logoled.value)) # red LED off, logo on
		else:
			Console().ePopen("fp_control -l 0 0") # red LED off
		global DisplayType
		print('[hs7810aVFD] Hardware displaytype:', DisplayType)
		print('[hs7810aVFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 9:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call=False)
			session.nav.record_event.append(self.gotRecordEvent)
		else:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evStart: self.writeName,
				})
		print('[hs7810aVFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs7810aVFD] Set text centering option")
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print('[hs7810aVFD] End initialisation')

	def __evStart(self):
		print('[hs7810aVFD] __evStart')
#		... and do nothing else

	def __evUpdatedEventInfo(self):
		print('[hs7810aVFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[hs7810aVFD] __evUpdatedInfo')
		self.checkAudioTracks()
		self.writeName()

	def writeName(self):
		if config.plugins.vfdicon.displayshow.value != "date" and config.plugins.vfdicon.displayshow.value != "day_date":
			servicename = "    "
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
						else: # show the file name
							self.service = self.session.nav.getCurrentlyPlayingServiceReference()
							if not self.service is None:
								service = self.service.toCompareString()
								servicename = ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
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
			if config.plugins.vfdicon.uppercase.value == True:
				servicename = servicename.upper()
			servicename = servicename.replace('  ', ' ')
			evfd.getInstance().vfd_write_string(servicename[0:63])

	def checkAudioTracks(self):
		self.dolbyAvailable = False
		self.mp3Available = False
		self.DTSAvailable = False
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

	def timerEvent(self):
		if (self.record == True and config.plugins.vfdicon.recredled.value != 0):
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredled.value))
		if (self.standby == True):
			disp = config.plugins.vfdicon.stbshow.value
		else:
			disp = config.plugins.vfdicon.displayshow.value
		if (disp == "date" or disp == "day_date" or disp == "time"):
			self.writeDate(disp)
			

	def gotRecordEvent(self, service, event):
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			recs = self.session.nav.getRecordings()
			nrecs = len(recs)
			if nrecs > 0: #recording active
				self.record = True
				if (config.plugins.vfdicon.recredled.value != 0 and self.standby == False):
					Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredled.value))
			else: # no recording active
				self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)
			if (config.plugins.vfdicon.recredled.value != 0 and self.standby == False):
				Console().ePopen("fp_control -l 0 0")

	def writeDate(self, disp):
		tm = localtime()
		length = 4
		if disp == "day_date":
			date = strftime("%a", tm)[0:2] + strftime("%d", tm)
		elif disp == "date":
			date = strftime("%d%m", tm)
		else: #TODO: blinking colon
			date = strftime("%H:%M", tm)
			length = 5
		Console().ePopen("fp_control -t " + str(date[0:length]))

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		evfd.getInstance().vfd_write_string("    ")
		if model in ("hs7810a", "hs7819"):
			Console().ePopen("fp_control -l 0 0 -l 1 " + str(config.plugins.vfdicon.logoled.value)) # LED off, logo on
		else:
			Console().ePopen("fp_control -l 0 0") # LED off
		print("[hs7810aVFD] set LEDs on Leave Standby")
		self.timerEvent()
#		self.timer.start(60000, False) # start one minute timer

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if config.plugins.vfdicon.standbyredled.value:
			if model in ("hs7810a", "hs7819"):
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value) + "-l 1 0") #Red LED on, logo off
			else:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value)) #Red LED on
#		self.timer.start(1000, False) # start second timer
		if config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "time":
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_write_string("    ")
		self.standby = True
		print("[hs7810aVFD] set display & icons on Enter Standby")

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 9:
		if config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date" or config.plugins.vfdicon.displayshow.value == "time":
			sleep(1)
			VFDIconsInstance.timerEvent()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name=_("hs7810aVFD"),
		description=_("LED display configuration"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=VFDdisplaymenu),
		PluginDescriptor(
		name=_("hs7810aVFD"),
		description=_("LED control for Fortis HS7810A"),
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name=_("hs7810aVFD"),
			description=_("LED display configuration for Fortis HS7810A"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=opencfg))
	return l

