#include <lib/base/cfile.h>
#include <lib/base/eerror.h>
#include <lib/dvb/volume.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <linux/dvb/version.h>
#if DVB_API_VERSION < 3
#define VIDEO_DEV "/dev/dvb/card0/video0"
#define AUDIO_DEV "/dev/dvb/card0/audio0"
#include <ost/audio.h>
#include <ost/video.h>
#else
#define VIDEO_DEV "/dev/dvb/adapter0/video0"
#define AUDIO_DEV "/dev/dvb/adapter0/audio0"
#include <linux/dvb/audio.h>
#include <linux/dvb/video.h>
#endif

#ifdef HAVE_ALSA
# ifndef ALSA_VOLUME_MIXER
#  define ALSA_VOLUME_MIXER "Master"
# endif
# ifndef ALSA_CARD
#  define ALSA_CARD "default"
# endif
#endif

eDVBVolumecontrol* eDVBVolumecontrol::instance = NULL;

eDVBVolumecontrol* eDVBVolumecontrol::getInstance()
{
	if (instance == NULL)
		instance = new eDVBVolumecontrol;
	return instance;
}

eDVBVolumecontrol::eDVBVolumecontrol()
:m_volsteps(5)
{
#ifdef HAVE_ALSA
	mainVolume = NULL;
	openMixer();
#endif
	volumeUnMute();
// dont reset volume on start
//	setVolume(100, 100);
}

void eDVBVolumecontrol::closeMixer(int fd)
{
#ifdef HAVE_ALSA
	/* we want to keep the alsa mixer */
#else
	if (fd >= 0) close(fd);
#endif
}

void eDVBVolumecontrol::setVolumeSteps(int steps)
{
	m_volsteps = steps;
}

void eDVBVolumecontrol::volumeUp(int left, int right)
{
	setVolume(leftVol + (left ? left : m_volsteps), rightVol + (right ? right : m_volsteps));
}

void eDVBVolumecontrol::volumeDown(int left, int right)
{
	setVolume(leftVol - (left ? left : m_volsteps), rightVol - (right ? right : m_volsteps));
}

int eDVBVolumecontrol::checkVolume(int vol)
{
	if (vol < 0)
		vol = 0;
	else if (vol > 100)
		vol = 100;
	return vol;
}

void eDVBVolumecontrol::setVolume(int left, int right)
{
		/* left, right is 0..100 */
	leftVol = checkVolume(left);
	rightVol = checkVolume(right);

#ifdef HAVE_ALSA
	eDebug("[eDVBVolumecontrol] Setvolume: ALSA leftVol=%d", leftVol);
	if (mainVolume)
		snd_mixer_selem_set_playback_volume_all(mainVolume, muted ? 0 : leftVol);
#else
		/* convert to -1dB steps */
	left = 63 - leftVol * 63 / 100;
	right = 63 - rightVol * 63 / 100;
		/* now range is 63..0, where 0 is loudest */
	//HACK?
	CFile::writeInt("/proc/stb/avs/0/volume", left); /* in -1dB */
#endif
}

int eDVBVolumecontrol::getVolume()
{
	return leftVol;
}

bool eDVBVolumecontrol::isMuted()
{
	return muted;
}


void eDVBVolumecontrol::volumeMute()
{
#ifdef HAVE_ALSA
	eDebug("[eDVBVolumecontrol] Setvolume: ALSA Mute");
	if (mainVolume)
		snd_mixer_selem_set_playback_volume_all(mainVolume, 0);
	muted = true;
#else
	muted = true;

	//HACK?
	CFile::writeInt("/proc/stb/audio/j1_mute", 1);
#endif
}

void eDVBVolumecontrol::volumeUnMute()
{
#ifdef HAVE_ALSA
	eDebug("[eDVBVolumecontrol] Setvolume: ALSA unMute to %d", leftVol);
	if (mainVolume)
		snd_mixer_selem_set_playback_volume_all(mainVolume, leftVol);
	muted = false;
#else
	muted = false;

	//HACK?
	CFile::writeInt("/proc/stb/audio/j1_mute", 0);
#endif
}

void eDVBVolumecontrol::volumeToggleMute()
{
	if (isMuted())
		volumeUnMute();
	else
		volumeMute();
}
