/*
 * vfd.cpp
 *
 * (c) 20?? ?
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 *
 ****************************************************************************
 *
 * VFD/LED driver for enigma2.
 *
 ****************************************************************************
 *
 * Changes
 *
 * Date     By              Description
 * --------------------------------------------------------------------------
 * 20130905 Audioniek       Code for Sparks added in.
 * 20130905 Audioniek       vfd_write_string_scrollText now uses actual
 *                          display length in stead of always 16.
 * 20131021 Audioniek       Octagon 1008 (Fortis HS9510) added.
 * 20131130 Audioniek       HDBOX (Fortis FS9000/9200) added
 * 20131210 Audioniek       Sign on string now scrolls once if longer than
 *                          displaylength.
 * 20140221 Audioniek       Fortis HS7119 and HS7819 added.
 * 20140527 Audioniek       Spark7162 spins circle on init.
 * 20150316 Audioniek       Spark7162 circle spin on init removed.
 * 20160101 Audioniek       Fortis HS7420 and HS7429 added.
 * 20170313 Audioniek       Kathrein UFS910/912 added.
 * 20190317 Audioniek       Several CubeRevo's added.
 * 20190518 Audioniek       vitamin_hd5000 added.
 * 20200417 Audioniek       adb_box added.
 * 20200508 Audioniek       pace7241 added.
 * 20200719 Audioniek       hl101, vip1_v2 and vip2_v1 added.
 * 20200828 Audioniek       Add vip1_v1, rename vip2.
 *
 ****************************************************************************/
#include <stdarg.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <ctype.h>
#include <sys/stat.h>
#include <pthread.h>

#include <lib/base/eerror.h>
#include <lib/driver/vfd.h>

#if defined (ENABLE_TF7700)
#include "../../../tools/tffpctl/frontpanel.h"
#endif

// global variables
bool startloop_running = false;
static bool icon_onoff[45];
static int led_onoff[7];
static pthread_t thread_start_loop = 0;
void *start_loop (void *arg);
bool blocked    = false;
bool requested  = false;
bool VFD_CENTER = false;
int  VFD_SCROLL = 1;  // 1=scroll once
bool scroll_loop = false;

// E2 scroll parameters
int scroll_repeat;
int scroll_delay;
int initial_scroll_delay;
int final_scroll_delay;

char chars[64];
char g_str[64];

evfd* evfd::instance = NULL;

evfd* evfd::getInstance()
{
	if (instance == NULL)
	{
		instance = new evfd;
	}
	return instance;
}

evfd::evfd()
{
	file_vfd = 0;
	memset (chars, ' ', 63);
#if defined (ENABLE_SPARK)
	vfd_type = 4;
#elif defined (ENABLE_ATEVIO7500)
	vfd_type = 5;
#elif defined (ENABLE_FORTIS_HDBOX)
	vfd_type = 6;
#elif defined (ENABLE_OCTAGON1008)
	vfd_type = 7;
#elif defined (ENABLE_SPARK7162) \
   || defined (ENABLE_HL101) \
   || defined (ENABLE_VIP1_V1) \
   || defined (ENABLE_VIP1_V2) \
   || defined (ENABLE_VIP2)
	vfd_type = 8;
#elif defined (ENABLE_HS7810A) \
   || defined (ENABLE_HS7819) \
   || defined (ENABLE_HS7119)
	vfd_type = 9;
#elif defined (ENABLE_HS7110)
	vfd_type = 10;
#elif defined (ENABLE_HS7420) \
   || defined (ENABLE_HS7429)
	vfd_type = 11;
#elif defined (ENABLE_UFS912) \
   || defined (ENABLE_UFS913)
	vfd_type = 12;
#elif defined (ENABLE_CUBEREVO)
	vfd_type = 13;
#elif defined (ENABLE_CUBEREVO_MINI_FTA) \
   || defined (ENABLE_CUBEREVO_250HD)
	vfd_type = 14;
#elif defined (ENABLE_CUBEREVO_MINI) \
   || defined (ENABLE_CUBEREVO_MINI2) \
   || defined (ENABLE_CUBEREVO_2000HD) \
   || defined (ENABLE_CUBEREVO_3000HD)
	vfd_type = 15;
#elif defined (ENABLE_CUBEREVO_9500HD)
	vfd_type = 16;
#elif defined (ENABLE_VITAMIN_HD5000)
	vfd_type = 17;
#elif defined (ENABLE_ADB_BOX)
	vfd_type = 18;
#elif defined (ENABLE_PACE7241)
	vfd_type = 19;
#else
	vfd_type = -1;
#endif
}

