#ifndef VFD_H_
#define VFD_H_

// define display width
#if defined ENABLE_TF7700
	#define MAX_CHARS 8
	#define VFDLENGTH 8
#elif defined (ENABLE_HS7810A) \
   || defined (ENABLE_HS7819) \
   || defined (ENABLE_HS7119) \
   || defined (ENABLE_SPARK) \
   || defined (ENABLE_CUBEREVO_MINI_FTA) \
   || defined (ENABLE_CUBEREVO_250HD)
	#define VFDLENGTH 4
#elif defined (ENABLE_OCTAGON1008) \
   || defined (ENABLE_HS7420) \
   || defined (ENABLE_HS7429) \
   || defined (ENABLE_SPARK7162) \
   || defined (ENABLE_HL101) \
   || defined (ENABLE_VIP1_V2) \
   || defined (ENABLE_VIP2_V1)
	#define VFDLENGTH 8
#elif defined (ENABLE_VITAMIN_HD5000)
	#define VFDLENGTH 11
#elif defined (ENABLE_FORTIS_HDBOX) \
   || defined (ENABLE_ATEVIO7500) \
   || defined (ENABLE_CUBEREVO)
	#define VFDLENGTH 12
#elif defined (ENABLE_CUBEREVO_9500HD)
	#define VFDLENGTH 13
#elif defined (ENABLE_CUBEREVO_MINI) \
   || defined (ENABLE_CUBEREVO_MINI2) \
   || defined (ENABLE_CUBEREVO_2000HD) \
   || defined (ENABLE_CUBEREVO_3000HD)
	#define VFDLENGTH 14
#else
	#define VFDLENGTH 16
#endif

// define number of icons
#if defined (ENABLE_SPARK7162) \
 || defined (ENABLE_HL101) \
 || defined (ENABLE_VIP1_V2) \
 || defined (ENABLE_VIP2_V1)
#define ICON_MAX 45
#elif defined (ENABLE_FORTIS_HDBOX)
#define ICON_MAX 39
#elif defined (ENABLE_OCTAGON1008)
#define ICON_MAX 28
#elif defined (ENABLE_ATEVIO7500)
#define ICON_MAX 22
#elif defined (ENABLE_UFS912) \
 ||   defined (ENABLE_UFS913)
#define ICON_MAX 15
#elif defined (ENABLE_CUBEREVO)
#define ICON_MAX 27
#elif defined (ENABLE_CUBEREVO_MINI) \
 ||   defined (ENABLE_CUBEREVO_MINI2) \
 ||   defined (ENABLE_CUBEREVO_2000HD) \
 ||   defined (ENABLE_CUBEREVO_3000HD)
#define ICON_MAX 6
#elif defined (ENABLE_VITAMIN_HD5000)
#define ICON_MAX 16
#elif defined (ENABLE_ADB_BOX) \
 ||   defined (ENABLE_PACE7241)
#define ICON_MAX 20
#else
#define ICON_MAX -1
#endif

// IOCTL definitions
#define VFD_DEVICE            "/dev/vfd"
#define VFDDISPLAYCHARS       0xc0425a00
#define VFDBRIGHTNESS         0xc0425a03
#define VFDDISPLAYWRITEONOFF  0xc0425a05
#define VFDICONDISPLAYONOFF   0xc0425a0a
#define VFDSETFAN             0xc0425af8
#define VFDSETLED             0xc0425afe

#define ICON_ON  1
#define ICON_OFF 0

#if 0 //!defined (ENABLE_FORTIS_HDBOX)
typedef enum { USB = 0x10, HD, HDD, LOCK, BT, MP3, MUSIC, DD, MAIL, MUTE, PLAY, PAUSE, FF, FR, REC, CLOCK } tvfd_icon;
typedef enum { RED_LED = 0, GREEN_LED } tvfd_led;
//#else
//typedef enum { USB = 1, I_STANDBY, I_SAT, I_REC, I_TIMESHIFT, I_TIMER, I_HD, I_LOCK, I_DD, I_MUTE, I_TUNER1, I_TUNER2, I_MP3, I_REPEAT,
//               I_PLAY, I_PAUSE, I_TER, I_FILE_, I_480i, I_480p, I_576i, I_576p, I_720p, I_1080i, I_1080p } tvfd_icon;
//typedef enum { RED_LED = 0, BLUE_LED, CROSS_UP, CROSS_LEFT, CROSS_RIGHT, CROSS_DOWN } tvfd_led;
#endif
typedef enum { RED_LED = 0, GREEN_LED } tvfd_led;

struct vfd_ioctl_data
{
	unsigned char start;
	unsigned char data[64];
	unsigned char length;
};

class evfd
{
protected:
		static evfd *instance;
		int file_vfd;
		int vfd_type;
#ifdef SWIG
		evfd();
		~evfd();
#endif
	public:
#ifndef SWIG
		evfd();
		~evfd();
#endif
		void init();
		static evfd* getInstance();

		int getVfdType() { return vfd_type; }
		void vfd_set_SCROLL(int id);
		void vfd_set_CENTER(bool id);
		void vfd_set_icon(int id, bool onoff);
		void vfd_set_icon(int id, bool onoff, bool force);
		void vfd_set_led(tvfd_led id, int onoff);
		void vfd_clear_icons();

		void vfd_write_string(char *string);
		void vfd_write_string(char *str, bool force);
		void vfd_write_string_scrollText(char *text);
	void vfd_clear_string();

		void vfd_set_brightness(unsigned int setting);
		void vfd_set_light(bool onoff);
		void vfd_set_fan(int speed);
};

#endif // VFD_H_
// vim:ts=4
