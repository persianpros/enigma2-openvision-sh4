#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from config import config, ConfigSubsection, ConfigSlider, ConfigOnOff, ConfigEnableDisable
from enigma import eQBOXSenseWheel
from Components.SystemInfo import SystemInfo


class SENSEWHEEL:
	def __init__(self):
		self.orig_flag_enable_sense = False
		self.flag_enable_sense = False
		self.enable_panel_leds = False
		self.H_panel = 0
		self.S_panel = 0
		self.V_panel = 0
		self.enable_board_leds = False
		self.H_board = 0
		self.S_board = 0
		self.V_board = 0
		self.standby_panel_leds = False
		self.standby_board_leds = False
		self.enable_standby_panel = True

	def setPanelLedsEnable(self, value):
		self.enable_panel_leds = value
		if value:
			eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, self.V_panel)
		else:
			eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, 0)

	def setBoardLedsEnable(self, value):
		self.enable_board_leds = value
		if value:
			eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, self.V_board)
		else:
			eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, 0)

	def setPanelLedsHue(self, value):
		if value > 359:
			value = 359
		if value < 0:
			value = 0
		self.H_panel = value
		eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, self.V_panel)

	def setBoardLedsHue(self, value):
		if value > 359:
			value = 359
		if value < 0:
			value = 0
		self.H_board = value
		eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, self.V_board)

	def setPanelLedsSaturation(self, value):
		if value > 99:
			value = 99
		if value < 0:
			value = 0
		self.S_panel = value
		eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, self.V_panel)

	def setBoardLedsSaturation(self, value):
		if value > 99:
			value = 99
		if value < 0:
			value = 0
		self.S_board = value
		eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, self.V_board)

	def setPanelLedsValue(self, value):
		if value > 99:
			value = 99
		if value < 0:
			value = 0
		self.V_panel = value
		eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, self.V_panel)

	def setBoardLedsValue(self, value):
		if value > 99:
			value = 99
		if value < 0:
			value = 0
		self.V_board = value
		eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, self.V_board)

	def setEnableFlag(self, value):
		self.flag_enable_sense = value

	def setInitEnableFlag(self, value):
		self.orig_flag_enable_sense = value
		self.flag_enable_sense = value

	def IsFlagSenseEnabled(self):
		return self.flag_enable_sense

	def setStandbyPanelLeds(self, value):
		self.standby_panel_leds = value

	def setStandbyBoardLeds(self, value):
		self.standby_board_leds = value

	def setStandbyPanel(self, value):
		self.enable_standby_panel = value
		eQBOXSenseWheel.getInstance().setStandbyOnPanel(self.enable_standby_panel)

	def ConfirmFlagSenseEnabled(self):
		self.orig_flag_enable_sense = self.flag_enable_sense

	def RestoreOrigFlagSenseEnabled(self):
		self.flag_enable_sense = self.orig_flag_enable_sense

	def enableSense(self):
		eQBOXSenseWheel.getInstance().setEnableSense()
		#print("[SENSEWHEEL] enable Sense.\n")

	def disableSense(self):
		eQBOXSenseWheel.getInstance().setDisableSense()
		#print("[SENSEWHEEL] disable Sense.\n")

	def enterStandby(self):
		print("[SENSEWHEEL] enter Standby.\n")
		#Enter to standby mode
		eQBOXSenseWheel.getInstance().setDisableSense()
		#print("[SENSEWHEEL] disable Sense.\n")
		eQBOXSenseWheel.getInstance().enterStandby(self.standby_panel_leds, self.standby_board_leds)
		if (not self.enable_standby_panel):
			eQBOXSenseWheel.getInstance().setDisableSense()

	def leaveStandby(self):
		print("[SENSEWHEEL] leave Standby.\n")
		# Leave from standby mode
		eQBOXSenseWheel.getInstance().leaveStandby()
		eQBOXSenseWheel.getInstance().setDisableSense()
		#print("[SENSEWHEEL] disable Sense.\n")
		#Power on leds for leave standby
		if self.enable_panel_leds:
			eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, self.V_panel)
		else:
			eQBOXSenseWheel.getInstance().setLedsPanel(self.H_panel, self.S_panel, 0)
		if self.enable_board_leds:
			eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, self.V_board)
		else:
			eQBOXSenseWheel.getInstance().setLedsBoard(self.H_board, self.S_board, 0)
		if (config.sensewheel.enabled.value):
			eQBOXSenseWheel.getInstance().setEnableSense()
			print("[SENSEWHEEL] re-Enable Sense.\n")
		else:
			self.setPanelLedsEnable(False)