void evfd::init()
{
	pthread_create (&thread_start_loop, NULL, &start_loop, NULL);
}

evfd::~evfd()
{
	// close (file_vfd);
}

#if defined (ENABLE_TF7700)

char *getProgress()
{
	int n;
	static char progress[20] = "0";
	int fd = open ("/proc/progress", O_RDONLY);

	if (fd < 0)
	{
		return 0;
	}
	n = read(fd, progress, sizeof(progress));
	close(fd);

	if (n < 0)
	{
		n = 0;
	}
	else if((n > 1) && (progress[n- 1] == 0xa))
	{
		n--;
	}
	progress[n] = 0;
	return progress;
}

void *start_loop (void *arg)
{
	int fplarge = open ("/dev/fplarge", O_WRONLY);
	int fpsmall = open ("/dev/fpsmall", O_WRONLY);
	int fpc = open ("/dev/fpc", O_WRONLY);
//	char spc[10];

	if ((fplarge < 0) || (fpsmall < 0) || (fpc < 0))
	{
		printf("Failed opening devices (%d, %d, %d)\n", fplarge, fpsmall, fpc);
		return NULL;
	}
	blocked = true;

	// set scroll mode
	// frontpanel_ioctl_scrollmode scrollMode = { 2, 10, 15 };
	// ioctl(fpc, FRONTPANELSCROLLMODE, &scrollMode);

	// display string
	char str[] = "OV";
	int length = strlen(str);
	char dispData[MAX_CHARS + 1];
	int offset = 0;
	int i;

	frontpanel_ioctl_icons icons = { 0, 0, 0xf };

	// start the display loop
	char *progress = getProgress();
	int index = 2;
	while (!requested)
	{
		// display the CD segments
		icons.Icons2 = (((1 << index) - 1)) & 0x1ffe;
		ioctl(fpc, FRONTPANELICON, &icons);
		index++;
		if (index > 13)
		{
			index = 2;
			icons.BlinkMode = (~icons.BlinkMode) & 0xf;
		}

		// display the visible part of the string
		for (i = 0; i < MAX_CHARS; i++)
		{
			dispData[i] = str[(offset + i) % length];
		}
		offset++;
		write(fplarge, dispData, sizeof(dispData));
		usleep(200000);
		if ((index % 4) == 0)
		{
			// display progress
			progress = getProgress();
//			if (strlen(progress) == 1)
//			{
//				spc = "  ";
//			}
//			if (strlen(progress) == 2)
//			{
//				spc = " ";
//			}
//			strcat(spc, progress);
			write(fpsmall, progress, strlen(progress) + 1);
			if (strncmp("100", progress, 3) == 0)
			{
				break;
			}
		}
	}
	// clear all icons
	frontpanel_ioctl_icons iconsOff = { 0xffffffff, 0xffffffff, 0x0 };
	ioctl(fpc, FRONTPANELICON, &iconsOff);

	// clear display
	write(fpsmall, "    ", 5);
	write(fplarge, "        ", MAX_CHARS);

	close(fplarge);
	close(fpsmall);
	close(fpc);
	blocked = false;

	return NULL;
}
#else  // next code for boxes other than Topfield TF77X0HDPVR

