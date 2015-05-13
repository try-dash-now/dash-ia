#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-

__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import os,sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))

aa = '''CMD'''
import telnetlib
import traceback
from Case import Case
import sys
print(sys.path)
suts={}
casename=''
import time
import threading
import os

from common import csvfile2dict
print('CWD:',os.getcwd())
runcfg = csvfile2dict('./manualrun.cfg')
dbname =runcfg.get('db')
tcpportpool = runcfg.get('tcppool')
benchdir = runcfg.get('benchdir')
defaultlogdir = runcfg.get('logdir')
manuallogdir = runcfg.get('manuallogdir')
casename = 'tc'+time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())
benchname = sys.argv[1]
sutnames = sys.argv[2:len(sys.argv)]
print (sys.argv)
#    def __init__(self,name,suts,CasePort=50001, steps=[[],[],[]],mode='FULL',DebugWhenFailed=False,logdir='./',caseconfigfile='./case.cfg'):
if benchname.find(os.sep)==-1:
    bench= '%s%s%s'%(benchdir, os.sep,benchname)
else:
    bench = benchname    


from Case import Case
#from Server import Server
#name,suts,CasePort=50001, steps=[[],[],[]],mode='FULL',DebugWhenFailed=False,logdir='./',caseconfigfile='./case.cfg'
from common import bench2dict




import json
import re
import time
from cmd import Cmd
class Interaction(Cmd):
    tabend='enable'
    lastCmdIssueTime = 0.0
    sutname='tc'
    history_cmd = []
    index=0
    QureyOutput=True
    benchinfo=None
    QureyInterval =1.0
    tc = None
    client = 'interaction'
    thQureyOut=None
    sut={}
    PauseOut=False
    prompt='\n(tc)>>>'#''#'\n>>>'
    quoting = '"'
    InteractionOutput=''
    InteractionRunning= True
    cmdlist = []
    defaultfunction= 'action'
    mode='cli'
    currentIndex = 0
    casename=None
    UpdatingOutput=True
    MoreHistory= False
    cmdbank = None
    
    def h(self):
        return self.history()
    def history(self):
        index = 1
        total = len(self.cmdlist)
        lineInPage= 15
        if total>lineInPage:
            self.MoreHistory=True
        block = 1
        print(self.prompt, 'total %d command in history'%total)
        while index <=total:
            cmd = self.cmdlist[index-1]
            if (block*lineInPage)>=index:
                print('\t%3d\t%s\t\t%s'%(index, cmd[0],str(cmd[1])))
                index +=1
            else:
                print(self.prompt,'"q" to quit, any key to view more')
                ch = sys.stdin.read(1)
                #ch = getch()
                
                if ch=='q':
                    break
                block+=1
                
    def loadcmd(self, filename):
        with open(filename ,'r') as f:
            cmd = f.readlines()
            self.cmdbank=[]
            for c in cmd:                
                self.cmdbank.append(c)
                
    def dump(self):
        index = 1
        total = len(self.cmdbank)
        lineInPage= 15
        if total>lineInPage:
            self.MoreHistory=True
        block = 1
        print(self.prompt, 'total %d command in history'%total)
        while index <=total:
            cmd = self.cmdbank[index-1]
            if (block*lineInPage)>=index:
                print('\t%d\t %s'%(index, cmd))
                index +=1
            else:
                print(self.prompt,'"q" to quit, any key to view more')
                ch = sys.stdin.read(1)
                #ch = getch()
                
                if ch=='q':
                    break
                block+=1        
    def run(self,index, sut=None):
        if sut==None:
            sut=self.sut
        else:
            self.setsut(sut)
        index =int(index)
        if 0<int(index)<len(self.cmdbank)+1:
            if len(self.cmdbank[index-1])>0:
                mode = self.mode
                try:
                    return self.RunCmd(self.cmdbank[index-1])
                except:
                    pass
                self.mode = mode        
    def index(self,index):
        index =int(index)
        if 0<int(index)<len(self.cmdlist)+1:
            if len(self.cmdlist[index-1])>2:
                fun = self.cmdlist[index-1][7]
                real_vars= self.cmdlist[index-1][8]
                timeStr = time.strftime("_%Y%m%d_%H%M%S", time.localtime())
                nowTime =time.time()
                interval = nowTime - self.lastCmdIssueTime 
                self.lastCmdIssueTime=nowTime
                newcmd = self.cmdlist[index-1]
                newcmd[ 4]=timeStr
                newcmd[5]=interval
                
            #[self.sutname, "%s(%s)"%(self.defaultfunction,args), '.*', 1.0, timeStr, interval, data, fun, real_vars]
                self.cmdlist.append(newcmd)
                
                return fun(*real_vars)

                
        
    def getCurrentIndex(self):
        return self.currentIndex
    def exit(self,name='tc'):
        self.do_Exit(name)
    def tab(self,flag=None):
        self.do_tab(flag)
    def do_tab(self, flag=None):
        if flag==None or flag =='':
            flag = 'disable'
        self.tabend =flag
    def do_Exit(self, name ='tc'):
        #, killProcess=True
        self.InteractionRunning=False
        self.QureyOutput=False
        import csv
        MAX_LENGTH_OF_CELL =256
        csvfile='%s%s%s.csv'%('./html/case'.replace('/', os.path.sep), os.path.sep,name)
        #0    sut     1 action      2  expect      3 waittime    4 time    5 interval6raw  7fun 8 aurgs  
        case = [
                ['[%s]'%name],
                ['#VAR'],
                ['#SETUP']] + self.cmdlist+[
                ['#RUN'],
                ['#TEARDOWN'],
                ['#!---']
                ]
        with open(csvfile, 'w') as f:
            writer = csv.writer(f)
            for row in case:
                maxlen= 0
                for item in row[:6]:
                    if type(item)!=type(''):
                        item=str(item)
                    l = len(item)
                    if l> maxlen:
                        maxlen = l
                if maxlen > MAX_LENGTH_OF_CELL:
                    index = 0
                    block =0
                    maxcol = 6#len(row)
                    newrow =[]
                    while index <maxlen:
                        for i in range(maxcol):
                            newrow.append(row[i][block:(block+1)*MAX_LENGTH_OF_CELL]) 
                        writer.writerow(newrow)
                        block+=1
                        index=block*MAX_LENGTH_OF_CELL
                        
                else:
                    writer.writerow(row[:6])   
            #writer.writerow(['#!---'])
        
        
        
