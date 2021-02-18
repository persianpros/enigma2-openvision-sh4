#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
import ServiceReference
from enigma import iPlayableService, eTimer, eServiceCenter, iServiceInformation, evfd
import time
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase


class VFDIcons:

    def __init__(self, session):
        self.session = session
        self.service = None
        self.onClose = []
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
         iPlayableService.evUpdatedEventInfo: self.__evUpdatedEventInfo,
         iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged,
         iPlayableService.evSeekableStatusChanged: self.__evSeekableStatusChanged,
         iPlayableService.evStart: self.__evStart})
        session.nav.record_event.append(self.gotRecordEvent)
        self.mp3Available = False
        self.dolbyAvailable = False
        return

    def __evStart(self):
        self.__evSeekableStatusChanged()

    def __evUpdatedInfo(self):
        self.checkAudioTracks()
        self.writeChannelName()
        self.showCrypted()
        self.showDolby()
        self.showMp3()

    def writeChannelName(self):
        servicename = ''
        currPlay = self.session.nav.getCurrentService()
        if currPlay != None and self.mp3Available:
            servicename = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
        else:
            self.service = self.session.nav.getCurrentlyPlayingServiceReference()
            if self.service is not None:
                service = self.service.toCompareString()
                servicename = ServiceReference.ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
                subservice = self.service.toString().split('::')
                if subservice[0].count(':') == 9:
                    servicename = subservice[1].replace('\xc2\x87', '').replace('\xc3\x9f', 'ss').replace('\xc2\x86', '').ljust(16)
                else:
                    servicename = servicename
            else:
                print('[VFD-Icons] no Service found')
        evfd.getInstance().vfd_write_string(servicename[0:63])
        return 1

    def showCrypted(self):
        service = self.session.nav.getCurrentService()
        if service is not None:
            info = service.info()
            crypted = info and info.getInfo(iServiceInformation.sIsCrypted) or -1
        return

    def checkAudioTracks(self):
        self.dolbyAvailable = False
        self.mp3Available = False
        service = self.session.nav.getCurrentService()
        if service is not None:
            audio = service.audioTracks()
            if audio:
                n = audio.getNumberOfTracks()
                for x in range(n):
                    i = audio.getTrackInfo(x)
                    description = i.getDescription()
                    if description.find('MP3') != -1:
                        self.mp3Available = True
                    if description.find('AC3') != -1 or description.find('DTS') != -1:
                        self.dolbyAvailable = True

        return

    def showDolby(self):
        print('[VFD-Icons] showDolby')

    def showMp3(self):
        print('[VFD-Icons] showMp3')

    def __evUpdatedEventInfo(self):
        print('[VFD-Icons] __evUpdatedEventInfo')

    def getSeekState(self):
        service = self.session.nav.getCurrentService()
        if service is None:
            return False
        else:
            seek = service.seek()
            if seek is None:
                return False
            return seek.isCurrentlySeekable()

    def __evSeekableStatusChanged(self):
        print('[VFD-Icons] __evSeekableStatusChanged')

    def __evVideoSizeChanged(self):
        service = self.session.nav.getCurrentService()
        if service is not None:
            info = service.info()
            height = info and info.getInfo(iServiceInformation.sVideoHeight) or -1
        return

    def gotRecordEvent(self, service, event):
        recs = self.session.nav.getRecordings()
        nrecs = len(recs)


VFDIconsInstance = None


def main(session, **kwargs):
    global VFDIconsInstance
    if VFDIconsInstance is None:
        VFDIconsInstance = VFDIcons(session)
    return


def Plugins(**kwargs):
    return [PluginDescriptor(name='VFD Icons', description='Icons in VFD', where=PluginDescriptor.WHERE_SESSIONSTART, fnc=main)]