void *start_loop(void *arg)
{
	evfd vfd;

	// display signon string
	blocked = true;
	char str[] = "OV";
	int vfddev = open ("/dev/vfd", O_WRONLY);
	write(vfddev, str, strlen(str));
	close(vfddev);

	/* These boxes can control display brightness */
	#if !defined (ENABLE_FORTIS_HDBOX) \
	 && !defined (ENABLE_OCTAGON1008) \
	 && !defined (ENABLE_ATEVIO7500) \
	 && !defined (ENABLE_CUBEREVO) \
	 && !defined (ENABLE_CUBEREVO_MINI) \
	 && !defined (ENABLE_CUBEREVO_MINI2) \
	 && !defined (ENABLE_CUBEREVO_MINI_FTA) \
	 && !defined (ENABLE_CUBEREVO_250HD) \
	 && !defined (ENABLE_CUBEREVO_2000HD) \
	 && !defined (ENABLE_CUBEREVO_3000HD) \
	 && !defined (ENABLE_CUBEREVO_9500HD) \
	 && !defined (ENABLE_SPARK7162) \
	 && !defined (ENABLE_UFS912) \
	 && !defined (ENABLE_UFS913) \
	 && !defined (ENABLE_HS7119) \
	 && !defined (ENABLE_HS7420) \
	 && !defined (ENABLE_HS7429) \
	 && !defined (ENABLE_HS7810A) \
	 && !defined (ENABLE_HS7819) \
	 && !defined (ENABLE_VITAMIN_HD5000) \
	 && !defined (ENABLE_ADB_BOX) \
	 && !defined (ENABLE_PACE7241) \
	 && !defined (ENABLE_HL101) \
	 && !defined (ENABLE_VIP1_V1) \
	 && !defined (ENABLE_VIP1_V2) \
	 && !defined (ENABLE_VIP2)
	/* Others cycle their icons */
	for (int vloop = 0; vloop < 128; vloop++)
	{
		if (vloop % 2 == 1)
		{
			vfd.vfd_set_icon((((vloop % 32) / 2) % 16), ICON_OFF, true);
			usleep(2000);
			vfd.vfd_set_icon(((((vloop % 32) / 2) % 16) + 1), ICON_ON, true);
		}
	}
	#else // Modulate brightness 3 times
	for (int vloop = 0; vloop < 3 * 14; vloop++)
	{
		if (vloop % 14 == 0)
		{
			vfd.vfd_set_brightness(6);
		}
		else if (vloop % 14 == 1)
		{
			vfd.vfd_set_brightness(5);
		}
		else if (vloop % 14 == 2)
		{
			vfd.vfd_set_brightness(4);
		}
		else if (vloop % 14 == 3)
		{
			vfd.vfd_set_brightness(3);
		}
		else if (vloop % 14 == 4)
		{
			vfd.vfd_set_brightness(2);
		}
		else if (vloop % 14 == 5)
		{
			vfd.vfd_set_brightness(1);
		}
		else if (vloop % 14 == 6)
		{
			vfd.vfd_set_brightness(0);
		}
		else if (vloop % 14 == 7)
		{
			vfd.vfd_set_brightness(1);
		}
		else if (vloop % 14 == 8)
		{
			vfd.vfd_set_brightness(2);
		}
		else if (vloop % 14 == 9)
		{
			vfd.vfd_set_brightness(3);
		}
		else if (vloop % 14 == 10)
		{
			vfd.vfd_set_brightness(4);
		}
		else if (vloop % 14 == 11)
		{
			vfd.vfd_set_brightness(5);
		}
		else if (vloop % 14 == 12)
		{
			vfd.vfd_set_brightness(6);
		}
		else if (vloop % 14 == 13)
		{
			vfd.vfd_set_brightness(7);
		}
		usleep(75000);
	}
	vfd.vfd_set_brightness(7); // set final brightness
	#endif

	vfd.vfd_clear_icons();
	#if !defined (ENABLE_FORTIS_HDBOX) \
	 && !defined (ENABLE_OCTAGON1008) \
	 && !defined (ENABLE_ATEVIO7500) \
	 && !defined (ENABLE_CUBEREVO) \
	 && !defined (ENABLE_CUBEREVO_MINI) \
	 && !defined (ENABLE_CUBEREVO_MINI2) \
	 && !defined (ENABLE_CUBEREVO_MINI_FTA) \
	 && !defined (ENABLE_CUBEREVO_250HD) \
	 && !defined (ENABLE_CUBEREVO_2000HD) \
	 && !defined (ENABLE_CUBEREVO_3000HD) \
	 && !defined (ENABLE_CUBEREVO_9500HD) \
	 && !defined (ENABLE_SPARK7162) \
	 && !defined (ENABLE_VITAMIN_HD5000) \
	 && !defined (ENABLE_ADB_BOX) \
	 && !defined (ENABLE_PACE7241) \
	 && !defined (ENABLE_HL101) \
	 && !defined (ENABLE_VIP1_V1) \
	 && !defined (ENABLE_VIP1_V2) \
	 && !defined (ENABLE_VIP2)
	// Set all blocked icons
	for (int id = 0x10; id < 0x20; id++)
	{
		vfd.vfd_set_icon(id, icon_onoff[id]);
	}
#endif
	blocked = false;
	return NULL;
}
#endif

