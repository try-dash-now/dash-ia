#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
import os,sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
sys.path.append(os.path.sep.join([pardir,'lib']))
from common import csvfile2array
import re as sre
import os
import time
import signal
from Database import FetchOne, UpdateRecord

sreTry = sre.compile("^\s*try\s+([0-9]+)\s*", sre.I)
sreAbort = sre.compile("^\s*abort\s*", sre.I)

class Task(object):
    '''this class is to launch, monitor, maintain the test cases'''
    SuiteFile= None
    CaseList =None
    RunCfg = None
    fStopTask= False
    fTaskRunning=False
    fCanncelTask =False
    RunningThread = None
    fRunning =True
    index=0
    Args=''
    TaskStartTime =''
    PASS=0
    FAIL=0
    SKIP=0

    #STATUS='TASK is launching'
    Current= {
                     '1-index':-1,
                     '2-case':'',
                     '3-tcpport':-1,                     
                     '4-logdir':'',                      
                     '5-pid':-1,                    
                     '6-starttime':'',
                     '7-endtime':'',
                     '8-result':''
                     }
    CaseRange=None
    CaseRangeStr= ''
    ArgStr= ''
    Report=[['index', 'case','TCP port', 'logdir', 'pid', 'start time', 'end time','duration','result']]
    def __init__(self, config='./manualrun.cfg'):
        from common import csvfile2dict
        self.RunCfg = csvfile2dict(config)
        import time
        self.TaskStartTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        pass
    def LoadFile(self, SuiteFile, caserange=None, args=None):
        if caserange==None:
            caserange='ALL'
        if args==None:
            args=''
        self.ArgStr=args
        import os
        if str(SuiteFile).find(os.path.sep)!=-1:
            self.SuiteFile = SuiteFile
        else:
            self.SuiteFile = self.RunCfg['suitedir']+os.path.sep+SuiteFile
        
        with open(self.SuiteFile) as f:#, newline=''
            suitestring = f.read()
            index = 0
            temp = args.split(',')[1:]
            print(temp)
            for arg in temp:
                suitestring= suitestring.replace("${%d}"%(index+1), arg)
                index=index+1
            print(suitestring)
        from common import csvstring2array
        self.CaseList = csvstring2array(suitestring)
        
        
        response = '%s(%s):completed'%(sys._getframe().f_code.co_name, self.SuiteFile)
        self.CaseRangeStr = caserange
        self.SetRange(caserange)  
        return response
    def LoadCaseInArray(self,suitname, caselist=[], caserange ='ALL',args=''):
        self.ArgStr=args
        self.SuiteFile = suitname
        self.CaseList = caselist
        self.Args=args
        self.CaseRangeStr = caserange
        self.SetRange(caserange)
        self.Report =[['index', 'case','TCP port', 'logdir', 'pid', 'start time', 'end time','duration','result']]
    def Run1Case(self, cmd, tcpport,  logdir, DebugWhenFailed=False):
        from csv2case import csv2case 
        import tempfile
        import re as sre
        cmd = cmd.strip()
        pipe_input ,file_name =tempfile.mkstemp()
        exe_cmd = " "
        c =cmd.strip()
        if cmd.startswith('./run.p') or cmd.startswith('./t.p') or cmd.startswith('t.p'):
            pass
        else:
            cmd = '../case/%s'%cmd
        if str(cmd).find(".py") !=-1:
            rePythonVersion = sre.compile(".+?;([0-9]+\.[0-9]+)\s*$", sre.M)
            m = sre.match(rePythonVersion, str(cmd))
            
            if m!=None:
                #print str(m.group(1))
                cmd = str(cmd)[ 0:str(cmd).find(";")]
                exe_cmd = "python%s "%(str(m.group(1)))
            else:
                exe_cmd = "python "
        else:
            exe_cmd = " "
        #print exe_cmd  
        import time
        sst =time.time() 
        st = time.localtime()
        starttime =time.strftime("%Y-%m-%d %H:%M:%S", st)
        #from Database import FetchOne, UpdateRecord, InsertRecord
        dbname = self.RunCfg.get('db')
        caseinfo = self.RunCfg.get('caseinfo')
  
        import subprocess
        pp =None
        if DebugWhenFailed:
            DebugWhenFailed='True'
        else:
            DebugWhenFailed= 'False'
        
        if cmd.find('t.py') !=-1 :  #cmd.startswith('r.py ') or 
            exe_cmd =exe_cmd+ cmd+" -l "+logdir
            pp = subprocess.Popen(args = exe_cmd ,shell =True, stdin=pipe_input)
        else:
            exe_cmd = exe_cmd+ cmd+" %d %s "%(tcpport, DebugWhenFailed)+logdir
            pp = subprocess.Popen(args = exe_cmd,shell =True, stdin=pipe_input)  
        #InsertRecord(dbname, caseinfo, """%f, 0.0, %d,  '%s', 'started'"""%(sst, pp.pid,  exe_cmd ))

        self.Current.update({'5-pid':pp.pid, '6-starttime': starttime})
        self.Report[self.Report.__len__()-1][4]=pp.pid
        self.Report[self.Report.__len__()-1][5]=starttime
        print('CURRENT STATUS',self.Current)
        ChildRuning = True
        first =True
        while ChildRuning:
            if pp.poll() is None:
                interval = 1
                if first:
                    first=False
                    #UpdateRecord(dbname, caseinfo, """status='running'""", 'start_time=%f and pid= %d'%(sst, pp.pid))

                time.sleep(interval)
            else:
                #return pp.returncode:
                ChildRuning = False  
        et = time.localtime()
        eet =time.time()        
        duration = '%.2f'%(eet-sst)
        self.Report[self.Report.__len__()-1][7]=duration
        et= time.strftime("%Y-%m-%d %H:%M:%S", et)
        self.Report[len(self.Report)-1][6]=et
        self.Current.update({'7-endtime':et})
        result='pass'
        if pp.returncode:
            result='fail'
        #UpdateRecord(dbname, caseinfo, """status='%s', end_time=%f"""%(result,eet), 'start_time=%f and pid= %d'%(sst, pp.pid))

        self.Current.update({'8-result':result})
        self.Report[len(self.Report)-1][8]=result
        return pp.returncode #non-zero means failed



    def Run(self, server=None):
        '''start to run cases in pole'''
        subdirname = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        dirname = os.path.basename(self.SuiteFile)       
        dirname = "%s%s%s"%(self.RunCfg['logdir'], os.path.sep,  dirname.replace(',', '_').replace('-', '_'))
        subdirname= "%s%s%s"%(dirname,os.path.sep, subdirname.replace(',', '_').replace('-', '_'))
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if not os.path.exists(subdirname):
            os.mkdir(subdirname)
        #index = 0
        
        self.PASS=0
        self.FAIL=0
        self.SKIP =0
        self.Report
        self.Report=[['index', 'case','TCP port', 'logdir', 'pid', 'start time', 'end time','duration','result']]
        while self.index <len(self.CaseList):
            self.Current.update({
                     '1-index':-1,
                     '2-case':'',
                     '3-tcpport':-1,                     
                     '4-logdir':'',                      
                     '5-pid':-1,                    
                     '6-starttime':'',
                     '7-endtime':'',
                     '8-result':''
                     }
                    )
            
            self.Report.append([self.index+1, '', -1, '','0',0.0,0.0,'-',''])
            if self.InRange(self.index):
                pass
            elif len(self.CaseList)<self.index:
                self.index= self.index+1
                self.SKIP=self.SKIP+1
                self.Report[len(self.Report)-1][8]='SKIP'
                continue
            else:
                self.index= self.index+1
                continue
            if self.fCanncelTask:
                break
            while self.fStopTask:
                time.sleep(1)
            item = self.CaseList[self.index]
            if len(item)==0:
                continue
            elif len(item)==1:
                item.append('')
                item.append('')
            elif len(item)==2:
                item.append('')
            self.Current.update({'1-index':self.index+1, '2-case':item})    
            self.Report[len(self.Report)-1][1]=item 
        #for item in self.CaseList:
            case =item[0]
            if server==None:
                tcpport =0
            else:
                dbname =self.RunCfg['db']
                tcpportpool = self.RunCfg['tcppool']
                
                       
                tcpport = FetchOne(dbname, tcpportpool, 'status="idle"')           
                
                if not tcpport:
                    self.STATUS= 'Index#%d (1 based) is going to be ran, no TCP port is idle, waiting for an avaiable TCP'%(self.index+1)
                    time.sleep(1)
                    continue
                tcpport=tcpport[0]
            self.Current.update({'3-tcpport':tcpport})
            self.Report[len(self.Report)-1][2]=tcpport
            #self.Report[self.Report.__len__()-1][1]=item
            if server:
                UpdateRecord(dbname,tcpportpool,'status="in-used"','port=%d'%int(tcpport))
            
