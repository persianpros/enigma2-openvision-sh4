#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from enigma import iPlayableService, evfd, getBoxType
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen


try:
	DisplayType = evfd.getInstance().getVfdType()
	if DisplayType != 10:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if getBoxType() == "hs7110":
		DisplayType = 10
	else:
		DisplayType = None
config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.standbyredled = ConfigSlider(default=7, limits=(1, 7))
#config.plugins.vfdicon.dstandbyredled = ConfigSlider(default=1, limits=(1, 7))
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
		self.setTitle(_("LED configuration"))
		self.createSetup()

	def createSetup(self):
		self.cfglist = []
		self.cfglist.append(getConfigListEntry(_("Standby LED brightness"), config.plugins.vfdicon.standbyredled))
#		self.cfglist.append(getConfigListEntry(_("Deep standby LED brightness"), config.plugins.vfdicon.dstandbyredled))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyredled:
			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value))
#		elif self["config"].getCurrent()[1] == config.plugins.vfdicon.dstandbyredled:
#			Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.dstandbyredled.value))
		else:
			Console().ePopen("fp_control -l 0 0")
		print("[hs7110VFD] newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		Console().ePopen("fp_control -l 0 0")
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		Console().ePopen("fp_control -l 0 0 ")
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
		return [(_("LED control"), opencfg, "vfd_display", 44)]
	else:
		return []

class VFDIcons:
	def __init__(self, session):
		self.session = session
		self.onClose = []
		print('[hs7110VFD] Start')
		self.standby = False
		global DisplayType
		print('[hs7110VFD] Hardware displaytype:', DisplayType)
		print('[hs7110VFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 10:
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
					iPlayableService.evStart: self.__evStart
				})
			config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call=False)
		print('[hs7110VFD] End initialisation')

	def __evStart(self):
		print('[hs7110VFD] __evStart')
#		... and do nothing else

#	def __evUpdatedEventInfo(self):
#		print('[VFD-Icons] __evUpdatedEventInfo')
#		... and do nothing else

#	def UpdatedInfo(self):
#		print('[VFD-Icons] __evUpdatedInfo')
#		... and do nothing else

#	def timerEvent(self):
#		print('[VFD-Icons] Timer event')
#		... and do nothing else

#	def __evTunedIn(self):
#		self.tuned = True

#	def __evTuneFailed(self):
#		self.tuned = False

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		if DisplayType == 10:
			Console().ePopen("fp_control -l 0 0") #Red LED off

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 10:
			if config.plugins.vfdicon.standbyredled.value:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredled.value)) #Red LED on
		self.standby = True

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name=_("hs7110VFD"),
		description=_("LED configuration"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=VFDdisplaymenu),
		PluginDescriptor(
		name=_("hs7110VFD"),
		description=_("LED control for Fortis HS7110"),
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name=_("hs7110VFD"),
			description=_("LED control for Fortis HS7110"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=opencfg))
	return l
