installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = CutListEditor PicturePlayer MediaScanner MediaPlayer GraphMultiEPG SocketMMI DVDBurn

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if ENABLE_ADB_BOX
SUBDIRS += ADBVFD
endif

if ENABLE_ADB_2850
SUBDIRS += ADBVFD
endif

if ENABLE_TF7700
SUBDIRS += TopfieldVFD
endif

if HAVE_CubeRevoSTB
SUBDIRS += CuberevoVFD
endif

if ENABLE_FORTIS_HDBOX
SUBDIRS += fs9000VFD
endif

if ENABLE_OCTAGON1008
SUBDIRS += hs9510VFD
endif

if ENABLE_ATEVIO7500
SUBDIRS += hs8200VFD
endif

if ENABLE_HS7110
SUBDIRS += hs7110VFD
endif

if ENABLE_HS7420
SUBDIRS += hs742xVFD
endif

if ENABLE_HS7810A
SUBDIRS += hs7810aVFD
endif

if ENABLE_HS7119
SUBDIRS += hs7810aVFD
endif

if ENABLE_HS7429
SUBDIRS += hs742xVFD
endif

if ENABLE_HS7819
SUBDIRS += hs7810aVFD
endif

if ENABLE_SPARK7162
SUBDIRS += spark7162VFD
endif
 
if ENABLE_SPARK
SUBDIRS += sparkVFD
endif

if ENABLE_VIP1_V1
SUBDIRS += spark7162VFD
endif

if ENABLE_VIP1_V2
SUBDIRS += spark7162VFD
endif

if ENABLE_VIP2
SUBDIRS += spark7162VFD
endif

if ENABLE_PACE7241
SUBDIRS += pace7241VFD
endif

install_PYTHON =	\
	__init__.py
