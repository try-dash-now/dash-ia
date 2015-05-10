#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
from Socket import startTCPServer,Rx, Tx, EncodeMsg,SendRequest2Server
import json
import inspect
class Server(object):
    '''start TCP server, listen on a TCP port of a given host, and initialize an instance of class Handler,
    receive message from tcp port, and pass it to instance of class Handler, 
    Attributes is a string in form of csv, for each section, the form is 'attributeName=attributeValue'
    returns what instance of class Handler returns'''
    Socket= None # the socket for TCP listening
    Handler=None # the instance of the given class, TCP message received by TCP thread, and pass to this instance, and response will be sent back
    bEnd    =False #flag of this instance, if it's True, then TCP daemon thread will be ended 
    thWait4Request =None
    thCase =None
    IsHandlerAliveFun=''
    host = None
    port = None
    def InitHandler(self, ClassName, attributes={},ModuleName =''):
        if ModuleName== '':
            ModuleName =ClassName
        ModuleName = __import__(ModuleName)
        handlerClass = ModuleName.__getattribute__(ClassName)          

        import inspect
        (args, varargs, keywords, defaults) =inspect.getargspec(handlerClass.__init__)
        argument=list(defaults)
        while argument.__len__()<args.__len__()-1:
            argument.insert(0,None)
        for k in attributes.keys():
            argument[args.index(k)-1]= attributes[k]
         
        self.Handler= handlerClass(*argument)
    
    def __init__(self,host, listenningPort,Module, Handler,Attributes, IsAlive):
        self.host=host
        self.port = listenningPort
        self.Socket = startTCPServer(host ,listenningPort)
        self.IsHandlerAliveFun=IsAlive
        if self.Socket:
            import threading
            self.thWait4Request =threading.Thread(target=self.ListenningTcpPort,args =[])
            self.thWait4Request.start()
            #self.ListenningTcpPort()
        else:
            print("can't start tcpserver (host=%s, listenningport= %s, handler= %s)"%(host,listenningPort,Handler))
            return
        self.InitHandler(Handler, Attributes, Module)
        
    
    def CallFunction(self, functionName, args=[]):
            fun = self.Handler.__getattribute__(functionName)            
            (argns, varargs, keywords, defaults) =inspect.getargspec(fun)
            argument=[]
            if defaults:
                argument=list(defaults)
            
            while argument.__len__()<argns.__len__():#
                argument.insert(0,None)
            #argument[0]=self.Handler
            index = 0
            #while index <=argns.__len__+1:
            for a in args:
                argument[index+1]= args[index]
                index =index+1
                
            argument= argument[1:]
            result = fun(*argument)
            return result
            
    def Wait4Request(self,conn):
        
        try: 
            request= Rx(conn)         
            request =json.loads(request)
            FunctionName = request[0]
            Args = request[1:]
            response = 'Done'
            response= self.CallFunction(FunctionName, Args)
            if response !='':
                response =json.dumps(response)
            Tx(conn,response) 
        except Exception as e:
            
            response= 'Error to call function in Server: %s\nFunctionName: %s , Args: %s'%(e.__str__, FunctionName, Args)
            response =json.dumps(response) 
            Tx(conn,response) 
            #return e)

        try:
            conn.close()
        except Exception as e:
            response= 'Error to call function in Server' 
            response =json.dumps(response) 
            Tx(conn,response)
            conn.close()
            return response
          
    def ListenningTcpPort(self):
        import threading
        while not self.bEnd:
        #Accepting incoming connections
            try:
                conn, addr = self.Socket.accept()
                th =threading.Thread(target=self.Wait4Request,args =[conn])
                th.start()            
            except Exception as e:    
                if e.__str__()==   '[Errno 22] Invalid argument':
                    pass
                else:    
                    print('error in Server::Wait4Request')
    def IsHandlerAlive(self):
        return self.CallFunction(self.IsHandlerAliveFun)
    def StopServer(self):
        self.bEnd=True
        import json
        cmd = ['EndCase', 1]
        jcmd = json.dumps(cmd)
        rsp =SendRequest2Server(self.host, self.port, jcmd)