isensewheel = SENSEWHEEL()


def InitSenseWheel():
	detected = eQBOXSenseWheel.getInstance().detected()
	SystemInfo["SenseWheel"] = detected
	config.sensewheel = ConfigSubsection()

	def setPanelLedsEnable(configElement):
		isensewheel.disableSense()
		config.sensewheel.ledpanelhue.enable = configElement.value
		config.sensewheel.ledpanelsaturation.enable = configElement.value
		config.sensewheel.ledpanelvalue.enable = configElement.value
		isensewheel.setPanelLedsEnable(configElement.value)

	def setBoardLedsEnable(configElement):
		isensewheel.disableSense()
		config.sensewheel.ledboardhue.enable = configElement.value
		config.sensewheel.ledboardsaturation.enable = configElement.value
		config.sensewheel.ledboardvalue.enable = configElement.value
		isensewheel.setBoardLedsEnable(configElement.value)

	def setPanelLedsHue(configElement):
		isensewheel.disableSense()
		isensewheel.setPanelLedsHue(configElement.value)

	def setPanelLedsSaturation(configElement):
		isensewheel.disableSense()
		isensewheel.setPanelLedsSaturation(configElement.value)

	def setPanelLedsValue(configElement):
		isensewheel.disableSense()
		isensewheel.setPanelLedsValue(configElement.value)

	def setBoardLedsHue(configElement):
		isensewheel.disableSense()
		isensewheel.setBoardLedsHue(configElement.value)

	def setBoardLedsSaturation(configElement):
		isensewheel.disableSense()
		isensewheel.setBoardLedsSaturation(configElement.value)

	def setBoardLedsValue(configElement):
		isensewheel.disableSense()
		isensewheel.setBoardLedsValue(configElement.value)

	def disableSense(configElement):
		isensewheel.disableSense()

	def enableSense(configElement):
		isensewheel.enableSense()

	def setEnableFlag(configElement):
		isensewheel.setEnableFlag(configElement.value)

	def setStandbyPanelLeds(configElement):
		isensewheel.setStandbyPanelLeds(configElement.value)

	def setStandbyBoardLeds(configElement):
		isensewheel.setStandbyBoardLeds(configElement.value)

	def setStandbyPanel(configElement):
		isensewheel.setStandbyPanel(configElement.value)

	def saveAndExitFromSensePlugin(configElement):
		if (isensewheel.IsFlagSenseEnabled()):
			isensewheel.enableSense()
		else:
			isensewheel.setPanelLedsEnable(False)
			isensewheel.disableSense() #-<
		# confirm flag enabled sensewheel
		isensewheel.ConfirmFlagSenseEnabled()

	def reloadAndExitFromSensePlugin(configElement):
		# restore old sense enable situation saved
		isensewheel.RestoreOrigFlagSenseEnabled()
		if (isensewheel.IsFlagSenseEnabled()):
			isensewheel.enableSense()
		else:
			isensewheel.setPanelLedsEnable(False)
			isensewheel.disableSense() #-<
	# WHEEL -----------------------------------------------------------------------------------
	config.sensewheel.ledpanelhue = ConfigSlider(default=150, increment=4, limits=(0, 359))
	config.sensewheel.ledpanelhue.addNotifier(setPanelLedsHue)
	config.sensewheel.ledpanelhue.apply = lambda: setPanelLedsHue(config.sensewheel.ledpanelhue)
	config.sensewheel.ledpanelhue.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledpanelhue.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledpanelsaturation = ConfigSlider(default=50, increment=2, limits=(0, 99))
	config.sensewheel.ledpanelsaturation.addNotifier(setPanelLedsSaturation)
	config.sensewheel.ledpanelsaturation.apply = lambda: setPanelLedsSaturation(config.sensewheel.ledpanelsaturation)
	config.sensewheel.ledpanelsaturation.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledpanelsaturation.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledpanelvalue = ConfigSlider(default=50, increment=2, limits=(0, 99))
	config.sensewheel.ledpanelvalue.addNotifier(setPanelLedsValue)
	config.sensewheel.ledpanelvalue.apply = lambda: setPanelLedsValue(config.sensewheel.ledpanelvalue)
	config.sensewheel.ledpanelvalue.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledpanelvalue.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledpanelenabled = ConfigOnOff()
	config.sensewheel.ledpanelenabled.addNotifier(setPanelLedsEnable)
	config.sensewheel.ledpanelenabled.apply = lambda: setPanelLedsEnable(config.sensewheel.ledpanelenabled)
	config.sensewheel.ledpanelenabled.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledpanelenabled.addNotifierSave(saveAndExitFromSensePlugin)
	# BOARD -----------------------------------------------------------------------------------
	config.sensewheel.ledboardhue = ConfigSlider(default=150, increment=4, limits=(0, 359))
	config.sensewheel.ledboardhue.addNotifier(setBoardLedsHue)
	config.sensewheel.ledboardhue.apply = lambda: setBoardLedsHue(config.sensewheel.ledboardhue)
	config.sensewheel.ledboardhue.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledboardhue.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledboardsaturation = ConfigSlider(default=50, increment=2, limits=(0, 99))
	config.sensewheel.ledboardsaturation.addNotifier(setBoardLedsSaturation)
	config.sensewheel.ledboardsaturation.apply = lambda: setBoardLedsSaturation(config.sensewheel.ledboardsaturation)
	config.sensewheel.ledboardsaturation.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledboardsaturation.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledboardvalue = ConfigSlider(default=50, increment=2, limits=(0, 99))
	config.sensewheel.ledboardvalue.addNotifier(setBoardLedsValue)
	config.sensewheel.ledboardvalue.apply = lambda: setBoardLedsValue(config.sensewheel.ledboardvalue)
	config.sensewheel.ledboardvalue.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledboardvalue.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.ledboardenabled = ConfigOnOff()
	config.sensewheel.ledboardenabled.addNotifier(setBoardLedsEnable)
	config.sensewheel.ledboardenabled.apply = lambda: setBoardLedsEnable(config.sensewheel.ledboardenabled)
	config.sensewheel.ledpanelenabled.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.ledpanelenabled.addNotifierSave(saveAndExitFromSensePlugin)
	# TOUCH ----------------------------------------------------------------------------------
	config.sensewheel.enabled = ConfigEnableDisable()
	config.sensewheel.enabled.addNotifier(setEnableFlag)
	config.sensewheel.enabled.apply = lambda: setEnableFlag(config.sensewheel.enabled.value)
