# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/22 
'''
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler

class HttpHandler(BaseHTTPRequestHandler):
    logger=None
    hdrlog =None
    runcfg = None
    fDBReseting=False
    def __del__(self):
        #self.hdrlog.close()
        print('end http server')

    def InitLogging(self):
        return
        import logging
        #root = logging.getLogger()
        logfile ="./html/log/webserver.log"
        logging.basicConfig( level = logging.DEBUG, format = '%(asctime)s -%(levelname)s: %(message)s' )
        from common import CLogger
        self.logger = CLogger('')
        self.hdrlog = logging.FileHandler(logfile)
        self.logger.setLevel(logging.DEBUG)
        self.hdrlog .setFormatter(logging.Formatter('%(asctime)s -%(levelname)s: %(message)s'))
        self.logger.addHandler(self.hdrlog )
    def info(self,msg):
        #return
        print(str(self.client_address) + ' ' +str(msg))
    def debug(self,msg):
        #return
        print(str(self.client_address) + ' ' +str(msg))
    def error(self,msg):
        #return
        print(str(self.client_address) + ' ' +str(msg))


    def do_GET(self):
        home= "../lib/html/"
        if self.path=='/':
            #indexpage= open('./index.html', 'r')
            #encoded=indexpage.read()
            #encoded = encoded%(name)
            indexpage= open(home+ 'index.html', 'r')
            #"Hello "+name+" <form action='' method='POSt'>Name:<input name='name' /><br /><input type='submit' value='submit' /></form>"
            encoded=indexpage.read()
            encoded = encoded.encode(encoding='utf_8')
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            #self.end_headers()
        elif self.path =='/favicon.ico':
            indexpage= open(home+'dash.ico', 'r')
            encoded=indexpage.read()
            self.send_response(200)
            self.send_header("Content-type", "application/x-ico")
        self.end_headers()
        self.wfile.write(encoded)






    def OnManualTestRequest(self):
        self.info(self.OnManualTestRequest.__name__+' start')
        from os import listdir
        from os.path import isfile, join
        path = './html/bench/'
        benchlist=''
        onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
        onlyfiles = sorted(onlyfiles)
        CHECKED = 'CHECKED'
        for bed in onlyfiles:
            line = '<input type="radio" name="benchname" value="%s" %s/> %s </a><br>\n'%(bed,CHECKED,bed)
            CHECKED =''
            benchlist += line
        encoded = self.LoadHTMLPage('./html/ManualTest4BenchList.html', [benchlist])

        self.info(self.OnManualTestRequest.__name__+' end')
        return encoded.encode(encoding='utf_8')

    def LoadHTMLPage(self, filename, replace=[], Pattern4ESCAPE1='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT1#',Pattern4ESCAPE2='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT2#'):

        indexpage= open(filename, 'r')
        encoded=indexpage.read()
        encoded =encoded.replace('%s',Pattern4ESCAPE1 )
        encoded =encoded.replace('%',Pattern4ESCAPE2 )
        encoded =encoded.replace(Pattern4ESCAPE1,'%s' )

        for item in replace:
            encoded =encoded.replace('%s', item, 1)
        encoded =encoded.replace(Pattern4ESCAPE2, '%' )

        return encoded
    def OnManualTestSelectSUTs(self,benchname):
        self.info(self.OnManualTestSelectSUTs.__name__+' start')
        bench = './html/bench/%s'%benchname
        from common import bench2dict
        benchinfo = bench2dict(bench)
        #print benchinfo
        keys = sorted(benchinfo.keys())


        sutliststring = ''
        sut =[]
        for key in keys:
            if type(benchinfo[key])==type({}):
                sut.append(key)
                line = '''<input id="sutid" type="checkbox"  name="sutid" value="%s" />  %s  [ %s ]<br>\n'''%(key,key,benchinfo[key]['CMD'])
                sutliststring = sutliststring+line
        encoded = self.LoadHTMLPage('./html/ManualTest4SutList.html', [sutliststring, bench ])
        #encoded = encoded%()
        self.info(self.OnManualTestSelectSUTs.__name__+' end')
        return encoded.encode(encoding='utf_8')
    def RunCase(self, case=[],logdir="./html/log/manual" ,maualrun=False):

        exe_cmd = " "
        if str(case[0]).find(".py") !=-1:

            #if str(case[0]).find(";([0-9.])")!=-1:
            #print str(case[0])
            import re
            rePythonVersion = re.compile(".+?;([0-9]+\.[0-9]+)\s*$", re.M|re.MULTILINE)
            m = re.match(rePythonVersion, str(case[0]))

            if m!=None:
                #print str(m.group(1))
                case[0] = str(case[0])[ 0:str(case[0]).find(";")]
                exe_cmd = "python%s "%(str(m.group(1)))
            else:
                exe_cmd = "python3 "
        else:
            exe_cmd = " "
        #print exe_cmd
        if  maualrun==False:
            logoption = ' -l '
        else:
            logoption = ' '
        exe_cmd =exe_cmd+ case[0]+logoption +logdir #exe_cmd+ case[0]+logoption +logdir
        self.info('Run Case : %s'%(exe_cmd))

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
        self.info('PID: %d runcase(%s) has been launched, stdin(%s), stdout(%s)'%(pp.pid,exe_cmd,file_name_in,file_name_out))

        #CreateTable(dbname, CaseInfo, 'start_time double primary key UNIQUE, end_time double, case_cmd varchar(1024), status varchar(32)')
        if not self.runcfg:
            self.LoadRunCfg()
        dbname = self.runcfg.get('db')
        caseinfo = self.runcfg.get('caseinfo')
        #InsertRecord(dbname, tcppool, """50010, 'idle'""")
        import time
        starttime  = time.time()

        if not self.fDBReseting:
            InsertRecord(dbname, caseinfo, """%f, 0.0, %d,  '%s', 'started'"""%(starttime, pp.pid,  exe_cmd ))

        ChildRuning = True
        firstTime = True
        while ChildRuning:
            if pp.poll() is None:
                if not self.fDBReseting and firstTime:
                    UpdateRecord(dbname, caseinfo, """status='running'""", 'start_time=%f and pid= %d'%(starttime, pp.pid))
                    firstTime=False
                interval = 1
                time.sleep(interval)
            else:
                #return pp.returncode:
                if not self.fDBReseting:
                    UpdateRecord(dbname, caseinfo, """status='ended',end_time=%f"""%(time.time()), 'start_time=%f and pid= %d'%(starttime, pp.pid))
                ChildRuning = False
        returncode = pp.returncode
        self.info('PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode))
        if not self.fDBReseting:
            UpdateRecord(dbname, caseinfo, """status='ended(%d)'"""%(returncode), 'start_time=%f and pid= %d'%(starttime, pp.pid))
        return returncode #non-zero means failed
        #for debug print 'SERVER 2 WEB%s: ('%(str(conn)),response,')'
    def LoadRunCfg(self):
        from common import csvfile2dict
        self.runcfg = csvfile2dict('./manualrun.cfg')

    def OnRunManualTest(self,bench,sutlist):
        self.info(self.OnRunManualTest.__name__+' start')
        self.LoadRunCfg()
        runcfg = self.runcfg
        dbname =runcfg.get('db')
        tcpportpool = runcfg.get('tcppool')
        casedir = runcfg.get('casedir')
        suitedir= runcfg.get('suitedir')
        benchdir = runcfg.get('benchdir')
        defaultlogdir = runcfg.get('logdir')

        #UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%(50010))
        #UpdateRecord(dbname,tcpportpool,'status="in-used"','port=%d'%(50011))
        #UpdateRecord(dbname,tcpportpool,'status="in-used"','port=%d'%(50012))
        encoded=''
        try:

            #UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%(50010))
            tcpport,status = FetchOne(dbname,tcpportpool,'status="idle"')
            UpdateRecord(dbname,tcpportpool,'status="in-used"','port=%d'%tcpport)

            #sutlines ='<table border="0" width="100%" >\n<tr class="noborders">\n'
            selecttag = ""
            first = True
            selected = 'selected="selected" '
            sutbuttons =''
            for sut in  sutlist:
                if first !=True:
                    selected =''
                first=False
                selecttag += """<option value="%s" %s >%s</option>"""%(sut, selected ,sut)
                sutbuttons+='''<input value="%s" type="button" onClick="onOpenSutPage(%s ,'%s');">'''%(sut,str(tcpport),sut)
            import os
            if bench.find(os.sep)==-1:
                bench= '%s%s%s'%(benchdir, os.sep,bench)
            import time
            tm = time.strftime('CASE%Y-%m-%d %H:%M:%S',time.localtime())
            client= str(self.client_address)+tm
            client= client.replace("'",'').replace('(','').replace(')','_').replace(',','_').replace(' ','')
            encoded = self.LoadHTMLPage('./html/ManualTest4CaseGUI.html',[client, str(tcpport),client, str(tcpport),client,str(tcpport),client, client,selecttag, sutbuttons, bench ,bench])
            casename = 'mr'
            cmd= './runManualCase.py %d  %s %s '%(tcpport, casename ,bench)
            for sut in sutlist:
                cmd= cmd + '%s '%sut
            cmd +=';3.4'
            import threading
            th =threading.Thread(target=self.RunCase,args =[[cmd], defaultlogdir+"/manual", True])
            th.start()
        except Exception as e:
            encoded = "no idle tcp port is avaiable, can't launch test case"
            self.info(encoded)
        self.info(self.OnRunManualTest.__name__+' end')
        return encoded.encode(encoding='utf_8')
    def CheckCaseStatus(self,tcpport):
        from common import csvfile2dict
        runcfg = csvfile2dict('./manualrun.cfg')
        dbname =runcfg.get('db')
        tcpportpool = runcfg.get('tcppool')
        casedir = runcfg.get('casedir')
        suitedir= runcfg.get('suitedir')
        benchdir = runcfg.get('benchdir')
        defaultlogdir = runcfg.get('logdir')
        from CDatabase import FetchOne, UpdateRecord
        tcpport,status = FetchOne(dbname,tcpportpool,'port="%s"'%tcpport)
        return status

        UpdateRecord(dbname,tcpportpool,'status="idle"','port=%s'%(tcpport))
    def OnCaseEnd(self,tcpport):
        from common import csvfile2dict
        runcfg = csvfile2dict('./manualrun.cfg')
        dbname =runcfg.get('db')
        tcpportpool = runcfg.get('tcppool')
        casedir = runcfg.get('casedir')
        suitedir= runcfg.get('suitedir')
        benchdir = runcfg.get('benchdir')
        defaultlogdir = runcfg.get('logdir')
        from CDatabase import FetchOne, UpdateRecord
        UpdateRecord(dbname,tcpportpool,'status="idle"','port=%s'%(tcpport))

    def CaseRequest(self, host, tcpport, sut, cmd,expect='.+',wait=1):
        from CSocket import SendRequest2Server


        if self.CheckCaseStatus(tcpport)!='in-used':
            resp=''
            return resp.encode(encoding='utf_8')
        import json#import base64
        import re
        reFunction = re.compile('\s*FUN\s*:\s*(.+?)\s*\(\s*(.*)\s*\)|\s*(.+?)\s*\(\s*(.*)\s*\)',re.IGNORECASE)

        if sut=='__case__':
            m =  re.match(reFunction, cmd)
            if m:
                if m.group(1) !=None:
                    fun = m.group(1)
                    arg = m.group(2)
                else:
                    fun = m.group(3)
                    arg = m.group(4)
                arg = arg.split(',')
                cmd =arg
                cmd.insert(0, fun)
        else:
            cmd = ['ActionCheck', [sut,cmd,expect,str(wait)]]
        jcmd = json.dumps(cmd)
        resp =SendRequest2Server(host, int(tcpport) ,jcmd)
        if sut=='__case__' and cmd[0].find('EndCase')!=-1:
            try:
                self.OnCaseEnd(tcpport)
            except Exception as e:
                print(e)
                resp= '%s'%(str(e))
        #=======================================================================
        # if resp[0]=='b' and resp[1]=='"':
        #     resp = resp.replace('\\n','\n')
        #     resp = resp.replace('\\r','\r')
        #     resp = resp[2:-1]
        #=======================================================================
        resp+='\n'
        return resp.encode(encoding='utf_8')
    def onOpenSutPage(self,client, host, tcpport,sut):
        self.info(self.onOpenSutPage.__name__+' start')
        from CSocket import SendRequest2Server
        #import base64

        import json#import base64
        cmd = ['AddClient', client]
        action = json.dumps(cmd)
        resp =SendRequest2Server(host, int(tcpport) ,action)
        if resp=='':
            encoded = 'AddClient Failed: %s'%action
            print(encoded)


        print(resp)
        self.info(self.onOpenSutPage.__name__+' end')
        encoded = self.LoadHTMLPage('./html/ManualTest4SutGUI.html',[sut,client, str(tcpport),sut,client, str(tcpport),sut,client,sut])
        return encoded.encode(encoding='utf_8')
    def onRequestSutOutput(self, client, host, tcpport, sut):
        #self.info(self.onRequestSutOutput.__name__+' start')
        #if self.CheckCaseStatus(tcpport)!='in-used':
        #    resp=''
        #    return resp.encode(encoding='utf_8')
        from CSocket import SendRequest2Server


        import json#import base64
        cmd = ['RequestSUTOutput', client,sut]
        action = json.dumps(cmd)
        encoded =SendRequest2Server(host, int(tcpport) ,action)
        #encoded=encoded[2:-1]
        if encoded.startswith('"'):
            encoded= encoded[1:]
        if encoded.endswith('"'):
            encoded= encoded[:-1]
        encoded=encoded.replace('\\r\\n', '\n').replace('\n', '\r\n')
        return encoded.encode(encoding='utf_8')
    def OnCaseList(self):
        self.info(self.OnCaseList.__name__+' start')
        from os import listdir
        from os.path import isfile, join
        path = './html/case/'
        caselist=''
        onlyfiles = [ f for f in listdir(path) if (isfile(join(path,f) ) and not str(f).endswith('~')) ]
        onlyfiles = sorted(onlyfiles)
        CHECKED = 'CHECKED'
        for case in onlyfiles:
            line = '<input type="checkbox" name="casename" value="%s" %s/> %s <input id="ARGS" name="ARGS" style="width:200"  type="text" value="" rows="1"   autocomplete="on"> </a><br>\n'%(case,CHECKED,case)
            CHECKED =''
            caselist += line
        encoded = self.LoadHTMLPage('./html/SelectCaseList4Task.html', [caselist])
        #encoded = encoded%()
        self.info(self.OnCaseList.__name__+' end')
        return encoded.encode(encoding='utf_8')
    def ParseFormData(self, s):
        import re
        reP = re.compile('^(-+[\d\w]+)\r\n(.+)-+[\d\w]+-*', re.M|re.DOTALL)
        #s = '''-----------------------------186134213815046583202125303385\r\nContent-Disposition: form-data; name="fileToUpload"; filename="case1.csv"\r\nContent-Type: text/csv\r\n\r\n,ACTION,EXPECT,TIMEOUT,CASE OR COMMENTS\n[case1],,,,\n#var,\ncmd,${5}\ncmd2,${cmd2}\n#setup,,,,\ntel,pwd,],10\ntel,ls,],10,\n,ls,],10,\ntel,${cmd},],10,\n,${cmd2},],10,\n#!---,,,,\n\n\r\n-----------------------------186134213815046583202125303385--\r\n'''
        #rs = re.escape(s)
        rs =s
        m = re.match(reP, rs)
        print(rs)
        if m:
            print('match!')
            boundary = m.group(1)

            print(m.group(2))

            c = m.group(2)
            index =c.find(boundary)
            if index ==-1:
                pass
            else:
                c = c[:index]
            l = c.split('\r\n')
            print(l)
            attribute=l[0].split('; ')
            da={}
            la =attribute[0].split(':')
            da.update({la[0]:la[1]})
            for a in attribute[1:]:
                la=a.split('=')
                da.update({la[0]:la[1].replace('"','').replace('\'','')})
            data = '\r\n'.join(l[3:-1])
            filename = da['filename']
            if filename.find('\\')!=-1:
                filename=filename[filename.rfind('\\')+1:]
            else:
                filename=filename[filename.rfind('/')+1:]
            return (da['name'],filename,data)
        else:
            print('not match')
            return None
    def SaveFile(self, path,filename, data):

        fullfilename = '%s%s%s'%(path, os.path.sep, filename)
        if os.path.exists(fullfilename):
            historypath= '%s%shistory'%(path,os.path.sep)
            try:
                os.mkdir(historypath)
            except Exception as e:
                print(e)
            import time
            new_filename = '%s%s%s_%s'%(historypath, os.path.sep,filename,time.strftime("%Y%m%d%H%M%S", time.localtime()))
            with open(new_filename, 'w') as f:
                with open(fullfilename, 'r') as fo:
                    f.write(fo.read())

        with open(fullfilename, 'w') as f:
            f.write(data)

    def onUploadFile(self, type, filename, data):
        type=type.lower()
        encoded = '%s has been saved!'%(filename)
        if type=='case':
            self.SaveFile('./html/case', filename, data)
        elif type=='suite':
            self.SaveFile('./html/suite', filename, data)
        elif type == 'bench':
            self.SaveFile('./html/bench', filename, data)
        else:
            encoded = '%s has NOT been saved!'%(filename)
        return encoded.encode(encoding='utf_8')
    def longToInt(self, value):
        if value > 2147483647 :
            return (value & (2 ** 31 - 1))
        else :
            return value
    def onOpenSuiteList(self):
        path = './html/suite/'
        suitelist=''
        import sys,os
        os.path.isfile(path)
        onlyfiles = [ f for f in os.listdir(path) if os.path.isfile(os.path.sep.join([path,f])) ]
        onlyfiles = sorted(onlyfiles)
        CHECKED = 'CHECKED'

        for suite in onlyfiles:
            line = '<input type="radio" name="suitename" value="%s" %s/> %s </a><br>\n'%(suite,CHECKED,suite)
            CHECKED =''
            suitelist = suitelist+line
        encoded =self.LoadHTMLPage('./html/SuiteList.html', [suitelist])
        return encoded.encode(encoding='utf_8')
    def onSuiteSelected(self,suitename):
        from common import csvfile2array
        path = './html/suite/'
        suite = csvfile2array(os.path.sep.join([path,suitename]))
        newsuite = []
        for  i in suite:
            if len(i)>0 :
                if len(i[0])>0:
                    newsuite.append(i)
        suite = newsuite

        rangebutton = '''<form name="f1" onsubmit="onSuiteSelectedRun(); return false;">
        <p>Case Range: <input id="caserange" name="caserange" type="text" value="%d-%d" rows="1" cols="1" />
        <p>ARGs: <input id="suiteargs" name="suiteargs" type="text" value="" rows="1" cols="1" />
          <input name="go" value="Run" type="button" onClick="onSuiteSelectedRun();"></p>
        </form>'''%(1,len(suite))
        caselines = '<table border="1" width="100%" >\n<tr>\n<th>No.</th><th>CASE NAME</th><th>Action when Case Failed</th><th>MAX RETRY TIMES</th></tr>\n'
        index = 1
        for  case in suite:
            if len(case)==0:
                break
            elif len(case)==1:
                case.append('')
                case.append('')
            elif len(case)==2:
                case.append('')

            line = """<tr> <td>%d</td> <td>%s</td> <td> %s </td> <td> %s </td> </tr>\n"""%(index,case[0],case[1],case[2])
            index=index+1
            caselines = caselines+line
        encoded =self.LoadHTMLPage('./html/CaseInSuite.html', [suitename,suitename,rangebutton,caselines])

        return encoded.encode(encoding='utf_8')

    def onRunSuite(self,suitename,caserange, args, schedule=0.0):
        encoded ="Suite %s has been launched\nrange is %s\n Arguments:%s"%(suitename,caserange, str(args))
        from CTask import CTask
        args = str(args).split(',')
        import time, datetime
        from common import csvstring2array
        with open('./html/suite/%s'%suitename, newline='') as f:
            suitestring = f.read()
            index = 0
            for arg in args:
                suitestring= suitestring.replace("${%d}"%(index+1), arg)
        suite = csvstring2array(suitestring)
        newsuite = []
        for  i in suite:
            if len(i)>0 :
                if len(i[0])>0:
                    newsuite.append(i)
        suite = newsuite

        from CServer import CServer
        from CSocket import cmd2
        from common import csvfile2dict
        RunCfg = csvfile2dict('./manualrun.cfg')
        dbname =RunCfg['db']
        tcpportpool = RunCfg['taskpool']
        tcpport = FetchOne(dbname, tcpportpool, 'status="idle"')[0]
        time.sleep(1.5)
        try:
            svr = CServer('localhost', tcpport,'CTask', 'CTask',{}, 'IsAlive')
        except Exception as e:
            encoded="Suite %s has NOT been launched\nrange is %s\n Arguments:%s\nError info is:\n\t%s"%(suitename,caserange, ','.join(args), str(e))
            print(encoded)
            return encoded.encode(encoding='utf_8')
        UpdateRecord(dbname,tcpportpool,'status="in-used"','port=%d'%int(tcpport))
        t = svr.Handler
        t.LoadCaseInArray(suitename, suite,caserange, ','.join(args))

        #t.Load('CaseListFile')
        print(cmd2('localhost', tcpport, ['LoadCaseInArray',suitename,  suite, caserange,','.join(args) ]))
        dbname = RunCfg.get('db')
        taskinfo = RunCfg.get('taskinfo')
        #InsertRecord(dbname, tcppool, """50010, 'idle'""")
        import time
        starttime  = time.time()

        if not self.fDBReseting:
            InsertRecord(dbname, taskinfo, """%f, 0.0, %d,  '%s', 'started'"""%(starttime, tcpport,  "suite:%s range:%s arg:%s"%(suitename,caserange, ','.join(args)) ))


        import time
        time.sleep(schedule)
        try:
            t.Run()
        except Exception as e:
            endtime =time.time()
            svr.StopServer()
            UpdateRecord(dbname,taskinfo,'status="fail", end_time=%f'%(endtime),'start_time=%f'%(starttime))
            UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%int(tcpport))
            encoded = 'error: %s'%(str(e))
            return encoded.encode(encoding='utf_8')
        #print(cmd2('localhost', tcpport, ['Run']))
        while svr.IsHandlerAlive():
            time.sleep(5)
        svr.StopServer()
        endtime =time.time()
        UpdateRecord(dbname,taskinfo,'status="done", end_time=%f'%(endtime),'start_time=%f'%(starttime))
        UpdateRecord(dbname,tcpportpool,'status="idle"','port=%d'%int(tcpport))
        return encoded.encode(encoding='utf_8')
    def onDumpDB(self):
        import sqlite3
        dbname= 'sean.db'#sys.argv[1]
        import sys
        rtdb = sqlite3.connect(dbname)
        cu=rtdb.cursor()
        tables = cu.execute('''SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name; ''')
        ltable=list(tables)
        strtable =''
        strhtml = '<table border="0" align="left"><tr><td><table border="8" align="left"><tr><td>DataBase: %s</tr></td></table></td></tr><BR><tr><td>'%dbname
        for t in ltable:
            t = t[0]
            #print('-'*80)
            strtable = ''''''

            header = list(cu.execute("""PRAGMA table_info( %s )"""%t))
            line =''
            for h in header:
                line = line+ '<td>%s<br>%s</td>'%(h[1],h[2])
            header = '<tr>%s</tr>'%line
            allrecord = cu.execute('''select * from %s'''%t)
            table =''
            for r in allrecord:
                line=''
                for i in r:
                    line = line+'<td>%s</td>\n'%(i)
                table = table+'<tr>%s</tr>\n'%line

            strtable ='''
            <tr><td>
            <table id="%s" border="4" align='left'>
                <tr>
                    <td>Table: %s</td>
                </tr>
            </table>
            </td></tr>
            <tr><td>
            <table id="%s1" border="1" align='left'>
            %s
            %s
            </table>
            </td>
            </tr>
            <tr>
            <td>
            </td>
            </tr>

            '''%(t, t,t,header,table)
            strhtml = strhtml+strtable
        strhtml ='%s</table></table><br>'%strhtml
        encoded =self.LoadHTMLPage('./html/DumpDB.html', [dbname,strhtml])
        return encoded.encode(encoding='utf_8')
    def onResetDataBase(self):
        self.LoadRunCfg()
        self.fDBReseting=True
        self.RunCase(['CDatabase.py reset'])
        self.fDBReseting=False
        return 'DB reseted'.encode(encoding='utf_8')
    def RunScript(self, script, args=[]):


        exe_cmd = '%s %s'%(script, ' '.join(args))
        if script.find('.py')!=-1:
            exe_cmd = 'python3 '+exe_cmd
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
        self.info('PID: %d runcase(%s) has been launched, stdin(%s), stdout(%s)'%(pp.pid,exe_cmd,file_name_in,file_name_out))

        import time
        ChildRuning = True
        while ChildRuning:
            if pp.poll() is None:
                interval = 1
                time.sleep(interval)
            else:
                ChildRuning = False
        returncode = pp.returncode
        self.info('PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode))
        return returncode #non-zero means failed


    def do_POST(self):
        content_len = int(self.headers['Content-Length'])
        #self.queryString
        s = self.rfile.read(content_len)
        try:
            s=str(s,'UTF-8')
            req=urllib.parse.parse_qs(urllib.parse.unquote(s))
            print(req['REQIRETYPE'])
            if not self.logger :
                self.InitLogging()
            if req['REQIRETYPE'][0]=='SUTOUTPUTREQUEST':
                encoded = self.onRequestSutOutput(req['CLIENT'][0],'localhost',req['TCPPORT'][0],req['SUTNAME'][0])
            else:
                for key in req.keys():
                    self.info('%s: %s'%(str(key), str(req[key])))
                self.info(s)

                self.info(str(self.client_address)+' Call do_POST()')
                self.info('%s, %s, %s'%(str(self.command), str(self.path), str(self.request_version)))#,str(self.headers)

                if req['REQIRETYPE'][0]=='BenchList4ManualTest':
                    encoded = self.OnManualTestRequest()
                elif req['REQIRETYPE'][0]=='SutList4ManualTest':
                    encoded = self.OnManualTestSelectSUTs(req['BENCH'][0])
                elif req['REQIRETYPE'][0]=='RunManualTest':
                    encoded = self.OnRunManualTest(req['BENCH'][0],req['SUT'])
                elif req['REQIRETYPE'][0]=='CaseRequest':
                    encoded = self.CaseRequest(req['PORT'],req['CMD'],req['EXP'],req['WAIT'])
                elif req['REQIRETYPE'][0]=='CMD2CASE':
                    encoded = self.CaseRequest('localhost',req['TCPPORT'][0],req['TARGET'][0],req['CMD'][0])
                elif req['REQIRETYPE'][0]=='OPENSUTGUI':
                    encoded = self.onOpenSutPage(req['CLIENT'][0],'localhost',req['TCPPORT'][0],req['SUTNAME'][0])
                elif req['REQIRETYPE'][0]=='SuiteList':
                    encoded = self.onOpenSuiteList()
                elif req['REQIRETYPE'][0]=='SuiteSelected':
                    encoded = self.onSuiteSelected(req['suitename'][0])
                elif req['REQIRETYPE'][0]=='RunSuite':
                    if not req.get('args'):
                        arg = ''
                    else:
                        arg = req['args'][0]
                    import threading
                    th =threading.Thread(target=self.onRunSuite,args =[req['suitename'][0],req['range'][0],arg])
                    th.start()
                    encoded = 'Suite:(%s) has been launched!'.encode(encoding='utf_8')             #elif req['REQIRETYPE'][0]=='CaseList':
                #    encoded = self.OnCaseList()
                elif req['REQIRETYPE'][0]=='DumpDataBase':
                    encoded = self.onDumpDB()
                elif req['REQIRETYPE'][0]=='ResetDataBase':
                    encoded = self.onResetDataBase()
                else:
                    try:
                        requestline = self.requestline
                        import re
                        reScript=re.compile('POST\s+(.+)\s+HTTP.*', re.DOTALL)
                        m= re.match(reScript, requestline)
                        if m:
                            script = m.group(1).replace('%20', ' ')
                            self.RunScript(script,[])
                    except Exception as e:
                        encoded ='can\'t run script!'
                        encoded = encoded.encode(encoding='utf_8', errors='strict')


        except Exception as e:
            print(e)

            response = self.ParseFormData(s)
            if response:
                type, filename, data =response

                encoded = self.onUploadFile(type, filename, data)
            else:
                encoded ='ERROR: %s, Can\'t parse Form data: %s'%(str(e),s)
                encoded= encoded.encode(encoding='utf_8')
            try:
                requestline = self.requestline
                import re
                reScript=re.compile('POST\s+(.+)\s+HTTP.*', re.DOTALL)
                m= re.match(reScript, requestline)
                if m:
                    returncode =self.RunScript(m.group(1),[])
                    encoded ='script %s completed with return code %d!'%(m.group(1), returncode)
            except Exception as e:
                encoded ='can\'t run script!'
                encoded = encoded.encode(encoding='utf_8', errors='strict')

        self.send_response(200)
        self.send_header("Content-type", "text/html")#; charset=%s" % enc)
        self.end_headers()
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        shutil.copyfileobj(f,self.wfile)


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass