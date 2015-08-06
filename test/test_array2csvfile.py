__author__ = 'Sean Yu'
'''created @2015/7/27'''


import unittest
import sys,os
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
print('\n'.join(sys.path))
from common import  array2csvfile
a =['error info:',
    ['cell21', 'cell22'],
    ['cell31', 'cell32'],
    'line4',
    ]

array2csvfile(a, 'c://logs/abc.csv')
