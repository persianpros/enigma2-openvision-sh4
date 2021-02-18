#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import *
from Components.Sources.StaticText import StaticText
from ServiceReference import ServiceReference
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd, getBoxType
from time import localtime, strftime, sleep
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console


try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 11:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if getBoxType() in ("hs7420", "hs7429"):
		DisplayType = 11
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
config.plugins.vfdicon.logoled = ConfigSlider(default=4, limits=(0, 7))
config.plugins.vfdicon.standbyredled = ConfigSlider(default=0, limits=(0, 7))
#config.plugins.vfdicon.dstandbyredled = ConfigSlider(default=7, limits=(0, 7))
config.plugins.vfdicon.recredled = ConfigSlider(default=2, limits=(0, 7))
config.plugins.vfdicon.extMenu = ConfigYesNo(default=True)

class ConfigVFDDisplay(Screen, ConfigListScreen):
#	skin = """
#	<screen position="center,center" size="700,340" title="VFD display configuration">
#		<widget name="lab1" position="10,30" halign="center" size="680,60" zPosition="1" font="Regular;24" valign="top" transparent="1" />
#		<widget name="config" position="10,100" size="680,180" scrollbarMode="showOnDemand" />
#		<ePixmap position="140,290" size="140,40" pixmap="buttons/red.png" alphatest="on" />
#		<widget name="key_red" position="140,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
#		<ePixmap position="420,290" size="140,40" pixmap="buttons/green.png" alphatest="on" zPosition="1" />
#		<widget name="key_green" position="420,290" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
#	</screen>"""

	def __init__(self, session):
#		self.skin = ConfigVFDDisplay.skin
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
#		self.edittext = "* Not available on some models"

		self["introduction"] = StaticText(self.edittext)
#		self.list = []
#		ConfigListScreen.__init__(self, self.list)
#		self["lab1"] = Label(_("* not available on some models"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
#		self["introduction"] = StaticText(self.edittext)
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
		if DisplayType == 11:
			self.cfglist.append(getConfigListEntry(_("VFD brightness"), config.plugins.vfdicon.contrast))
			self.cfglist.append(getConfigListEntry(_("Standby brightness"), config.plugins.vfdicon.stbcontrast))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
		self.cfglist.append(getConfigListEntry(_('Logo brightness *'), config.plugins.vfdicon.logoled))
		self.cfglist.append(getConfigListEntry(_('Standby LED brightness'), config.plugins.vfdicon.standbyredled))
#		self.cfglist.append(getConfigListEntry(_('Deepstandby LED brightness'), config.plugins.vfdicon.dstandbyredled))
		self.cfglist.append(getConfigListEntry(_('Rec LED brightness'), config.plugins.vfdicon.recredled))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if DisplayType == 11:
			if self["config"].getCurrent()[1] == config.plugins.vfdicon.stbcontrast:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.stbcontrast.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyredled:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value))
#			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.dstandbyredled:
#				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.dstandbyredled.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.recredled:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredled.value))
			else:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
				print("")
				Console().ePopen("fp_control -l 0 0")
		print("[hs742xVFD] newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		Console().ePopen("fp_control -l 0 0")
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if DisplayType == 11:
			Console().ePopen("fp_control -l 0 0")
			print("[hs742xVFD] set brightness", config.plugins.vfdicon.contrast.value)
			Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs742xVFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[hs742xVFD] set text centering", config.plugins.vfdicon.textcenter.value)
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
		print('[hs742xVFD] Start')
		self.play = False
		self.record = False
		self.standby = False
		self.mp3Available = False
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(60000, False) # start one minute timer
		Console().ePopen("fp_control -l 0 0")
		global DisplayType
		print('[hs742xVFD] Hardware displaytype:', DisplayType)
		print('[hs742xVFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 11:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evUpdatedInfo: self.UpdatedInfo,
					iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
					iPlayableService.evStart: self.__evStart
				})
			session.nav.record_event.append(self.gotRecordEvent)
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call=False)
		else:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evStart: self.writeName,
				})
		print('[hs742xVFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[hs742xVFD] Set text centering option")
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print('[hs742xVFD] End initialisation')

	def __evStart(self):
		print('[hs742xVFD] __evStart')
#		... and do nothing else

	def __evUpdatedEventInfo(self):
		print('[hs742xVFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[hs742xVFD] __evUpdatedInfo')
		self.checkAudioTracks()
		self.writeName()

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
						self.play = False
			if config.plugins.vfdicon.uppercase.value == True:
				servicename = servicename.upper()
			servicename = servicename.replace('  ', ' ')
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

	def timerEvent(self):
 		if self.standby == False:
			if self.record == False:
				disptype = config.plugins.vfdicon.displayshow.value
		else:
			disptype = config.plugins.vfdicon.stbshow.value
			self.writeDate(disptype)

	def gotRecordEvent(self, service, event):
		if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
			recs = self.session.nav.getRecordings()
			nrecs = len(recs)
			if nrecs > 0: #recording active
				self.record = True
				if (config.plugins.vfdicon.recredled.value != 0):
					Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.recredled.value))
			else: # no recording active
				self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)
			if (config.plugins.vfdicon.recredled.value != 0):
				Console().ePopen("fp_control -l 0 0")

	def writeDate(self, disp):
		tm = localtime()
		if disp == "day_date":
			date = strftime("%a", tm)[0:2] + strftime(" %d-%m", tm)
		elif disp == "date":
			date = strftime("%d-%m-", tm) + strftime("%y", tm)[0:2] 
		else:
			date = strftime("%H.%M.%S", tm)
		evfd.getInstance().vfd_write_string(date[0:8])

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		evfd.getInstance().vfd_write_string("       ")
		self.timer.stop() # stop one second timer
		self.timer.start(60000, False) # start one minute timer
		if DisplayType == 11:
			evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.contrast.value)
			print("[hs742xVFD] set brightness", config.plugins.vfdicon.contrast.value)
			self.timerEvent()
			Console().ePopen("fp_control -l 0 0") # LED off
			Console().ePopen("fp_control -l 1 " + str(config.plugins.vfdicon.logoled.value)) # Logo on
			print("[hs742xVFD] set LEDs on Leave Standby")

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 11:
			if config.plugins.vfdicon.stbshow.value == "nothing":
				evfd.getInstance().vfd_set_light(0)
			else:
				evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.stbcontrast.value)
			print("[hs742xVFD] set standby brightness", config.plugins.vfdicon.stbcontrast.value)
			if config.plugins.vfdicon.standbyredled.value:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value)) #Red LED on
			Console().ePopen("fp_control -l 1 0") # Logo off
		if config.plugins.vfdicon.stbshow.value == "time":
			self.timer.stop() # stop minute timer
			self.timer.start(999, False) # start one second timer
		if config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "time":
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_clear_string()
		self.standby = True
		print("[hs742xVFD] set display & LEDs on Enter Standby")

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	global hddUsed
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 11:
		if config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date" or config.plugins.vfdicon.displayshow.value == "time":
			sleep(1)
			VFDIconsInstance.timerEvent()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name=_("hs742xVFD"),
		description=_("VFD display configuration"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=VFDdisplaymenu),
		PluginDescriptor(
		name=_("hs742xVFD"),
		description=_("VFD icons for Fortis HS7420 & HS7429"),
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name=_("hs742xVFD"),
			description=_("VFD display configuration for Fortis HS742X"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=opencfg))
	return l
