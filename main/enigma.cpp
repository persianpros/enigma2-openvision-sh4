#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <libsig_comp.h>
#include <linux/dvb/version.h>

#include <lib/actions/action.h>
#include <lib/driver/rc.h>
#include <lib/base/ioprio.h>
#include <lib/base/e2avahi.h>
#include <lib/base/ebase.h>
#include <lib/base/eenv.h>
#include <lib/base/eerror.h>
#include <lib/base/init.h>
#include <lib/base/init_num.h>
#include <lib/base/nconfig.h>
#include <lib/gdi/gmaindc.h>
#include <lib/gdi/glcddc.h>
#include <lib/gdi/grc.h>
#ifdef ENABLE_QBOXHD
#include <lib/gdi/sensewheel.h>
#endif
#ifdef ENABLE_QBOXHDMINI
#include <lib/gdi/lpcqbox.h>
#endif
#include <lib/gdi/epng.h>
#include <lib/gdi/font.h>
#include <lib/gui/ebutton.h>
#include <lib/gui/elabel.h>
#include <lib/gui/elistboxcontent.h>
#include <lib/gui/ewidget.h>
#include <lib/gui/ewidgetdesktop.h>
#include <lib/gui/ewindow.h>
#include <lib/gui/evideo.h>
#include <lib/python/connections.h>
#include <lib/python/python.h>
#include <lib/python/pythonconfig.h>
#include <lib/service/servicepeer.h>
// vfd class
#include <lib/driver/vfd.h>
#include "bsod.h"
#include "version_info.h"

#include <Python.h>

#ifdef OBJECT_DEBUG
int object_total_remaining;

void object_dump()
{
	printf("%d items left\n", object_total_remaining);
}
#endif

static eWidgetDesktop *wdsk, *lcddsk;
#ifdef ENABLE_QBOXHD
static eQBOXSenseWheel *sensewheel;
#endif
#ifdef ENABLE_QBOXHDMINI
static eQBOXFrontButton *frontbutton;
#endif
static int prev_ascii_code;

int getPrevAsciiCode()
{
	int ret = prev_ascii_code;
	prev_ascii_code = 0;
	return ret;
}

void keyEvent(const eRCKey &key)
{
	static eRCKey last(0, 0, 0);
	static int num_repeat;
	static int long_press_emulation_pushed = false;
	static time_t long_press_emulation_start = 0;

	ePtr<eActionMap> ptr;
	eActionMap::getInstance(ptr);

	int flags = key.flags;
	int long_press_emulation_key = eConfigManager::getConfigIntValue("config.usage.long_press_emulation_key");
	if ((long_press_emulation_key > 0) && (key.code == long_press_emulation_key))
	{
		long_press_emulation_pushed = true;
		long_press_emulation_start = time(NULL);
		last = key;
		return;
	}

	if (long_press_emulation_pushed && (time(NULL) - long_press_emulation_start < 10) && (key.producer == last.producer))
	{
		// emit make-event first
		ptr->keyPressed(key.producer->getIdentifier(), key.code, key.flags);
		// then setup condition for long-event
		num_repeat = 3;
		last = key;
		flags = eRCKey::flagRepeat;
	}

	if ((key.code == last.code) && (key.producer == last.producer) && flags & eRCKey::flagRepeat)
		num_repeat++;
	else
	{
		num_repeat = 0;
		last = key;
	}

	if (num_repeat == 4)
	{
#ifdef ENABLE_QBOXHD
		ptr->keyPressed(key.producer->getIdentifier(), key.producer->getRCIdentifier(), key.code, eRCKey::flagLong);
#else
		ptr->keyPressed(key.producer->getIdentifier(), key.code, eRCKey::flagLong);
#endif
		num_repeat++;
	}

	if (key.flags & eRCKey::flagAscii)
	{
		prev_ascii_code = key.code;
#ifdef ENABLE_QBOXHD
		ptr->keyPressed(key.producer->getIdentifier(), key.producer->getRCIdentifier(), 510 /* faked KEY_ASCII */, 0);
#else
		ptr->keyPressed(key.producer->getIdentifier(), 510 /* faked KEY_ASCII */, 0);
#endif
	}
	else
#ifdef ENABLE_QBOXHD
		ptr->keyPressed(key.producer->getIdentifier(), key.producer->getRCIdentifier(), key.code, key.flags);
#else
		ptr->keyPressed(key.producer->getIdentifier(), key.code, flags);
#endif
	long_press_emulation_pushed = false;
}

/************************************************/
#include <lib/components/scan.h>
#include <lib/dvb/idvb.h>
#include <lib/dvb/dvb.h>
#include <lib/dvb/db.h>
#include <lib/dvb/dvbtime.h>
#include <lib/dvb/epgcache.h>
#include <lib/dvb/epgtransponderdatareader.h>

/* Defined in eerror.cpp */
void setDebugTime(int level);

class eMain: public eApplication, public sigc::trackable
{
	eInit init;
	ePythonConfigQuery config;

