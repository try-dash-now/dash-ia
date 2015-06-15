# -*- coding:  UTF-8 -*-

__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
"""
created 2015/5/8 
"""
import io,csv,re
DELIMITER = '[${PATTERN_NOT_EXIST}$]'
import time
class baseSession(object):
    sutname=None
    attrs =None
    seslog=None
    loginstep =None
    argvs=None
    kwargvs =None
    def __init__(self, name,attrs={},logger=None, logpath=None):
        self.argvs=[]
        self.kwargvs={}
        if logpath ==None:
            import os
            logpath = '.%s'%(os.path.sep)
        self.sutname=name
        self.attrs=attrs
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
    def CallFun(self,functionName,args=[], kwargs={}):
        functionName(*args, **kwargs)

    def GetFunArgs(self,*argvs, **kwargs):
        self.argvs=[]
        self.kwargvs={}
        #re-assign for self.argvs and self.kwargvs
        for arg in argvs:
            self.argvs.append(arg)
        for k in kwargs.keys():
            self.kwargvs.update({k:kwargs[k]})
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
                    self.argvs =[arg]

            arg =self.argvs
            kwarg = self.kwargvs
        else:
            IsCallFunction = False
            fun = cmd
        return (IsCallFunction,fun,arg,kwarg)
    def SLEEP(self,sec=1.0):
        time.sleep(float(sec))


def bench2dict(csvfile, delimiter='='):
    reComment = re.compile('\s*#', re.I)
    
    a =csvfile2array(csvfile)
    d={}

    for i in a:
        l = len(i)
        if l <2:
            continue
        name = str(i[0]).strip()
        if re.match(reComment,name):
            continue

        if l==2:
            name = str(i[0]).strip()
            value = i[1]
            d.update({name:value})
        else :
            name = str(i[0]).strip()
            if name=='':
                continue
            attr=i[1:]
            d.update({name:{}})
            
            for a in attr:
                if len(a)>2:
                    if re.match(reComment,a):
                        break
                    attrname, value= a.split(delimiter)
                    d[name].update({attrname.strip():value})

        
    return d    
def csvfile2dict(csvfile):
    a =csvfile2array(csvfile)
    d={}
    for i in a:
        if len(i)>1:
            d.update({str(i[0]).strip():str(i[1]).strip()})
    return d
def csvstring2array(csvstring):    
    lines= csvstring.replace('\\r\\n','\\n').split('\\n')
    a=[]
    for line in lines:
        csvfile= io.StringIO(unicode(line, "utf-8"))
        for row in csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL):
            a.append(row)
    return a
def csvfile2array(csvfile):
    a=[]
    if os.name!='nt':
        f= open(csvfile, 'r', newline='')
    else:
        f = open(csvfile,'r')
    #with open(csvfile,'r', newline='') as f:
    reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
    for row in reader:
        a.append(row)
    return a 
def array2csvfile(array, csvfile):

    with open(csvfile, 'w',newline ='') as f:  #,newline =''
        writer = csv.writer(f)
        for row in array:
            writer.writerow(row)   
import sys,logging, string
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.DEBUG):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
            
class CLogger(logging.Logger,object):
    stdout =None
    def __init__(self,name,level=logging.DEBUG):
        logging.Logger.__init__(self, name, level)
        self.stdout = sys.stdout
        #sys.stdout =self
    def write(self,data):
        #self.info(data)        
        #self.stdout.write(data) #issue RuntimeError: maximum recursion depth exceeded
        super(CLogger,self).info(data)
    def __del__(self):
        sys.stdout = self.stdout
        #sys.stdout.close()
    def info(self,data):
        super(CLogger,self).info(str(data))
        #self.stdout.write(str(data)+"\n")#issue RuntimeError: maximum recursion depth exceeded
        #self.stdout.flush()   
    def debug(self,data):
        super(CLogger,self).debug(str(data))
        #self.stdout.write(str(data)+'\n')#issue RuntimeError: maximum recursion depth exceeded
        #self.stdout.flush()   
    def errors(self,data):
        self.error(data)
    def error(self,data):
        super(CLogger,self).error(str(data))
        #self.stdout.write(str(data)+'\n')#issue RuntimeError: maximum recursion depth exceeded
        #self.stdout.flush()
    def flush(self):
        self.stdout.flush()     
