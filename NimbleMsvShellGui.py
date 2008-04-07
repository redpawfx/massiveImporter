import sys
import os
import os.path
import wx

import ns.py.ui.FileCtrl as nsFileCtrl

_border = 5
_spacerWidth = 50

class MainWindow(wx.Frame):
	
	def __init__(self,parent,id,title):	
		wx.Frame.__init__( self, parent, wx.ID_ANY, title,
						   style=wx.DEFAULT_FRAME_STYLE |
						   wx.NO_FULL_REPAINT_ON_RESIZE)
		
		self.panel = wx.Panel(self, -1)
		self.masFileCtrl = nsFileCtrl.FileSelectCtrl( "Setup File (.mas)",
													  [ ".mas" ],
													  ( 50, 50 ),
													  ( 50, 50 ) )
		self.masFileCtrl.CreateControl(self.panel)
		
		#self.masFileLabel = wx.StaticText( panel, -1, "Setup File (.mas)" )
		#self.masFileText = wx.TextCtrl( panel, -1, "",
		#								size=(-1, -1),
		#								style=wx.TE_PROCESS_ENTER )
		#self.masFileInput.SetInsertionPoint( 0 )
		#self.Bind( wx.EVT_TXT, self.masFileInput, self.onMasFile )
		
		self.sizer = wx.FlexGridSizer( cols=3, hgap=6, vgap=6 )
		self.sizer.Add( (_spacerWidth, -1) )
		#sizer.Add( self.masFileLabel, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=_border )
		#sizer.Add( self.masFileInput, flag=wx.EXPAND|wx.ALL, border=_border )
		self.sizer.Add( self.masFileCtrl, flag=wx.EXPAND|wx.ALL, border=_border )
		self.sizer.Add( (_spacerWidth, -1) )
		#sizer.Add( (_spacerWidth, -1) )
		#sizer.AddGrowableCol( 2 )
		#sizer.AddGrowableRow( 0 )
		self.panel.SetSizer( self.sizer )
		self.sizer.Fit(self)


if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = MainWindow(None, -1, "NimbleMsvShell")
	frame.Show()
	app.MainLoop()
