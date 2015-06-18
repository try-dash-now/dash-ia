#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-
import os
import sys

pardir =os.path.dirname(os.path.realpath(os.getcwd()))
libpath = os.path.sep.join([pardir,'lib'])
if libpath not in sys.path:
    sys.path.insert(0,libpath)
prodpath = os.path.sep.join([pardir,'product'])
if prodpath not in sys.path:
    sys.path.insert(1,prodpath)
from common import csvfile2dict
if __name__ == "__main__":
    returncode = 0
    try:

        runcfgfile = os.path.abspath('./run.cfg')
        runcfg = csvfile2dict(runcfgfile)
        dbname =runcfg.get('db')
        tcpportpool = runcfg.get('tcppool')
        casedir = runcfg.get('casedir')
        suitedir= runcfg.get('suitedir')
        benchdir = runcfg.get('benchdir')
        defaultlogdir = os.path.abspath(runcfg.get('logdir'))
        import sys
        print('format: t.py str_feature_name str_bench_name str_case_name [str_parameter1,str_parameter2 ....str_parameterN, bool_TroubleshootingWhenFail,str_case_log_dir] ')
        argvlen= len(sys.argv)
        if argvlen>6:
            pass
        elif argvlen== 6:
            sys.argv.append(False)
            sys.argv.append(defaultlogdir)
        elif argvlen ==5:
            sys.argv.append("FULL")
            sys.argv.append(False)
            sys.argv.append(defaultlogdir)
        elif argvlen ==4:
            sys.argv.append(str(os.path.basename(sys.argv[1])).replace(".csv", ""))
            sys.argv.append("FULL")
            sys.argv.append(False)
            sys.argv.append(defaultlogdir)
        elif argvlen ==3:
            sys.argv.append(str(os.path.basename(sys.argv[1])).replace(".csv", ""))
            sys.argv.append("FULL")
            sys.argv.append(False)
            sys.argv.append(defaultlogdir)
        else:
            print ('''format error, example: run.py  feature bench [case mode logdir]
case--case name, format is "[casename]"default is the feature file name without extension
mode--default is full, is one of [full,setup,run,teardown,setuprun,runteardown,setupteardown]
logdir--the log dir ,default is ../html/log/tmp''')
        print (sys.argv)
        bench= '%s%s%s'%(benchdir, os.sep,sys.argv[2])
        if sys.argv[2].find(os.sep)!=-1:
            feature=sys.argv[1]
        else:
            feature= '%s%s%s'%(casedir, os.sep,sys.argv[1])
        case=sys.argv[3]
        mode= sys.argv[4]
        TroulbeshootingWhenCaseFailed = sys.argv[len(sys.argv)-2]
        logdir = sys.argv[len(sys.argv)-1]
        name = '%s_%s_%s'%(os.path.basename(bench),os.path.basename(feature),case)
        import re
        name =re.sub(r'[^\w\\/@+\-:,|#]+', '', name)
        for arg in sys.argv[5 :len(sys.argv)-1]:
            name='%s_%s'%(name,arg)
        from Case import Case
        from common import LoadCaseFromCsv
        sut,steps,mode = LoadCaseFromCsv(bench,feature,case, mode, sys.argv)
        TestCase = Case(name=name, suts=sut, steps=steps,mode=mode, logdir=sys.argv[-1], DebugWhenFailed=False, caseconfigfile=runcfgfile)
        TestCase.RunCase(mode, 'setup.1', 'teardown.-1')
        try:
            TestCase.EndCase(True,True)
        except:
            pass

        import time
        print ("======================== CASE PASS ========================")
    except Exception as e:
        import traceback
        msg = traceback.format_exc()
        print(msg)
        print(e)
        print ("!!!!!!!!!!!!!!!!!!!!!!!! CASE FAIL !!!!!!!!!!!!!!!!!!!!!!!!")
        try:
            TestCase.EndCase(True,True)
        except:
            pass
        os._exit(1)
        #exit(1)

