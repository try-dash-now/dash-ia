# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/11 
'''
import unittest
import sys,os
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))
try:
    class TestStringMethods(unittest.TestCase):
        def test_Task(self):

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
            #svr = Server('localhost', tcpport,'Task', 'Task',{}, 'IsAlive')
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
except Exception as e:

    import traceback
    msg = traceback.format_exc()
    print(msg)
    print(e)
    raise e
