#! /usr/bin/env python3
# -*- coding:  UTF-8 -*-

import socket
MAX_LENGTH_OF_MSG= 1024-1-2 
from common import DumpStack

def startTCPServer(host='localhost', port=50000):
    #Sock = socket.socket()
    #Binding socket to a address. bind() takes tuple of host and port.
    
    Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    Sock.bind((host, int(port)))
    #Listening at the address
    Sock.listen(0) #5 denotes the number of clients can queue    
    return Sock

def Rx(conn):
    try:
        EndOfMsg=False
        rcvdata=None
        msg=[]
        #conn.settimeout(1.5)        
        while not EndOfMsg :
            rcvdata = conn.recv(1024)#.decode() # 1024 stands for bytes of data to be received
            if len(rcvdata)>0:
                EndOfMsg=int(ord(rcvdata[0]))
                MsgLength = int(ord(rcvdata[1]))*255+ int(ord(rcvdata[2]))
                data = rcvdata[3:]
                data = list(data)
                msg=msg+data 
        
        msg = ''.join(e for e in msg)  
        tmpmsg = msg.split(',')
        #=======================================================================
        # #print('CSocket::Rx Msg:')
        # for seg in tmpmsg:
        #     try:
        #         print('\t%s'%(base64.b64decode(seg).decode()))
        #     except:
        #         print('\t%s'%seg)
        # print('CSocket::Rx Msg end')
        #=======================================================================

        return msg
    except Exception as e:
        response= ('Rx() Failed:\n%s'%(DumpStack(e).replace('\n','\t\n'))) 
        #print(response)
        return response
def EncodeMsg(data='', EndOfMsg=1):
    data= list(data)
    length= len(data)                
    data.insert(0,chr(int(length%255)))
    data.insert(0,chr(int(length/255)))
    data.insert(0,chr(EndOfMsg))
    data =''.join(e for e in data)
    #data= str(data).encode(encoding = 'utf_8' , errors='strict')#encoding='utf_8', errors='strict')
    return data
        
def Tx(conn,msg):  
    global MAX_LENGTH_OF_MSG        
    try:
        msg=list(msg)
        block= int(len(msg)/MAX_LENGTH_OF_MSG)
        index = 0
       # 'h', 'o', 's', 't', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '2', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '6', '4', '6', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '3', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '5', '6', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '4', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '6', '0', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '5', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '5', '3', ' ', 'm', 's', '\\', 'r', '\\', 'n', '\\', 'r', '\\', 'n', '-', '-', '-', ' ', 'l', 'o', 'c', 'a', 'l', 'h', 'o', 's', 't', ' ', 'p', 'i', 'n', 'g', ' ', 's', 't', 'a', 't', 'i', 's', 't', 'i', 'c', 's', ' ', '-', '-', '-', '\\', 'r', '\\', 'n', '5', ' ', 'p', 'a', 'c', 'k', 'e', 't', 's', ' ', 't', 'r', 'a', 'n', 's', 'm', 'i', 't', 't', 'e', 'd', ',', ' ', '5', ' ', 'r', 'e', 'c', 'e', 'i', 'v', 'e', 'd', ',', ' ', '0', '%', ' ', 'p', 'a', 'c', 'k', 'e', 't', ' ', 'l', 'o', 's', 's', ',', ' ', 't', 'i', 'm', 'e', ' ', '4', '4', '1', '8', 'm', 's', '\\', 'r', '\\', 'n', 'r', 't', 't', ' ', 'm', 'i', 'n', '/', 'a', 'v', 'g', '/', 'm', 'a', 'x', '/', 'm', 'd', 'e', 'v', ' ', '=', ' ', '0', '.', '2', '5', '3', '/', '0', '.', '3', '4', '4', '/', '0', '.', '6', '4', '6', '/', '0', '.', '1', '5', '3', ' ', 'm', 's', '\\', 'r', '\\', 'n', 'S', 'L', 'V', '1', '>', '"']
        while index <=block:                
            index =index+1
            EndOfMsg=0
            if index>block:
                EndOfMsg=1
            data = msg[(index-1)*MAX_LENGTH_OF_MSG:(index)*MAX_LENGTH_OF_MSG]
            data =EncodeMsg(data, EndOfMsg)
            s=''
            for c in data[4:]:
                try:
                    c = chr(c)
                except:
                    c = c
                s+=c
            s.replace('\n','\n\t')
            #print('CSocket::Tx Msg:')
            #print('\t',s)
            #print('CSocket::Tx Msg end')
            conn.send(data)

    except Exception as e:
        import traceback
        errormessage = traceback.format_exc()
        print(errormessage)
        print('Tx():%s: msg(%s), block:%d'%(str(e),  ''.join(msg), block))

