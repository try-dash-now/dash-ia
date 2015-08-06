__author__ = 'Sean Yu'
'''created @2015/6/16'''
import os, sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
libpath = os.path.sep.join([pardir,'lib'])
if libpath not in sys.path:
    sys.path.insert(0,libpath)
import inspect
from Case import Case
caseInit = inspect.getsource(Case.__init__)
print(caseInit)



#dump description of function
import pydoc
des = pydoc.help(Case.__init__)
class testclass( object):
    '''class description'''
    def fun1(self,aaa,
             bbb,
             ccc='aaa'):
        '''fun1 description
        line2
        line3
        line4'''
        print(aaa)
    def fun2(self):
        '''fun2 description'''
        print('function2')
    def doc(self, name):
        return  pydoc.help(name)


obj = testclass()
aaa =obj.doc(obj.fun1)



members = dir(obj)
print('#'*16)
pydoc.Doc()
des =pydoc.describe(obj)
print(des)
print('#'*16)
for m in sorted(members):
    if m.startswith('__'):
        pass
    else:
        print(m+'\n\t')
        fundef = inspect.getsource(eval('obj.%s'%m))
        fundefstr = fundef[:fundef.find(':')]
        listoffun =fundef.split('\n')
        print(fundefstr)
        ret = eval('obj.%s.__doc__'%m)
        if ret:
            print('\t'+'\n\t'.join(ret.split('\n')))
