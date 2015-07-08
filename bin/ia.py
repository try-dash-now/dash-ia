


#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-

__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import os,sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
sys.path.append(os.path.sep.join([pardir,'product']))
print('\n'.join(sys.path))



suts={}
casename=''
import time

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





aa = '''CMD'''
from IAshell import IAshell

      
i =IAshell('TC',bench, sutnames,manuallogdir )
i.do_tab(False)
#i.setmode('fun')
#i.setsut('Sean3') 
#i.RunCmd('showme')
#i.RunCmd('showme money')
print('#'*80)
import traceback
while i.InteractionRunning:
    try:
        i.cmdloop()
        time.sleep(.1)
    except Exception as e:
        msg = traceback.format_exc()
        print(msg)
        
        
    
    
   