def SendRequest2Server(host,port, msg): 
    try:
        import socket
        #print(host,port,msg)
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,int(port)))
        global MAX_LENGHT_OF_MSG
        block= int(len(msg)/MAX_LENGTH_OF_MSG)
        index = 0
        while index <=block:
            #print('index: %d, total block:%d'%(index, block))
            index =index+1
            EndOfMsg=False
            if index>block:
                EndOfMsg=True
            data = msg[(index-1)*MAX_LENGTH_OF_MSG:(index)*MAX_LENGTH_OF_MSG]
            data =EncodeMsg(data, EndOfMsg)
            sock.send(data)
    
        EndOfMsg=False
        rcvdata=None
        msg=[]
        msg = Rx(sock)
        sock.close()
        return msg
    
    except Exception as e:
        print(e)
        return str(e)

def cmd2(host, port, cmd):
    import json
    jcmd =json.dumps(cmd)
    from CSocket import SendRequest2Server  
    resp = SendRequest2Server(host, port, jcmd)
    return resp

if __name__=='__main__':
    msg = ['"', 'h', 'o', 's', 't', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '2', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '6', '4', '6', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '3', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '5', '6', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '4', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '6', '0', ' ', 'm', 's', '\\', 'r', '\\', 'n', '6', '4', ' ', 'b', 'y', 't', 'e', 's', ' ', 'f', 'r', 'o', 'm', ' ', '1', '2', '7', '.', '0', '.', '0', '.', '1', ':', ' ', 'i', 'c', 'm', 'p', '_', 'r', 'e', 'q', '=', '5', ' ', 't', 't', 'l', '=', '6', '4', ' ', 't', 'i', 'm', 'e', '=', '0', '.', '2', '5', '3', ' ', 'm', 's', '\\', 'r', '\\', 'n', '\\', 'r', '\\', 'n', '-', '-', '-', ' ', 'l', 'o', 'c', 'a', 'l', 'h', 'o', 's', 't', ' ', 'p', 'i', 'n', 'g', ' ', 's', 't', 'a', 't', 'i', 's', 't', 'i', 'c', 's', ' ', '-', '-', '-', '\\', 'r', '\\', 'n', '5', ' ', 'p', 'a', 'c', 'k', 'e', 't', 's', ' ', 't', 'r', 'a', 'n', 's', 'm', 'i', 't', 't', 'e', 'd', ',', ' ', '5', ' ', 'r', 'e', 'c', 'e', 'i', 'v', 'e', 'd', ',', ' ', '0', '%', ' ', 'p', 'a', 'c', 'k', 'e', 't', ' ', 'l', 'o', 's', 's', ',', ' ', 't', 'i', 'm', 'e', ' ', '4', '4', '1', '8', 'm', 's', '\\', 'r', '\\', 'n', 'r', 't', 't', ' ', 'm', 'i', 'n', '/', 'a', 'v', 'g', '/', 'm', 'a', 'x', '/', 'm', 'd', 'e', 'v', ' ', '=', ' ', '0', '.', '2', '5', '3', '/', '0', '.', '3', '4', '4', '/', '0', '.', '6', '4', '6', '/', '0', '.', '1', '5', '3', ' ', 'm', 's', '\\', 'r', '\\', 'n', 'S', 'L', 'V', '1', '>', '"']

    aaa = EncodeMsg(msg)
    #resp =SendRequest2Server('localhost', 50010 ,'dump("abc")')
    #print(resp)
    #resp =SendRequest2Server('localhost', 50010 ,'''"tel,ActionCheck([tel','ls','~]',30])"''')
   #bad print(SendRequest2Server('localhost', 50010 ,'''tel,ActionCheck([tel','ls','~]',30]),'''))

    print(SendRequest2Server('localhost', 50010 ,'''__case__,"ActionCheck(['tel','ls',']',2])",.,2,,,'''))
    #print(SendRequest2Server('localhost', 50010 ,'''tel,"ActionCheck(['tel','ls',']',2])",.,2,,,'''))
    # good
    print(SendRequest2Server('localhost', 50010 ,'''tel,ls,],10,,,,'''))
     
    print("Socket client end!!!!!!!!!!!!")        