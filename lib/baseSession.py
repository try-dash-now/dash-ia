__author__ = 'Sean Yu'
'''created @2015/7/2'''
import time
import re as sre
class baseSession(object):
    fSending = False
    sutname=None
    attrs =None
    seslog=None
    loginstep =None
    argvs=None
    kwargvs =None
    InteractionBuffer=None
    fInteractionMode=False
    InteractionMatch =None
    FailFlag=False # the flag means in Session's perspective view, case failed
    ErrorMessage =None # to store the error message
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
        self.InteractionBuffer=''
        self.InteractionMatch=''
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
        import re as sre
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
    def SetInteractionMode(self,flag):
        self.fInteractionMode=flag
    def AppendData2InteractionBuffer(self,data):
        self.InteractionBuffer+=data
        self.output = self.InteractionBuffer
    def StartInteractionMode(self,flag):
        self.fInteractionMode=flag
    def SendLine(self,command, clearbuffer=True,AntiIdle=False,Ctrl=False,Alt=False):
        pass
    def Expect(self,pat , wait=2, nowait=False):
        pass
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
    def Write2Csv(self, msgList,CsvFileName=None, path=None):
        '''
        msgList: if msgList is a list, then each element will be in a cell
                 if msgList is a string, then all chars will be written to a cell
        CSVFileName: a file name, default is None, means to create a SUT_NAME_.csv file, and write msg to it, similiar to SUT_NAME.log
        '''
        if not path:
            import os
            path =  os.path.dirname(self.seslog.name)

        from common import array2csvfile
        csvfile = self.seslog.name.replace('.log', '.csv')
        arrayToBeWritten = msgList
        if  isinstance( msgList, type('string')):
            arrayToBeWritten = [[msgList]]
        if CsvFileName:
            if CsvFileName.find('\\')!=-1 or CsvFileName.find('/')!=-1:
                csvfile = CsvFileName
            else:
                csvfile = os.path.sep.join([path,CsvFileName])
        array2csvfile(arrayToBeWritten, csvfile)

    def setFailFlag(self, Message):
        if not self.FailFlag:
            self.FailFlag = True
        if not self.ErrorMessage:
            self.ErrorMessage=[Message]#change the type
        else:
            self.ErrorMessage.append(Message)