#         with open('%s%s%s.csv'%(self.tc.LogDir, os.path.sep,name),'w', newline='\r\n') as f:
#             index = 1  
#             f.write("#index\tinterval(s)\ttime\tcmd\tfun\targuments\r\n")
#             
#             for line in self.cmdlist:   
#                  #0    sut     1 action      2  expect      3 waittime    4 time    5 interval6raw  7fun 8 aurgs       
#                 f.write('%d\t%.2f\t%s\t%s\t%s\t%s\r\n'%(index, 
#                                                         line[4], 
#                                                         str(line[3]),
#                                                         line[0], 
#                                                         str(line[1]), 
#                                                         str(line[2])
#                                                         )
#                         )
#                 index+=1
        self.tc.EndCase(force=True, killProcess=True)
        exit()

    def __init__(self,casename,sutnames):
        self.benchinfo = bench2dict(bench)
        #self.benchinfo = benchinfo
        self.casename =casename
        self.sut ={}
        for sutname in sutnames:
            self.sut.update({sutname:self.benchinfo[sutname]})
        steps=[[],[],[]]
        mode ='FULL'
        self.tc= Case(casename,self.sut,steps=[[],[],[]],mode='FULL',DebugWhenFailed=False,logdir=manuallogdir,caseconfigfile='../lib/case.cfg')
        self.thQureyOut = threading.Thread(target=self.QureyOutput)
        self.thQureyOut.start() 
        self.client ='interaction'
        self.tc.AddClient(self.client)      
        self.tc.troubleshooting()
        nowTime =time.time()
        self.lastCmdIssueTime=nowTime
        Cmd.__init__(self, 'tab', sys.stdin, sys.stdout)
        self.use_rawinput=True
        #import readline
        #readline.set_completer_delims('\t\n')