### Init ###
	isensewheel.setInitEnableFlag(config.sensewheel.enabled.value)
	if (isensewheel.IsFlagSenseEnabled()):
		print("ENABLE")
		isensewheel.enableSense()
	else:
		print("DISABLE")
		isensewheel.setPanelLedsEnable(False)
		isensewheel.disableSense() #-<
############
	config.sensewheel.enabled.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.enabled.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.standbypanelled = ConfigOnOff()
	config.sensewheel.standbypanelled.addNotifier(setStandbyPanelLeds)
	config.sensewheel.standbypanelled.apply = lambda: setStandbyPanelLeds(config.sensewheel.standbypanelled)
	config.sensewheel.standbypanelled.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.standbypanelled.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.standbyboardled = ConfigOnOff()
	config.sensewheel.standbyboardled.addNotifier(setStandbyBoardLeds)
	config.sensewheel.standbyboardled.apply = lambda: setStandbyBoardLeds(config.sensewheel.standbyboardled)
	config.sensewheel.standbyboardled.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.standbyboardled.addNotifierSave(saveAndExitFromSensePlugin)
	config.sensewheel.enablepanelstandby = ConfigOnOff()
	config.sensewheel.enablepanelstandby.addNotifier(setStandbyPanel)
	config.sensewheel.enablepanelstandby.apply = lambda: setStandbyPanel(config.sensewheel.enablepanelstandby)
	config.sensewheel.enablepanelstandby.addNotifierLoad(reloadAndExitFromSensePlugin)
	config.sensewheel.enablepanelstandby.addNotifierSave(saveAndExitFromSensePlugin)
