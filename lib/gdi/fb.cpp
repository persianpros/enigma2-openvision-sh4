#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <memory.h>
#include <linux/kd.h>

#include <lib/gdi/fb.h>
#include <linux/stmfb.h>

#ifndef FBIO_WAITFORVSYNC
#define FBIO_WAITFORVSYNC _IOW('F', 0x20, uint32_t)
#endif

#ifndef FBIO_BLIT
#define FBIO_SET_MANUAL_BLIT _IOW('F', 0x21, uint8_t)
#define FBIO_BLIT 0x22
#endif

fbClass *fbClass::instance;

fbClass *fbClass::getInstance()
{
	return instance;
}

fbClass::fbClass(const char *fb)
{
	m_manual_blit=-1;
	instance=this;
	locked=0;
	lfb = 0;
	available=0;
	cmap.start=0;
	cmap.len=256;
	cmap.red=red;
	cmap.green=green;
	cmap.blue=blue;
	cmap.transp=trans;

	fbFd=open(fb, O_RDWR);
	if (fbFd<0)
	{
		eDebug("[fb] %s %m", fb);
		goto nolfb;
	}


	fb_fix_screeninfo fix;
	if (ioctl(fbFd, FBIOGET_FSCREENINFO, &fix)<0)
	{
		eDebug("[fb] FBIOGET_FSCREENINFO: %m");
		goto nolfb;
	}

	available = fix.smem_len;
	m_phys_mem = fix.smem_start;
	eDebug("[fb] %s: %dk video mem", fb, available/1024);
	// The first 1920x1080x4 bytes are reserved
	// After that we can take 1280x720x4 bytes for our virtual framebuffer
	available -= 1920*1080*4;
	eDebug("%dk usable video mem", available/1024);
	lfb=(unsigned char*)mmap(0, available, PROT_WRITE|PROT_READ, MAP_SHARED, fbFd, 1920*1080*4);
	if (!lfb)
	{
		eDebug("[fb] mmap %m");
		goto nolfb;
	}
	return;
nolfb:
	if (fbFd >= 0)
	{
		::close(fbFd);
		fbFd = -1;
	}
	eDebug("[fb] framebuffer not available");
	return;
}

int fbClass::SetMode(int nxRes, int nyRes, int nbpp)
{
	if (fbFd < 0) return -1;
	xRes=nxRes;
	yRes=nyRes;
	bpp=32;
	m_number_of_pages = 1;
	topDiff=bottomDiff=leftDiff=rightDiff = 0;
	ioctl(fbFd, FBIOGET_VSCREENINFO, &screeninfo);
	xResSc=screeninfo.xres;
	yResSc=screeninfo.yres;
	stride=xRes*4;
	blit();
	return 0;
}

void fbClass::getMode(int &xres, int &yres, int &bpp)
{
	xres = xRes;
	yres = yRes;
	bpp = 32;
}

int fbClass::setOffset(int off)
{
	if (fbFd < 0) return -1;
	screeninfo.xoffset = 0;
	screeninfo.yoffset = off;
	return ioctl(fbFd, FBIOPAN_DISPLAY, &screeninfo);
}

int fbClass::waitVSync()
{
	int c = 0;
	if (fbFd < 0) return -1;
	return ioctl(fbFd, FBIO_WAITFORVSYNC, &c);
}

void fbClass::blit()
{
	if (fbFd < 0) return;
	int modefd=open("/proc/stb/video/3d_mode", O_RDWR);
	char buf[16] = "off";
	if (modefd > 0)
	{
		read(modefd, buf, 15);
		buf[15]='\0';
		close(modefd);
	}

	STMFBIO_BLT_DATA    bltData;
	memset(&bltData, 0, sizeof(STMFBIO_BLT_DATA));
	bltData.operation  = BLT_OP_COPY;
	bltData.srcOffset  = 1920*1080*4;
	bltData.srcPitch   = xRes * 4;
	bltData.dstOffset  = 0;
	bltData.dstPitch   = xResSc*4;
	bltData.src_top    = 0;
	bltData.src_left   = 0;
	bltData.src_right  = xRes;
	bltData.src_bottom = yRes;
	bltData.srcFormat  = SURF_BGRA8888;
	bltData.dstFormat  = SURF_BGRA8888;
	bltData.srcMemBase = STMFBGP_FRAMEBUFFER;
	bltData.dstMemBase = STMFBGP_FRAMEBUFFER;

	if (strncmp(buf,"sbs",3)==0)
	{
		bltData.dst_top    = 0 + topDiff;
		bltData.dst_left   = 0 + leftDiff/2;
		bltData.dst_right  = xResSc/2 + rightDiff/2;
		bltData.dst_bottom = yResSc + bottomDiff;
		if (ioctl(fbFd, STMFBIO_BLT, &bltData ) < 0)
		{
			perror("STMFBIO_BLT");
		}
		bltData.dst_top    = 0 + topDiff;
		bltData.dst_left   = xResSc/2 + leftDiff/2;
		bltData.dst_right  = xResSc + rightDiff/2;
		bltData.dst_bottom = yResSc + bottomDiff;
		if (ioctl(fbFd, STMFBIO_BLT, &bltData ) < 0)
		{
			perror("STMFBIO_BLT");
		}
	}
	else if (strncmp(buf,"tab",3)==0)
	{
		bltData.dst_top    = 0 + topDiff/2;
		bltData.dst_left   = 0 + leftDiff;
		bltData.dst_right  = xResSc + rightDiff;
		bltData.dst_bottom = yResSc/2 + bottomDiff/2;
		if (ioctl(fbFd, STMFBIO_BLT, &bltData ) < 0)
		{
			perror("STMFBIO_BLT");
		}
		bltData.dst_top    = yResSc/2 + topDiff/2;
		bltData.dst_left   = 0 + leftDiff;
		bltData.dst_right  = xResSc + rightDiff;
		bltData.dst_bottom = yResSc + bottomDiff/2;
		if (ioctl(fbFd, STMFBIO_BLT, &bltData ) < 0)
		{
			perror("STMFBIO_BLT");
		}
	}
	else
	{
		bltData.dst_top    = 0 + topDiff;
		bltData.dst_left   = 0 + leftDiff;
		bltData.dst_right  = xResSc + rightDiff;
		bltData.dst_bottom = yResSc + bottomDiff;
		if (ioctl(fbFd, STMFBIO_BLT, &bltData ) < 0)
		{
			perror("STMFBIO_BLT");
		}
	
	}

	if (ioctl(fbFd, STMFBIO_SYNC_BLITTER) < 0)
	{
		perror("STMFBIO_SYNC_BLITTER");
	}
}

