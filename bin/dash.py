__author__ = 'Sean Yu'
'''created @2015/5/27'''


import os, sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
libpath = os.path.sep.join([pardir,'lib'])
if libpath not in sys.path:
    sys.path.insert(0,libpath)
# begin wxGlade: dependencies
import gettext
import re, string

import wx

ID_LAUNCH_HTTP = wx.NewId()
import signal
class MyFrame(wx.Frame):
    webserver=None
    weblogfilename=None
    weblogfile=None
    IAThread=None
    bIARunning =False
    ia = None
    historyCmd =None
    CmdIndex = -1
    ManualCaseHistoryCmd =None
    ManualCaseCmdIndex = -1
    def __init__(self, parent, title):
        if self.TrialExpired():
            return
        self.dirname=''
        #ico = wx.Icon('../lib/html/dash.ico', wx.BITMAP_TYPE_ICO)

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(200,-1))
        self.MainOutput = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)
        self.MainOutput.SetValue('''Read Only Output.
                               launch HTTP server on port 8080: menu 'File'->'Launch HTTP server'
                               run a single case: http://localhost:8080/case
                               run a test suite: http://localhost:8080/suite
                               Recard and Replay: 'bench SUT_Name1 SUT_Name2 ... in edit box below, example: local l''')
        self.MainInput = wx.TextCtrl(self)
        self.MainInput.SetValue('Start test here: bench SUT_Name1 SUT_Name2 ...')
        self.icon = wx.Icon('../lib/html/dash.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuLaunchHttp = filemenu.Append(ID_LAUNCH_HTTP, "&Launch HTTP server"," Launch HTTP server")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.historyCmd=[]
        self.ManualCaseHistoryCmd=[]


        # self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # self.buttons = []
        # self.buttonName= ['StartHttpServer', 'RunCase', 'RunSuite', 'InterAction']
        # for i in range(0, len(self.buttonName)):
        #     self.buttons.append(wx.Button(self, -1, self.buttonName[i]))
        #     self.sizer2.Add(self.buttons[i], 1, wx.EXPAND)

        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.MainOutput, 1,wx.ALL| wx.EXPAND)

        self.sizer.Add(self.MainInput, 0 ,wx.ALL|wx.EXPAND, 5 )
        #self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        # Events.

        #self.Bind()#, self.MainOutput
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnRunHTTPServer, menuLaunchHttp)
        #self.Bind(wx.EVT_BUTTON , self.OnRunScript, self.buttons[1])
        self.MainInput.Bind(wx.EVT_KEY_DOWN, self.onEnter)
        #self.Bind(wx.EVT_TEXT_ENTER , self.onMainInput, self.MainInput)
        #self.Bind(wx.EVT_BUTTON, self.onManualRun, self.buttons[3])
        self.Bind(wx.EVT_KEY_DOWN, self.onEnter, self.MainInput)
        self.MainInput.SetFocus()
        self.MainOutput.Bind(wx.EVT_KILL_FOCUS, self.OnSelection)
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()
        sys.stdout = self.MainOutput
        self.Maximize(True)

    def info(self, msg):
        self.MainOutput.AppendText(msg+'\n')
        self.Show()
    def OnAbout(self,e):
        # Create a message dialog box
        txt = '''
        this is an automation framework created by Sean Yu.
        It provides:
         1. launch test remotely
         2. check test result/report remotely
         3. create HTML test report
         4. Record and Replay: an interaction way to create test case
         5. Device/SUT Oriented structure--easy to extend and add more device/SUT
        '''
        dlg = wx.MessageDialog(self, txt, "About DasH", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.
    def OnClose(self,e): #fix: RuntimeError: maximum recursion depth exceeded while calling a Python object
        self.Hide()
        if self.bIARunning or self.IAThread:
            self.bIARunning=False
            if self.ia:
                self.ia.do_Exit()

        try:
            os.kill(self.webserver.pid, signal.SIGTERM)
        except:
            pass

        self.Destroy()
        #self.Close(True)  # Close the frame.
    def OnExit(self,e):
        self.Hide()
        if self.bIARunning or self.IAThread:
            self.bIARunning=False
            self.ia.do_Exit()
        if self.webserver:
            try:
                os.kill(self.webserver.pid,signal.SIGTERM)
            except:
                pass


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
        if not self.webserver:
            self.info('launching webserver on port 8080!')

            self.weblogfile, self.weblogfilename =tempfile.mkstemp()
            self.info('web logfile is %s'%(self.weblogfilename))
        else:
            self.info('Killing webserver and restart it')
            os.kill(self.webserver.pid ,signal.SIGTERM)
            self.info('Restarting web server on port 8080')
            self.weblogfile, self.weblogfilename =tempfile.mkstemp()
            self.info('web logfile is %s'%(self.weblogfilename))
        if os.path.exists("runWebServer.py"):
            exe_cmd= 'python runWebServer.py'
            pp = subprocess.Popen(args = exe_cmd ,shell =True, stdout=self.weblogfile)
        else:
            self.info('try to run executable file')
            exe_cmd= os.getcwd()+ '/runWebServer.exe'
            self.info(exe_cmd)
            if os.name=='nt':
                pp = subprocess.Popen(args = exe_cmd,shell =True, stdout=self.weblogfile,creationflags=0x08000000)
            else:
                pp = subprocess.Popen(args = exe_cmd,shell =True, stdout=self.weblogfile)

        MaxCounter = 2
        first =True
        self.webserver = pp
        self.MainOutput.AppendText('web server process Id:%d\n'%pp.pid)
        respone = 'launched http server on port 8080!'
        while MaxCounter:
            MaxCounter-=1
            if pp.poll() is None:
                interval = 1
                if first:
                    first=False
                #

                time.sleep(interval)
            else:
                #return pp.returncode:
                os.kill(self.webserver.pid,signal.SIGTERM)
                self.webserver=None
                MaxCounter = 0
                respone ='Failed to launch http server on port 8080!'

        self.info(respone)

    def TrialExpired(self):
        return False
        import time
        time.ctime()
        from datetime import datetime
        createtime=os.path.getctime('./')
        print(time.ctime(createtime))


        now = time.time()
        #now  = datetime.now()
        delta = now -createtime
        print(time.ctime(now))
        if delta> 30*24*3600:
            wx.MessageBox('Trial Expired!', 'Info',
                wx.OK )
            return True
        return False




    def onManualRun(self, e):

        if self.bIARunning:
            self.bIARunning=False
            #self.buttons[3].SetName('ManualRun')
        else:
            self.bIARunning =True
            #self.buttons[3].SetName('Stop ManualRun')


        import threading
        self.IAThread = threading.Thread(target=self.ManualRun)
        self.IAThread.start()
    def OnSelection(self,e):
        if self.bIARunning:
            select= self.MainOutput.GetStringSelection()
            self.MainOutput.SetSelection(0,0)
            if len(select)>0:
                self.MainInput.SetValue("Expect('%s',1)"%select)
            self.MainInput.SetFocus()
            #self.MainOutput.Bind(wx.EVT_KILL_FOCUS, self.OnSelection)
            self.Refresh()
        e.EventObject.Navigate()
        e.Skip()

    def onEnter(self, e):
        """"""
        event =e
        keycode = e.GetKeyCode()
        try:
            if keycode in [ wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_TAB]:
                line = str(self.MainInput.GetValue())

                if self.bIARunning and self.ia.tc.IsAlive():
                    self.historyCmd.append(line)
                    self.CmdIndex =len(self.historyCmd)-1

                    self.MainOutput.AppendText('\t%s\n'%line)
                    if keycode ==wx.WXK_TAB:
                        line = line+'\t'

                    line = self.ia.precmd(line)
                    line = self.ia.precmd(line)
                    stop = self.ia.onecmd(line)
                    stop = self.ia.postcmd(stop, line)
                    self.ia.postloop()

                    self.MainInput.SetValue('')
                    self.MainOutput.AppendText('\n'+self.ia.prompt)
                    self.Show()
                else:
                    self.ManualCaseHistoryCmd.append(line)
                    self.ManualCaseCmdIndex =len(self.ManualCaseHistoryCmd)-1
                    self.onManualRun(e)
            elif keycode ==wx.WXK_UP:
                if self.bIARunning and self.ia.tc.IsAlive():
                    self.CmdIndex-=1
                    l = len(self.historyCmd)
                    if -1 <self.CmdIndex <l:
                        pass
                    else:
                        self.CmdIndex=l-1

                    if l>0:
                        self.MainInput.SetValue(self.historyCmd[self.CmdIndex])
                    else:
                        self.MainInput.SetValue('')
                else:
                    self.ManualCaseCmdIndex-=1
                    l = len(self.ManualCaseHistoryCmd)
                    if -1 <self.ManualCaseCmdIndex <l:
                        pass
                    else:
                        self.ManualCaseCmdIndex=l-1

                    if l>0:
                        self.MainInput.SetValue(self.ManualCaseHistoryCmd[self.ManualCaseCmdIndex])
                    else:
                        self.MainInput.SetValue('')
            elif keycode ==wx.WXK_DOWN:
                if self.bIARunning and self.ia.tc.IsAlive():
                    self.CmdIndex+=1
                    l = len(self.historyCmd)
                    if -1 <self.CmdIndex <l:
                        pass
                    else:
                        self.CmdIndex=0

                    if l>0:
                        self.MainInput.SetValue(self.historyCmd[self.CmdIndex])
                    else:
                        self.MainInput.SetValue('')
                else:
                    self.ManualCaseCmdIndex+=1
                    l = len(self.ManualCaseHistoryCmd)
                    if -1 <self.ManualCaseCmdIndex <l:
                        pass
                    else:
                        self.ManualCaseCmdIndex=0

                    if l>0:
                        self.MainInput.SetValue(self.ManualCaseHistoryCmd[self.ManualCaseCmdIndex])
                    else:
                        self.MainInput.SetValue('')
        except :
                self.MainInput.SetValue('')
                self.Show()


        event.EventObject.Navigate()
        event.Skip()

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
        self.MainInput.SetValue('')
        if  argv.strip()=='':
            self.bIARunning=False
            #self.buttons[3].SetName('ManualRun')
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

        self.bIARunning =True
        try:
            self.ia =IAshell('TC',bench, sutnames,manuallogdir)


            print('#'*80)

            try:
                while self.ia.tc.IsAlive():
                    try:
                        self.MainOutput.SetStyle(1, 5, wx.TextAttr("red", "blue"))
                        self.Show()
                        time.sleep(.1)
                    except Exception as e:
                        msg = traceback.format_exc()
                        self.info(msg)
                        self.info(msg)
            except:
                pass
            self.ia.InteractionRunning=False
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            #print('can\'t run interaction test:%s'%(e) )


        self.bIARunning =False
        self.CmdIndex=-1
        self.ia=None
        sys.stdout =tmp

app = wx.App(False)
frame = MyFrame(None, 'DasH')
app.MainLoop()