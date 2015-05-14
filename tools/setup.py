# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/11 
'''
import os,sys
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))
from distutils.core import setup
import py2exe

setup(console=["../bin/ia.py"],
      data_files= ['../bin/manualrun.cfg',
                   ( 'bench',['../bench/local']),
                   ('case', []),
                   ('suite', []),
                   ('database',[]),
                   ('log',[]),
                   ('bin',[]),
                   ('lib',['../lib/case.cfg']),
                    ( 'log/manual', []),]

)















