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
import os

try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 20:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if getBoxType() == "opt9600":
		DisplayType = 20
	else:
		DisplayType = None

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
config.plugins.vfdicon.vfd_enable = ConfigYesNo(default = False)
config.plugins.vfdicon.extMenu = ConfigYesNo(default = True)

class ConfigVFDDisplay(Screen, ConfigListScreen):
	def __init__(self, session):

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
		if DisplayType == 20:
			self.cfglist.append(getConfigListEntry(_("Display brightness"), config.plugins.vfdicon.contrast))
			self.cfglist.append(getConfigListEntry(_("Standby brightness"), config.plugins.vfdicon.stbcontrast))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if DisplayType == 20:
			if self["config"].getCurrent()[1] == config.plugins.vfdicon.stbcontrast:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.stbcontrast.value))
		print("newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if DisplayType == 20:
			print("[opt9600VFD] set brightness", config.plugins.vfdicon.contrast.value)
			Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[opt9600VFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[opt9600VFD] set text centering", config.plugins.vfdicon.textcenter.value)
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
		print('[opt9600VFD] Start')
		self.play = False
		self.record = False
		self.timeshift = False
		self.standby = False
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(60000, False) # start one minute timer
		global DisplayType
		print('[opt9600VFD] Hardware displaytype:', DisplayType)
		print('[opt9600VFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 20:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evSeekableStatusChanged: self.__evSeekableStatusChanged,
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call = False)
			session.nav.record_event.append(self.gotRecordEvent)
		else:
			self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
				{
					iPlayableService.evStart: self.writeName,
				})
		print('[opt9600VFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		evfd.getInstance().vfd_set_CENTER(False)
		print("[opt9600VFD] Set text centering option")
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		print('[opt9600VFD] End initialisation')

	def __evStart(self):
		print('[opt9600VFD] __evStart')
		self.__evSeekableStatusChanged()

	def __evUpdatedEventInfo(self):
		print('[opt9600VFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[opt9600VFD] __evUpdatedInfo')
		self.writeName()

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
			servicename = servicename.upper()
			servicename = servicename.replace('  ', ' ')
			evfd.getInstance().vfd_write_string(servicename[0:63])

	def timerEvent(self):
#		print('[opt9600VFD] timerEvent')
		if self.record == False and self.timeshift == False:
	 		if self.standby == False:
				disptype = config.plugins.vfdicon.displayshow.value
			else:
				disptype = config.plugins.vfdicon.stbshow.value
			self.writeDate(disptype)

	def __evSeekableStatusChanged(self):
		service = self.session.nav.getCurrentService()
		if service:
			if self.play == False:
				ts = service and service.timeshift()
#				if ts and ts.isTimeshiftEnabled() > 0:
				if ts and ts.isTimeshiftActive() > 0:
					self.timeshift = True
				else:
					self.timeshift = False

	def gotRecordEvent(self, service, event):
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			recs = self.session.nav.getRecordings()
			nrecs = len(recs)
			if nrecs > 0: #recording active
				self.record = True
			else: # no recording active
				self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)

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

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		self.timer.stop() # stop one second timer
		evfd.getInstance().vfd_write_string("        ")
		self.timer.start(60000, False) # start one minute timer
		print("[opt9600VFD] minute timer started")
		if DisplayType == 20:
			evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.contrast.value)
			print("[opt9600VFD] set brightness", config.plugins.vfdicon.contrast.value)
			self.timerEvent()

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 20:
			print("[opt9600VFD] set display on Enter Standby")
			if config.plugins.vfdicon.stbshow.value == "nothing":
				evfd.getInstance().vfd_set_light(0)
			else:
				evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.stbcontrast.value)
			print("[opt9600VFD] set standby brightness", config.plugins.vfdicon.stbcontrast.value)
		if (config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.timer.stop() # stop minute timer
			self.timer.start(999, False) # start one second timer
			print("[opt9600VFD] second timer started")
		if (config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "timeHM" or config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_clear_string()
		self.standby = True

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 20:
		if (config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date"
			or config.plugins.vfdicon.displayshow.value == "time" or config.plugins.vfdicon.displayshow.value == "time_date"):
			sleep(1)
			VFDIconsInstance.timerEvent()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name = _("opt9600VFD"),
		description = _("VFD display configuration"),
		where = PluginDescriptor.WHERE_MENU,
		fnc = VFDdisplaymenu),
		PluginDescriptor(
		name = _("opt9600VFD"),
		description = _("VFD icons for Opticum HD 9600 series"),
		where = PluginDescriptor.WHERE_SESSIONSTART,
		fnc = main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name = _("opt9600VFD"),
			description = _("VFD configuration for Opticum HD 9600 series"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			fnc = opencfg))
	return l