fbClass::~fbClass()
{
	if (lfb)
	{
		msync(lfb, available, MS_SYNC);
		munmap(lfb, available);
	}
	if (fbFd >= 0)
	{
		::close(fbFd);
		fbFd = -1;
	}
}

int fbClass::PutCMAP()
{
	if (fbFd < 0) return -1;
	return ioctl(fbFd, FBIOPUTCMAP, &cmap);
}

int fbClass::lock()
{
	if (locked)
		return -1;
		locked = 1;

	outcfg.outputid = STMFBIO_OUTPUTID_MAIN;
	if (ioctl( fbFd, STMFBIO_GET_OUTPUT_CONFIG, &outcfg ) < 0)
		perror("STMFBIO_GET_OUTPUT_CONFIG\n");

	outinfo.outputid = STMFBIO_OUTPUTID_MAIN;
	if (ioctl( fbFd, STMFBIO_GET_OUTPUTINFO, &outinfo ) < 0)
		perror("STMFBIO_GET_OUTPUTINFO\n");

	//if (ioctl( fbFd, STMFBIO_GET_VAR_SCREENINFO_EX, &infoex ) < 0)
	//	printf("ERROR\n");

	planemode.layerid = 0;
	if (ioctl( fbFd, STMFBIO_GET_PLANEMODE, &planemode ) < 0)
		perror("STMFBIO_GET_PLANEMODE\n");

	if (ioctl( fbFd, STMFBIO_GET_VAR_SCREENINFO_EX, &infoex ) < 0)
		perror("STMFBIO_GET_VAR_SCREENINFO_EX\n");
	return fbFd;
}

void fbClass::unlock()
{
	if (!locked)
		return;
	locked=0;

	if (ioctl( fbFd, STMFBIO_SET_VAR_SCREENINFO_EX, &infoex ) < 0)
		perror("STMFBIO_SET_VAR_SCREENINFO_EX\n");

	if (ioctl( fbFd, STMFBIO_SET_PLANEMODE, &planemode ) < 0)
		perror("STMFBIO_SET_PLANEMODE\n");

	if (ioctl( fbFd, STMFBIO_SET_VAR_SCREENINFO_EX, &infoex ) < 0)
		perror("STMFBIO_SET_VAR_SCREENINFO_EX\n");

	if (ioctl( fbFd, STMFBIO_SET_OUTPUTINFO, &outinfo ) < 0)
		perror("STMFBIO_SET_OUTPUTINFO\n");

	if (ioctl( fbFd, STMFBIO_SET_OUTPUT_CONFIG, &outcfg ) < 0)
		perror("STMFBIO_SET_OUTPUT_CONFIG\n");

	memset(lfb, 0, stride*yRes);

	SetMode(xRes, yRes, bpp);
	PutCMAP();
}

void fbClass::clearFBblit()
{
	//set real frambuffer transparent
//	memset(lfb, 0x00, xRes * yRes * 4);
	blit();
}

int fbClass::getFBdiff(int ret)
{
	if(ret == 0)
		return topDiff;
	else if(ret == 1)
		return leftDiff;
	else if(ret == 2)
		return rightDiff;
	else if(ret == 3)
		return bottomDiff;
	else
		return -1;
}

void fbClass::setFBdiff(int top, int left, int right, int bottom)
{
	if(top < 0) top = 0;
	if(top > yRes) top = yRes;
	topDiff = top;
	if(left < 0) left = 0;
	if(left > xRes) left = xRes;
	leftDiff = left;
	if(right > 0) right = 0;
	if(-right > xRes) right = -xRes;
	rightDiff = right;
	if(bottom > 0) bottom = 0;
	if(-bottom > yRes) bottom = -yRes;
	bottomDiff = bottom;
}
