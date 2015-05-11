__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import shlex
import re as sre
import csv
import io#StringIO
import sys,traceback
class csv2case(object):
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
    def __init__(self,filename="",casename=""):
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
        #s =self.RemoveComment(s)
        if self.Debug: print (s)
        s = io.StringIO.StringIO(s)
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
            #print "the command is :",row[1]
            #print row,len(row)
            #r = row

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
            if self.Debug:
                print (str("r[3]= %s"%str(r[3])))
            try:
                r[3]= int(r[3])
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
        if sre.match(self.reCaseEnd,line,sre.IGNORECASE):

            self.bFindCaseEnd = True
            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.bFindComment =True
            self.lastSUT =""
        elif sre.match(self.reVar,line,sre.IGNORECASE):

            self.bFindVar = True
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reSetup,line,sre.IGNORECASE):

            self.bFindVar = False
            self.bFindSetup =True
            self.bFindRun = False
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reRun,line,sre.IGNORECASE):

            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = True
            self.bFindTeardown = False
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reTeardown,line,sre.IGNORECASE):

            self.bFindVar = False
            self.bFindSetup =False
            self.bFindRun = False
            self.bFindTeardown = True
            self.bFindOnFail = False
            self.lastSUT =""
            self.bFindComment =True
        elif sre.match(self.reOnFail,line,sre.IGNORECASE):

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

    def DumpCase(self):
            if self.Debug!=True:
                return
            for i in self.Var:                
                print (i, len(i))
            print ("*"*5,"setup","*"*5)
            for i in self.Setup:
                print (i, len(i))
            print ("*"*5,"run","*"*5)
            for i in self.Run:
                print (i, len(i))
            print ("*"*5,"teardown","*"*5)
            for i in self.Teardown:
                print( i, len(i))
            print ("*"*5,"onfail","*"*5)
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
                elif sre.match(self.reCaseName,line,sre.IGNORECASE):
                    self.bFindCase = True
                    print( "find Case: ",casename,"at line %d"%self.LineNumber)
                    continue
                else:
                    #search for the beginning of the TestCase
                    continue
            if self.bFindCase==False:
                raise Exception("Case(%s) can't be found in file(%s)"%(casename, filename))
        except Exception as e:
            print ("\n\r"+"=22"*80)
            traceback.print_exc(file=sys.stdout)

def sustitude(mode = None, arg=None, var =None,step=None):
    if not mode:
        mode = 'full'
    if not arg:
        arg=[]
    if not var:
        var = []
    if not step:
        step = [[], [], []]
    if str(mode).upper()=='RUN':
        step[0]=[]
        step[2]=[]
    elif str(mode).upper()=='SETUP':
        step[1]=[]
        step[2]=[]
    elif str(mode).upper()=='TEARDOWN':
        step[1]=[]
        step[0]=[]
    elif str(mode).upper()=='SETUPRUN':
        step[2]=[]
    elif str(mode).upper()=='RUNTEARDOWN':
        step[0]=[]
    elif str(mode).upper()=='SETUPTEARODOWN':
        step[1]=[]

    larg = len(arg)
    lvar = len(var)
    lstep = len(step)
    for gi in range(larg):
        for i in range(lvar):
            var[i][0]=str(var[i][1]).replace("${%d}"%(gi), str(arg[gi]))
            var[i][1]=str(var[i][1]).replace("${%d}"%(gi), str(arg[gi]))
            
    if lvar>1:
        index = 0
        while index < lvar:
            sindex = index+1
            while sindex <lvar:
                var[sindex][0]= str(var[sindex][0]).replace("${%s}"%(var[index][0]), str(var[index][1]))
                var[sindex][1]= str(var[sindex][1]).replace("${%s}"%(var[index][0]), str(var[index][1]))
                sindex =+1
            index =+1
    index = 0
    i = 0    
    sut =[]
    while i <lstep:
        lsstep = len(step[i])
        while index <lsstep:
            for gi in range(larg):
                step[i][index ][0]= str(step[index][0]).replace("${%d}"%(gi), str(arg[gi]))
                step[i][index ][1]= str(step[index][1]).replace("${%d}"%(gi), str(arg[gi]))
                step[i][index ][2]= str(step[index][2]).replace("${%d}"%(gi), str(arg[gi]))
                
            for vi in range(lvar):
                step[i][index][0]= str(step[index][0]).replace("${%s}"%(var[vi][0]), str(var[vi][1]))
                step[i][index][1]= str(step[index][1]).replace("${%s}"%(var[vi][0]), str(var[vi][1]))
                step[i][index][2]= str(step[index][2]).replace("${%s}"%(var[vi][0]), str(var[vi][1]))
            try:
                sut.index(step[i][0])
            except Exception as e:
                sut.append(step[i][0])

            
    return sut, step