// These models handle display scrolling in a separate thread
#if defined (ENABLE_FORTIS_HDBOX) \
 || defined (ENABLE_OCTAGON1008) \
 || defined (ENABLE_ATEVIO7500) \
 || defined (ENABLE_HS7420) \
 || defined (ENABLE_HS7429) \
 || defined (ENABLE_HS7119) \
 || defined (ENABLE_HS7810A) \
 || defined (ENABLE_HS7819) \
 || defined (ENABLE_CUBEREVO) \
 || defined (ENABLE_CUBEREVO_MINI) \
 || defined (ENABLE_CUBEREVO_MINI2) \
 || defined (ENABLE_CUBEREVO_MINI_FTA) \
 || defined (ENABLE_CUBEREVO_250HD) \
 || defined (ENABLE_CUBEREVO_2000HD) \
 || defined (ENABLE_CUBEREVO_3000HD) \
 || defined (ENABLE_CUBEREVO_9500HD) \
 || defined (ENABLE_SPARK) \
 || defined (ENABLE_SPARK7162) \
 || defined (ENABLE_VITAMIN_HD5000) \
 || defined (ENABLE_ADB_BOX) \
 || defined (ENABLE_PACE7241) \
 || defined (ENABLE_HL101) \
 || defined (ENABLE_VIP1_V1) \
 || defined (ENABLE_VIP1_V2) \
 || defined (ENABLE_VIP2)
void evfd::vfd_write_string_scrollText(char *text)
{
	return;
}

#if 0
int read_scroll_procfs(char *name)
{
	int res = 0;  // result
	int i;
	FILE *f;
	char filename[30] = {0};
	char path[] = "/proc/stb/info/lcd/";
	char buf[6];
//	int stat;

	snprintf(filename, sizeof(filename), "%s%s", path, name);
	printf("%s: filename = %s\n", __func__, filename);

	f = fopen(filename, "r");
	fgets(buf, sizeof(buf), f);

	i = 0;
	while (buf[i] != '\0')
	{
		res = (res * 10) + (buf[i] - 0x30);
		i++;
	}
	return res;
}

void get_procfs_scroll_params(void)
{	// get scroll parameters
	scroll_repeat = read_scroll_procfs((char*)"scroll_repeat");
	scroll_delay = read_scroll_procfs((char*)"scroll_delay");
	initial_scroll_delay = read_scroll_procfs((char*)"initial_scroll_delay");
	final_scroll_delay = read_scroll_procfs((char*)"final_scroll_delay");
}

