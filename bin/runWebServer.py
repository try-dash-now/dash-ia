__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import os,sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))

from HttpServer import ThreadingHttpServer, HttpHandler



if __name__=='__main__':    
    httpd=ThreadingHttpServer(('',8080), HttpHandler)
    
    print("Server started on 127.0.0.1,port 8080.....")     
    httpd.serve_forever() 