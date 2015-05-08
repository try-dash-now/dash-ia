# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/8 
'''

import unittest
import sys,os
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))


class TestStringMethods(unittest.TestCase):
    def test_WinSession(self):
        from WinSession import WinSession
        cmd = 'telnet 192.168.1.1'
        attr={'TIMEOUT':180,'LOGIN': 'admin,assword:,30\nadmin,>,30','CMD':cmd, 'LINEEND':u''+chr(13), 'EXP':'name:' }
        s = WinSession('sut_local',attr)
        command='SendLine("abcddddddddddddd",AntiIdle=True)'
        s.SendLine('command', True, False)
        s.SendLine('command2', True, False)
        (ActionIsFunction,action,arg,kwarg) = s.ParseCmdInAction(command)
        s.CallFun(action, arg, kwarg)
        s.EndSession()
