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
try:

    class TestStringMethods(unittest.TestCase):


        def test_csvstring2array(self):
            if __package__ is None:
                #import sys
                #from os import path
                #sys.path.append(os.path.sep.join([os.getcwd(),'..','lib']))
                #sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
                from common import csvstring2array, csvfile2array, LoadCaseFromCsv
            else:
                from ..lib.common import csvfile2array, csvstring2array
            a =csvstring2array('one,two,three\nline2,line2-2')
            print(a)
            #array2csvfile(a,'a.csv')
            print()
            pardir =os.path.dirname(os.path.realpath(__file__))
            b = csvfile2array(os.path.sep.join([pardir, 'a.csv']))
            print(b)

            sys.argv=[sys.argv[0],'../bench/local','../case/case1.csv','case1', 'full','cmd1']
            sut,steps,mode = LoadCaseFromCsv('../bench/local','../case/case1.csv','case1', 'full', sys.argv)



except Exception as e:

    import traceback
    msg = traceback.format_exc()
    print(msg)
    print(e)
    raise e