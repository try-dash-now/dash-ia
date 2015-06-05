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
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll','MSVCP90.dll']
dist = setup(
    console=["../bin/ia.py",
                      "../bin/runTask.py",
                      "../bin/runWebServer.py",
                      "../bin/t.py",
                      ],
    windows = ['../bin/dash.py'],
    data_files= ['../bin/manualrun.cfg',
                   '../bin/run.cfg',
                   '../LICENSE.TXT',
                   ( 'bench',['../bench/local']),

                   ('case', []),
                   ('case', ['../case/case1.csv']),
                   ( 'case/manual', []),
                   ('suite', []),
                   ('suite', ['../suite/suite1.csv']),
                   ('report', []),
                   ('database',[]),
                   ('log',[]),
                   ('bin',[]),
                   ('lib',['../lib/case.cfg']),
                   ( 'lib/html', []),
                   ( 'lib/html', ['../lib/html/index.html']),
                   ( 'lib/html', ['../lib/html/dash.ico']),
                    ( 'log/manual', []),
                   ],
    options = {"py2exe":
                   {
                       "compressed": 2,
                      "optimize": 2,
                      "includes":[],# includes,
                      "excludes":[],# excludes,
                      "packages": [],#packages,
                      "dll_excludes": dll_excludes,
                      "bundle_files": 1,
                      "dist_dir": "dist",
                      "xref": False,
                      "skip_archive": False,
                      "ascii": False,
                      "custom_boot_script": '',
                    }
               }

)



folder = './dist'
for op in sys.argv:

    indexOfd = op.find('-d')
    if indexOfd !=-1:
        folder = sys.argv[sys.argv.index(op)+1]
        break




import shutil
targetDir = os.sep.join([folder, 'bin'])
for file in os.listdir(folder):
    sourceFile = os.path.join(folder,  file)
    targetFile = os.path.join(targetDir,  file)
    #cover the files
    if os.path.basename(sourceFile)=='LICENSE.TXT':
        continue
    if os.path.isfile(sourceFile):
        open(targetFile, "wb").write(open(sourceFile, "rb").read())
        os.remove(sourceFile)


















