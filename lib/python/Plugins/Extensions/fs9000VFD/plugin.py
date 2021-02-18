#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference
from Components.ServiceList import ServiceList
from enigma import iPlayableService, iServiceInformation, iRecordableService, eTimer, evfd, eDVBVolumecontrol, getBoxType
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
	if DisplayType != 6:
		DisplayType = None
except:
	DisplayType = None
DisplayTypevfd = DisplayType

if DisplayTypevfd is None:
	if getBoxType() == "fortis_hdbox":
		DisplayType = 6
	else:
		DisplayType = None

config.plugins.vfdicon = ConfigSubsection()
config.plugins.vfdicon.displayshow = ConfigSelection(default="channel",
	choices=[
		("nothing", _("blank")),
		("channel number", _("channel number")),
		("channel", _("channel name")),
		("channel namenumber", _("channel number and name")),
		("time", _("time")),
		("date", _("date")),
		("time_date", _("time and date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.stbshow = ConfigSelection(default="time_date",
	choices=[
		("nothing", _("nothing")),
		("time", _("time")),
		("date", _("date")),
		("time_date", _("time and date")),
		("day_date", _("day and date"))
		])
config.plugins.vfdicon.contrast = ConfigSlider(default=4, limits=(0, 7))
config.plugins.vfdicon.stbcontrast = ConfigSlider(default=2, limits=(0, 7))
config.plugins.vfdicon.uppercase = ConfigYesNo(default=False)
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
config.plugins.vfdicon.standbyredledon = ConfigSlider(default=7, limits=(0, 31))
config.plugins.vfdicon.ledbright = ConfigSlider(default=15, limits=(0, 31))
config.plugins.vfdicon.crossbright = ConfigSlider(default=31, limits=(0, 31))
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
		if DisplayType == 6:
			self.cfglist.append(getConfigListEntry(_("VFD brightness"), config.plugins.vfdicon.contrast))
			self.cfglist.append(getConfigListEntry(_("Standby brightness"), config.plugins.vfdicon.stbcontrast))
		self.cfglist.append(getConfigListEntry(_("Uppercase letters only"), config.plugins.vfdicon.uppercase))
		self.cfglist.append(getConfigListEntry(_("Scroll text"), config.plugins.vfdicon.textscroll))
		self.cfglist.append(getConfigListEntry(_("Center text"), config.plugins.vfdicon.textcenter))
		self.cfglist.append(getConfigListEntry(_("Show icons"), config.plugins.vfdicon.showicons))
		self.icons_showicons = config.plugins.vfdicon.showicons.value
		if DisplayType == 6:
			self.cfglist.append(getConfigListEntry(_('Standby LED brightness'), config.plugins.vfdicon.standbyredledon))
			self.cfglist.append(getConfigListEntry(_('Blue LED brightness'), config.plugins.vfdicon.ledbright))
			self.cfglist.append(getConfigListEntry(_('Cross brightness'), config.plugins.vfdicon.crossbright))
	        self.cfglist.append(getConfigListEntry(_('Show this plugin in plugin menu'), config.plugins.vfdicon.extMenu))
		self["config"].list = self.cfglist
		self["config"].l.setList(self.cfglist)

	def newConfig(self):
		global DisplayType
		if DisplayType == 6:
			if self["config"].getCurrent()[1] == config.plugins.vfdicon.stbcontrast:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.stbcontrast.value))
			elif self["config"].getCurrent()[1] == config.plugins.vfdicon.standbyredledon:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredledon.value) + " -l 1 0 -l 4 0 -l 5 0 -l 6 0 -l 7 0")
			else:
				Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
				print("")
				b = str(config.plugins.vfdicon.ledbright.value)
				c = str(config.plugins.vfdicon.crossbright.value)
				Console().ePopen("fp_control -l 0 0 -l 1 " + b + " -l 4 " + c + " -l 5 " + c + " -l 6 " + c + " -l 7 " + c)
		print("[fs9000VFD] newConfig", self["config"].getCurrent())
		self.createSetup()

	def cancel(self):
		main(self)
		b = str(config.plugins.vfdicon.ledbright.value)
		c = str(config.plugins.vfdicon.crossbright.value)
		Console().ePopen("fp_control -l 0 0 -l 1 " + b + " -l 4 " + c + " -l 5 " + c + " -l 6 " + c + " -l 7 " + c)
		ConfigListScreen.keyCancel(self)

	def keySave(self):
		global DisplayType
		if DisplayType == 6:
			b = str(config.plugins.vfdicon.ledbright.value)
			c = str(config.plugins.vfdicon.crossbright.value)
			Console().ePopen("fp_control -l 0 0 -l 1 " + b + " -l 4 " + c + " -l 5 " + c + " -l 6 " + c + " -l 7 " + c)
			print("[fs9000VFD] set brightness", config.plugins.vfdicon.contrast.value)
			Console().ePopen("fp_control -b " + str(config.plugins.vfdicon.contrast.value))
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[fs9000VFD] set text scroll", config.plugins.vfdicon.textscroll.value)
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print("[fs9000VFD] set text centering", config.plugins.vfdicon.textcenter.value)
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
		print('[fs9000VFD] Start')
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
		Console().ePopen("fp_control -i 40 0")
		b = str(config.plugins.vfdicon.ledbright.value)
		c = str(config.plugins.vfdicon.crossbright.value)
		Console().ePopen("fp_control -l 0 0 -l 1 " + b + " -l 4 " + c + " -l 5 " + c + " -l 6 " + c + " -l 7 " + c)
		global DisplayType
		print('[fs9000VFD] Hardware displaytype:', DisplayType)
		print('[fs9000VFD] VFD displaytype     :', DisplayTypevfd)
		if DisplayType == 6:
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
		print('[fs9000VFD] Set text scrolling option')
		if config.plugins.vfdicon.textscroll.value is not None:
			evfd.getInstance().vfd_set_SCROLL(int(config.plugins.vfdicon.textscroll.value))
		else:
			evfd.getInstance().vfd_set_SCROLL(1)
		print("[fs9000VFD] Set text centering option")
		if config.plugins.vfdicon.textcenter.value == "1":
			evfd.getInstance().vfd_set_CENTER(True)
		else:
			evfd.getInstance().vfd_set_CENTER(False)
		print('[fs9000VFD] End initialisation')

	def __evStart(self):
		print('[fs9000VFD] __evStart')
		self.__evSeekableStatusChanged()

	def __evUpdatedEventInfo(self):
		print('[fs9000VFD] __evUpdatedEventInfo')
