__author__ = 'Sean Yu'
'''created @2015/5/27'''


import os, sys


# begin wxGlade: dependencies
import gettext
import re, string

import wx
class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):

        self.dirname=''

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(200,-1))
        self.MainOutput = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.MainOutput.SetValue('output')
        self.MainInput = wx.TextCtrl(self)

        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.



        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []
        self.buttonName= ['StartHttpServer', 'RunCase', 'RunSuite']
        for i in range(0, 3):
            self.buttons.append(wx.Button(self, -1, self.buttonName[i]))
            self.sizer2.Add(self.buttons[i], 1, wx.EXPAND)

        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.MainOutput, 1,wx.ALL| wx.EXPAND)

        self.sizer.Add(self.MainInput, 0 ,wx.ALL|wx.EXPAND, 5 )
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_BUTTON, self.OnRunHTTPServer, self.buttons[0])

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()


    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.MainOutput.SetValue(f.read())
            f.close()
        dlg.Destroy()
    def OnRunHTTPServer(self,e):
        import subprocess, tempfile,time
        pipe_input ,file_name =tempfile.mkstemp()
        try:
            exe_cmd= 'python runWebServer.py'
            pp = subprocess.Popen(args = exe_cmd ,shell =True, stdin=pipe_input)
        except:
            exe_cmd= 'runWebServer.exe'
            pp = subprocess.Popen(args = exe_cmd,shell =True, stdin=pipe_input)

        MaxCounter = 2
        first =True
        while MaxCounter:
            MaxCounter-=1
            if pp.poll() is None:
                interval = 1
                if first:
                    first=False
                self.MainOutput.SetValue('launched http server on port 8080!')

                time.sleep(interval)
            else:
                #return pp.returncode:
                MaxCounter = 0
                self.MainOutput.SetValue('Failed to launch http server on port 8080!')
        self.Show(1)


app = wx.App(False)
frame = MyFrame(None, 'DasH')
app.MainLoop()