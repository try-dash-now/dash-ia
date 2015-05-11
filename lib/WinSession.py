# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
"""
created 2015/5/8 
WinSession is the basic class for telnet session, it provide the basic functions, as SendLine, Expect...
"""


import  os
from telnetlib import Telnet as spawn
import time
import re as sre
import traceback
reSessionClosed =sre.compile ('Connection closed by foreign host',sre.M)
class WinSession(spawn, object):
    match = None
    attrs={}
    sutname='SUT'
    logger= None
    loginstep=[]
    argvs=[]
    kwargvs={}
    seslog=None
    output=''
    Connect2SUTDone=False
    lastActionTime=None
    fInteractionMode=False
    InteractionBuffer=''
    InteractionMatch=''
    fExpecting=False
    fSending = False
    stdout=None
    def __del__(self):
        if self.seslog:
            try:
                output =self.expect(['.+'], 1)
                self.seslog.flush()
            except:
                pass
            if not self.seslog.closed:
                self.seslog.flush()
                self.close()

    def __init__(self,name,attrs={},logger=None, logpath=None):
        if logpath ==None:
            import os
            logpath = '.%s'%(os.path.sep)
        self.sutname=name
        self.attrs=attrs
        command = attrs.get('CMD')
        if not attrs.get('TIMEOUT'):
            self.attrs.update({'TIMEOUT':int(30)})
        else:
            self.attrs.update({'TIMEOUT':int(attrs.get('TIMEOUT'))})
        import os
        log = os.path.abspath(logpath)
        log= '%s%s%s'%(log,os.path.sep,'%s.log'%name)
        if self.attrs.get('LOGIN'):
            from common import csvstring2array
            self.loginstep= csvstring2array(self.attrs['LOGIN'])

        self.seslog = open(log, "wb")
        host=""
        port=23
        reHostOnly=  sre.compile('\s*telnet\s+([\d.\w\-_]+)\s*',sre.I)
        reHostPort = sre.compile('\s*telnet\s+([\d.\w]+)\s+(\d+)', sre.I )
        m1=sre.match(reHostOnly, command)
        m2=sre.match(reHostPort, command)
        if m1:
            host= m1.groups(1)[0]
        elif m2:
            host= m2.groups(1)[0]
            port= m2.groups(2)[0]

        spawn.__init__(self, str(host), port)
        self.set_debuglevel(0)
        self.Login2SUT()
        self.Connect2SUTDone=True

    def info(self,msg):
        if not self.logger:
            print(self.sutname,':INFO:%s'%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),msg)
            return
        for line in str(msg).split("\n"):
            ln = "%s::%s"%(self.sutname,line)
            print(ln)
            self.logger.info(ln)
    def debug(self,msg):
        if not self.logger:
            print(self.sutname,':DEBUG:%s'%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),msg)
            return
        for line in str(msg).split("\n"):
            self.logger.debug("%s::%s"%(self.sutname,line))
    def error(self,msg):
        if not self.logger:
            print(self.sutname,':ERROR:%s'%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),msg)
            return
        for line in str(msg).split("\n"):
            self.logger.error("%s::%s"%(self.sutname,line))

    def Login2SUT(self):
        self.Connect2SUTDone=False
        if self.attrs.get('EXP'):
            output =self.expect([self.attrs['EXP']], int(self.attrs['TIMEOUT']))
            if output[0]!=-1:
                pass
            else:
                raise
        else:
            self.write(os.linesep)

        for step in self.loginstep:
            self.write(step[0]+os.linesep)
            output=''
            timeout = int(self.attrs['TIMEOUT'])
            if len(step)>2:
                timeout =int(step[2])
            output = self.expect([step[1]],timeout)
            if output[0]!=-1:
                pass
            else:

                msg = traceback.format_exc()
                msg += 'send(%s), expect(%s), within(%s)'%(step[0],step[1],str(step[2]))
                print(msg)
                raise Exception(msg)
    def EndSession(self):
        command = self.attrs['CMD']
        output =self.expect(['.*'], 1)

        if command.find('telnet')!=-1:
            self.write('\x1d')
            output= self.expect(['telnet>'],10)
            self.write('quit')
            output= self.expect(['.*'],10)
        else:
            try:
                self.write('exit')
                if self.attrs.get('LINEEND'):
                    self.write(self.attrs.get('LINEEND'))
            except Exception as e:
                self.error(str(e))
    def msg(self, msg, *args):
        if msg.find('recv')!=-1:
            self.output+=args[0]
            self.seslog.write(args[0])

        super(WinSession, self).msg(msg,*args)

    def GetFunArgs(self,*argvs, **kwargs):
        self.argvs=[]
        self.kwargvs={}
        #re-assign for self.argvs and self.kwargvs
        for arg in argvs:
            self.argvs.append(arg)
        for k in kwargs.keys():
            self.kwargvs.update({k:kwargs[k]})
    def CallFun(self,functionName,args=[], kwargs={}):
        functionName(*args, **kwargs)

    def isalive(self):
        try:
            if os.name!='nt':
                return super(WinSession,self).isalive()
            else:
                return self.sock_avail()
        except Exception as e:
            if str(e).find("\"terminated\" is 0")==-1:
                return False
            else:
                return True

    def sendcontrol(self, c):
        ascii = ord(c) & 0x1f
        ch = chr(ascii)
        self.write(ch)
    def SendLine(self,command, clearbuffer=True,AntiIdle=False,Ctrl=False,Alt=False):

        if not AntiIdle:
            self.info('%s:SendLine(command="%s",clearbuffer=%d,AntiIdle=%d, Ctrl=%d, Alt=%d)'%(self.sutname,command,clearbuffer,AntiIdle, Ctrl,Alt))
        try:
            if self.fInteractionMode:
                self.Expect("Connection closed by foreign host.", 0.1)
            else:
                output=self.expect(["Connection closed by foreign host."], 0.1)
                if output[0]==-1:
                    raise
            self.Login2SUT()
        except Exception as e:
            pass#

        if clearbuffer:
            if self.fInteractionMode:
                self.InteractionBuffer=''
            else:
                pat = sre.compile('.+',sre.MULTILINE|sre.DOTALL)
                output =self.expect([pat], 0.1)[2]

        if AntiIdle ==False:
            self.info("%s SENDLINE:(%s)"%(self.sutname,str(command)))
        else:
            pass
        if self.fInteractionMode:
            pass
        self.fSending =True
        time.sleep(0.3)

        if Ctrl:
            for c in command:
                self.info("%s SendControl:(%s)"%(self.sutname,str(c)))
                self.sendcontrol(c)
                self.write(os.linesep)

        else:
            if command == '':
                command = os.linesep

            self.write(command+os.linesep)
            if self.attrs.get("LINEEND") and self.Connect2SUTDone ==True:
                self.write(os.linesep)
        self.fSending=False
        self.seslog.flush()

    def Expect(self,pat , wait=2, nowait=False):
        self.fExpecting=True
        if wait==None:
            wait=0.5
        found =None

        global reSessionClosed
        output =self.expect([reSessionClosed], 0.1)
        found = output[0]
        isalive = self.isalive()
        if (self.Connect2SUTDone):
            if (found !=-1):
                command = self.attrs['CMD']
                self.error("Session(%s) has been closed by remote host!"%(self.sutname))
                if command.find('telnet')!=-1:
                    host=""
                    port=23
                    args = command.split(' ')
                    if len(args)==2:
                        host = args[1]
                    elif len(args)==3:
                        host= args [1]
                        port = args[2]
                    spawn.__init__(self, host, port)
                self.set_debuglevel(1)
                self.Login2SUT()
        m =None
        if not nowait:
            if not self.fInteractionMode:
                output =self.expect(["%s"%(pat)],wait)
                self.output= output[2]
                if output[0]==-1:
                    raise
                m = sre.search(pat,self.output, sre.M|sre.DOTALL)
            else:
                interval=0.1
                counter =0
                max_counter=round(float(wait)/interval)+1
                interactionpat = '(%s)(.*)'%pat
                while counter<max_counter:
                    counter+=1
                    m =sre.search(interactionpat,self.InteractionBuffer,sre.M|sre.DOTALL)
                    if m:
                        self.InteractionMatch=m.group(0)
                        self.InteractionBuffer=m.group(1)#.decode("utf-8")
                        break

                    time.sleep(interval)
        else:
            m = sre.search(pat,self.output, sre.M|sre.DOTALL)
        self.seslog.flush()
        self.fExpecting=False
        if not m:
            raise Exception('Expect("%s", %f) Failed'%(pat,float(wait)))
        self.match = self.output
        return self.output

    def SetInteractionMode(self,flag):
        self.fInteractionMode=flag

    def AppendData2InteractionBuffer(self,data):
        self.InteractionBuffer+=data
    def ParseCmdInAction(self,cmd):
        IsCallFunction= True
        sreFunction = sre.compile('\s*FUN\s*:\s*(.+?)\s*\(\s*(.*)\s*\)|\s*(.+?)\s*\(\s*(.*)\s*\)',sre.IGNORECASE)
        m = sre.match(sreFunction, cmd)
        fun =cmd
        arg = ""
        kwarg ={}
        if m != None :
            if m.group(1) !=None:
                fun = m.group(1)
                arg = m.group(2)
            else:
                fun = m.group(3)
                arg = m.group(4)

            fun = self.__getattribute__(fun) #self.__getattribute__(fun)
            import inspect
            (args, varargs, keywords, defaults) =inspect.getargspec(fun)
            try:
                parsestr= "self.GetFunArgs(%s)"%(str(arg))
                eval(parsestr)
            except Exception as e:
                str(arg).strip()
                if sre.search(',',arg):
                    self.argvs =arg.split(',')
                elif len(str(arg).strip())==0:
                    self.argvs =[]
                else:
                    self.argvs =[self.argvs]

            arg =self.argvs
            kwarg = self.kwargvs
        else:
            IsCallFunction = False
            fun = cmd
        return (IsCallFunction,fun,arg,kwarg)
    def SLEEP(self,sec=1.0):
        time.sleep(float(sec))
    def StartInteractionMode(self,flag):

        self.fInteractionMode=flag

if __name__=='__main__':
    try:
        cmd ='telnet 192.168.37.222' #cdc-dash'
        cmd = 'telnet cdc-dash'
        cmd = 'telnet 10.245.66.10'
        attr={'TIMEOUT':180,'LOGIN': 'e7,assword:,30\nadmin,>,30','CMD':cmd, 'LINEEND':u''+chr(13), 'EXP':'name:' }
        s = WinSession('sut_local',attr)
        command='SendLine("abcddddddddddddd",AntiIdle=True)'
        s.SendLine('command', True, False)
        s.SendLine('command2', True, False)
        (ActionIsFunction,action,arg,kwarg) = s.ParseCmdInAction(command)
        s.CallFun(action, arg, kwarg)
        s.EndSession()
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!CASE End!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    except Exception as e:

        import traceback
        msg = traceback.format_exc()
        print(msg)
        print(e)