#     def do_set(self,name):
#         print(name)
    def do_setmode (self,mode):  
        mode = mode.lower()
        if mode in ('cli','fun'):
            self.mode= mode
            return 'current mode is %s'%self.mode
               
    def do_setsut(self,sutname='tc'):
        if sutname =='':
            sutname='tc'
        if self.sut.get(sutname) or sutname =='tc' or sutname =='__case__':
            self.sutname=sutname
            self.prompt= '\n(%s)>>>'%self.sutname
            return 'current SUT: %s'%(self.sutname)
        else:
            return 'sutsut(\'%s\') is not defined'%self.sutname
    def postcmd(self,stop, line):
        if stop!=None and len(str(stop))!=0:
            self.InteractionOutput+='\n'+self.prompt+str(stop)+self.prompt
            #print(self.InteractionOutput,end='')
        return None 


    def completedefault(self, *ignored):
        #print(ignored)
        if self.sutname!='tc':
        #
            self.onecmd(ignored[1]+'\t')
            #i.cmdqueue=[]
            #pass
            #self.RunCmd(ignored[1]+'\t')
        return []#Cmd.completedefault(self ,ignored)
        
        
    def precmd(self,line):
        #print('line:',line)
        temp =line.strip().lstrip()
        if self.sutname!='tc':
            if line==' ':
                self.RunCmd(line)
            elif temp=='':
                self.RunCmd(line)
            elif temp.lower()=='help' or temp=='?':
                self.RunCmd(line)
                line= ''
        #print(self.InteractionOutput,end='')
        return line      
    def default(self,line):
        #print('line: %s======'%line)
        try:
            #print('@@@line is:%s=='%line)
            if line[-1]=='\t':
                print("@"*80)
            if self.sutname!='tc':
                
                if self.tabend!='disable':
                    line+='\t'             
                    
                self.RunCmd(line)
                #i.cmdqueue=[]
                #time.sleep(.1)
        except Exception as e:
            msg = traceback.format_exc()
            print(msg)
    def emptyline(self):
        pass
        #print('empty line')
        #self.RunCmd('')
        
    def QureyOutput(self):

        while self.InteractionRunning:
            if not self.PauseOut:
                if self.sutname!='tc':
                    output = self.tc.RequestSUTOutput(self.client, self.sutname)
                    if len(output)!=0 and self.UpdatingOutput :
                        print('\n\t'+output.replace('\n', '\n\t'), self.prompt)
            if len(self.InteractionOutput)   :
                print(self.InteractionOutput)
            self.InteractionOutput=''
            import time
            time.sleep(self.QureyInterval)

    def IARunCmd(self,data):
        import shlex
        lex = shlex.shlex(data)
        lex.quotes = '"'
        lex.whitespace_split = True
        cmd=list(lex)
        reQuoting=re.compile('\s*"(.*)"', re.DOTALL)             
        for i in range(0, len(cmd)):
            m = re.match(reQuoting, cmd[i] )                
            if m:                    
                cmd[i]=m.group(1) 
        funname = cmd[0]
        i_arg = cmd[1:]
        fun = self.__getattribute__(funname)            
        import inspect
        (def_args, def_varargs, def_keywords, def_defaults) =inspect.getargspec(fun)

        def_args=def_args[1:]
        if def_defaults!=None  :  
            real_vars =list(def_defaults)
        else:
            real_vars=[]
        
        def_len = len(def_args)

        while len(real_vars)<def_len:
            real_vars.insert(0, None)
        index =0
        for a in i_arg:
            real_vars[index]=a
            index+=1      

        response =fun(*real_vars)
        return response
    def pause(self):
        self.UpdatingOutput=False
    def resume(self):
        self.UpdatingOutput=True
    def RunCmd(self,data):
        mode =self.mode
        reIA = re.compile('\s*i\.(.+)')
        m = re.match(reIA, data)
        if m :
            response = self.IARunCmd(m.group(1))       
            
        else:
            import shlex
            if self.sutname =='tc':
                tmpdata =data.strip()
                if tmpdata=='':
                    return
                lex = shlex.shlex(data)
                lex.quotes = self.quoting
                lex.whitespace_split = True
                cmd=list(lex)
                reQuoting=re.compile('\s*"(.*)"', re.DOTALL)             
                for i in range(0, len(cmd)):
                    m = re.match(reQuoting, cmd[i] )                
                    if m:                    
                        cmd[i]=m.group(1) 
                if len(cmd)>0:
                    fun = cmd[0]
                    i_arg = cmd[1:]
                    fun = self.__getattribute__(fun)
            else:
                reFun= re.compile('\s*(sut\.)(.*)', re.DOTALL) 
                mfun = re.match(reFun, data)                
                funname = self.defaultfunction
                if mfun :
                     mode ='fun'
                     data= mfun.group(2)