#		... and do nothing else

	def UpdatedInfo(self):
		print('[fs9000VFD] __evUpdatedInfo')
		self.checkAudioTracks()
		self.writeName()
		self.showDTS()
		if DisplayType == 6:
			self.showCrypted()
			self.showDolby()
			self.showMP3()
			self.showTuned()
			self.showMute()

	def writeName(self):
		if (config.plugins.vfdicon.displayshow.value != "date" and config.plugins.vfdicon.displayshow.value != "day_date"
			and config.plugins.vfdicon.displayshow.value != "time_date" and config.plugins.vfdicon.displayshow.value != "time"):
			servicename = "        "
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
							Console().ePopen("fp_control -i 27 0 -i 29 0 -i 31 0 -i 32 0 -i 38 0 -i 39 1") #Radio icon on, TV off
						else: # show the file name
							Console().ePopen("fp_control -i 38 1 -i 39 0") #Radio icon off, TV on
							self.service = self.session.nav.getCurrentlyPlayingServiceReference()
							if not self.service is None:
								service = self.service.toCompareString()
#								servicename = ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(63)
								servicename = ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '')
						Console().ePopen("fp_control -i 15 1 -i 16 1 -i 25 1") #play, file
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
						Console().ePopen("fp_control -i 15 0 -i 16 0 -i 25 0") #play, file off
						#evaluate radio or tv
						if config.plugins.vfdicon.showicons.value == "all":
							if config.servicelist.lastmode.value == 'tv':
								Console().ePopen("fp_control -i 38 1 -i 39 0") #TV icon on, Radio off
							else:
								Console().ePopen("fp_control -i 27 0 -i 29 0 -i 31 0 -i 32 0 -i 38 0 -i 39 1") #Radio icon on, TV off
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
					Console().ePopen("fp_control -i 8 1") #padlock icon
				else:
					Console().ePopen("fp_control -i 8 0")

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
			Console().ePopen("fp_control -i 9 1") #Dolby
		else:
			Console().ePopen("fp_control -i 9 0")

	def showMP3(self):
		if self.mp3Available:
			Console().ePopen("fp_control -i 13 1") #MP3
		else:
			Console().ePopen("fp_control -i 13 0")

	def showDTS(self):
		if self.DTSAvailable:
			Console().ePopen("fp_control -i 9 1") #DTS (dolby)
		else:
			Console().ePopen("fp_control -i 9 0")

	def showTuned(self):
		if config.plugins.vfdicon.showicons.value == "all":
			if self.tuned == True:
				service = self.session.nav.getCurrentService()
				if service is not None and self.play == False:
					info = service.info()
					TPdata = info and info.getInfoObject(iServiceInformation.sTransponderData)
					tunerType = TPdata.get("tuner_type")
					if tunerType == "DVB-S":
						Console().ePopen("fp_control -i 2 1 -i 26 0") #SAT on, TER off
						feinfo = service.frontendInfo()
						FEdata = feinfo and feinfo.getAll(True)
						tunerNumber = FEdata and FEdata.get("tuner_number")
						print("[fs9000VFD] Set SAT icon; tuner number", tunerNumber)
						if tunerNumber == 0:
							Console().ePopen("fp_control -i 11 1 -i 12 0") #Tu1 on, Tu2 off
						else:
							Console().ePopen("fp_control -i 11 0 -i 12 1") #Tu1 off, Tu2 on
