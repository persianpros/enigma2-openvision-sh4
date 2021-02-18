#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd
from time import localtime, strftime, sleep
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen


try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 4:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	DisplayType = 4

config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.displayshow = ConfigSelection(default = "channel_namenumber",
	choices = [
		("nothing", _("blank")),
		("channel_number", _("channel number")),
		("channel", _("channel name")),
		("channel_namenumber", _("channel number and name")),
		("time", _("time")),
		("date", _("date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.stbdisplayshow = ConfigSelection(default = "time",
	choices = [
		("nothing", _("nothing")),
		("time", _("time")),
		("date", _("date")),
		("time_date", _("time and date")),
		("day_date", _("day and date")),
		("time_day_date", _("time, day and date"))
		])
config.plugins.vfdicon.uppercase = ConfigYesNo(default=True)
config.plugins.vfdicon.textscroll = ConfigSelection(default = "1",
	choices = [
		("0", _("no")),
		("1", _("once")),
		("2", _("continuous"))
		])
config.plugins.vfdicon.standbyredledon = ConfigYesNo(default=False)
config.plugins.vfdicon.dstandbyredledon = ConfigYesNo(default=False)
config.plugins.vfdicon.recredledon = ConfigSelection(default = "2",
	choices = [
		("0", _("off")),
		("1", _("on")),
		("2", _("blink"))
		])
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
		ConfigListScreen.__init__(self, self.cfglist, session = session)
		self.setTitle(_("LED display configuration"))
		self.createSetup()

	def createSetup(self):
		self.cfglist = []
		self.cfglist.append(getConfigListEntry(_("Show on LED display"), config.plugins.vfdicon.displayshow))
		self.cfglist.append(getConfigListEntry(_("Show on LED display in standby"), config.plugins.vfdicon.stbdisplayshow))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_('Red LED on in standby'), config.plugins.vfdicon.standbyredledon))
		self.cfglist.append(getConfigListEntry(_('Red LED on in deep standby'), config.plugins.vfdicon.dstandbyredledon))
		self.cfglist.append(getConfigListEntry(_('Red LED during recording'), config.plugins.vfdicon.recredledon))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		print("newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[sparkVFD] set text scroll", config.plugins.vfdicon.textscroll.value)
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

def LEDdisplaymenu(menuid, **kwargs):
	if menuid == "system":
		return [(_("LED display"), opencfg, "led_display", 44)]
	else:
		return []


class VFDIcons:
	def __init__(self, session):
		self.session = session
		self.onClose = []
		print('[sparkVFD] Start')
		self.play = False
		self.record = False
		self.mp3Available = False
		self.standby = False
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(59998, False) # start one minute timer
		global DisplayType
		global dot
		dot = 0
		print('[sparkVFD] Hardware displaytype:', DisplayType)
		print('[sparkVFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 4:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call = False)
			session.nav.record_event.append(self.gotRecordEvent)
		else:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evStart: self.writeName,
				})
		print('[sparkVFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print('[sparkVFD] End initialisation')

	def __evStart(self):
		print('[sparkVFD] __evStart')
#		... and do nothing else

	def __evUpdatedEventInfo(self):
		print('[sparkVFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[sparkVFD] __evUpdatedInfo')
		self.checkAudioTracks()
		self.writeName()

	def writeName(self):
		displayshow = config.plugins.vfdicon.displayshow.value
		if displayshow != "time" and displayshow != "date" and displayshow != "day_date":
			servicename = "        "
			if displayshow != "nothing":
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
						if displayshow == "channel_number" or displayshow == "channel_namenumber":
							servicename = str(service.getChannelNum())
							if len(servicename) == 1:
								servicename = '000' + servicename
							elif len(servicename) == 2:
								servicename = '00' + servicename
							elif len(servicename) == 3:
								servicename = '0' + servicename
						if displayshow == "channel_namenumber":
							servicename = servicename + ' ' + ServiceReference(service).getServiceName()
						if displayshow == "channel":
							servicename = ServiceReference(service).getServiceName()
			if config.plugins.vfdicon.uppercase.value is not None:
				servicename = servicename.upper()
			evfd.getInstance().vfd_write_string(servicename[0:63])

	def checkAudioTracks(self):
		self.mp3Available = False
		service = self.session.nav.getCurrentService()
		if service:
			audio = service.audioTracks()
			if audio:
				n = audio.getNumberOfTracks()
				for x in range(n):
					i = audio.getTrackInfo(x)
					description = i.getDescription()
					if description.find("MP3") != -1:
						self.mp3Available = True

	def gotRecordEvent(self, service, event):
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			led = config.plugins.vfdicon.recredledon.value
			recs = self.session.nav.getRecordings()
			nrecs = len(recs)
			if nrecs > 0: #one or more recordings active
				self.record = True
				if (self.record == True and config.plugins.vfdicon.recredledon.value):
					Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredledon.value))
					if led == "2":
						self.timer.stop() # stop minute timer
						self.timer.start(2000, False) # start two second timer
					if led == "1":
						Console().ePopen("fp_control -l 0 1") #Red LED on
			else:
				self.timer.stop() # stop 2 second timer
				if self.standby == True:
					if config.plugins.vfdicon.standbyredledon.value:
						Console().ePopen("fp_control -l 0 1") #Red LED on
					if stbdisplayshow == "time":
						self.timer.start(1000, False) # start second timer
				else:
					Console().ePopen("fp_control -l 0 0") # red LED off
					self.timer.start(59998, False) # start minute timer
				self.record = False
				self.session.nav.record_event.remove(self.gotRecordEvent)

	def timerEvent(self):
		global dot
		if self.standby == False:
			disptype = config.plugins.vfdicon.displayshow.value
		else:
			disptype = config.plugins.vfdicon.stbdisplayshow.value
			if config.plugins.vfdicon.stbdisplayshow.value == "time":
				if dot == 0:
					dot = 1
				else:
					dot = 0
		if self.record == True and config.plugins.vfdicon.recredledon.value:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredledon.value))
		self.writeDate(disptype)

	def writeDate(self, disp):
		global dot
		if disp == "time" or disp == "date" or disp == "time_date" or disp == "day_date" or disp == "time_day_date":
			tm = localtime()
			time = strftime("%H%M", tm)
			date = strftime("%a", tm)[0:2] + strftime("%d-%m", tm) # day_date
			if disp == "time_day_date":
				date = time + date
			if disp == "date":
				date = strftime("%d%m-%y", tm)
			if disp == "time":
				date = strftime("%H.%M", tm)
				if self.standby == True and dot == 0:
					date = time
			Console().ePopen("fp_control -t " + date[0:8])
 
	def onLeaveStandby(self):
		if config.plugins.vfdicon.stbdisplayshow.value == "time":
			self.timer.stop() # stop second timer
			self.timer.start(59998, False) # start minute timer
			Console().ePopen("fp_control -l 0 0") #Red LED off
		self.standby = False

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 4:
			if config.plugins.vfdicon.standbyredledon.value:
				Console().ePopen("fp_control -l 0 1") #Red LED on
			stbdisplayshow = config.plugins.vfdicon.stbdisplayshow.value
		if stbdisplayshow == "time" and self.record == False:
			self.timer.stop() # stop minute timer
			self.timer.start(1000, False) # start second timer
			dot = 1
		if stbdisplayshow == "time" or stbdisplayshow == "date" or stbdisplayshow == "day_date":
			self.writeDate(stbdisplayshow)
		else:
			evfd.getInstance().vfd_clear_string()
		self.standby = True
		print("[sparkVFD] set display on Enter Standby")


VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 4:
		displayshow = config.plugins.vfdicon.displayshow.value
		if displayshow == "time" or displayshow == "date" or displayshow == "day_date" or displayshow == "time_day_date":
			sleep(1)
			VFDIconsInstance.timerEvent()
		else:
			VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name = _("sparkVFD"),
		description = _("LED display configuration"),
		where = PluginDescriptor.WHERE_MENU,
		fnc = LEDdisplaymenu),
		PluginDescriptor(
		name = _("sparkVFD"),
		description = _("LED display control Spark"),
		where = PluginDescriptor.WHERE_SESSIONSTART,
		fnc = main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name = _("sparkVFD"),
			description = _("LED display configuration for Spark"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			fnc = opencfg))
	return l
