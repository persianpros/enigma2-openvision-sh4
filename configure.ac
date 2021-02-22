AC_INIT([enigma2],[10],[openvision.tech])
AM_INIT_AUTOMAKE([dist-bzip2 no-define tar-pax -Wno-portability])
AC_CONFIG_HEADERS([enigma2_config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])
AC_OPENMP()

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PKG_SWIG
AX_SWIG_ENABLE_CXX
AX_SWIG_PYTHON
AX_PTHREAD

TUXBOX_APPS_DVB

AM_CONDITIONAL(HAVE_GIT_DIR, test -d "$srcdir/.git")
AM_CONDITIONAL(HAVE_FAKE_GIT_DIR, test -f "$srcdir/.git/last_commit_info")

AC_ARG_WITH(sh4stb,
	AC_HELP_STRING([--with-sh4stb], [use SH4 STB]),
	[[with_sh4stb=$withval]],
	[[with_sh4stb=no]]
)
AM_CONDITIONAL(HAVE_SH4STB, test x"$with_sh4stb" = xyes)
if test x"$with_sh4stb" = xyes ; then
	AC_DEFINE(HAVE_SH4STB, 1,[Enables SH4 STB support])
fi

AC_ARG_WITH(cuberevostb,
	AC_HELP_STRING([--with-cuberevostb], [use CubeRevo STB]),
	[[with_cuberevostb=$withval]],
	[[with_cuberevostb=no]]
)
AM_CONDITIONAL(HAVE_CubeRevoSTB, test x"$with_cuberevostb" = xyes)
if test x"$with_cuberevostb" = xyes ; then
	AC_DEFINE(HAVE_CubeRevoSTB, 1,[Enables CubeRevo STB support])
fi

AC_ARG_ENABLE(adb_box,
	[  --enable-adb_box            enable adb_box stuff],
	[AC_DEFINE(ENABLE_ADB_BOX, 1, [enable adb_box stuff])])
AM_CONDITIONAL(ENABLE_ADB_BOX, test "$enable_adb_box" = "yes")
if test "$enable_adb_box" = "yes"; then
	AC_DEFINE(ENABLE_ADB_BOX, 1, [enable adb_box stuff])
fi

AC_ARG_ENABLE(adb_2850,
	[  --enable-adb_2850            enable adb_2850 stuff],
	[AC_DEFINE(ENABLE_ADB_2850, 1, [enable adb_2850 stuff])])
AM_CONDITIONAL(ENABLE_ADB_2850, test "$enable_adb_2850" = "yes")
if test "$enable_adb_2850" = "yes"; then
	AC_DEFINE(ENABLE_ADB_2850, 1, [enable adb_2850 stuff])
fi

AC_ARG_ENABLE(arivalink200,
	[  --enable-arivalink200            enable arivalink200 stuff],
	[AC_DEFINE(ENABLE_ARIVALINK200, 1, [enable arivalink200 stuff])])
AM_CONDITIONAL(ENABLE_ARIVALINK200, test "$enable_arivalink200" = "yes")
if test "$enable_arivalink200" = "yes"; then
	AC_DEFINE(ENABLE_ARIVALINK200, 1, [enable arivalink200 stuff])
fi

AC_ARG_ENABLE(atemio520,
	[  --enable-atemio520            enable atemio520 stuff],
	[AC_DEFINE(ENABLE_ATEMIO520, 1, [enable atemio520 stuff])])
AM_CONDITIONAL(ENABLE_ATEMIO520, test "$enable_atemio520" = "yes")
if test "$enable_atemio520" = "yes"; then
	AC_DEFINE(ENABLE_ATEMIO520, 1, [enable atemio520 stuff])
fi

AC_ARG_ENABLE(atemio530,
	[  --enable-atemio530            enable atemio530 stuff],
	[AC_DEFINE(ENABLE_ATEMIO520, 1, [enable atemio530 stuff])])
AM_CONDITIONAL(ENABLE_ATEMIO530, test "$enable_atemio530" = "yes")
if test "$enable_atemio530" = "yes"; then
	AC_DEFINE(ENABLE_ATEMIO520, 1, [enable atemio530 stuff])
fi

AC_ARG_ENABLE(atevio7500,
	[  --enable-atevio7500            enable atevio7500 stuff],
	[AC_DEFINE(ENABLE_ATEVIO7500, 1, [enable atevio7500 stuff])])
AM_CONDITIONAL(ENABLE_ATEVIO7500, test "$enable_atevio7500" = "yes")
if test "$enable_atevio7500" = "yes"; then
	AC_DEFINE(ENABLE_ATEVIO7500, 1, [enable atevio7500 stuff])
fi

