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

if __name__=='__main__':
    from common import DumpStack
    try:
        try :
            abc='str, abc'
            import inspect
            print(globals())
            print(locals())
            trace= inspect.trace()
            lastframe = trace[-1][0]
            locals= repr(lastframe.f_locals).replace('\\\\', '\\')
            globals= repr(lastframe.f_globals).replace('\\\\', '\\')
            print(locals)
            print(globals)
            raise 'abc'

        except Exception as e:
            def dumpenv(env):
                import operator
                d = {}
                s=''
                key =env.keys()
                key = sorted(key)
                for k in key:
                    n = k
                    o= env[k]
                    s+='\t%s: %s\n'%(repr(n),repr(o).replace('\\\\', '\\'))
                print(s)
                return d
            dumpenv(locals())
            def dump_into_ns(env,*x):
                class A:
                    def __init__(self):
                        for n,o in env.items():
                            vars(self).update({n: o})

                return A(*x)


            a = 19
            b = 'Monday'
            c = 'Wednesday'

            print()
            def ftry(x,y):
                palat = 'obastey'
                a = x -1
                b = y +100
                c = x*y -8
                return dump_into_ns(locals(),a,b,c)


            import sys,traceback
            h = dump_into_ns(globals())
            exc_type, exc_value, exc_traceback = sys.exc_info()
            str = traceback.format_exception(exc_type, exc_value,exc_traceback)
            str = ''.join(str)
            str=str.replace('\n', '\n*\t')

            trace= inspect.trace()
            lastframe = trace[-1][0]
            locals= repr(lastframe.f_locals).replace('\\\\', '\\')
            globals= repr(lastframe.f_globals).replace('\\\\', '\\')
            from common import csvstring2array
            d =csvstring2array(locals)
            print(d)




        cmd = 'telnet 192.168.1.112'
        attr={'TIMEOUT':180,'LOGIN': 'test,assword:,30\nadmin,>,30','CMD':cmd, 'LINEEND':u''+chr(13), 'EXP':'name:', 'SUT':'' }

        #attr={'TIMEOUT': 10,'LOGIN': 'syu,assword:,10\nyxw123,~],20','CMD':'telnet 192.168.1.112' 'EXP':'login:','LINEEND':"u''+chr(13)"}
        sut = {'tel':attr}
        tcpport =50001
        ip = '192.168.1.110'
        from Server import Server

        svr = Server(ip, tcpport,'Case', 'Case',{'name':'abc', 'suts':sut,  'logdir':'../log', 'caseconfigfile':'../lib/case.cfg'}, 'IsAlive')
        c = svr.Handler
        try :
            raise 'abc'

        except Exception as e:
            s =DumpStack(e)
            print(s)
        print(c.pp('SUTs'))
        #c.ActionCheck(['telLocal','pwd','~]',10])
        c.troubleshooting()
        client='192.168.1.100_61429_CASE2014-07-1702:20:12'
        resp =c.AddClient(client)
        resp = c.RequestSUTOutput(client,"tel")
        c.ActionCheck(['tel','ping localhost','.*', 1])
        c.ActionCheck(['tel','try 3:ctrl:c','SLV1 >', 30])
        #time.sleep(10)
        #resp =c.ActionCheck(['__case__', 'RequestSUTOutput("192.168.1.100_55710_CASE2014-07-1719:42:25""'])
        #resp =c.ActionCheck(['__case__', 'RequestSUTOutput("192.168.1.100_55710_CASE2014-07-1719:42:25""'])
        #resp =c.RequestSUTOutput(client,'tel')
        #time.sleep(10)
        #resp =c.RequestSUTOutput(client,'tel')
        #    c.ActionCheck(['telLocal','SLEEP(20.0)','~]',30])
        #c.ActionCheck(['telLocal','TRY 2:pwd','no:abc',30])
        #c.ActionCheck(['telLocal','TRY 2:noaction:pwd','nowait:no:abc',30])
        #import base64
        import json
        cmd =['RequestSUTOutput', client, 'tel']
        jcmd =json.dumps(cmd)
        from CSocket import SendRequest2Server
        resp = SendRequest2Server(ip, tcpport, jcmd)
        print(resp)
        #time.sleep(2)
#        resp = SendRequest2Server(ip, tcpport, jcmd)
        c.EndCase(True)
        svr.StopServer()
    except Exception as e:

        print(DumpStack(e))
        print(e.__str__())
        msg = traceback.format_exc()
        print(msg)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!CASE Failed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        exit(1)

    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!CASE End!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    exit(0)