#					elif tunerType == "DVB-T" or tunerType == "DVB-C":
#						print("[VFD-Icons] Set TER icon")
#						Console().ePopen("fp_control -i 26 1 -i 2 0 -i 44 0 -i 45 0 -i 29 0") #TER on, SAT, Tu1, Tu2 off
				else:
					print("[fs9000VFD] No TER or SAT icon")
					Console().ePopen("fp_control -i 26 0 -i 2 0 -i 11 0 -i 12 0") #TER, SAT, Tu1, Tu2 off
			else:
				                             #TER,    SAT,   HD,    Timeshift,Dolby,MP3,   Tu1 Tu2 off
				Console().ePopen("fp_control -i 25 0 -i 3 0 -i 6 0 -i 4 0 -i 9 0 -i 13 0 -i 11 0 -i 12 0")

	def showMute(self):
		if config.plugins.vfdicon.showicons.value != "none":
			self.isMuted = eDVBVolumecontrol.getInstance().isMuted()
			if self.isMuted:
				Console().ePopen("fp_control -i 10 1") #Mute
			else:
				Console().ePopen("fp_control -i 10 0")

	def showTimer(self):
		if config.plugins.vfdicon.showicons.value == "all":
			# check if timers are set
			next_rec_time = -1
			next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
			if next_rec_time > 0:
				Console().ePopen("fp_control -i 5 1") #Timer
			else:
				Console().ePopen("fp_control -i 5 0")

	def timerEvent(self):
		self.showTimer() #update timer icon
		if self.standby == False:
			self.showMute() #update mute icon
			if config.plugins.vfdicon.showicons.value == "all":
				if (self.record == True or self.timeshift == True): # if recording or timeshifting, display a rotating disc
					self.displayHddUsed() # update HDD display
					if self.disc == 1:
						Console().ePopen("fp_control -i 17 0")
					if self.disc == 2:
						Console().ePopen("fp_control -i 18 0")
					if self.disc == 3:
						Console().ePopen("fp_control -i 19 0")
					if self.disc == 4:
						Console().ePopen("fp_control -i 20 0")
					if self.disc == 5:
						Console().ePopen("fp_control -i 21 0")
					if self.disc == 6:
						Console().ePopen("fp_control -i 22 0")
					if self.disc == 7:
						Console().ePopen("fp_control -i 23 0")
					if self.disc == 8:
						Console().ePopen("fp_control -i 24 0")
					if self.disc == 9:
						Console().ePopen("fp_control -i 17 1")
					if self.disc == 10:
						Console().ePopen("fp_control -i 18 1")
					if self.disc == 11:
						Console().ePopen("fp_control -i 19 1")
					if self.disc == 12:
						Console().ePopen("fp_control -i 20 1")
					if self.disc == 13:
						Console().ePopen("fp_control -i 21 1")
					if self.disc == 14:
						Console().ePopen("fp_control -i 22 1")
					if self.disc == 15:
						Console().ePopen("fp_control -i 23 1")
					if self.disc == 16:
						Console().ePopen("fp_control -i 24 1")
					self.disc += 1 # indicate next state
					if self.disc == 17:
						self.disc = 1
		if self.record == False and self.timeshift == False:
	 		if self.standby == False:
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
				if config.plugins.vfdicon.showicons.value == "all":
					if height > 479 and height < 576: #set 480i icon
						Console().ePopen("fp_control -i 27 1 -i 29 0 -i 31 0 -i 32 0")
					elif height > 575 and height < 720: #set 576i icon
						Console().ePopen("fp_control -i 27 0 -i 29 1 -i 31 0 -i 32 0")
					elif height > 719 and height < 1080: #set 720p icon
						Console().ePopen("fp_control -i 27 0 -i 29 0 -i 31 1 -i 32 0")
					elif height > 1079: #set 1080i icon
						Console().ePopen("fp_control -i 27 0 -i 29 0 -i 31 0 -i 32 1")
					else: #set all resolution icons off
						Console().ePopen("fp_control -i 27 0 -i 29 0 -i 31 0 -i 32 0")
				if height > 576: #set HD icon
					Console().ePopen("fp_control -i 6 1")
				else:
					Console().ePopen("fp_control -i 6 0")

	def __evSeekableStatusChanged(self):
		if config.plugins.vfdicon.showicons.value == "all":
			service = self.session.nav.getCurrentService()
			if service:
				if self.play == False:
					ts = service and service.timeshift()
