__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import os,sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))


from HttpServer import  ThreadingHttpServer, HttpHandler

httpd=ThreadingHttpServer(('',8080), HttpHandler)
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
try:
    s.bind(("", 1235))
    sq = socket(AF_INET, SOCK_DGRAM)
    sq.connect(("10.0.0.4", 1234))
    domain = getfqdn()
    hostip = sq.getsockname()[0]
    sq.close()
    from socket import *
    domain = getfqdn()
    #import os
    #user = os.getlogin()
    import getpass
    From = getpass.getuser()
except:
    pass
hostname =gethostname()

print("Server started on %s (%s),port 8080....."%(hostname,hostip))
httpd.serve_forever()
s.close()


