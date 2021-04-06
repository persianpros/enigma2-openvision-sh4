noinst_LIBRARIES += driver/libenigma_driver.a

driver_libenigma_driver_a_CXXFLAGS = $(LIBSDL_CFLAGS)

driver_libenigma_driver_a_SOURCES = \
	driver/avswitch.cpp \
	driver/etimezone.cpp \
	driver/misc_options.cpp \
	driver/rc.cpp \
	driver/rcinput.cpp \
	driver/rfmod.cpp \
	driver/hdmi_cec.cpp \
	driver/vfd.cpp

driverincludedir = $(pkgincludedir)/lib/driver
driverinclude_HEADERS = \
	driver/avswitch.h \
	driver/etimezone.h \
	driver/input_fake.h \
	driver/misc_options.h \
	driver/rc.h \
	driver/rcconsole.h \
	driver/rcdbox.h \
	driver/rcdreambox2.h \
	driver/rcinput.h \
	driver/rcinput_swig.h \
	driver/rfmod.h \
	driver/hdmi_cec.h \
	driver/vfd.h

if HAVE_LIBSDL
driver_libenigma_driver_a_SOURCES += driver/rcsdl.cpp
driverinclude_HEADERS += driver/rcsdl.h
endif

if ENABLE_QBOXHD
driver_libenigma_driver_a_SOURCES += driver/rcqbox2.cpp
driver_libenigma_driver_a_SOURCES += driver/swqbox2.cpp
driverinclude_HEADERS += driver/rcqbox2.h
driverinclude_HEADERS += driver/swqbox2.h
endif

if ENABLE_QBOXHDMINI
driver_libenigma_driver_a_SOURCES += driver/fpqboxmini.cpp
driverinclude_HEADERS += driver/fpqboxmini.h
endif
