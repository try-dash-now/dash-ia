# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/10 
'''
import unittest
import sys,os
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))
from Case import Case
from Server import Server
try:

    class TestStringMethods(unittest.TestCase):


        def test_Server(self):
            import json
            data = [1,2,3,'a','b', {'d1':'v1'}]
            data ='abcdef,2,3,4'
            jstring = json.dumps(data)
            print('json string:', jstring)
            jdata = json.loads(jstring)



            cmd ='telnet localhost'
            attr={'TIMEOUT': 10,'LOGIN': 'syu,assword:,10\nyxw123,~],20','CMD':'telnet localhost', 'SUT':'', 'EXP':'login:','LINEEND':"u''+chr(13)"}
            sut = {'tel':attr}
        #    import CCase
            port =50101
            svr = Server('localhost', port,'Case', 'Case',{'name':'abc', 'suts':sut,  'logdir':'../log', 'caseconfigfile':'../lib/case.cfg'}, 'IsAlive')
            from Socket import SendRequest2Server
            cmd = ['ActionCheck', ['tel', 'ping localhost', '.*', 1]]
            jcmd = json.dumps(cmd)
            rsp =SendRequest2Server('localhost', port, jcmd)
            cmd =['AddClient', '127.0.0.1_41715_CASE2014-12-2513:36:38']
            jcmd = json.dumps(cmd)
            rsp =SendRequest2Server('localhost', port, jcmd)
            cmd = ['EndCase', 1]
            jcmd = json.dumps(cmd)
            rsp =SendRequest2Server('localhost', port, jcmd)

            print(rsp)

            import time
            while svr.IsHandlerAlive():

                time.sleep(1)
            svr.StopServer()
except Exception as e:

    import traceback
    msg = traceback.format_exc()
    print(msg)
    print(e)
    raise e