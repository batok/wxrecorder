#!/bin/env python
# -*- coding: iso-8859-1 -*-

#Copyright 2009  Domingo Aguilera

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import wx
import sys
from threading import Thread
import pyaudio
import wave
import os
import subprocess

class RecordThread( Thread ):
	def __init__(self, window, seconds):
		Thread.__init__(self)
		self.window = window
		self.seconds = seconds
		
	def run(self):
		chunk = 1024
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 44100
		RECORD_SECONDS = self.seconds
		WAVE_FILENAME = "output.wav"
		p = pyaudio.PyAudio()

		stream = p.open(format = FORMAT,
		                channels = CHANNELS,
		                rate = RATE,
		                input = True,
		                frames_per_buffer = chunk)
		rec = []
		
		for i in range(0, RATE / chunk * RECORD_SECONDS):
			data = stream.read(chunk)
			rec.append(data)
			
		stream.close()
		p.terminate()
		sdata = ''.join(rec)
		f = wave.open(WAVE_FILENAME, 'wb')
		f.setnchannels(CHANNELS)
		f.setsampwidth(p.get_sample_size(FORMAT))
		f.setframerate(RATE)
		f.writeframes(sdata)
		f.close()
		self.window.recording_finished = True


class MainFrame( wx.Frame ):
	def __init__(self):
		wx.Frame.__init__(  self, None, -1, "wxrecorder - Audio Recorder", size = (650,500))
		mb = wx.MenuBar()
		recording_menu = wx.Menu()
		mb.Append(recording_menu, "Recording")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.Bind(wx.EVT_MENU, self.OnRecordAudio, recording_menu.Append(-1, "Record audio"))
		self.SetMenuBar(mb)	

	def OnClose(self, event):
		self.Destroy()
		
	def OnRecordAudio(self,event):
		RECORD_SECONDS = 15
		seconds = wx.GetNumberFromUser("Record Seconds", "Recording", "Time", value = RECORD_SECONDS, min = RECORD_SECONDS, max = RECORD_SECONDS + 100)
		self.RecordAudio( seconds )	
		dlg = wx.MessageDialog(self, "The file output.wav has been generated and is in your filesystem.\nDo you want to listen to it", "Recording finished", style = wx.YES_NO)
		retCode = dlg.ShowModal()
		if retCode == wx.ID_YES:
			if wx.Platform == "__WXMSW__":
				os.startfile("output.wav")
			else:
				if wx.Platform == "__WXMAC__":
					command = "open output.wav"
				else:
					command = "xdg_open output.wav"
			p = subprocess.Popen( command, shell = True)
			pid , sts = os.waitpid( p.pid, 0)
		return
	
	def RecordAudio(self, seconds):
		self.recording_finished = False
		RecordThread(self, seconds).start()
		
		dlg = wx.ProgressDialog("Recording Audio",
                               "Recording audio from wxrecorder",
                               maximum = seconds,
                               parent=self,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                #| wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                )
		count = 0
		while not self.recording_finished:
			count += 1
			wx.MilliSleep( 1000 )
			dlg.Update(count)
		dlg.Destroy()
	
	
if __name__ == "__main__":
	app = wx.PySimpleApp()
	f = MainFrame()
	f.CenterOnScreen()
	f.Show()
	app.MainLoop()