#                     funname = mfun.group(1)
#                     funname = funname.strip()
#                     argstring = mfun.group(2)
# 
#                     lex = shlex.shlex(argstring)
#                     lex.quotes = self.quoting
#                     lex.whitespace_split = True
#                     i_arg=list(lex)                    
                
                fun = self.tc.__getattribute__(funname)
                
            import inspect
            (def_args, def_varargs, def_keywords, def_defaults) =inspect.getargspec(fun)
    
            def_args=def_args[1:]
            real_vars=[]
            if def_defaults!=None:  
                real_vars =list(def_defaults)
            
            def_len = len(def_args)
            if self.sutname =='tc':
                while len(real_vars)<def_len:
                    real_vars.insert(0, None)
                index =0
                for a in i_arg:
                    real_vars[index]=a
                    index+=1
                response = fun(*real_vars)  
            else:
                minlen = def_len
                if mode =='fun':
                    lex = shlex.shlex(data)
                    lex.quotes = self.quoting
                    lex.whitespace_split = True
                    cmd=list(lex)
                    if len(cmd)>0:
                        funname = cmd[0]
                        funname = funname.strip()
                        newinput = '%s(%s)'%(funname, ', '.join(cmd[1:]))
                    else:
                        newinput= data
                    real_vars[0]=self.sutname
                    real_vars[1]= newinput
                    real_vars[2]='.*'
                    real_vars[3]= 0.1
                    
                elif mode == 'cli':
                    real_vars[0]=self.sutname
                    real_vars[1]= data
                    real_vars[2]='.*'
                    real_vars[3]= 0.1
                  
                timeStr = time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())  
                nowTime =time.time()
                interval = nowTime - self.lastCmdIssueTime 
                self.lastCmdIssueTime=nowTime
                if self.defaultfunction in ('action', 'ActionCheck'):
                              #0    sut     1 action      2  expect      3 waittime    4 time    5 interval6raw  7fun 8 aurgs
                    newcmd = [self.sutname, real_vars[1], real_vars[2], real_vars[3], timeStr, interval, data, fun, real_vars]
                else:
                    args= ",".join(real_vars)
                                    #0sut         1  action                       2exp   3wait 4time     5 inter   6raw  7 fun 8 augrs
                    newcmd = [self.sutname, "%s(%s)"%(self.defaultfunction,args), '.*', 1.0, timeStr, interval, data, fun, real_vars]
                
                self.cmdlist.append(newcmd)
                response =fun(*real_vars)
        if response!=None and len(str(response))!=0:
            self.InteractionOutput+=self.InteractionOutput+'\n'+self.prompt+str(response)+self.prompt

    def showme(self,data='hello'):
        print(data)
        return data
        
           
    
        
        
        

      
i =Interaction('TC',sutnames)   

#i.setmode('fun')
#i.setsut('Sean3') 
#i.RunCmd('showme')
#i.RunCmd('showme money')
print('#'*80)

while i.InteractionRunning:
    try:
        i.cmdloop()
        time.sleep(.1)
    except Exception as e:
        msg = traceback.format_exc()
        print(msg)
        
        
    
    
   