AC_ARG_ENABLE(cuberevo,
	[  --enable-cuberevo            enable cuberevo stuff],
	[AC_DEFINE(ENABLE_CUBEREVO, 1, [enable cuberevo stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO,test "$enable_cuberevo" = "yes")
if test "$enable_cuberevo" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO, 1, [enable cuberevo stuff])
fi

AC_ARG_ENABLE(cuberevo_2000hd,
	[  --enable-cuberevo_2000hd            enable cuberevo_2000hd stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_2000HD, 1, [enable cuberevo_2000hd stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_2000HD, test "$enable_cuberevo_2000hd" = "yes")
if test "$enable_cuberevo_2000hd" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_2000HD, 1, [enable cuberevo_2000hd stuff])
fi

AC_ARG_ENABLE(cuberevo_250hd,
	[  --enable-cuberevo_250hd            enable cuberevo_250hd stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_250HD, 1, [enable cuberevo_250hd stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_250HD, test "$enable_cuberevo_250hd" = "yes")
if test "$enable_cuberevo_250hd" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_250HD, 1, [enable cuberevo_250hd stuff])
fi

AC_ARG_ENABLE(cuberevo_3000hd,
	[  --enable-cuberevo_3000hd            enable cuberevo_3000hd stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_3000HD, 1, [enable cuberevo_3000hd stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_3000HD, test "$enable_cuberevo_3000hd" = "yes")
if test "$enable_cuberevo_3000hd" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_3000HD, 1, [enable cuberevo_3000hd stuff])
fi

AC_ARG_ENABLE(cuberevo_9500hd,
	[  --enable-cuberevo_9500hd            enable cuberevo_9500hd stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_9500HD, 1, [enable cuberevo_9500hd stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_9500HD, test "$enable_cuberevo_9500hd" = "yes")
if test "$enable_cuberevo_9500hd" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_9500HD, 1, [enable cuberevo_9500hd stuff])
fi

AC_ARG_ENABLE(cuberevo_mini,
	[  --enable-cuberevo_mini            enable cuberevo_mini stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_MINI, 1, [enable cuberevo_mini stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_MINI, test "$enable_cuberevo_mini" = "yes")
if test "$enable_cuberevo_mini" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_MINI, 1, [enable cuberevo_mini stuff])
fi

AC_ARG_ENABLE(cuberevo_mini2,
	[  --enable-cuberevo_mini2            enable cuberevo_mini2 stuff],
	[AC_DEFINE(ENABLE_CUBEREVO_MINI2, 1, [enable cuberevo_mini2 stuff])])
AM_CONDITIONAL(ENABLE_CUBEREVO_MINI2, test "$enable_cuberevo_mini2" = "yes")
if test "$enable_cuberevo_mini2" = "yes"; then
	AC_DEFINE(ENABLE_CUBEREVO_MINI2, 1, [enable cuberevo_mini2 stuff])
fi

AC_ARG_ENABLE(forever_2424hd,
	[  --enable-forever_2424hd            enable forever_2424hd stuff],
	[AC_DEFINE(ENABLE_FOREVER2424HD, 1, [enable forever_2424hd stuff])])
AM_CONDITIONAL(ENABLE_FOREVER2424HD, test "$enable_forever_2424hd" = "yes")
if test "$enable_forever_2424hd" = "yes"; then
	AC_DEFINE(ENABLE_FOREVER2424HD, 1, [enable forever_2424hd stuff])
fi

AC_ARG_ENABLE(forever_3434hd,
	[  --enable-forever_3434hd            enable forever_3434hd stuff],
	[AC_DEFINE(ENABLE_FOREVER3434HD, 1, [enable forever_3434hd stuff])])
AM_CONDITIONAL(ENABLE_FOREVER3434HD, test "$enable_forever_3434hd" = "yes")
if test "$enable_forever_3434hd" = "yes"; then
	AC_DEFINE(ENABLE_FOREVER3434HD, 1, [enable forever_3434hd stuff])
fi

AC_ARG_ENABLE(forever_9898hd,
	[  --enable-forever_9898hd            enable forever_9898hd stuff],
	[AC_DEFINE(ENABLE_FOREVER9898HD, 1, [enable forever_9898hd stuff])])
AM_CONDITIONAL(ENABLE_FOREVER9898HD, test "$enable_forever_9898hd" = "yes")
if test "$enable_forever_9898hd" = "yes"; then
	AC_DEFINE(ENABLE_FOREVER9898HD, 1, [enable forever_9898hd stuff])
fi

AC_ARG_ENABLE(forever_nanosmart,
	[  --enable-forever_nanosmart            enable forever_nanosmart stuff],
	[AC_DEFINE(ENABLE_FOREVERNANOSMART, 1, [enable forever_nanosmart stuff])])
AM_CONDITIONAL(ENABLE_FOREVERNANOSMART, test "$enable_forever_nanosmart" = "yes")
if test "$enable_forever_nanosmart" = "yes"; then
	AC_DEFINE(ENABLE_FOREVERNANOSMART, 1, [enable forever_nanosmart stuff])
fi

AC_ARG_ENABLE(fortis_hdbox,
	[  --enable-fortis_hdbox            enable fortis_hdbox stuff],
	[AC_DEFINE(ENABLE_FORTIS_HDBOX, 1, [enable fortis_hdbox stuff])])
AM_CONDITIONAL(ENABLE_FORTIS_HDBOX, test "$enable_fortis_hdbox" = "yes")
if test "$enable_fortis_hdbox" = "yes"; then
	AC_DEFINE(ENABLE_FORTIS_HDBOX, 1, [enable fortis_hdbox stuff])
fi

AC_ARG_ENABLE(hl101,
	[  --enable-hl101            enable hl101 stuff],
	[AC_DEFINE(ENABLE_HL101, 1, [enable hl101 stuff])])
AM_CONDITIONAL(ENABLE_HL101, test "$enable_hl101" = "yes")
if test "$enable_hl101" = "yes"; then
	AC_DEFINE(ENABLE_HL101, 1, [enable hl101 stuff])
fi

AC_ARG_ENABLE(opt9600,
	[  --enable-opt9600            enable opt9600 stuff],
	[AC_DEFINE(ENABLE_OPT9600, 1, [enable opt9600 stuff])])
AM_CONDITIONAL(ENABLE_OPT9600, test "$enable_opt9600" = "yes")
if test "$enable_opt9600" = "yes"; then
	AC_DEFINE(ENABLE_OPT9600, 1, [enable opt9600 stuff])
fi

AC_ARG_ENABLE(hs7110,
	[  --enable-hs7110            enable hs7110 stuff],
	[AC_DEFINE(ENABLE_HS7110, 1, [enable hs7110 stuff])])
AM_CONDITIONAL(ENABLE_HS7110, test "$enable_hs7110" = "yes")
if test "$enable_hs7110" = "yes"; then
	AC_DEFINE(ENABLE_HS7110, 1, [enable hs7110 stuff])
fi

AC_ARG_ENABLE(hs7119,
	[  --enable-hs7119            enable hs7119 stuff],
	[AC_DEFINE(ENABLE_HS7119, 1, [enable hs7119 stuff])])
AM_CONDITIONAL(ENABLE_HS7119, test "$enable_hs7119" = "yes")
if test "$enable_hs7119" = "yes"; then
	AC_DEFINE(ENABLE_HS7119, 1, [enable hs7119 stuff])
fi

AC_ARG_ENABLE(hs7420,
	[  --enable-hs7420            enable hs7420 stuff],
	[AC_DEFINE(ENABLE_HS7420, 1, [enable hs7420 stuff])])
AM_CONDITIONAL(ENABLE_HS7420, test "$enable_hs7420" = "yes")
if test "$enable_hs7420" = "yes"; then
	AC_DEFINE(ENABLE_HS7420, 1, [enable hs7420 stuff])
fi

AC_ARG_ENABLE(hs7429,
	[  --enable-hs7429            enable hs7429 stuff],
	[AC_DEFINE(ENABLE_HS7429, 1, [enable hs7429 stuff])])
AM_CONDITIONAL(ENABLE_HS7429, test "$enable_hs7429" = "yes")
if test "$enable_hs7429" = "yes"; then
	AC_DEFINE(ENABLE_HS7429, 1, [enable hs7429 stuff])
fi

AC_ARG_ENABLE(hs7810a,
	[  --enable-hs7810a            enable hs7810a stuff],
	[AC_DEFINE(ENABLE_HS7810A, 1, [enable hs7810a stuff])])
AM_CONDITIONAL(ENABLE_HS7810A, test "$enable_hs7810a" = "yes")
if test "$enable_hs7810a" = "yes"; then
	AC_DEFINE(ENABLE_HS7810A, 1, [enable hs7810a stuff])
fi

AC_ARG_ENABLE(hs7819,
	[  --enable-hs7819            enable hs7819 stuff],
	[AC_DEFINE(ENABLE_HS7819, 1, [enable hs7819 stuff])])
AM_CONDITIONAL(ENABLE_HS7819, test "$enable_hs7819" = "yes")
if test "$enable_hs7819" = "yes"; then
	AC_DEFINE(ENABLE_HS7819, 1, [enable hs7819 stuff])
fi

AC_ARG_ENABLE(ipbox55,
	[  --enable-ipbox55            enable ipbox55 stuff],
	[AC_DEFINE(ENABLE_IPBOX55, 1, [enable ipbox55 stuff])])
AM_CONDITIONAL(ENABLE_IPBOX55, test "$enable_ipbox55" = "yes")
if test "$enable_ipbox55" = "yes"; then
	AC_DEFINE(ENABLE_IPBOX55, 1, [enable ipbox55 stuff])
fi

AC_ARG_ENABLE(ipbox99,
	[  --enable-ipbox99            enable ipbox99 stuff],
	[AC_DEFINE(ENABLE_IPBOX99, 1, [enable ipbox99 stuff])])
AM_CONDITIONAL(ENABLE_IPBOX99, test "$enable_ipbox99" = "yes")
if test "$enable_ipbox99" = "yes"; then
	AC_DEFINE(ENABLE_IPBOX99, 1, [enable ipbox99 stuff])
fi

AC_ARG_ENABLE(ipbox9900,
	[  --enable-ipbox9900            enable ipbox9900 stuff],
	[AC_DEFINE(ENABLE_IPBOX9900, 1, [enable ipbox9900 stuff])])
AM_CONDITIONAL(ENABLE_IPBOX9900, test "$enable_ipbox9900" = "yes")
if test "$enable_ipbox9900" = "yes"; then
	AC_DEFINE(ENABLE_IPBOX9900, 1, [enable ipbox9900 stuff])
fi

AC_ARG_ENABLE(octagon1008,
	[  --enable-octagon1008            enable octagon1008 stuff],
	[AC_DEFINE(ENABLE_OCTAGON1008, 1, [enable octagon1008 stuff])])
AM_CONDITIONAL(ENABLE_OCTAGON1008, test "$enable_octagon1008" = "yes")
if test "$enable_octagon1008" = "yes"; then
	AC_DEFINE(ENABLE_OCTAGON1008, 1, [enable octagon1008 stuff])
fi

AC_ARG_ENABLE(pace7241,
	[  --enable-pace7241            enable pace7241 stuff],
	[AC_DEFINE(ENABLE_PACE7241, 1, [enable pace7241 stuff])])
AM_CONDITIONAL(ENABLE_PACE7241, test "$enable_pace7241" = "yes")
if test "$enable_pace7241" = "yes"; then
	AC_DEFINE(ENABLE_PACE7241, 1, [enable pace7241 stuff])
fi

AC_ARG_ENABLE(qboxhd,
	[  --enable-qboxhd            enable qboxhd stuff],
	[AC_DEFINE(ENABLE_QBOXHD, 1, [enable qboxhd stuff])])
AM_CONDITIONAL(ENABLE_QBOXHD, test "$enable_qboxhd" = "yes")
if test "$enable_qboxhd" = "yes"; then
	AC_DEFINE(ENABLE_QBOXHD, 1, [enable qboxhd stuff])
fi

AC_ARG_ENABLE(qboxhd_mini,
	[  --enable-qboxhd_mini            enable qboxhd_mini stuff],
	[AC_DEFINE(ENABLE_QBOXHDMINI, 1, [enable qboxhd_mini stuff])])
AM_CONDITIONAL(ENABLE_QBOXHDMINI, test "$enable_qboxhd_mini" = "yes")
if test "$enable_qboxhd_mini" = "yes"; then
	AC_DEFINE(ENABLE_QBOXHDMINI, 1, [enable qboxhd_mini stuff])
fi

AC_ARG_ENABLE(sagemcom88,
	[  --enable-sagemcom88            enable sagemcom88 stuff],
	[AC_DEFINE(ENABLE_SAGEMCOM88, 1, [enable sagemcom88 stuff])])
AM_CONDITIONAL(ENABLE_SAGEMCOM88, test "$enable_sagemcom88" = "yes")
if test "$enable_sagemcom88" = "yes"; then
	AC_DEFINE(ENABLE_SAGEMCOM88, 1, [enable sagemcom88 stuff])
fi

AC_ARG_ENABLE(spark,
	[  --enable-spark            enable spark stuff],
	[AC_DEFINE(ENABLE_SPARK, 1, [enable spark stuff])])
AM_CONDITIONAL(ENABLE_SPARK, test "$enable_spark" = "yes")
if test "$enable_spark" = "yes"; then
	AC_DEFINE(ENABLE_SPARK, 1, [enable spark stuff])
fi

AC_ARG_ENABLE(spark7162,
	[  --enable-spark7162            enable spark7162 stuff],
	[AC_DEFINE(ENABLE_SPARK7162, 1, [enable spark7162 stuff])])
AM_CONDITIONAL(ENABLE_SPARK7162, test "$enable_spark7162" = "yes")
if test "$enable_spark7162" = "yes"; then
	AC_DEFINE(ENABLE_SPARK7162, 1, [enable spark7162 stuff])
fi

AC_ARG_ENABLE(tf7700,
	[  --enable-tf7700            enable tf7700 stuff],
	[AC_DEFINE(ENABLE_TF7700, 1, [enable tf7700 stuff])])
AM_CONDITIONAL(ENABLE_TF7700, test "$enable_tf7700" = "yes")
if test "$enable_tf7700" = "yes"; then
	AC_DEFINE(ENABLE_TF7700, 1, [enable tf7700 stuff])
fi

AC_ARG_ENABLE(ufc960,
	[  --enable-ufc960            enable ufc960 stuff],
	[AC_DEFINE(ENABLE_UFC960, 1, [enable ufc960 stuff])])
AM_CONDITIONAL(ENABLE_UFC960, test "$enable_ufc960" = "yes")
if test "$enable_ufc960" = "yes"; then
	AC_DEFINE(ENABLE_UFC960, 1, [enable ufc960 stuff])
fi

AC_ARG_ENABLE(ufs910,
	[  --enable-ufs910            enable ufs910 stuff],
	[AC_DEFINE(ENABLE_UFS910, 1, [enable ufs910 stuff])])
AM_CONDITIONAL(ENABLE_UFS910, test "$enable_ufs910" = "yes")
if test "$enable_ufs910" = "yes"; then
	AC_DEFINE(ENABLE_UFS910, 1, [enable ufs910 stuff])
fi

AC_ARG_ENABLE(ufs912,
	[  --enable-ufs912            enable ufs912 stuff],
	[AC_DEFINE(ENABLE_UFS912, 1, [enable ufs912 stuff])])
AM_CONDITIONAL(ENABLE_UFS912, test "$enable_ufs912" = "yes")
if test "$enable_ufs912" = "yes"; then
	AC_DEFINE(ENABLE_UFS912, 1, [enable ufs912 stuff])
fi

AC_ARG_ENABLE(ufs913,
	[  --enable-ufs913            enable ufs913 stuff],
	[AC_DEFINE(ENABLE_UFS913, 1, [enable ufs913 stuff])])
AM_CONDITIONAL(ENABLE_UFS913, test "$enable_ufs913" = "yes")
if test "$enable_ufs913" = "yes"; then
	AC_DEFINE(ENABLE_UFS913, 1, [enable ufs913 stuff])
fi

AC_ARG_ENABLE(ufs922,
	[  --enable-ufs922            enable ufs922 stuff],
	[AC_DEFINE(ENABLE_UFS922, 1, [enable ufs922 stuff])])
AM_CONDITIONAL(ENABLE_UFS922, test "$enable_ufs922" = "yes")
if test "$enable_ufs922" = "yes"; then
	AC_DEFINE(ENABLE_UFS922, 1, [enable ufs922 stuff])
fi

AC_ARG_ENABLE(vip1_v1,
	[  --enable-vip1_v1            enable vip1_v1 stuff],
	[AC_DEFINE(ENABLE_VIP1_V1, 1, [enable vip1_v1 stuff])])
AM_CONDITIONAL(ENABLE_VIP1_V1, test "$enable_vip1_v1" = "yes")
if test "$enable_vip1_v1" = "yes"; then
	AC_DEFINE(ENABLE_VIP1_V1, 1, [enable vip1_v1 stuff])
fi

AC_ARG_ENABLE(vip1_v2,
	[  --enable-vip1_v2            enable vip1_v2 stuff],
	[AC_DEFINE(ENABLE_VIP1_V2, 1, [enable vip1_v2 stuff])])
AM_CONDITIONAL(ENABLE_VIP1_V2, test "$enable_vip1_v2" = "yes")
if test "$enable_vip1_v2" = "yes"; then
	AC_DEFINE(ENABLE_VIP1_V2, 1, [enable vip1_v2 stuff])
fi

AC_ARG_ENABLE(vip2,
	[  --enable-vip2            enable vip2 stuff],
	[AC_DEFINE(ENABLE_VIP2, 1, [enable vip2 stuff])])
AM_CONDITIONAL(ENABLE_VIP2, test "$enable_vip2" = "yes")
if test "$enable_vip2" = "yes"; then
	AC_DEFINE(ENABLE_VIP2, 1, [enable vip2 stuff])
fi

AC_ARG_ENABLE(vitamin_hd5000,
	[  --enable-vitamin_hd5000            enable vitamin_hd5000 stuff],
	[AC_DEFINE(ENABLE_VITAMIN_HD5000, 1, [enable vitamin_hd5000 stuff])])
AM_CONDITIONAL(ENABLE_VITAMIN_HD5000, test "$enable_vitamin_hd5000" = "yes")
if test "$enable_vitamin_hd5000" = "yes"; then
	AC_DEFINE(ENABLE_VITAMIN_HD5000, 1, [enable vitamin_hd5000 stuff])
fi

dnl versions of plugins-base
PKG_CHECK_MODULES(TUXTXT, tuxbox-tuxtxt)
PKG_CHECK_MODULES(BASE, [freetype2 fribidi glib-2.0 libdvbsi++ libpng libxml-2.0 sigc++-2.0 libssl libcrypto])
PKG_CHECK_MODULES(LIBDDVD, libdreamdvd, HAVE_LIBDDVD="yes", HAVE_LIBDDVD="no")
AM_CONDITIONAL(HAVE_LIBDDVD, test "$HAVE_LIBDDVD" = "yes")
PKG_CHECK_MODULES(AVAHI, avahi-client)

AC_CHECK_LIB([udfread], [udfread_init])
AC_CHECK_LIB([dl], [dlopen], [LIBDL_LIBS="-ldl"], [AC_MSG_ERROR([Could not find libdl])])
AC_SUBST(LIBDL_LIBS)
AC_CHECK_LIB([jpeg], [jpeg_set_defaults], [LIBJPEG_LIBS="-ljpeg"], [AC_MSG_ERROR([Could not find libjpeg])])
AC_SUBST(LIBJPEG_LIBS)
AC_CHECK_LIB([ungif], [DGifOpen], [LIBGIF_LIBS="-lungif"], [AC_CHECK_LIB([gif], [DGifOpen], [LIBGIF_LIBS="-lgif"], [AC_MSG_ERROR([Could not find libgif or libungif])])])
AC_SUBST(LIBGIF_LIBS)

AC_ARG_WITH(crashlogemail,
	[  --with-crashlogemail=crash log email address],
	[CRASHLOGEMAIL="$withval"],[CRASHLOGEMAIL="crash@openvision.tech"])
AC_SUBST(CRASHLOGEMAIL)
AC_DEFINE_UNQUOTED(CRASH_EMAILADDR,"$CRASHLOGEMAIL",[crash log email address])

AC_ARG_WITH(boxtype,
	AS_HELP_STRING([--with-boxtype],[build for BOXTYPE, $withval]),
	[BOXTYPE="$withval"],[BOXTYPE=""])
AC_SUBST(BOXTYPE)
AC_DEFINE_UNQUOTED(BOXTYPE,"$BOXTYPE",[box type])

AC_ARG_WITH(boxbrand,
	AS_HELP_STRING([--with-boxbrand],[build for BOXBRAND, $withval]),
	[BOXBRAND="$withval"],[BOXBRAND=""])
AC_SUBST(BOXBRAND)
AC_DEFINE_UNQUOTED(BOXBRAND,"$BOXBRAND",[box brand])

AC_ARG_WITH(stbplatform,
	AS_HELP_STRING([--with-stbplatform],[build for STBPLATFORM, $withval]),
	[STBPLATFORM="$withval"],[STBPLATFORM=""])
AC_SUBST(STBPLATFORM)
AC_DEFINE_UNQUOTED(STBPLATFORM,"$STBPLATFORM",[stb platform])

AC_ARG_WITH(e2rev,
	AS_HELP_STRING([--with-e2rev],[value of E2REV, $withval]),
	[E2REV="$withval"],[E2REV=""])
AC_SUBST(E2REV)
AC_DEFINE_UNQUOTED(E2REV,"$E2REV",[enigma2 revision])

AC_ARG_WITH(nolcd,
	AC_HELP_STRING([--with-nolcd], [disable ascii based lcd, yes or no]),
	[[withnolcd=$withval]],
	[[withnolcd=no]]
)
if test x"$withnolcd" != xno ; then
	AC_DEFINE(NO_LCD, 1,[Define when disable an ascii based lcd device])
fi
AM_CONDITIONAL(NO_LCD, test x"$withnolcd" != xno)

AC_ARG_WITH(textlcd,
	AC_HELP_STRING([--with-textlcd], [use ascii based lcd, yes or no]),
	[[withtextlcd=$withval]],
	[[withtextlcd=no]]
)
if test x"$withtextlcd" != xno ; then
	AC_DEFINE(HAVE_TEXTLCD, 1,[Define when using an ascii based lcd device])
fi
AM_CONDITIONAL(HAVE_TEXTLCD, test x"$withtextlcd" != xno)

AC_ARG_WITH(7segment,
	AC_HELP_STRING([--with-7segment], [use 7 segment lcd, yes or no]),
	[[TEXTSKIN="7segment"]],
	[[TEXTSKIN="default"]]
)
AC_SUBST(TEXTSKIN)

AC_ARG_WITH(graphlcd,
	AC_HELP_STRING([--with-graphlcd], [use GraphLCD color display, yes or no]),
	[[withgraphlcd=$withval]],
	[[withgraphlcd=no]]
)
if test x"$withgraphlcd" != xno ; then
	AC_DEFINE(HAVE_GRAPHLCD, 1,[Define when using a GraphLCD color display device])
fi
AM_CONDITIONAL(HAVE_GRAPHLCD, test x"$withgraphlcd" != xno)

AC_ARG_WITH(lcd,
	AC_HELP_STRING([--with-lcd], [use LCD display, yes or no]),
	[[withlcd=$withval]],
	[[withlcd=no]]
)
if ! test x"$withlcd" != xno ; then
	AC_DEFINE(NO_LCD, 1,[Define when not using a LCD display device])
fi
AM_CONDITIONAL(NO_LCD, test x"$withlcd" != xno)

AC_ARG_WITH(libsdl,
	AS_HELP_STRING([--with-libsdl],[use libsdl, yes or no]),
	[with_libsdl=$withval],[with_libsdl=no])
if test "$with_libsdl" = "yes"; then
	PKG_CHECK_MODULES(LIBSDL, sdl)
fi
AM_CONDITIONAL(HAVE_LIBSDL, test "$with_libsdl" = "yes")

AC_ARG_WITH(libxine,
	AS_HELP_STRING([--with-libxine],[use libxine, yes or no]),
	[with_libxine=$withval],[with_libxine=no])
if test "$with_libxine" = "yes"; then
	PKG_CHECK_MODULES(LIBXINE, libxine)
	AC_DEFINE([WITH_XINE],[1],[Define to 1 if you have libxine])
fi
AM_CONDITIONAL(HAVE_LIBXINE, test "$with_libxine" = "yes")

AC_ARG_WITH(debug,
	AS_HELP_STRING([--without-debug],[disable debugging code]),
	[with_debug="$withval"],[with_debug="yes"])
if test "$with_debug" = "yes"; then
	AC_DEFINE([DEBUG],[1],[Define to 1 to enable debugging code])
fi

AC_ARG_WITH(memcheck,
	AS_HELP_STRING([--with-memcheck],[enable memory leak checks]),
	[with_memcheck="$withval"],[with_memcheck="no"])
if test "$with_memcheck" = "yes"; then
	AC_DEFINE([MEMLEAK_CHECK],[1],[Define to 1 to enable memory leak checks])
fi

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit)
	AC_PATH_PROG(MSGMERGE, msgmerge)
	AC_PATH_PROG(MSGUNIQ, msguniq)
	AC_PATH_PROG(MSGATTRIB, msgattrib)
	AC_PATH_PROG(XGETTEXT, xgettext)
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$MSGATTRIB" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "yes")

AC_ARG_WITH(alsa,
	AC_HELP_STRING([--with-alsa], [Enable ALSA support]),
	[[with_alsa=$withval]],
	[[with_alsa=no]]
)
if test x"$with_alsa" == xyes ; then
	AC_DEFINE(HAVE_ALSA, 1,[Enables ALSA support])
	PKG_CHECK_MODULES(ALSA, alsa)
fi

AC_ARG_WITH(alsacard,
	AC_HELP_STRING([--with-alsacard=card], [use 'card' for alsa card device, e.g. hw:0]),
	[[with_alsacard=$withval]],
	[[with_alsacard=no]]
)
if test x"$with_alsacard" != xno ; then
	AC_DEFINE_UNQUOTED(ALSA_CARD, "$withval",[Defines which alsa card to use])
fi

AC_ARG_WITH(alsamixer,
	AC_HELP_STRING([--with-alsamixer=mixername], [use alsa 'mixername' for volume control, e.g. Master]),
	[[with_alsamixer=$withval]],
	[[with_alsamixer=no]]
)
if test x"$with_alsamixer" != xno ; then
	AC_DEFINE_UNQUOTED(ALSA_VOLUME_MIXER, "$withval",[Defines which alsa mixer to use for volume control])
fi

AC_ARG_WITH(fbdev,
	AC_HELP_STRING([--with-fbdev=devicename], [use devicename for framebuffer device, e.g. /dev/fb0 ]),
	[[with_fbdev=$withval]],
	[[with_fbdev=no]]
)
if test x"$with_fbdev" != xno ; then
	AC_DEFINE_UNQUOTED(FB_DEV, "$withval", [Defines which device to use for main framebuffer (e.g. /dev/fb0)])
fi

AC_ARG_WITH(lcddev,
	AC_HELP_STRING([--with-lcddev=devicename], [use devicename for lcd framebuffer device, e.g. /dev/fb1 ]),
	[[with_lcddev=$withval]],
	[[with_lcddev=no]]
)
if test x"$with_lcddev" != xno ; then
	AC_DEFINE_UNQUOTED(LCD_DEV, "$withval", [Defines which device to use for lcd (e.g. /dev/fb1)])
fi

AC_ARG_WITH(alphablendingacceleration,
	AC_HELP_STRING([--with-alphablendingacceleration=never/always/auto], [alphablending acceleration strategy: never accelerate / always accelerate / automatically decide when to accelerate (default)]),
	[[with_alphablendingacceleration=$withval]],
	[[with_alphablendingacceleration=auto]]
)
if test x"$with_alphablendingacceleration" = xnever ; then
	AC_DEFINE_UNQUOTED(FORCE_NO_BLENDING_ACCELERATION, 1, [Do not attempt to accelerate alphablending blits])
elif test x"$with_alphablendingacceleration" = xalways ; then
	AC_DEFINE_UNQUOTED(FORCE_ALPHABLENDING_ACCELERATION, 1, [Accelerate alphablending blits])
fi

AC_ARG_WITH(accelerationthreshold,
	AC_HELP_STRING([--with-accelerationthreshold=n], [use acceleration threshold of n bytes]),
	[[with_accelerationthreshold=$withval]],
	[[with_accelerationthreshold=48000]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_ACCELERATION_THRESHOLD, $with_accelerationthreshold,[Configure threshold for accelerated surfaces (in bytes)])

AC_ARG_WITH(fillaccelerationthreshold,
	AC_HELP_STRING([--with-fillaccelerationthreshold=n], [use fill acceleration threshold of n bytes]),
	[[with_fillaccelerationthreshold=$withval]],
	[[with_fillaccelerationthreshold=80000]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_FILL_ACCELERATION_THRESHOLD, $with_fillaccelerationthreshold,[Configure threshold for accelerated fill operations (in bytes)])

AC_ARG_WITH(blitaccelerationthreshold,
	AC_HELP_STRING([--with-blitaccelerationthreshold=n], [use blit acceleration threshold of n bytes]),
	[[with_blitaccelerationthreshold=$withval]],
	[[with_blitaccelerationthreshold=0]]
)
AC_DEFINE_UNQUOTED(GFX_SURFACE_BLIT_ACCELERATION_THRESHOLD, $with_blitaccelerationthreshold,[Configure threshold for accelerated blit operations (in bytes)])

AC_ARG_WITH(accelerationaccumulation,
	AC_HELP_STRING([--with-accelerationaccumulation], [accumulate blit/fill acceleration operations]),
	[[with_accelerationaccumulation=$withval]],
	[[with_accelerationaccumulation=no]]
)
if test x"$with_accelerationaccumulation" = xyes ; then
	AC_DEFINE(SUPPORT_ACCUMULATED_ACCELERATION_OPERATIONS, 1,[Accumulate blit/fill acceleration operations])
fi

AC_ARG_WITH(subttxtabnormalptsdiffs,
	AC_HELP_STRING([--with-subttxtabnormalptsdiffs=n], [use n/90 msec diffs for subtitle and teletext abnormal pts]),
	[[with_subttxtabnormalptsdiffs=$withval]],
	[[with_subttxtabnormalptsdiffs=1800000]]
)
AC_DEFINE_UNQUOTED(SUBT_TXT_ABNORMAL_PTS_DIFFS, $with_subttxtabnormalptsdiffs,[Configure abnormal pts for subtitle and teletext])

AC_ARG_WITH(fcc,
	AC_HELP_STRING([--with-fcc], [use FCC specific codes for fast channel change]),
	[[fcc=$withval]],
	[[fcc=no]]
)
AM_CONDITIONAL(HAVE_FCC_ABILITY, test x"$with_fcc" = xyes)
if test x"$with_fcc" = xyes ; then
	AC_DEFINE(HAVE_FCC_ABILITY, 1,[use FCC specific codes for fast channel change])
fi

AC_CHECK_HEADERS([sys/klog.h])
AC_CHECK_FUNCS([klogctl])

AC_CHECK_HEADERS([shadow.h])
AC_CHECK_LIB([crypt], [crypt], [BASE_LIBS+=" -lcrypt"], [AC_MSG_ERROR([Could not find crypt])])
AC_CHECK_LIB([rt], [clock_gettime], [BASE_LIBS+=" -lrt"], [AC_MSG_ERROR([Could not find rt])])

ENIGMA2_CFLAGS="-fno-rtti -fno-exceptions -rdynamic -funwind-tables"
AC_SUBST(ENIGMA2_CFLAGS)

AX_CXX_COMPILE_STDCXX_11([ext],[mandatory])

AX_CHECK_COMPILE_FLAG([-Wattribute-alias], [CXXFLAGS="$CXXFLAGS -Wattribute-alias"])
AX_CHECK_COMPILE_FLAG([-Wattribute-alias=1], [CXXFLAGS="$CXXFLAGS -Wattribute-alias=1"])

CPPFLAGS="$CPPFLAGS $PYTHON_CPPFLAGS"
CFLAGS="$CFLAGS -Wall"
CXXFLAGS="$CXXFLAGS -Wall -Wextra \
	-Wformat=2 -Wformat-nonliteral -Wformat-security \
	-Wtrampolines \
	-Wswitch \
	-Wunused-but-set-parameter -Wuninitialized \
	-Woverlength-strings \
	-Wunsafe-loop-optimizations -Wpointer-arith \
	-Wfloat-equal -Wlogical-op \
	-Wno-error=ignored-qualifiers \
	-Wno-error=shadow -Wno-error=cast-qual \
	-Wno-error=aggregate-return -Wno-error=missing-field-initializers \
	-Wno-error=packed -Wno-error=vla -Wno-error=clobbered -Wno-error=unused-parameter \
	$BASE_CFLAGS $ENIGMA2_CFLAGS $PTHREAD_CFLAGS $OPENMP_CFLAGS $ALSA_CFLAGS"

AC_CONFIG_FILES([
Makefile
data/Makefile
data/countries/Makefile
data/display/Makefile
data/extensions/Makefile
data/fonts/Makefile
data/keymaps/Makefile
data/rc_models/Makefile
data/skin_default/Makefile
data/skin_default/menu/Makefile
data/skin_default/icons/Makefile
data/skin_default/buttons/Makefile
data/skin_default/epg/Makefile
data/skin_default/spinner/Makefile
data/skin_default/LCDIcons/Makefile
data/skin_fallback_1080/Makefile
data/skin_fallback_1080/buttons/Makefile
data/skin_fallback_1080/icons/Makefile
data/VirtualKeyBoard_Icons/Makefile
data/VirtualKeyBoard_Icons/buttonsHD/Makefile
data/VirtualKeyBoard_Icons/buttonsFHD/Makefile
include/Makefile
lib/Makefile
lib/base/eenv.cpp
lib/python/Makefile
lib/python/Components/Makefile
lib/python/Components/Converter/Makefile
lib/python/Components/Renderer/Makefile
lib/python/Components/Sources/Makefile
lib/python/Screens/Makefile
lib/python/Plugins/Makefile
lib/python/Plugins/SystemPlugins/CableScan/Makefile
lib/python/Plugins/SystemPlugins/FastChannelChange/Makefile
lib/python/Plugins/SystemPlugins/FastChannelChange/meta/Makefile
lib/python/Plugins/SystemPlugins/FastScan/Makefile
lib/python/Plugins/SystemPlugins/OSDPositionSetup/Makefile
lib/python/Plugins/SystemPlugins/OSD3DSetup/Makefile
lib/python/Plugins/SystemPlugins/HdmiCEC/Makefile
lib/python/Plugins/SystemPlugins/VideoClippingSetup/Makefile
lib/python/Plugins/Extensions/Makefile
lib/python/Plugins/Extensions/ADBVFD/Makefile
lib/python/Plugins/Extensions/ADBVFD/meta/Makefile
lib/python/Plugins/Extensions/CuberevoVFD/Makefile
lib/python/Plugins/Extensions/CuberevoVFD/meta/Makefile
lib/python/Plugins/Extensions/CutListEditor/Makefile
lib/python/Plugins/Extensions/CutListEditor/meta/Makefile
lib/python/Plugins/Extensions/DVDBurn/Makefile
lib/python/Plugins/Extensions/DVDBurn/meta/Makefile
lib/python/Plugins/Extensions/DVDPlayer/Makefile
lib/python/Plugins/Extensions/DVDPlayer/meta/Makefile
lib/python/Plugins/Extensions/fs9000VFD/Makefile
lib/python/Plugins/Extensions/fs9000VFD/meta/Makefile
lib/python/Plugins/Extensions/GraphMultiEPG/Makefile
lib/python/Plugins/Extensions/GraphMultiEPG/meta/Makefile
lib/python/Plugins/Extensions/hs7110VFD/Makefile
lib/python/Plugins/Extensions/hs7110VFD/meta/Makefile
lib/python/Plugins/Extensions/hs742xVFD/Makefile
lib/python/Plugins/Extensions/hs742xVFD/meta/Makefile
lib/python/Plugins/Extensions/hs7810aVFD/Makefile
lib/python/Plugins/Extensions/hs7810aVFD/meta/Makefile
lib/python/Plugins/Extensions/hs8200VFD/Makefile
lib/python/Plugins/Extensions/hs8200VFD/meta/Makefile
lib/python/Plugins/Extensions/hs9510VFD/Makefile
lib/python/Plugins/Extensions/hs9510VFD/meta/Makefile
lib/python/Plugins/Extensions/MediaPlayer/Makefile
lib/python/Plugins/Extensions/MediaPlayer/meta/Makefile
lib/python/Plugins/Extensions/MediaScanner/Makefile
lib/python/Plugins/Extensions/MediaScanner/meta/Makefile
lib/python/Plugins/Extensions/opt9600VFD/Makefile
lib/python/Plugins/Extensions/opt9600VFD/meta/Makefile
lib/python/Plugins/Extensions/pace7241VFD/Makefile
lib/python/Plugins/Extensions/pace7241VFD/meta/Makefile
lib/python/Plugins/Extensions/PicturePlayer/Makefile
lib/python/Plugins/Extensions/PicturePlayer/meta/Makefile
lib/python/Plugins/Extensions/PicturePlayer/data/Makefile
lib/python/Plugins/Extensions/SocketMMI/Makefile
lib/python/Plugins/Extensions/SocketMMI/meta/Makefile
lib/python/Plugins/Extensions/SocketMMI/src/Makefile
lib/python/Plugins/Extensions/sparkVFD/Makefile
lib/python/Plugins/Extensions/sparkVFD/meta/Makefile
lib/python/Plugins/Extensions/spark7162VFD/Makefile
lib/python/Plugins/Extensions/spark7162VFD/meta/Makefile
lib/python/Plugins/Extensions/TopfieldVFD/Makefile
lib/python/Plugins/Extensions/TopfieldVFD/meta/Makefile
lib/python/Plugins/SystemPlugins/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/Makefile
lib/python/Plugins/SystemPlugins/CommonInterfaceAssignment/meta/Makefile
lib/python/Plugins/SystemPlugins/DefaultServicesScanner/Makefile
lib/python/Plugins/SystemPlugins/DefaultServicesScanner/meta/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/Makefile
lib/python/Plugins/SystemPlugins/DiseqcTester/meta/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/Makefile
lib/python/Plugins/SystemPlugins/Hotplug/meta/Makefile
lib/python/Plugins/SystemPlugins/KeymapManager/Makefile
lib/python/Plugins/SystemPlugins/KeymapManager/meta/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/Makefile
lib/python/Plugins/SystemPlugins/NetworkWizard/meta/Makefile
lib/python/Plugins/SystemPlugins/OnErrorRestartService/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/Makefile
lib/python/Plugins/SystemPlugins/PositionerSetup/meta/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/Makefile
lib/python/Plugins/SystemPlugins/SatelliteEquipmentControl/meta/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/Makefile
lib/python/Plugins/SystemPlugins/Satfinder/meta/Makefile
lib/python/Plugins/SystemPlugins/SH4BoosterControl/Makefile
lib/python/Plugins/SystemPlugins/SH4BoosterControl/meta/Makefile
lib/python/Plugins/SystemPlugins/SH4OSDAdjustment/Makefile
lib/python/Plugins/SystemPlugins/SH4OSDAdjustment/meta/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/Makefile
lib/python/Plugins/SystemPlugins/SoftwareManager/meta/Makefile
lib/python/Plugins/SystemPlugins/SparkUnionTunerType/Makefile
lib/python/Plugins/SystemPlugins/SparkUnionTunerType/meta/Makefile
lib/python/Plugins/SystemPlugins/SystemOptions/Makefile
lib/python/Plugins/SystemPlugins/SystemOptions/meta/Makefile
lib/python/Plugins/SystemPlugins/TempFanControl/Makefile
lib/python/Plugins/SystemPlugins/TempFanControl/meta/Makefile
lib/python/Plugins/SystemPlugins/VFD-Icons/Makefile
lib/python/Plugins/SystemPlugins/VFD-Icons/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/Makefile
lib/python/Plugins/SystemPlugins/VideoEnhancement/meta/Makefile
lib/python/Plugins/SystemPlugins/Videomode/Makefile
lib/python/Plugins/SystemPlugins/Videomode/meta/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/Makefile
lib/python/Plugins/SystemPlugins/VideoTune/meta/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/Makefile
lib/python/Plugins/SystemPlugins/WirelessLan/meta/Makefile
lib/python/Tools/Makefile
po/Makefile
main/Makefile
tools/Makefile
tools/enigma2.sh
enigma2.pc
])
AC_OUTPUT