	ePtr<eDVBDB> m_dvbdb;
	ePtr<eDVBResourceManager> m_mgr;
	ePtr<eDVBLocalTimeHandler> m_locale_time_handler;
	ePtr<eEPGCache> m_epgcache;
	ePtr<eEPGTransponderDataReader> m_epgtransponderdatareader;

public:
	eMain()
	{
		e2avahi_init(this);
		init_servicepeer();
		init.setRunlevel(eAutoInitNumbers::main);
		/* TODO: put into init */
		m_dvbdb = new eDVBDB();
		m_mgr = new eDVBResourceManager();
		m_locale_time_handler = new eDVBLocalTimeHandler();
		m_epgcache = new eEPGCache();
		m_epgtransponderdatareader = new eEPGTransponderDataReader();
		m_mgr->setChannelList(m_dvbdb);
	}

	~eMain()
	{
		m_dvbdb->saveServicelist();
		m_mgr->releaseCachedChannel();
		done_servicepeer();
		e2avahi_close();
	}
};

int exit_code;

void quitMainloop(int exitCode)
{
#ifdef ENABLE_QBOXHDMINI
	FILE *f = fopen("/proc/stb/lpc/was_timer_wakeup", "w");
#else
	FILE *f = fopen("/proc/stb/fp/was_timer_wakeup", "w");
#endif
	if (f)
	{
		fprintf(f, "%d", 0);
		fclose(f);
	}
	else
	{
		int fd = open("/dev/dbox/fp0", O_WRONLY);
		if (fd >= 0)
		{
			if (ioctl(fd, 10 /*FP_CLEAR_WAKEUP_TIMER*/) < 0)
				eDebug("[quitMainloop] FP_CLEAR_WAKEUP_TIMER failed: %m");
			close(fd);
		}
		else
			eDebug("[quitMainloop] open /dev/dbox/fp0 for wakeup timer clear failed: %m");
	}
	exit_code = exitCode;
	eApp->quit(0);
}

void pauseInit()
{
	eInit::pauseInit();
}

void resumeInit()
{
	eInit::resumeInit();
}

static void sigterm_handler(int num)
{
	quitMainloop(128 + num);
}

void catchTermSignal()
{
	struct sigaction act;

	act.sa_handler = sigterm_handler;
	act.sa_flags = SA_RESTART;

	if (sigemptyset(&act.sa_mask) == -1)
		perror("sigemptyset");
	if (sigaction(SIGTERM, &act, 0) == -1)
		perror("SIGTERM");
}

