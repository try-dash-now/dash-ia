__author__ = 'Sean Yu'
'''created @2015/5/27'''


import os, sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))

# begin wxGlade: dependencies
import gettext
import re, string

import wx

class MyFrame(wx.Frame):
    webserver=None
    weblogfilename=None
    weblogfile=None
    IAThread=None
    bIARunning =False
    ia = None
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
        self.buttonName= ['StartHttpServer', 'RunCase', 'RunSuite', 'InterAction']
        for i in range(0, len(self.buttonName)):
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
        self.Bind(wx.EVT_BUTTON , self.OnRunScript, self.buttons[1])
        self.Bind(wx.EVT_TEXT_ENTER , self.onMainInput, self.MainInput)
        self.Bind(wx.EVT_BUTTON, self.onManualRun, self.buttons[3])
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def info(self, msg):
        self.MainOutput.AppendText(msg+'\n')
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
        if not self.webserver:
            self.info('launching webserver on port 8080!')
            import subprocess, tempfile,time
            self.weblogfile, self.weblogfilename =tempfile.mkstemp()
            self.info('web logfile is %s'%(self.weblogfilename))
        else:
            self.info('Killing webserver and restart it')
            try:
                self.weblogfile.close()
            except Exception as e:
                self.info('close web log file failed:'+str(e))
            os.kill(self.webserver.pid)
            self.info('Restarting web server on port 8080')
            self.weblogfile, self.weblogfilename =tempfile.mkstemp()
            self.info('web logfile is %s'%(self.weblogfilename))


        try:
            exe_cmd= 'python runWebServer.py'
            pp = subprocess.Popen(args = exe_cmd ,shell =True, stdout=self.weblogfile)
        except:
            exe_cmd= 'runWebServer.exe'
            pp = subprocess.Popen(args = exe_cmd,shell =True, stdin=self.weblogfile)

        MaxCounter = 2
        first =True
        while MaxCounter:
            MaxCounter-=1
            if pp.poll() is None:
                interval = 1
                if first:
                    first=False
                self.info('launched http server on port 8080 completed!')

                time.sleep(interval)
            else:
                #return pp.returncode:
                MaxCounter = 0
                self.info('Failed to launch http server on port 8080!')
    def onManualRun(self, e):
        if self.bIARunning:
            self.bIARunning=False
            self.buttons[3].SetName('ManualRun')
        else:
            self.bIARunning =True
            self.buttons[3].SetName('Stop ManualRun')


        import threading
        self.IAThread = threading.Thread(target=self.ManualRun)
        self.IAThread.start()
    def OnRunScript(self,e):
        line = str(self.MainInput.GetValue())


        exe_cmd = line
        tmp =sys.stdout
        sys.stdout=self.MainOutput
        if line.find('.py') != -1:
            exe_cmd = 'python '+exe_cmd
        import subprocess
        import tempfile
        pipe_input ,file_name_in =tempfile.mkstemp()
        pipe_output ,file_name_out =tempfile.mkstemp()

        pp = subprocess.Popen(exe_cmd,#sys.executable,
                     #cwd = os.sep.join([os.getcwd(),'..']),
                     stdin=pipe_input,
                     stdout=pipe_output,
                     shell=True
                     )
        print('PID: %d runcase(%s) has been launched, stdin(%s), stdout(%s)'%(pp.pid,exe_cmd,file_name_in,file_name_out))

        import time
        ChildRuning = True
        while ChildRuning:
            if pp.poll() is None:
                interval = 1
                time.sleep(interval)
            else:
                ChildRuning = False
        returncode = pp.returncode
        sys.stdout= tmp
        print('PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode))
        f = open(file_name_out, 'r')
        self.MainOutput.SetValue(f.read())
        f.close()
        return 'PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode) #non-zero means failed

    def onMainInput(self,e):
        if self.bIARunning:
            line = str(self.MainInput.GetValue())
            line = self.ia.precmd(line)
            line = self.ia.precmd(line)
            stop = self.ia.onecmd(line)
            stop = self.ia.postcmd(stop, line)
            self.ia.postloop()
            self.MainInput.SetValue('')
            self.Show()

            #self.ia.RunCmd(cmd)
    def ManualRun(self):
        import time
        suts={}
        casename=''

        from common import csvfile2dict
        runcfg = csvfile2dict('./manualrun.cfg')
        dbname =runcfg.get('db')
        tcpportpool = runcfg.get('tcppool')
        benchdir = runcfg.get('benchdir')
        defaultlogdir = runcfg.get('logdir')
        manuallogdir = runcfg.get('manuallogdir')
        casename = 'tc'+time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())

        argv = self.MainInput.GetValue()
        #argv = ''.join(argv)
        #argv = str(argv)[1:]

        if  argv.strip()=='':
            self.bIARunning=False
            self.buttons[3].SetName('ManualRun')
            return

        argv=argv.split(' ')
        try:
            argv =[x for x in argv if x!='']
        except:
            pass
        bench = str(argv[0])
        sutnames = argv[1:len(argv)]

        benchname = bench
        import os,sys
        #    def __init__(self,name,suts,CasePort=50001, steps=[[],[],[]],mode='FULL',DebugWhenFailed=False,logdir='./',caseconfigfile='./case.cfg'):
        if benchname.find(os.sep)==-1:
            bench= '%s%s%s'%(benchdir, os.sep,benchname)
        else:
            bench = benchname


        pardir =os.path.dirname(os.path.realpath(os.getcwd()))
        #pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
        sys.path.append(os.path.sep.join([pardir,'lib']))
        print('\n'.join(sys.path))
        import time
        from common import csvfile2dict
        print('CWD:',os.getcwd())
        from IAshell import IAshell
        tmp =sys.stdout
        sys.stdout = self.MainOutput
        self.ia =IAshell('TC',bench, sutnames,manuallogdir, outputfile=self.MainOutput )


        print('#'*80)


        while self.bIARunning:
            try:
                self.Show()
                time.sleep(.1)
            except Exception as e:
                msg = traceback.format_exc()
                self.info(msg)
                self.info(msg)
        sys.stdout =tmp

app = wx.App(False)
frame = MyFrame(None, 'DasH')
app.MainLoop()