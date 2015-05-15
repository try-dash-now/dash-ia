#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'

import os,time,re
import sys
sys.path.append(os.getcwd())
from common import DumpStack
import threading
reCtrl = re.compile("^\s*ctrl\s*:(.*)", re.I)
reAlt = re.compile("^\s*alt\s*:(.*)", re.I)
reCtrlAlt = re.compile("^\s*ctrlalt\s*:(.*)", re.I)
reRetry = re.compile("^\s*try\s+([0-9]+)\s*:(.*)", re.I)
reNoAction =re.compile("[\s]*NOACTION[\s]*:([\s\S]*)",re.IGNORECASE)
reNoWait =re.compile("[\s]*NOWAIT[\s]*:([\s\S]*)",re.IGNORECASE)
reNo = re.compile("^\s*NO\s*:(.*)", re.I)

reSegementIndex =re.compile ('\s*(SETUP|RUN|TEARDOWN)\s*.\s*([+-]*\d+)',re.I)

from common import csvstring2array,csvfile2array

if os.name!='nt':
    import queue
else:
    import Queue as queue
class Case(object):
    LogDir= './'
    Name= 'DefaultTestCaseName'
    SUTs={}
    Session={}
    Steps=[[],[],[]]
    logger=None
    
    arg =[]
    kwarg = {}  
    argvs=[]
    kwargvs =[]
    thInteraction =None
    bCaseEnd=False
    MoniterInterval =1 #second
    ServerPort=50000
    ServerHost ='localhost'
    #CasePort=50001
    #CaseHost ='localhost'
    SocketResponse=''
    Sock=None
    Mode= 'FULL'
    breakpoint=[[],[],[]]
    flagInteraction=False
    cp=[0,1]
    thWebclient =None
    CaseFailed= True
    DebugWhenFailed=False
    qCommand=queue.Queue()
    fRunning= False
    RecordReplay=[]
    IndexOfSutOutput ={'client':{'tel':[0,0]}}
    SUTNAME =[]
    InitialDone=False
    fActionInProgress=False
    lockOutput = None
    lockRR =None
    def SaveCase2File(self):
        import csv
        MAX_LENGTH_OF_CELL =256
        csvfile = '../case/manual/%s'%(self.Name+time.strftime("_%Y%m%d_%H%M%S", time.localtime()))
        with open(csvfile, 'w') as f:
            writer = csv.writer(f)
            lastcol2write = 4
            for row in self.RecordReplay:
                maxlen= 0
                row = row[:lastcol2write]
                for item in row:
                    l = len(str(item))
                    if l> maxlen:
                        maxlen = l
                if maxlen > MAX_LENGTH_OF_CELL:
                    index = 0
                    block =0
                    maxcol = len(row)
                    newrow =[]
                    while index <maxlen:
                        for i in range(maxcol):
                            newrow.append(row[i][block:(block+1)*MAX_LENGTH_OF_CELL]) 
                        writer.writerow(newrow)
                        block+=1
                        index=block*MAX_LENGTH_OF_CELL
                        
                else:
                    writer.writerow(row)   
            writer.writerow(['#!---'])
    def GetCurrentSutOutputIndex(self,sut):
        recordIndex = len(self.RecordReplay)-1
        colIndex = 4   +  self.SUTNAME.index(sut )
        offset = len(self.RecordReplay[recordIndex][colIndex])
        return [recordIndex,offset]
    def UpdateSutOutput2RecordReplay(self, sutname, data):
        self.lockRR.acquire()
        colIndex = 4   +  self.SUTNAME.index(sutname )
        rowIndex = len(self.RecordReplay)-1
        while len (self.RecordReplay[rowIndex])<colIndex+2:            
            self.RecordReplay[rowIndex].append('')
        self.RecordReplay[rowIndex][colIndex] = '''%s'''%(str(self.RecordReplay[rowIndex][colIndex])+ data)
        self.lockRR.release()
        
    def AddCmd2RecordReplay(self,cmd):
        newrecord = cmd[1:]
        if cmd[0]=='__case__':
            newrecord[0]='''#%s'''%newrecord[0]
        else:
            newrecord =cmd[:]
        while len(newrecord)<4:
            newrecord.append('')
        for sut in self.SUTNAME:            
            newrecord.append('')    
        self.lockOutput.acquire()    
        self.RecordReplay.append(newrecord)
        self.lockOutput.release()
    def AddClient(self, clientid):
        #lock= threading.Lock()
        self.lockOutput.acquire()
        self.IndexOfSutOutput.update({clientid:{}})
        for sut in self.Session.keys():
            self.IndexOfSutOutput[clientid].update({sut:self.GetCurrentSutOutputIndex(sut)})
            time.sleep(2)
        self.lockOutput.release()
        return 'Client %s Added'%clientid
    def RequestSUTOutput(self,client, sut):

            
        response = ''
        self.lockOutput.acquire()
        try:
            [recordIndex, offset] = self.IndexOfSutOutput[client][sut]
            cRecordIndex = len(self.RecordReplay)-1

            index = recordIndex
            colIndex =4   +  self.SUTNAME.index(sut )
            response = self.RecordReplay[index][colIndex][offset:]
            index +=1
            while cRecordIndex>=index:
                response = response + self.RecordReplay[index][colIndex][:]
                index +=1
            self.IndexOfSutOutput[client][sut]=self.GetCurrentSutOutputIndex(sut)
            time.sleep(0.2)
        except Exception as e:
            print('#####'*160)
            
            respone = DumpStack(e)
            self.error(response)
        self.lockOutput.release()
        return response 

    def QuerySUTOutput(self):
        self.info('QuerySUTOutput() is called,')
        while self.fActionInProgress:
            time.sleep(1)
        self.info('QuerySUTOutput(), Expect switchs to search in InteractionBuffer')
        for ses in self.SUTs:
            self.Session[ses].SetInteractionMode(True)
        if os.name !='nt':
            import pexpect

        while (not self.bCaseEnd) and self.flagInteraction :
            for sutname in self.SUTs.keys():
                acquired =self.lockOutput.acquire()
                try:       
                    self.Session[sutname].match=None
                    if self.InitialDone and (not self.Session[sutname].fSending):
                        if not acquired:
                            continue
                        if os.name =='nt':
                            try:
                                self.Session[sutname].match =self.Session[sutname].read_until('.+',0.01)
                            except Exception as e:
                                self.Session[sutname].match =''

                        else:
                            import pexpect
                            self.Session[sutname].expect(['.+',pexpect.TIMEOUT], 0,01)

                        match = self.Session[sutname].match
                        output=''
                        try:
                            if os.name =='nt':
                                if match!='':# and match!=pexpect.TIMEOUT :
                                    output = match #match.group().decode("utf-8")
                            else:
                                if match and match!=pexpect.TIMEOUT :
                                    output = match.group().decode('utf-8') #match.group().decode("utf-8")
                        except Exception as e:
                            self.error(DumpStack(e))
                        if len(output)>0:
                            self.Session[sutname].AppendData2InteractionBuffer(output)
                            self.UpdateSutOutput2RecordReplay(sutname, output)
                            
                            
                    
                except Exception as e:

                    if str(e.__str__).startswith('End Of File (EOF).'):
                        try:
                            self.Session[sutname].SendLine('')
                        except Exception as e: 
                            self.error(DumpStack(e))
                    else:            
                        self.error(DumpStack(e))
                self.lockOutput.release()
                time.sleep(0.49)
                
        print('Query SUT Output ended')
                #time.sleep(0.2)        
    def info(self,msg):
        self.logger.info(msg)
        self.UpdateSutOutput2RecordReplay('__case__', msg)
    def debug(self,msg):
        self.logger.debug(msg)
        self.UpdateSutOutput2RecordReplay('__case__', msg)
    def error(self,msg):
        self.logger.error(msg)
        self.UpdateSutOutput2RecordReplay('__case__', msg)
        
    def __init__(self,name,suts,steps=None,mode=None,DebugWhenFailed=False,logdir=None,caseconfigfile=None):
        if not steps :
            steps = [[],[],[]]
        if not mode:
            mode ='FULL'
        if not logdir:
            logdir = os.getcwd()
        if not caseconfigfile:
            caseconfigfile = './case.cfg'

        import threading
        self.lockOutput =threading.Lock()
        self.lockRR =threading.Lock()
        self.DebugWhenFailed=DebugWhenFailed
        a = csvfile2array(caseconfigfile)
        cfg={}
        for i in a:
            try:
                if len(i)>0:
                    cfg.update({i[0].strip().lower():i[1].strip()})
            except Exception as e:
                print(e.__str__())
        self.ServerHost = cfg['serverhost']
        self.ServerPort = int(cfg['serverport'])
        self.Name= name.replace('/','_').replace('\\','_')
        
        self.LogDir = '%s%s%s'%(logdir,os.sep,'%s%s'%(name.replace('/','_').replace('\\','_'),time.strftime("@%Y%m%d_%H%M%S", time.localtime())))
        self.LogDir = self.LogDir.replace('\\',os.path.sep).replace('/', os.path.sep)

        os.mkdir(os.path.abspath(self.LogDir))
        self.Setup=steps[0]
        self.Run =  steps[1]
        self.Teardown = steps[2]
        self.Steps=steps
        self.SUTs = suts
        self.Mode = mode.upper()
        

        import logging
        logfile = self.LogDir+os.sep+"TC_"+self.Name+".log"
        logging.basicConfig( level = logging.DEBUG, format = self.Name+' %(asctime)s -%(levelname)s: %(message)s' )
        from common import CLogger
        self.logger = CLogger(self.Name)
        self.hdrlog = logging.FileHandler(logfile)
        self.logger.setLevel(logging.DEBUG)
        self.hdrlog .setFormatter(logging.Formatter('%(asctime)s -%(levelname)s: %(message)s'))
        self.logger.addHandler(self.hdrlog )
        sutstring =''
        for sut in self.SUTs.keys():
            sutstring +='SUT(%s):[%s]\n'%(sut,self.SUTs[sut])
            self.Session.update({sut:self.Connect2Sut(sut)})

        self.SUTNAME= sorted(suts.keys())
        self.SUTNAME.append('__case__')
        
        self.RecordReplay = [['[cs]'], ['#VAR'],['#SETUP']]
        newrecord = ['#SUTNAME', 'COMMAND', 'EXPECT', 'WAIT TIME(s)']
        before1staction= ['#', '','','',]
        for sut in self.SUTNAME:
            newrecord.append(sut+' OUTPUT')
            before1staction.append('')
        self.RecordReplay.append(newrecord)
        self.RecordReplay.append(before1staction)
        self.InitialDone=True
        #print(self.thInteraction)
    def troubleshooting(self):
        import threading
        self.flagInteraction = True
        thWebclient=threading.Thread(target=self.QuerySUTOutput,args =[])
        thWebclient.start()

    def Connect2Sut(self,sutname):
        ses =None
        sutattr = self.SUTs.get(sutname)
        if sutattr["SUT"].strip() =='':
            if os.name!='nt':
                sutattr['SUT'] ='Session'
            else:
                sutattr['SUT'] ='WinSession'

        classname = sutattr["SUT"]
        ModuleName = __import__(classname)
        ClassName = ModuleName.__getattribute__(classname)    
        ses= ClassName(sutname, sutattr,logger=self.logger ,logpath = self.LogDir)
        return ses
    def EndCase(self, force=False, killProcess=False):
        if self.DebugWhenFailed ==True and self.CaseFailed==True:
            return 'case failed! and it is waiting for your debug, if you do want to end this case, please try EndCase(force=True)'
        elif self.flagInteraction==True and force==False:
            return 'case is in troubleshooting/interaction mode, if you do want to end this case, please try EndCase(force=True)'

        self.bCaseEnd=True
        import time
        import os
        if self.thInteraction and self.thInteraction.isAlive():
            time.sleep(1)
        time.sleep(self.MoniterInterval)
        for sut in self.Session.keys():            
            self.Session[sut].EndSession()

        from common import csvfile2dict
        #runcfg = csvfile2dict('./manualrun.cfg')
        #dbname =runcfg.get('db')
        #from Database import FetchOne, UpdateRecord
        
        #caseinfo = runcfg.get('caseinfo')

        pid = os.getpid()
        #UpdateRecord(dbname, caseinfo, """status='ended-closed',end_time=%f"""%(time.time()), "status='running' and pid= %d"%(pid))
        #self.logger.info('update database done!')
        self.SaveCase2File()
        #if self.Sock:
            #self.Sock.shutdown(socket.SHUT_RDWR)
            #self.Sock.close()
        import signal
        try:
            if killProcess:
                os.kill(os.getpid(), signal.SIGTERM)#exit(0)#
            pass
        except:
            pass
    def action(self,sut='__case__', cmd='',expect='.*',timeout=1.0):
        self.ActionCheck([sut, cmd,expect ,float(timeout)])
    def ActionCheck(self,step=[]):
        global reRetry,reNo,reNoWait,reNoAction,reCtrl,reAlt,reCtrlAlt
        #for step in steps:
        self.info('Start Step:sut(%s), action(%s), expect(%s) within %d'%(step[0],step[1],step[2],int(step[3])))
        [sut,cmd,exp,Time]=step[:4]
        [fretry,fNoAction,fNo,fNoWait]=[1,False,False,False]
        mRetry=re.match(reRetry, cmd)
        mCtrl= re.match(reCtrl,cmd)
        mAlt = re.match(reAlt,cmd)
        mCtrlAlt = re.match(reCtrlAlt,cmd)
        fCtrl =False
        fAlt= False
        if mCtrl:
            fCtrl=True
            cmd = mCtrl.group(1)
        if mAlt:
            fAlt=True
            cmd = mAlt.group(1)
        if mCtrlAlt:
            fCtrl=True
            fAlt=True
            cmd = mCtrlAlt.group(1)
            
        if mRetry:
            fretry= int(mRetry.group(1))
            cmd = mRetry.group(2)                
        mNoAction= re.match(reNoAction,cmd)
        if mNoAction:
            fNoAction=True
        mNoWait =   re.match(reNoWait,exp)
        if mNoWait:
            fNoWait=True
            exp=mNoWait.group(1)            
        mNo = re.match(reNo,exp)
        if mNo:
            fNo=True
            exp=mNo.group(1)
        
        s = self.Session[sut]
        (ActionIsFunction,action,arg,kwarg) = s.ParseCmdInAction(cmd)
        Failure=True
        totalretry=fretry
        while fretry>1:
            fretry= fretry-1
            try:
                if not fNoAction:
                    if ActionIsFunction:
                        s.CallFun(action, arg, kwarg)
                        Failure=False
                        break                       
                    else:
                        s.SendLine(command = cmd, Ctrl=fCtrl, Alt=fAlt)                
                                    
                try:
                    s.Expect(exp,Time,fNoWait)
                    if not fNo:
                        Failure=False
                        break
                        
                except Exception as e:
                    if fNo:
                        Failure=False
                        break
            except Exception as e:
                if os.name!='nt':
                    pass#print ('%d/%d failed'%(totalretry-fretry,totalretry), file=sys.stdout)
                else:
                    print ('%d/%d failed'%(totalretry-fretry,totalretry), sys.stdout)
                self.info('%d/%d failed'%(totalretry-fretry,totalretry))
        IgnoreExp=False
        if Failure:#try last time
            if not fNoAction:
                if ActionIsFunction:
                    IgnoreExp=True
                    s.CallFun(action, arg, kwarg)
                    Failure=False                        
                else:
                    s.SendLine(command = cmd, Ctrl=fCtrl, Alt=fAlt)
            if IgnoreExp:
                return
            if fNo:
                try:
                    s.Expect(exp,Time,fNoWait)
                    self.error('unexpect(%s) found within %d'% (exp, int(time)))
                    raise Exception('unexpect(%s) found within %d'% (exp, int(time)))
                except Exception as e:
                    self.info('no unexpected pattern (%s) found'%exp)
            else:
                s.Expect(exp,Time,fNoWait)
                #print('Expect (%s) found!'%(exp))


        
    def ParseCmdInAction(self,cmd):
        IsCallFunction= True
        reFunction = re.compile('\s*FUN\s*:\s*(.+?)\s*\(\s*(.*)\s*\)|\s*(.+?)\s*\(\s*(.*)\s*\)',re.IGNORECASE)
        m = re.match(reFunction, cmd)
        fun =cmd
        arg = ""
        kwarg ={}
        # noinspection PyComparisonWithNone
        if m != None :
            # noinspection PyComparisonWithNone
            if m.group(1) !=None:
                fun = m.group(1)
                arg = m.group(2)
            else:
                fun = m.group(3)
                arg = m.group(4)        

            fun = self.__getattribute__(fun)
            import inspect
            (args, varargs, keywords, defaults) =inspect.getargspec(fun)
            try:
                parsestr= "self.GetFunArgs(%s)"%((arg))
                eval(parsestr)
            except Exception as e:
                arg.strip()
                if re.search(',',arg):
                    self.argvs =arg.split(',')
                elif len(arg.strip())==0:
                    self.argvs =[]
                else:
                    self.argvs =[self.argvs]

            arg =self.argvs
            kwarg = self.kwargvs          
        else:
            IsCallFunction = False
            fun = cmd      
        return (IsCallFunction,fun,arg,kwarg)

    def GetFunArgs(self,*argvs, **kwargs):
        self.argvs=[]
        self.kwargvs={}
        #re-assign for self.argvs and self.kwargvs
        for arg in argvs:
            self.argvs.append(arg)
        for k in kwargs.keys():
            self.kwargvs.update({k:kwargs[k]})    
    def CallFun(self,functionName,args=[], kwargs={}):
        
        self.fActionInProgress=True
        resp = functionName(*args, **kwargs)  
        #self.info(resp)
        self.fActionInProgress=False
        # noinspection PyComparisonWithNone
        if resp ==None:
            return 'Done'
        else:
            return resp 
       
    def pp(self,varname):        
        return repr(self.__getattribute__(varname)).replace('\\\\n','\n').replace('\\\\r','\r')  
    def set(self,varname,value):
        return self.__setattr__(varname, value)
    def SetBreakPoint(self,segment,index):
        self.info('SetBreakPoint("%s","%s"'%(segment,str(index)))
        segment= segment.upper()
        if segment=='SETUP':
            segment= 0
        elif segment=='RUN':
            segment= 1
        elif segment=='TEARDOWN':
            segment=2
        else:
            msg= 'segment should be one of [SETUP,RUN, TEARDOWN]'
            self.error(msg)
            return msg
        if index<1:
            index =1
        self.breakpoint[segment].append(index)
        self.breakpoint[segment].sort()
    def str2indexSegment(self,segmentstr):
        segment= segmentstr.upper()
        if segment=='SETUP':
            segment= 0
        elif segment=='RUN':
            segment= 1
        elif segment=='TEARDOWN':
            segment=2
        else:
            raise
        return segment          
    def BreakPointCheck(self,segment,index):
        segment= segment.upper()
        segment =self.str2indexSegment(segment)  
        if len(self.breakpoint[segment])>0:
            self.info('BreakPointCheck("%s","%s")'%(segment,index))
            for i in self.breakpoint[segment].sort():
                if index==i:
                    return True
        return False    
    def getIntSegIndex(self,strSegIndex):        
        global reSegementIndex #=re.compile ('\s*(SETUP|RUN|TEARDOWN)\s*.\s*(\d+)',re.I)
        m = re.match(reSegementIndex, strSegIndex)
        seg= self.str2indexSegment(m.group(1).upper())
        index= int(m.group(2))
        if index==-1:
            index = len(self.Steps[seg])+1
        return seg,index
    def cpReset(self):
        self.cp = [0,1]
    def cpSet(self,seg, index):
        self.cp =[seg, index]
        strSeg=['setup','run','teardown']
        return '%s.%d'%(strSeg[seg],index)
    def getCP(self):
        strSeg=['setup','run','teardown']
        if self.cp[0]>2:
            seg, index = self.getIntSegIndex('teardown.-1')
            return 'teardown.%d'%(index+1)
        return '%s.%d'%(strSeg[self.cp[0]],self.cp[1])        
    def cpNext(self):
        l =len(self.Steps[self.cp[0]])
        self.cp[1]+=1
        if self.cp[1]>l:
            self.cp[1]=1
            self.cp[0]+=1           
                
       
    def RunCase(self,mode,startindex,endindex):
        self.info('case %s.RunCase(%s,%s,%s)'%(self.Name,mode ,startindex,endindex))
        startSeg, startIndex= self.getIntSegIndex(startindex)
        endSeg, endIndex= self.getIntSegIndex(endindex)  
        mode =mode.lower()
        self.info('step')
        self.cpSet(startSeg, startIndex)
        seg=['setup','run','teardown']

        while self.IndexInRange(self.getCP(), startindex, endindex):
            if self.BreakPointCheck(seg[self.cp[0]], self.cp[1]):
                self.flagInteraction=True
            while self.flagInteraction:
                time.sleep(0.5)
            skip=False            
            if mode =='full':
                    pass
            elif mode =='setupteardown' and self.cp[0]==1:
                skip=True
            elif mode =='setuprun' and self.cp[0]==2:
                skip=True
            elif mode =='runteardown' and self.cp[0]==0:
                skip=True
            elif mode =='setupteardown' and self.cp[0]==1:
                skip=True                
            elif mode =='setup' and self.cp[0]!=0:
                skip=True    
            elif mode =='run' and self.cp[0]!=1:
                skip=True     
            elif mode =='teardown' and self.cp[0]!=2:
                skip=True  
                                     
            if not skip:
                try:
                    try:
                        step = self.Steps[self.cp[0]][self.cp[1]-1]
                    except Exception as e:
                        break
                    self.fRunning=True
                    print('#'*80)
                    print('#step (%s.%d)'%(seg[self.cp[0]],int(self.cp[1])))
                    print('#SUT(%s), Action(%s), Exp(%s), Within (%d)'%(step[0],step[1],step[2],int(step[3])))

                    self.info('#'*80)
                    self.info('#step (%s.%d)'%(seg[self.cp[0]],int(self.cp[1])))
                    self.info('#SUT(%s), Action(%s), Exp(%s), Within (%d)'%(step[0],step[1],step[2],int(step[3])))
                    if len(step)>4:
                        print('#%s'%(step[4]))
                        self.info('#%s'%(step[4]))
                    print('#'*80)
                    self.info('#'*80)
                    self.AddCmd2RecordReplay(step)
                    self.ActionCheck(step)
                    
                except Exception as e:
                    self.error(DumpStack(e))
                    if not self.DebugWhenFailed:
                        self.bCaseEnd=True
                        raise
            self.fRunning=False
            if not self.flagInteraction:
                self.bCaseEnd=True
            self.cpNext()
        self.info('-'*80)
    def IndexInRange(self,testIndex,startindex='setup.1',endindex='teardown.-1'):    
        MAX_ACTION= 65535
        startSeg, startIndex= self.getIntSegIndex(startindex)
        endSeg, endIndex= self.getIntSegIndex(endindex)        
        testSeg, testIndex=self.getIntSegIndex(testIndex)   
        start = startSeg*MAX_ACTION+startIndex
        end = endSeg*MAX_ACTION+endIndex
        test = testSeg*MAX_ACTION+testIndex
        if test>=start and test<=end:
            return True
        else:
            return False

    def IsAlive(self):
        if self.bCaseEnd:
            return False
        else:
            return True
                  