#===============================================================================
# start_time
# double    end_time
# double    pid
# integer    case_cmd
# varchar(1024)    status
# varchar(32)
#===============================================================================

            casedir = os.path.sep.join([subdirname,'%d'%(self.index+1)])
            doublesep= '%s%s'%(os.path.sep,os.path.sep)
            casedir.replace(doublesep, os.path.sep)
            if not os.path.exists(casedir):
                os.mkdir(casedir)
            self.Current.update({'4-logdir':casedir})
            self.Report[len(self.Report)-1][3]=casedir            
            returncode = self.Run1Case(case, tcpport, casedir)

            
            if returncode:
                if len(item)>2:
                    mTry = sre.match(sreTry,item[2])                    
                    if mTry:
                        counter = int(mTry.group(1))
                        while counter:
                            returncode = self.Run1Case(case, tcpport , casedir)
                            if returncode:
                                counter-=1
                            else:
                                self.PASS=self.PASS+1
                                break
                        if returncode:
                            self.FAIL=self.FAIL+1
                    else:
                        self.FAIL=self.FAIL+1
            else:#case passed
                self.PASS=self.PASS+1
                pass
            
            mAbort = sre.match(sreAbort,item[1])
            print('CURRENT STATUS',self.Current)
            if server:
                UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%int(tcpport))
            self.DumpReport()
            if returncode and mAbort:               
                break        
           
            self.index =self.index+1

        
        self.fRunning=False
    def StartTask(self, index):
        self.fStopTask=False
        self.fCanncelTask=False
        self.Current.update({
                     '1-index':-1,
                     '2-case':'',
                     '4-pid':-1,
                     '3-port':-1,
                     '6-starttime':'',
                     '5-logdir':'',
                     '7-endtime':''
                     }
                    )
        self.Report.append([index, None,None,None,None,None,None, None])

        self.fTaskRunning=True
        self.index = index
        import threading
        self.RunningThread = threading.Thread(target=self.Run)
        self.RunningThread.start()
    def Pause(self,KillCurrentCase=True):
        '''just have a break, if KillCurrentCase==True by default, wait for another call for function Run'''
        self.fStopTask=True
        if KillCurrentCase:
            self.killCase()
        
        
    def CancelTask(self, KillCurrentCase=True):
        '''stop this task, kill current case, if KillCurrentCase==True by default, and cancel all remaining cases'''
        self.fCanncelTask=True
        self.fRunning=False
        dbname =self.RunCfg['db']
        tcpportpool = self.RunCfg['tcppool']
        UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%int(self.Current['3-tcpport']))
        if KillCurrentCase:
            self.killCase()
        self.DumpReport()    
        time.sleep(1)
        
    def DumpReport(self):
        try:
            print('Report:\n')
            print('-'*80)
            print('\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(self.Report[0][0], 
                                                          self.Report[0][8],
                                                          self.Report[0][2],
                                                          self.Report[0][4],
                                                          self.Report[0][7],
                                                          str(self.Report[0][1]),
                                                          self.Report[0][3],
                                                          self.Report[0][5],
                                                          self.Report[0][6]))
            for r in self.Report[1:]:
                try:
                    print('\t%d\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s'%(int(r[0]), 
                                                              r[8],
                                                              int(r[2]),
                                                              int(r[4]),
                                                              r[7],
                                                              str(r[1]),
                                                              r[3],
                                                              r[5],
                                                              r[6])
                      )
                except Exception as e:
                    print(e)
                    
                #print('')
            print('-'*80)
            report =self.GenerateHtmlReport()
            htmlfile = "../report/%s_%s_%s_%s.html"%(self.SuiteFile,'_'.join(self.ArgStr), self.CaseRangeStr, self.TaskStartTime)
            htmlfile=htmlfile.replace('-', '_').replace(',', '_').replace('/', '_')
            with open(htmlfile, 'wb') as f:
                f.write(report.encode(encoding='utf_8', errors='strict'))
        except Exception as e:
            print("Task::DumpReport() error: "+str(e))
    def GenerateHtmlReport(self):
        TOTAL = len(self.CaseRange)
        CASEPASS = self.PASS
        CASEFAIL = self.FAIL
        
        CASERUN = CASEPASS +CASEFAIL
        if CASERUN==0:
            CASERUN=1
        if TOTAL ==0:
            TOTAL=1
        PPASS = '%.0f'%((CASEPASS/CASERUN)*100.0)+'''%'''
        PFAIL = '%.0f'%((CASEFAIL/CASERUN)*100.0)+'''%'''
        CASENOTRUN  = TOTAL - CASEPASS-CASEFAIL
        PNOTRUN = '%.0f'%((CASENOTRUN /TOTAL)*100.0)+'''%'''

         
        response ="""
<HTML>
<HEAD>
<TITLE>Suite Test Report</TITLE>
</HEAD>
<BODY>
<table cellspacing="1" cellpadding="2" border="1">
<tr><td>SUITE NAME</td><td>ARGURMENTS</td><td>CASE RANGE</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td></tr>
</table>
<br><br>

<table cellspacing="1" cellpadding="2" border="1">
<tr>
    <td>TOTAL CASE</td><td bgcolor="#00FF00">PASS</td><td bgcolor="#FF0000">FAIL</td><td bgcolor="#0000FF">NOT RUN</td>
</tr>
<tr>
    <td>%d</td><td bgcolor="#00FF00" >%d</td><td bgcolor="#FF0000">%d</td><td  bgcolor="#0000FF">%d</td>
</tr>
<tr>
    <td> </td><td>%s</td><td>%s</td><td>%s</td>
</tr>
</table>
<BR>
<BR>
<table cellspacing="1" cellpadding="2" border="1">
"""%(self.SuiteFile, self.ArgStr, self.CaseRangeStr ,TOTAL, CASEPASS, CASEFAIL, CASENOTRUN, PPASS,PFAIL,PNOTRUN)
        
        response = response+ '''<tr><td>No.</td><td>Result</td><td>Case Name</td><td>Duration(s)</td></tr>'''        
        if len(self.Report)<2:
            return response+"""no Case result in this Task</table>
<br />
<br />
</body></html>"""
        for result in self.Report[1:]:
            bgcolor="#00FF00"
            if result[8]=='fail':
                bgcolor = "#FF0000"
            
            response = response +"""<tr><td>%d</td><td bgcolor="%s"><a target="+BLANK" href="%s">%s</td><td><a target="+BLANK" href="%s">%s</td><td>%s</td></tr>
"""%(result[0],bgcolor,result[3][1:],result[8],result[3][1:],result[1][0],result[7])



        
        return response+"""</table>
<br />
<br />
</body></html>"""
    def killCase(self):
        '''kill running case'''
        if self.Current['5-pid']!=-1:
            try:
                
                os.kill(self.Current['5-pid'], signal.SIGTERM)
                self.Report[self.Report.__len__()-1][6]='Canceled'
            except Exception as e:
                if str(e).find('No such process')!=-1:
                    pass
                else:
                    raise e
    def jump2Case(self,index):
        if index<len(self.CaseList) and index >=0:
            self.index= index

    def modifyCaseAttribute(self,index,attrName, attrValue):
        pass

    def IsAlive(self):
        return self.fRunning
    def InRange(self,index):
        try: 
            self.CaseRange.index(index)
            return True
        except Exception as e:
            return False
    def SetRange(self,caserange='ALL'):
        if not self.CaseList:
            return []
            
        if str(caserange).upper()=='ALL':
            caserange = range(0, len(self.CaseList)-1)
        else:        
            caserange = str(caserange).strip()
            caserange = str(caserange).split(',')
            drange = []
            for i in caserange:
                if str(i).find('-')!=-1:
                    s,e =str(i).split('-')
                    i = list(range(int(s)-1,int(e)))
                else:
                    i =[int(i)-1]
                drange =drange+i
            caserange= sorted(drange)
            self.CaseRange=caserange
            return self.CaseRange
        


if __name__=='__main__': 
    from Server import Server 
    from Socket import cmd2
    suitefile=sys.argv[1]
    caserange=sys.argv[2]
    args =sys.argv[3]
    print('suitefile:', suitefile)
    print('caserange:', caserange)
    print('args:', args)
    try:
        args = ','.join(sys.argv[2:])
    except:
        pass
    #tcpport=50009
    #svr = CServer('localhost', tcpport,'Task', 'Task',{}, 'IsAlive')  
    #t = svr.Handler
    t = Task()
    t.LoadFile(suitefile, caserange, args)
    print('start..............')
    #t.Load(suitfile)#'CaseListFile'
    t.Run() 
    #print(cmd2('localhost', tcpport, ['Load', 'CaseListFile']))
    #print(cmd2('localhost', tcpport, ['Run']))  
    import time
    time.sleep(5)
    #print(cmd2('localhost', tcpport, ['CancelTask', True]))    
    import time
    #while svr.IsHandlerAlive():
        
    #    time.sleep(1)
    #svr.StopServer()

    