import re as sre
import os, shlex
class CCSV2Case(object):
    Debug= False
    Var = []
    Setup = []
    Run = []
    Teardown=[]
    OnFail =[]
    FileName =""
    CaseName =""
    reCaseName  = None #
    lastSUT = ""
    reCaseEnd   = None #sre.compile("^[\s]*#[\s]*!---[\s]*",sre.I)
    reVar       = None #sre.compile("^[\s]*#[\s]*VAR[\s]*",sre.I)
    reSetup     = None #sre.compile("^[\s]*#[\s]*SETUP[\s]*",sre.I)
    reRun       = None #sre.compile("^[\s]*#[\s]*RUN[\s]*",sre.I)
    reTeardown  = None #sre.compile("^[\s]*#[\s]*TEARDOWN[\s]*",sre.I)
    reOnFail    = None #sre.compile("^[\s]*#[\s]*ONFAIL[\s]*",sre.I)
    LineNumber = 0
    logger =None
    BenchInfo=None
    ARGV=[]
    VAR =[]
    sut={}
    MODE=None
    def __init__(self,benchname='', filename="",casename="",argv=[]):
        self.BenchInfo = bench2dict(benchname)
        self.ARGV=argv
        self.reCaseName  = sre.compile("^[\s]*\[[\s]*%s[\s]*\]"%casename,sre.I)
        self.reCaseEnd   = sre.compile("^[\s]*#[\s]*!---[\s]*",sre.I)
        self.reVar       = sre.compile("^[\s]*#[\s]*VAR[\s]*",sre.I)
        self.reSetup     = sre.compile("^[\s]*#[\s]*SETUP[\s]*",sre.I)
        self.reRun       = sre.compile("^[\s]*#[\s]*RUN[\s]*",sre.I)
        self.reTeardown  = sre.compile("^[\s]*#[\s]*TEARDOWN[\s]*",sre.I)
        self.reOnFail    = sre.compile("^[\s]*#[\s]*ONFAIL[\s]*",sre.I)
        self.reComment    = sre.compile("^[\s]*#[\s]*[\S]*",sre.I)

        self.Var = []
        self.Setup = []
        self.Run = []
        self.Teardown=[]
        self.OnFail =[]
        self.FileName = filename
        self.CaseName = casename
    def RemoveComment(self,s):
        l = shlex.split(s,comments=True)
        #print shlex.commenters
        return " ".join(l)
        
    def ParseVar(self ,s):
        NewVar = self.ParseCommand(s,VarSegment=True)
        if len(NewVar)>1:
            if NewVar[0]=="":
                return
            for s in self.Var:
                if s[0]==NewVar[0]:
                    raise Exception("Variable (%s) has been re-assigned, please check line %d in case (%s) of file (%s)\n"%(NewVar[0],self.LineNumber,self.CaseName,self.FileName ))
            self.Var.append([NewVar[0],NewVar[1]])

    def ParseCommand(self, s,VarSegment=False):
        if self.bFindComment:
            return
        s = io.StringIO(unicode(s, "utf-8"))
        reader = csv.reader(s,delimiter=',')
        r =[]
        #print "="*100,"\n",s,"\n"
        for row in reader:
            for element in row:
                r.append(element.strip())
            if r[0]=="":#SUT is empty, it means this SUT is same as SUT of the previous line
                if self.lastSUT!= "":#last SUT is not empty 
                    if  not VarSegment: r[0]= self.lastSUT
                else:
                    raise Exception( "No SUT has been assigned in line %d %s"%(int(self.LineNumber),s))
            else:#record the last SUT
                self.lastSUT = r[0]

        number_col= len(r)
        if number_col>3:
            pass
        elif number_col ==3:
            if  not VarSegment: 
                r.append("")
                r[3]=300
        elif number_col ==2:
            if  not VarSegment: r.append("")
            if  not VarSegment: r[3]=300#r.append("0")
        elif number_col ==1:
            if  not  VarSegment: r.append("")
            if  not VarSegment: r.append("")
            if not  VarSegment: r[3]=300#r.append("0")

        if not VarSegment: 
            r[3] = str(r[3]).strip()
            if len(str(r[3]))==0:
                r[3]=300
            try:
                r[3]= float(r[3])
            except: 
                r[3] = 300
        return r
    def Add2Setup(self,s):        
        NewStep = self.ParseCommand(s)
        if len(NewStep)>1:
            self.Setup.append(NewStep)
    def Add2Run(self,s):
        NewStep = self.ParseCommand(s)
        if len(NewStep)>1:
            self.Run.append(NewStep)
    def Add2Teardown(self,s):
        NewStep = self.ParseCommand(s)
        if len(NewStep)>1:
            self.Teardown.append(NewStep) 
    def Add2OnFail(self,s):
        NewStep = self.ParseCommand(s)
        if len(NewStep)>1:
            self.OnFail.append(NewStep)
    def TestSeg(self, line, index):
        if sre.match(self.reCaseEnd,line):

            self.bFindCaseEnd = True
            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.bFindComment =True
            self.lastSUT =""
        elif sre.match(self.reVar,line):
            self.bFindVar = True
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reSetup,line):

            self.bFindVar = False
            self.bFindSetup =True
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reRun,line):
            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = True
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reTeardown,line):

            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = True
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reOnFail,line):
            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = True
            self.lastSUT ="" 
            self.bFindComment =True
        elif sre.match(self.reComment,line):
            self.bFindComment = True 
        else:
            self.bFindComment = False
            if self.Debug:
                print ("context: line, or comments, blank line...",index,line)
    def DumpCase(self):
            if self.Debug!=True:
                return
            print ("*"*5,self.CaseName,"*"*5)
            print ("*"*5,"Var","*"*5)
            for i in self.Var:                
                print (i, len(i))
            print ("*"*5,"setup","*"*5)
            for i in self.Setup:
                print (i, len(i))
            print( "*"*5,"run","*"*5)
            for i in self.Run:
                print (i, len(i))
            print ("*"*5,"teardown","*"*5)
            for i in self.Teardown:
                print( i, len(i))
            print( "*"*5,"onfail","*"*5)
            for i in self.OnFail:
                print (i, len(i))
            print ("*"*5,self.CaseName ," End","*"*5)
    def PopulateCase(self,filename, casename=None):
        if casename!=None:
            self.reCaseName  = sre.compile("^[\s]*\[[\s]*%s[\s]*\]"%casename,sre.I)
        self.Var = []
        self.Setup = []
        self.Run = []
        self.Teardown=[]
        self.OnFail =[]
        self.FileName = filename
        self.CaseName = casename
        try :
            #f =os.open(filename, "r")
            self.bFindCase = False
            self.bFindVar =False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.bFindCaseEnd = False
            self.bFindComment =False

            self.LineNumber = 0
            for line in open(filename, "r"):
                line = """%s"""%line
                if self.bFindCase and self.Debug:
                    print (line)
                self.LineNumber = self.LineNumber +1    
                if self.bFindCase==True:
                    self.TestSeg(line, self.LineNumber)
                    if self.bFindCaseEnd:
                        break
                    elif self.bFindComment:
                        continue
                    elif self.bFindVar:
                        self.ParseVar(line)
                    elif self.bFindSetup:
                        self.Add2Setup(line)
                    elif self.bFindRun:
                        self.Add2Run(line)
                    elif self.bFindTeardown:
                        self.Add2Teardown(line)
                    elif self.bFindOnFail:
                        self.Add2OnFail(line)
                    else:#just comments or blank line
                        continue         
                elif sre.match(self.reCaseName,line):
                    self.bFindCase = True
                    print ("find Case: ",casename,"at line %d"%self.LineNumber)
                    continue
                else:
                    #search for the beginning of the TestCase
                    continue
            if self.bFindCase==False:
                raise Exception("Case(%s) can't be found in file(%s)"%(casename, filename))
        except Exception as e:          
            import traceback
            msg = traceback.format_exc()
            print(msg)
            raise BaseException("Case(%s) can't be found in file(%s):%s"%(casename, filename, e.__str__()))
    def GetMode(self,mode):
        try:            
            if str(mode).upper() =="SETUP":
                self.MODE = "SETUP"
                self.Run=[]
                self.Teardown=[]                    
            elif str(mode).upper() =="RUN":
                self.MODE = "RUN"
                self.Setup=[]  
                self.Teardown=[]   
            elif str(mode).upper() =="TEARDOWN" :
                self.Run=[]
                self.Setup=[] 
            elif str(mode).upper() =="FULL":
                self.MODE = "FULL"
            elif str(mode).upper() =="NOTEARDOWN" or str(mode).upper() =="SETUPRUN"  :
                self.Teardown=[]   
                self.MODE = "SETUPRUN"
            elif str(mode).upper() =="LOG":
                self.Setup=[] 
                self.Run=[]        
                self.Teardown=[]   
                self.MODE = "LOG"
        except Exception as e:
            raise    
            
    def PopulateVar(self):
        try:
            var = self.Var#self.TESTCASE["VAR"]
            index = 0
            counter = 0

            for gi in range(len(self.ARGV)):
                for i in range(len(var)):
                    var[i][1]=str(var[i][1]).replace("${%d}"%(gi), str(self.ARGV[gi]))            

            if len(var)<2:
                #self.Var.append(var)
                return
            #there are more than 2 variables have been defined
            tmpvar=[]
            index = 0
            for v in var: 
                index = index +1               
                tmpvar.append(v)
                for i in var[index:]:
                    print ("index is %d, %s"%(index,str(i))) 
                    if index+1<len(var)-1:               
                        var[index+1][1]= str(var[index+1][1]).replace("${%s}"%(v[0]), str(v[1]))
            self.Var=tmpvar    
            for i in range(len(var)):            
                tmp = re.findall("\${([\s\S]+?)}", str(var[i][1]))
                for group in tmp:
                    v = self.BenchInfo[str(group)]
                    #v = self.ImportVarFromBench(str(group))
                    if self.Debug: print( str(v))
                    var[i][1]= str(var[i][1]).replace("${%s}"%(group), str(v)) 
                
            self.Var = var[:]
        except Exception as e:
            print (str(e))

            raise
    def PopulateCommand(self):
        try:
            if len(self.Var)==1:
                if len(self.Var[0])==0:
                    return
                name = self.Var[0][0][0]
                if name!='':
                    value = self.Var[0][0][1]
                    for index,v in enumerate(self.Setup):
                        for i3,v3 in enumerate(v):
                            self.Setup[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    for index,v in enumerate(self.Run):
                        for i3,v3 in enumerate(v):
                            self.Run[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    for index,v in enumerate(self.Teardown):
                        for i3,v3 in enumerate(v):
                            self.Teardown[index][i3]= str(v3).replace("${%s}"%(name), str(value))
#                     for index,v in enumerate(self.TESTCASE["FAILLOG"]):
#                         for i3,v3 in enumerate(v):
#                             self.TESTCASE["FAILLOG"][index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    for gi in range(len(self.ARGV)):
                        for index,v in enumerate(self.Setup):
                            for i3,v3 in enumerate(v):
                                self.Setup[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                        for index,v in enumerate(self.Run):
                            for i3,v3 in enumerate(v):
                                self.Run[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                        for index,v in enumerate(self.Teardown):
                            for i3,v3 in enumerate(v):
                                self.Teardown[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    #rvar = reversed(self.Var)
                    rvar = reversed(self.Var)
                    for name,value in rvar:
                        for index,v in enumerate(self.Setup):
                            for i3,v3 in enumerate(v):
                                self.Setup[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                        for index,v in enumerate(self.Run):
                            for i3,v3 in enumerate(v):
                                self.Run[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                        for index,v in enumerate(self.Teardown):
                            for i3,v3 in enumerate(v):
                                self.Teardown[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    #===========================================================
                    # for index,v in enumerate(self.TESTCASE["FAILLOG"]):
                    #     for i3,v3 in enumerate(v):
                    #         self.TESTCASE["FAILLOG"][index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    #===========================================================
            else:
                rvar = reversed(self.Var)

                for name,value in rvar:
                    for index,v in enumerate(self.Setup):
                        for i3,v3 in enumerate(v):
                            self.Setup[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    for index,v in enumerate(self.Run):
                        for i3,v3 in enumerate(v):
                            self.Run[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    for index,v in enumerate(self.Teardown):
                        for i3,v3 in enumerate(v):
                            self.Teardown[index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    #===========================================================
                    # for index,v in enumerate(self.TESTCASE["FAILLOG"]):
                    #     for i3,v3 in enumerate(v):
                    #         self.TESTCASE["FAILLOG"][index][i3]= str(v3).replace("${%s}"%(name), str(value))
                    #===========================================================
                for gi in range(len(self.ARGV)):
                    for index,v in enumerate(self.Setup):
                        for i3,v3 in enumerate(v):
                            self.Setup[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    for index,v in enumerate(self.Run):
                        for i3,v3 in enumerate(v):
                            self.Run[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    for index,v in enumerate(self.Teardown):
                        for i3,v3 in enumerate(v):
                            self.Teardown[index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    #===========================================================
                    # for index,v in enumerate(self.TESTCASE["FAILLOG"]):
                    #     for i3,v3 in enumerate(v):
                    #         self.TESTCASE["FAILLOG"][index][i3]= str(v3).replace("${%s}"%(gi), str(self.ARGV[gi]))
                    #===========================================================
        except Exception as e:
            raise("FAIL", "CDasHLog::ParseCommand() failed: %s"%(str(e)))  
    def ImportSUT(self):
        sutdic={}
        for key in self.BenchInfo.keys():
            if type(self.BenchInfo.get(key)) is dict:
                sutdic.update({key:self.BenchInfo.get(key)})
        return sutdic
    def GetSUT(self):   
        try:  
            sut =[]
            #self.sut.update({"BENCH": self.BENCH})
            for s in self.Setup:
                if s[0] not in sut:
                    sut.append(s[0])
            for s in self.Run:
                if s[0] not in sut:
                    sut.append(s[0])  
            for s in self.Teardown:
                if s[0] not in sut:
                    sut.append(s[0])
                                
            sutinbench = self.ImportSUT()
            for i in sut:
                if sutinbench.get(i):
                    self.sut.update({i:sutinbench[i]})
                else:
                    self.TestPass = False
                    raise Execption("(%s) in TestCase (%s) is not defined in Bench file (%s)"%(i,self.CaseName,sut["BENCH"]))
        except Exception as e:
            import traceback
            msg = traceback.format_exc()
            print(msg)
            raise Exception( "GetSUT() failed: %s"%(str(e)))
def LoadCaseFromCsv(bench,csvfile,casename, mode, argv=[]):
    case = CCSV2Case(bench, csvfile,casename, argv)
    case.PopulateCase(csvfile, casename)
    case.GetMode(mode)
    case.PopulateVar()
    case.PopulateCommand()
    case.GetSUT()
    return case.sut,[case.Setup,case.Run,case.Teardown],case.MODE

def DumpDict(dicts):
    import operator
    d = {}
    s=''

    key =dicts.keys()
    key = sorted(key)
    for k in key:
        n = k
        o= dicts[k]
        s+='\t%s: %s\n'%(repr(n),repr(o).replace('\\\\', '\\'))
    return s
import inspect
import sys, traceback
def DumpStack(e):

    exc_type, exc_value, exc_traceback = sys.exc_info()
    str = traceback.format_exception(exc_type, exc_value,exc_traceback)
    str = ''.join(str)
    str=str.replace('\n', '\n*\t') 
    
    trace= inspect.trace()
    lastframe = trace[-1][0]  

    locals=  DumpDict(lastframe.f_locals).replace('\n','\n*\t')        
    globals= DumpDict(lastframe.f_globals).replace('\n','\n*\t')      
              
    return '%s\n*\t%s\n*\tglobals=> %s\n*\tlocals => %s\n*Traceback:\n*%s\n%s'%('*'*80,e.__str__().replace('\n','\n*\t'), globals,locals,str,'*'*80)


if __name__=='__main__':
    unittest.main()
    a =csvstring2array('one,two,three\nline2,line2-2')
    print(a)

    array2csvfile(a,'a.csv')
    print(csvfile2array('a.csv'))

    sys.argv=[sys.argv[0],'./bench/local','./case/case1.csv','case1', 'full','cmd1']
    sut,steps,mode = LoadCaseFromCsv('./bench/local','./case/case1.csv','case1', 'full', sys.argv)


    