// We cannot use a member function (vfd_write_string_scrollText) in pthread,
// so we use a second (same content) non-member function (vfd_write_string_scrollText1)
static void *vfd_write_string_scrollText1(void *arg)
{
	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	char out[VFDLENGTH + 1];
	int i, j, len;
	evfd vfd;

	get_procfs_scroll_params();
	scroll_loop = true;
	len = strlen((char *)g_str);

// initial display is handled outside this thread
//	memcpy(out, g_str, VFDLENGTH);  // get 1st VFDLENGTH characters
//	vfd.vfd_write_string(out, true);  // initial display: write 1st VFDLENGTH characters

	// scroll ?
	if (scroll_loop && (len > VFDLENGTH))
	{
		for (i = 0; i < scroll_repeat; i++)
		{
			for (j = 1; j <= len; j++)
			{
				memset(out, ' ', VFDLENGTH + 1);  // clear scroll buffer
				memcpy(out, g_str + j, VFDLENGTH);  // then put string in
				vfd.vfd_write_string(out, true);  // print string on VFD
				if (blocked)
				{
					usleep(scroll_delay * 1000);  // loop delay
				}
				else
				{
					scroll_loop = false;
				}
			}
		}
		// final display
		memcpy(out, g_str, VFDLENGTH); // put string in
		vfd.vfd_write_string(out, true);  // print string on VFD
		if (VFD_SCROLL != 2 || !blocked)
		{
			scroll_loop = false;
		}
		else
		{
			usleep(final_scroll_delay * 1000);  // final delay
		}
	}
#else
static void *vfd_write_string_scrollText1(void *arg)
{
	pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	char out[VFDLENGTH + 1];
	int i, len;
	evfd vfd;

	scroll_loop = true;
	len = strlen((char *)g_str);
	memset(out, ' ', VFDLENGTH + 1);
	while (scroll_loop && (len > VFDLENGTH))
	{
		if (blocked)
		{
			usleep(750000);  // 0.75s pause between scroll loops
		}
		else
		{
			scroll_loop = false;
		}
		for (i = 0; i <= (len - VFDLENGTH); i++)  // scroll part 1: write full string scrolling and wait 0.75s between scrolls
		{
			if (blocked)
			{
				memset(out, ' ', VFDLENGTH);  // fill buffer with spaces
				memcpy(out, g_str + i, VFDLENGTH);  // then put string in
				vfd.vfd_write_string(out, true);  // print string on VFD
				usleep(750000);  // 0.75 sec character delay
			}
			else
			{
				scroll_loop = false;
				i = len - VFDLENGTH;
			}
		}
		for (i = 1; i <= VFDLENGTH; i++)  // scroll part 2: write full string shifted 1 character scrolling and wait 0.75s between scrolls
		{
			if (blocked)
			{
				memset(out, ' ', VFDLENGTH);  // fill buffer with spaces
				memcpy(out, g_str + len + i - VFDLENGTH, VFDLENGTH - i);  // copy string shifted 1 character
				vfd.vfd_write_string(out, true);
				usleep(750000);  // 0.75 sec character delay
			}
			else
			{
				scroll_loop = false;
				i = VFDLENGTH;
			}
		}
		memcpy(out, g_str, VFDLENGTH);
		vfd.vfd_write_string(out, true);  // final display: write 1st VFDLENGTH characters
		if (VFD_SCROLL != 2 || !blocked)
		{
			scroll_loop = false;
		}
		else
		{
			sleep(1);  // 1 sec delay between loops
		}
	}
#endif
	blocked = false;
	return NULL;
}

void evfd::vfd_write_string(char * str)
{
	int i = strlen(str);

	if (i > 63)  // display 63
	{
		i = 63;  // characters maximum
	}
	if (blocked)  // if display running
	{
		pthread_cancel(thread_start_loop);  // stop it
		pthread_join(thread_start_loop, NULL);
		blocked = false;
	}
	memset(g_str, ' ', 64);  // clear scroll buffer
	strcpy(g_str, str);  // and set display string in it
	vfd_write_string(str, false);  // initial display: 1st VFDLENGTH characters
	if (i > VFDLENGTH && VFD_SCROLL)  // if string longer than display and scroll mode
	{
//		usleep(initial_scroll_delay * 1000);  // wait initial delay
		blocked = true;  // flag scrolling
		pthread_create(&thread_start_loop, NULL, vfd_write_string_scrollText1, (void *)str);
		pthread_detach(thread_start_loop);
	}
}

void evfd::vfd_write_string(char *str, bool force)
{
	int ws = 0;
	int i = strlen(str);
	struct vfd_ioctl_data data;

	if (VFD_CENTER == true)
	{
		if (i < VFDLENGTH)
		{
			ws = (VFDLENGTH - i) / 2;
		}
		else
		{
			ws = 0;
		}
	}

	if (i > VFDLENGTH)
	{
		i = VFDLENGTH;
	}
	memset(data.data, ' ', VFDLENGTH);
	if (VFD_CENTER == true)
	{
		memcpy(data.data + ws, str, VFDLENGTH - ws);
	}
	else
	{
		memcpy(data.data, str, i);
	}
	data.start = 0;
	if (VFD_CENTER == true)
	{
		data.length = i + ws <= VFDLENGTH ? i + ws : VFDLENGTH;
	}
	else
	{
		data.length = i;
	}
	file_vfd = open (VFD_DEVICE, O_WRONLY);
	write(file_vfd,data.data,data.length);
	close (file_vfd);
}
#else  // non-thread scrolling

void evfd::vfd_write_string(char *str)
{
	vfd_write_string(str, false);
}

void evfd::vfd_write_string(char *str, bool force)
{
	int i = strlen(str);

	if (i > 63)
	{
		i = 63;
	}
	memset (chars, ' ', 63);
	memcpy (chars, str, i);
#if defined (ENABLE_TF7700)
	// request the display to cancel the start loop
	requested = true;
	while(blocked)
	{
		usleep(200000);
	}
#else
	if (!blocked || force)
#endif
	{
		struct vfd_ioctl_data data;
		memset (data.data, ' ', 63);
		memcpy (data.data, str, i);

		data.start = 0;
		data.length = i;

		file_vfd = open (VFD_DEVICE, O_WRONLY);
		ioctl (file_vfd, VFDDISPLAYCHARS, &data);
		close (file_vfd);
	}
}

void evfd::vfd_write_string_scrollText(char *text)
{  // not used?
//	get_procfs_scroll_params();

	if (!blocked)
	{
		int i, len = strlen(text);
		char *out = (char *)malloc(63);

		for (i = 0; i <= (len - 63); i++)
		{  // scroll text until end
			memset(out, ' ', 63);
			memcpy(out, text + i, 63);
			vfd_write_string(out);
			usleep(750000);
		}
		for (i = 1; i < 63; i++)
		{  // scroll text with whitespaces from right
			memset(out, ' ', 63);
			memcpy(out, text + len + i - 63, 63 - i);
			vfd_write_string(out);
			usleep(750000);
		}
		memcpy(out, text, VFDLENGTH);  // final: display first VFDLENGTH chars after scrolling
		vfd_write_string(out);
		free (out);
	}
}
#endif

void evfd::vfd_clear_string()
{
	char out[VFDLENGTH + 1];
	memset(out, 0, VFDLENGTH + 1);
	memset(out, ' ', VFDLENGTH);
	vfd_write_string(out, true);
}

void evfd::vfd_set_icon(int id, bool onoff)
{
	vfd_set_icon(id, onoff, false);
}

void evfd::vfd_set_icon(int id, bool onoff, bool force)
{
	icon_onoff[id] = onoff;
	if (!blocked || force)
	{
		struct vfd_ioctl_data data;
		if (!startloop_running)
		{
			memset(&data, 0, sizeof(struct vfd_ioctl_data));

			data.start = 0x00;
			data.data[0] = id;
			data.data[4] = onoff;
			data.length = 5;

			file_vfd = open (VFD_DEVICE, O_WRONLY);
			ioctl(file_vfd, VFDICONDISPLAYONOFF, &data);
			close (file_vfd);
		}
	}
}

void evfd::vfd_set_led(tvfd_led id, int onoff)
{
	led_onoff[id] = onoff;
	struct vfd_ioctl_data data;
	if (!startloop_running)
	{
		memset(&data, 0, sizeof(struct vfd_ioctl_data));
		data.start = 0x00;
		data.data[0] = id;
		data.data[4] = onoff;
		data.length = 5;
		file_vfd = open (VFD_DEVICE, O_WRONLY);
		ioctl(file_vfd, VFDSETLED, &data);
		close (file_vfd);
	}
}

void evfd::vfd_clear_icons()
{
	int id;

	if (ICON_MAX != -1)
	{
		for (id = 1; id <= ICON_MAX; id++)
		{
			vfd_set_icon(id, false);
		}
	}
	else
	{
		for (id = 0x10; id < 0x20; id++)
		{
			vfd_set_icon(id, false);
		}
	}
	return;
}

void evfd::vfd_set_brightness(unsigned int setting)
{
	struct vfd_ioctl_data data;

	memset(&data, 0, sizeof(struct vfd_ioctl_data));

	data.start = setting & 0x07;
	data.length = 0;

	file_vfd = open(VFD_DEVICE, O_WRONLY);
	ioctl(file_vfd, VFDBRIGHTNESS, &data);
	close(file_vfd);
}

void evfd::vfd_set_light(bool onoff)
{
	struct vfd_ioctl_data data;

	memset(&data, 0, sizeof(struct vfd_ioctl_data));

	if (onoff)
	{
		data.start = 0x01;
	}
	else
	{
		data.start = 0x00;
	}
	data.length = 0;

	file_vfd = open (VFD_DEVICE, O_WRONLY);
	ioctl(file_vfd, VFDDISPLAYWRITEONOFF, &data);

	close (file_vfd);
}

void evfd::vfd_set_fan(int speed)
{
	struct vfd_ioctl_data data;

	memset(&data, 0, sizeof(struct vfd_ioctl_data));

#if defined (ENABLE_CUBEREVO) \
 || defined (ENABLE_CUBEREVO_9500HD)
	if (speed)
	{
		data.start = 0x01;
	}
	else
	{
		data.start = 0x00;
	}
#else
	data.start = speed;
#endif
	data.length = 0;

	file_vfd = open (VFD_DEVICE, O_WRONLY);
	ioctl(file_vfd, VFDSETFAN, &data);

	close (file_vfd);
//#endif
}

void evfd::vfd_set_SCROLL(int id)
{
	if (id > 2)  // if more than 2, set 2 (scroll continously)
	{
		id = 2;
	}
	if (id < 0)  // if less than zero, set zero (no scroll)
	{
		id = 0;
	}
	VFD_SCROLL = id;
}

void evfd::vfd_set_CENTER(bool id)
{
	VFD_CENTER = id;
}
// vim:ts=4
