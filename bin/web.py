# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/6/17 
'''

import os, sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
libpath = os.path.sep.join([pardir,'lib'])
if libpath not in sys.path:
    sys.path.insert(0,libpath)
from WebSession import  WebSession
attr ={
    'BROWSER':''
}
web = WebSession('wb', attr)