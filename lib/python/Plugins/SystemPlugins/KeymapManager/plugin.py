#!/usr/bin/python
# -*- coding: utf-8 -*-

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.config import config
from Components.MenuList import MenuList
import keymapparser
from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_CURRENT_PLUGIN
from os import path as os_path, listdir

VER = "0.3"
KPATH = resolveFilename(SCOPE_SKIN)

# installs keymap_???.xml files found in KPATH


class KeymapSelector(Screen):
	skin = """
		<screen position="center,center" size="560,340" name="KeymapManagerScreen" title="Keymap Manager" >
			<ePixmap name="ButtonRed" pixmap="buttons/red.png" position="0,0" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
			<widget render="Label" source= "ButtonRedtext" position="0,0" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<ePixmap name="ButtonGreen" pixmap="buttons/green.png" position="140,0" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
			<widget render="Label" source= "ButtonGreentext" position="140,0" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<ePixmap name="ButtonYellow" pixmap="buttons/yellow.png" position="280,0" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
			<widget render="Label" source= "ButtonYellowtext" position="280,0" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<ePixmap name="ButtonBlue" pixmap="buttons/blue.png" position="420,0" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
			<widget render="Label" source= "ButtonBluetext" position="420,0" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<ePixmap name="icon" pixmap="%s" position="5,50" size="240,114" zPosition="4" transparent="1" alphatest="on"/>
			<widget render="Label" source= "text1" position="255, 95" size="300,24" halign="left" zPosition="5" transparent="1" foregroundColor="white" font="Regular;20"/>
			<ePixmap pixmap="div-h.png" position="0,175" zPosition="1" size="560,2" />
			<widget render="Label" source= "text2" position="5, 190" size="550,24" halign="left" zPosition="5" transparent="1" foregroundColor="white" font="Regular;20"/>
			<widget name="KeymapList" position="10,230" size="540,100" scrollbarMode="showOnDemand" />
		</screen>""" % resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/KeymapManager/input-keyboard.png")

	def __init__(self, session):
		self.skin = KeymapSelector.skin
		Screen.__init__(self, session)

		self.keymaplist = []

		# readout directory...
		for fname in listdir(KPATH):
			if fname.startswith("keymap") and fname.endswith(".xml"):
				self.keymaplist.append((self.getKeymapName(fname), fname))

		self.keymaplist.sort() 

		self["text1"] = StaticText(_("Active Keymap: %s") % self.getKeymapName(os_path.basename(config.usage.keymap.value)))
		self["text2"] = StaticText(_("Keymaps found: (press green or ok to select)"))
		self["ButtonRedtext"] = StaticText(_("exit "))
		self["ButtonGreentext"] = StaticText(_("select "))
		self["ButtonYellowtext"] = StaticText()
		self["ButtonBluetext"] = StaticText()
		self["KeymapList"] = MenuList(self.keymaplist)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "EPGSelectActions"],
		{
			"ok": self.ok,
			"red": self.close,
			"green": self.ok,
			"cancel": self.close,
			"info": self.info
		}, -1)

	def getKeymapName(self, fname):
		if fname == "keymap.xml":
			return "standard e2"
		else:
			return fname[7:-4]

	def info(self):
		aboutbox = self.session.open(MessageBox, _("Merlin Enigma2 Keymapselector v%s\n\nIf you experience any problems please contact\nwww.dreambox-tools.info\n\n2009-2012 DarkVolli") % VER, MessageBox.TYPE_INFO)
		aboutbox.setTitle(_("About..."))

	# ask user for install the selected keymap...
	def ok(self):
		if self["KeymapList"].getCurrent() is not None:
			self.keymap = KPATH + self["KeymapList"].getCurrent()[1]
			fname = os_path.basename(config.usage.keymap.value)
			yesnobox = self.session.openWithCallback(self.installKeymap, MessageBox, _("installed keymap \"%s\"\nactivate now keymap \"%s\"?") % (self.getKeymapName(fname), self["KeymapList"].getCurrent()[0]), MessageBox.TYPE_YESNO)
			yesnobox.setTitle(_("Activate Keymap now?"))

	# install selected keymap...
	def installKeymap(self, install):
		if install is True:
			keymapparser.removeKeymap(config.usage.keymap.value)
			keymapparser.readKeymap(self.keymap)
			config.usage.keymap.value = self.keymap
			config.usage.keymap.save()
		self.close()


def KeymapSelMain(session, **kwargs):
	session.open(KeymapSelector)


def KeymapSelSetup(menuid, **kwargs):
	if menuid == "system":
		return [(_("Keymap"), KeymapSelMain, "keymap_selector", None)]
	else:
		return []


def Plugins(**kwargs):
	return PluginDescriptor(name=_("Keymap selector"), description=_("Select your keymap"), where=PluginDescriptor.WHERE_MENU, fnc=KeymapSelSetup)

