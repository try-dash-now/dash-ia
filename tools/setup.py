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

dist = setup(console=["../bin/ia.py",
                      "../bin/runTask.py",
                      "../bin/runWebServer.py",
                      ],
      data_files= ['../bin/manualrun.cfg',
                   ( 'bench',['../bench/local']),
                   ('case', []),
                   ( 'case/manual', []),
                   ('suite', []),
                   ('report', []),
                   ('database',[]),
                   ('log',[]),
                   ('bin',[]),
                   ('lib',['../lib/case.cfg']),
                   ( 'lib/html', []),
                   ( 'lib/html', ['../lib/html/index.html']),
                    ( 'log/manual', []),]

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

    if os.path.isfile(sourceFile):
        open(targetFile, "wb").write(open(sourceFile, "rb").read())
        os.remove(sourceFile)














