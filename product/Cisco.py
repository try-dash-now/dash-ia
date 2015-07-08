#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-
#from pexpect import spawn, TIMEOUT
import time
import re as sre

import os
if os.name!='nt':
    from Session import Session as CSession
else:
    from WinSession import WinSession as CSession
reSessionClosed =sre.compile ('Connection closed by foreign host',sre.M)
class Cisco(CSession):
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
    def __init__(self,name,attrs={},logger=None,logpath='./'):
        self.sutname=name
        self.attrs=attrs        
        command = attrs.get('CMD')
        if not attrs.get('TIMEOUT'):
            self.attrs.update({'TIMEOUT':int(30)})
        else:
            self.attrs.update({'TIMEOUT':int(attrs.get('TIMEOUT'))})
        #spawn.__init__(self, command, args, timeout, maxread, searchwindowsize, logfile, cwd, env, ignore_sighup)
        import os
        log = os.path.abspath(logpath)
        log= '%s%s%s'%(log,os.path.sep,'%s.log'%name)
        if self.attrs.get('LOGIN'):
            from common import csvstring2array
            self.loginstep= csvstring2array(self.attrs['LOGIN'])
         
        self.seslog = open(log, "wb")
        CSession.__init__(self, name, attrs,logger, logpath)

        
    def Login2SUT(self):
        exp = self.attrs['EXP']
        if os.name=='nt':
            exp = [self.attrs['EXP']]

        if self.attrs.get('EXP'):
            self.expect(exp, float(self.attrs['TIMEOUT']))
        for step in self.loginstep:
            if os.name !='nt':
                self.send(step[0])
                self.send('\r\n')
            else:
                self.write(step[0])
                self.write('\r\n')
            if os.name=='nt':
                exp = [step[1]]
            if len(step)>2:
                self.expect(exp,int(step[2]))
            else:
                self.expect(exp,float(self.attrs['TIMEOUT']))
                         
if __name__=='__main__':
    cmd ='telnet 10.245.3.17'
    attr={'TIMEOUT': 10,'LOGIN': 'Calix,E7-SIT-S3-2960-2>,40\nenable,word:,40\nadmin,E7-SIT-S3-2960-2#,40','CMD':cmd, 'EXP':'.*'}
    s = Cisco('sut_local',attr)
    command='SendLine("abcddddddddddddd",AntiIdle=True)'
    s.SendLine('command', True, False)
    (ActionIsFunction,action,arg,kwarg) = s.ParseCmdInAction(command)
    s.CallFun(action, arg, kwarg)
    s.EndSession()
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!CASE End!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')