int main(int argc, char **argv)
{
#ifdef MEMLEAK_CHECK
	atexit(DumpUnfreed);
#endif

#ifdef OBJECT_DEBUG
	atexit(object_dump);
#endif

	// Clear LD_PRELOAD so that shells and processes launched by Enigma2 can pass on file handles and pipes
	unsetenv("LD_PRELOAD");

	// set pythonpath if unset
	setenv("PYTHONPATH", eEnv::resolve("${libdir}/enigma2/python").c_str(), 0);
	printf("PYTHONPATH: %s\n", getenv("PYTHONPATH"));
	printf("DVB_API_VERSION %d DVB_API_VERSION_MINOR %d\n", DVB_API_VERSION, DVB_API_VERSION_MINOR);

	// get enigma2 debug level settings
#if PY_MAJOR_VERSION >= 3
	debugLvl = getenv("ENIGMA_DEBUG_LVL") ? atoi(getenv("ENIGMA_DEBUG_LVL")) : 4;
#else
	debugLvl = getenv("ENIGMA_DEBUG_LVL") ? atoi(getenv("ENIGMA_DEBUG_LVL")) : 3;
#endif
	if (debugLvl < 0)
		debugLvl = 0;
	printf("ENIGMA_DEBUG_LVL=%d\n", debugLvl);
	if (getenv("ENIGMA_DEBUG_TIME"))
		setDebugTime(atoi(getenv("ENIGMA_DEBUG_TIME")));

	ePython python;
	eMain main;

	ePtr<gMainDC> my_dc;
	gMainDC::getInstance(my_dc);

	//int double_buffer = my_dc->haveDoubleBuffering();

	ePtr<gLCDDC> my_lcd_dc;
	gLCDDC::getInstance(my_lcd_dc);


		/* ok, this is currently hardcoded for arabic. */
			/* some characters are wrong in the regular font, force them to use the replacement font */
	for (int i = 0x60c; i <= 0x66d; ++i)
		eTextPara::forceReplacementGlyph(i);
	eTextPara::forceReplacementGlyph(0xfdf2);
	for (int i = 0xfe80; i < 0xff00; ++i)
		eTextPara::forceReplacementGlyph(i);

#ifdef ENABLE_QBOXHD
	unsigned int xres, yres, bpp;
	/* Read from FrameBuffer the resolution */
	if (my_dc->fb->getfbResolution( &xres, &yres, &bpp) < 0)
		eFatal("Framebuffer Error");
	eWidgetDesktop dsk(eSize(xres, yres));
// 	eWidgetDesktop dsk(eSize(720, 576));
	eWidgetDesktop dsk_lcd(eSize(DISPLAY_WIDTH, DISPLAY_HEIGHT));
#else
	eWidgetDesktop dsk(my_dc->size());
	eWidgetDesktop dsk_lcd(my_lcd_dc->size());
#endif

	dsk.setStyleID(0);
#ifdef HAVE_GRAPHLCD
	dsk_lcd.setStyleID(my_lcd_dc->size().width() == 320 ? 1 : 2);
#else
	dsk_lcd.setStyleID(my_lcd_dc->size().width() == 96 ? 2 : 1);
#endif

/*	if (double_buffer)
	{
		eDebug("[MAIN] - double buffering found, enable buffered graphics mode.");
		dsk.setCompositionMode(eWidgetDesktop::cmBuffered);
	} */

	wdsk = &dsk;
	lcddsk = &dsk_lcd;

	dsk.setDC(my_dc);
	dsk_lcd.setDC(my_lcd_dc);

	dsk.setBackgroundColor(gRGB(0,0,0,0xFF));

		/* redrawing is done in an idle-timer, so we have to set the context */
	dsk.setRedrawTask(main);
	dsk_lcd.setRedrawTask(main);


	eDebug("[MAIN] Loading spinners...");

	{
		int i;
#define MAX_SPINNER 64
		ePtr<gPixmap> wait[MAX_SPINNER];
		for (i=0; i<MAX_SPINNER; ++i)
		{
			char filename[64];
			std::string rfilename;
			snprintf(filename, sizeof(filename), "${datadir}/enigma2/skin_default/spinner/wait%d.png", i + 1);
			rfilename = eEnv::resolve(filename);

			if (::access(rfilename.c_str(), R_OK) < 0)
				break;

			loadImage(wait[i], rfilename.c_str());
			if (!wait[i])
			{
				eDebug("[MAIN] failed to load %s: %m", rfilename.c_str());
				break;
			}
		}
		eDebug("[MAIN] found %d spinner!", i);
		if (i)
			my_dc->setSpinner(eRect(ePoint(100, 100), wait[0]->size()), wait, i);
		else
			my_dc->setSpinner(eRect(100, 100, 0, 0), wait, 1);
	}

	gRC::getInstance()->setSpinnerDC(my_dc);

	eRCInput::getInstance()->keyEvent.connect(sigc::ptr_fun(&keyEvent));
// initialise the vfd class
	evfd * vfd = new evfd;
	vfd->init();
	delete vfd;

	printf("[MAIN] executing main\n");

#ifdef ENABLE_QBOXHD
	/* SenseWheel*/
	sensewheel = new eQBOXSenseWheel();
#endif
#ifdef ENABLE_QBOXHDMINI
	/* FrontButton*/
	frontbutton = new eQBOXFrontButton();
#endif

	bsodCatchSignals();
	catchTermSignal();

	setIoPrio(IOPRIO_CLASS_BE, 3);

	/* start at full size */
	eVideoWidget::setFullsize(true);

	python.execFile(eEnv::resolve("${libdir}/enigma2/python/StartEnigma.py").c_str());

	/* restore both decoders to full size */
	eVideoWidget::setFullsize(true);

	if (exit_code == 5) /* python crash */
	{
		eDebug("[MAIN] (exit code 5)");
		bsodFatal(0);
	}

#ifdef ENABLE_QBOXHD
	if (exit_code == 6) /* terminated by signal */
	{
		eDebug("(exit code 6)");
		bsodFatal("enigma2, signal");
	}
#endif

	dsk.paint();
	dsk_lcd.paint();

	{
		gPainter p(my_lcd_dc);
#ifdef ENABLE_QBOXHD
		p.resetClip(eRect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT));
#else
		p.resetClip(eRect(ePoint(0, 0), my_lcd_dc->size()));
#endif
		p.clear();
		p.flush();
	}

	return exit_code;
}

eWidgetDesktop *getDesktop(int which)
{
	return which ? lcddsk : wdsk;
}

eApplication *getApplication()
{
	return eApp;
}

void runMainloop()
{
	catchTermSignal();
	eApp->runLoop();
}

const char *getEnigmaVersionString()
{
	return enigma2_version;
}

const char *getBoxType()
{
	return BOXTYPE;
}

const char *getBoxBrand()
{
	return BOXBRAND;
}

const char *getE2Rev()
{
	return E2REV;
}

const char *getPyExt()
{
	return PYEXT;
}

#include <malloc.h>

void dump_malloc_stats(void)
{
#ifdef __GLIBC__
	struct mallinfo mi = mallinfo();
	eDebug("[ENIGMA] MALLOC: %d total", mi.uordblks);
#else
	eDebug("[ENIGMA] MALLOC: info not exposed");
#endif
}