#					if ts and ts.isTimeshiftEnabled() > 0:
					if ts and ts.isTimeshiftActive() > 0:
						self.timeshift = True
						Console().ePopen("fp_control -i 4 1") #Time shift
						self.discOn()
					else:
						self.timeshift = False
						Console().ePopen("fp_control -i 4 0") #Time shift icon off
						if self.record == False:
							self.discOff()


	def gotRecordEvent(self, service, event):
		if config.plugins.vfdicon.showicons.value != 'none':
			if event in (iRecordableService.evEnd, iRecordableService.evStart, None):
				recs = self.session.nav.getRecordings()
				nrecs = len(recs)
				if nrecs > 0: #recording active
					self.record = True
					Console().ePopen("fp_control -i 3 1") #REC on
					self.discOn()
				else: # no recording active
					Console().ePopen("fp_control -i 3 0") #REC off
					if self.timeshift == False:
						self.discOff()
					self.RecordEnd()

	def RecordEnd(self):
		if self.record:
			self.record = False
			self.session.nav.record_event.remove(self.gotRecordEvent)
			self.showTimer() #update timer icon

	def discOn(self):
		if config.plugins.vfdicon.showicons.value == "all":
			self.timer.stop() # stop minute timer
			Console().ePopen("fp_control -i 16 1 -i 17 1 -i 18 1 -i 19 1 -i 20 1 -i 21 1 -i 22 1 -i 23 1 -i 24 1")
			self.disc = 1 #start with state #1
			self.timer.start(2000, False) # start two second timer

	def discOff(self):
		if config.plugins.vfdicon.showicons.value == "all":
			self.timer.stop() # stop two second timer
			Console().ePopen("fp_control -i 16 0 -i 17 0 -i 18 0 -i 19 0 -i 20 0 -i 21 0 -i 22 0 -i 23 0 -i 24 0")
			self.timer.start(60000, False) # start minute timer

	def writeDate(self, disp): #TODO: replace with case
		if disp == "date" or disp == "day_date" or disp == "time" or disp == "time_date" or disp == "nothing":
			tm = localtime()
			if disp == "day_date":
				date = strftime("%a", tm)[0:2] + strftime(" %d-%m-%y", tm)
				Console().ePopen("fp_control -i 33 0 -i 34 0 -i 35 0 -i 37 0") # colons off
			elif disp == "date":
				date = strftime("%d-%m-", tm) + strftime("%y", tm)[0:2] 
				Console().ePopen("fp_control -i 33 0 -i 34 0 -i 35 0 -i 37 0") # all colons off
			elif disp == "time_date":
				date = strftime("%d-%m %H%M%S", tm) 
				Console().ePopen("fp_control -i 33 0 -i 34 0 -i 35 1 -i 37 1") # 2 colons on
			elif disp == "time":
				date = strftime("      %H%M%S", tm)
				Console().ePopen("fp_control -i 33 0 -i 34 0 -i 35 1 -i 37 1") # 2 colons on
			elif disp == "nothing":
				date = "            "
				Console().ePopen("fp_control -i 33 0 -i 34 0 -i 35 0 -i 37 0") # all colons off
			evfd.getInstance().vfd_write_string(date[0:12])

	def __evTunedIn(self):
		self.tuned = True

	def __evTuneFailed(self):
		self.tuned = False

	def onLeaveStandby(self):
		self.standby = False
		global DisplayType
		Console().ePopen("fp_control -i 1 0 -i 35 0 -i 37 0") # standby & colons off
		self.timer.stop() # stop one second timer
		evfd.getInstance().vfd_write_string("           ")
		self.timer.start(60000, False) # start one minute timer
		print("[fs9000VFD] minute timer started")
		if DisplayType == 6:
			evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.contrast.value)
			print("[fs9000VFD] set brightness", config.plugins.vfdicon.contrast.value)
			self.timerEvent()
			b = str(config.plugins.vfdicon.ledbright.value)
			c = str(config.plugins.vfdicon.crossbright.value)
			Console().ePopen("fp_control -l 0 0 -l 1 " + b + " -l 4 " + c + " -l 5 " + c + " -l 6 " + c + " -l 7 " + c) #Red LED off, cross and blue on
			if config.plugins.vfdicon.showicons.value == "all":
				global hddUsed
				hddUsed = -1 #force hdd display
				self.displayHddUsed()
				if self.usb == 1:
					Console().ePopen("fp_control -i 17 1") #USB
				else:
					Console().ePopen("fp_control -i 17 0")
			print("[fs9000VFD] set icons on Leave Standby")

	def onEnterStandby(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.onLeaveStandby)
		global DisplayType
		if DisplayType == 6:
			Console().ePopen("fp_control -i 40 0") #clear all VFD icons
			print("[fs9000VFD] set display & icons on Enter Standby")
			if config.plugins.vfdicon.stbshow.value == "nothing":
				evfd.getInstance().vfd_set_light(0)
			else:
				evfd.getInstance().vfd_set_brightness(config.plugins.vfdicon.stbcontrast.value)
			print("[fs9000VFD] set standby brightness", config.plugins.vfdicon.stbcontrast.value)
			if config.plugins.vfdicon.standbyredledon.value:
				Console().ePopen("fp_control -l 0 " + str(config.plugins.vfdicon.standbyredledon.value) + " -l 1 0 -l 4 0 -l 5 0 -l 6 0 -l 7 0") #Red LED on, cross off
		if (config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.timer.stop() # stop minute timer
			self.timer.start(999, False) # start one second timer
			print("[fs9000VFD] second timer started")
		if (config.plugins.vfdicon.stbshow.value == "date" or config.plugins.vfdicon.stbshow.value == "day_date" or config.plugins.vfdicon.stbshow.value == "time" or config.plugins.vfdicon.stbshow.value == "time_date"):
			self.writeDate(config.plugins.vfdicon.stbshow.value)
		else:
			evfd.getInstance().vfd_clear_string()
		Console().ePopen("fp_control -i 1 1") #Standby icon on
		self.standby = True

	def hotplugCB(self, dev, media_state):
		if config.plugins.vfdicon.showicons.value == "all":
			if dev.__contains__('sda') or dev.__contains__('sdb') or dev.__contains__('sdc'):
#				if media_state == "add" or media_state == "change":
				if media_state == "add":
					Console().ePopen("fp_control -i 7 1")
					self.usb = 1
					self.displayHddUsedOff() # signal hot plug
					self.mount = None # force remount
					self.SetMount() # determine mount
					if self.firstmount == -1 and self.mount:
						self.firstmount = self.mount
					self.displayHddUsed() # and display icon
				if media_state == "remove":
					Console().ePopen("fp_control -i 7 0")
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
				Console().ePopen("fp_control -i 14 1") #HDD on
				print("[fs9000VFD] HDD mount point:", self.mount)
		else:
			self.displayHddUsedOff()

	def displayHddUsedOff(self): #switch off hdd icon
		Console().ePopen("fp_control -i 14 0")

VFDIconsInstance = None

def main(session, **kwargs):
	global VFDIconsInstance
	global DisplayType
	global hddUsed
	if VFDIconsInstance is None:
		VFDIconsInstance = VFDIcons(session)
	if DisplayType == 6:
		if (config.plugins.vfdicon.displayshow.value == "date" or config.plugins.vfdicon.displayshow.value == "day_date"
			or config.plugins.vfdicon.displayshow.value == "time" or config.plugins.vfdicon.displayshow.value == "time_date"):
			sleep(1)
			VFDIconsInstance.timerEvent()
		else:
			if config.plugins.vfdicon.showicons.value == "none":
				Console().ePopen("fp_control -i 40 0")		
			else:
				hddUsed = -1
				VFDIconsInstance.displayHddUsed()
		VFDIconsInstance.UpdatedInfo()
	else:
		VFDIconsInstance.writeName()

def Plugins(**kwargs):
	l = [PluginDescriptor(
		name=_("fs9000VFD"),
		description=_("VFD display configuration"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=VFDdisplaymenu),
		PluginDescriptor(
		name=_("fs9000VFD"),
		description=_("VFD icons for Fortis FS9000/9200"),
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=main)]
	if config.plugins.vfdicon.extMenu.value:
		l.append(PluginDescriptor(
			name=_("fs9000VFD"),
			description=_("VFD configuration for Fortis FS9000/9200"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=opencfg))
	return l
