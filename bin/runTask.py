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
#from Database import FetchOne, UpdateRecord


sreTry = sre.compile("^\s*try\s+([0-9]+)\s*", sre.I)
sreAbort = sre.compile("^\s*abort\s*", sre.I)
from Task import Task


if __name__=='__main__': 

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
    print('end..............')

    