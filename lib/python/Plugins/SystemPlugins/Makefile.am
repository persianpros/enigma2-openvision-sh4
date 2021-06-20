installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = SoftwareManager PositionerSetup Satfinder \
	SatelliteEquipmentControl Videomode VideoTune Hotplug \
	DefaultServicesScanner DiseqcTester CommonInterfaceAssignment \
	CableScan FastScan OSDPositionSetup OSD3DSetup HdmiCEC VideoClippingSetup \
	VideoEnhancement WirelessLan NetworkWizard \
	SH4OSDAdjustment VFD-Icons SystemOptions SH4BoosterControl

if HAVE_FCC_ABILITY
SUBDIRS += FastChannelChange
endif

install_PYTHON =	\
	__init__.py
