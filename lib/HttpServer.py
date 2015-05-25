# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/5/22 
'''
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import os
import StringIO, cgi , urllib

class HttpHandler(BaseHTTPRequestHandler):
    logger=None
    hdrlog =None
    runcfg = None
    fDBReseting=False
    httpserver =None
    rootdir = None
    def __del__(self):
        #self.hdrlog.close()
        print('end http server')






    def list_dir(self, path, related_path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        content =""
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        #f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        content='<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        content+="<html>\n<title>Directory listing for %s</title>\n" % displaypath
        content+="<body>\n<h2>Directory listing for %s</h2>\n" % displaypath
        content+="<hr>\n<ul>\n"
        content+='''
        <SCRIPT>
    function post( id, dest )
        {
            element = document.getElementById(id);
            value = element.value
            params = 'script='+encodeURI(id)+'&arg='+encodeURI(value)
            var xmlhttp;

            if (window.XMLHttpRequest)
            {// code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp=new XMLHttpRequest();
            }
            else
            {// code for IE6, IE5
                xmlhttp=new ActiveXObject('Microsoft.XMLHTTP');
            }

            xmlhttp.onreadystatechange=function()
            {
                if (xmlhttp.readyState==4 && xmlhttp.status==200)
                {
                    setTimeout("window.close()",3000);
                }
            }
            xmlhttp.open("POST",dest,true);
            xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
            xmlhttp.send( params );
        }

        </SCRIPT>
        '''
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            input_button =""
            filename = urllib.quote(linkname)
            if related_path.startswith('/case') and os.path.isfile(fullname):
                input_button = """<input id=%s name="ARGS" style="width:200"  type="text" value="" rows="1"   autocomplete="on"> <input name="go" value="Run" type="button" onClick="post('%s', 'RunCase')";>"""%(filename,filename)
            content+='<li><a href="%s">%s</a>\n'% ('/'.join([related_path, urllib.quote(linkname)]), cgi.escape(displayname))+input_button
        content+="</ul>\n<hr>\n</body>\n</html>\n"

        return content
    def array2htmltable(self,Array):
        content = "<table   border='1' align='left' width=autofit  >"

        for sublist in Array:
            content += '  <tr><td>\n'
            content += '    </td><td>'.join([x if x!='' else '&nbsp;' for x in sublist ])
            content += '  \n</td></tr>\n'
        content += ' \n </table><br>'
        return  content
    def do_GET(self):
        home= "../lib/html/"
        root = '../'
        response = 200
        type = 'text/html'
        if self.path=='/':
            indexpage= open(home+ 'index.html', 'r')
            encoded=indexpage.read()
            encoded = encoded.encode(encoding='utf_8')
        elif self.path =='/favicon.ico':
            indexpage= open(home+'dash.ico', 'r')
            encoded=indexpage.read()
            type =  "application/x-ico"
        else:
            path = os.path.abspath(root)
            path = '/'.join([path, self.path])
            if  os.path.isfile(path):
                from common import csvfile2array
                arrary = csvfile2array(path)
                encoded = self.array2htmltable(arrary)
            else:
                encoded =self.list_dir(path, self.path)


        self.send_response(200)
        self.send_header("Content-type", type)
        self.end_headers()
        self.wfile.write(encoded)








    def LoadHTMLPage(self, filename, replace=[], Pattern4ESCAPE1='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT1#',Pattern4ESCAPE2='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT2#'):

        indexpage= open(filename, 'r')
        encoded=indexpage.read()
        encoded =encoded.replace('%s',Pattern4ESCAPE1 )
        encoded =encoded.replace('%',Pattern4ESCAPE2 )
        encoded =encoded.replace(Pattern4ESCAPE1,'%s' )

        for item in replace:
            encoded =encoded.replace('%s', item, 1)
        encoded =encoded.replace(Pattern4ESCAPE2, '%' )

        return encoded

    def RunScript(self, script, args=None):
            if not args:
                args =[]

            exe_cmd = '%s %s'%(script, ' '.join(args))
            if script.find('.py') != -1:
                exe_cmd = 'python '+exe_cmd
            import subprocess
            import tempfile
            pipe_input ,file_name_in =tempfile.mkstemp()
            pipe_output ,file_name_out =tempfile.mkstemp()
            pp = subprocess.Popen(exe_cmd,#sys.executable,
                         #cwd = os.sep.join([os.getcwd(),'..']),
                         stdin=pipe_input,
                         stdout=pipe_output,
                         shell=True
                         )
            print('PID: %d runcase(%s) has been launched, stdin(%s), stdout(%s)'%(pp.pid,exe_cmd,file_name_in,file_name_out))

            import time
            ChildRuning = True
            while ChildRuning:
                if pp.poll() is None:
                    interval = 1
                    time.sleep(interval)
                else:
                    ChildRuning = False
            returncode = pp.returncode
            print('PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode))
            return 'PID: %d runcase(%s) ended with returncode(%d)'%(pp.pid,exe_cmd, returncode) #non-zero means failed













    def ParseFormData(self, s):
        import re
        reP = re.compile('^(-+[\d\w]+)\r\n(.+)-+[\d\w]+-*', re.M|re.DOTALL)
        #s = '''-----------------------------186134213815046583202125303385\r\nContent-Disposition: form-data; name="fileToUpload"; filename="case1.csv"\r\nContent-Type: text/csv\r\n\r\n,ACTION,EXPECT,TIMEOUT,CASE OR COMMENTS\n[case1],,,,\n#var,\ncmd,${5}\ncmd2,${cmd2}\n#setup,,,,\ntel,pwd,],10\ntel,ls,],10,\n,ls,],10,\ntel,${cmd},],10,\n,${cmd2},],10,\n#!---,,,,\n\n\r\n-----------------------------186134213815046583202125303385--\r\n'''
        #rs = re.escape(s)
        rs =s
        m = re.match(reP, rs)
        print(rs)
        if m:
            print('match!')
            boundary = m.group(1)

            print(m.group(2))

            c = m.group(2)
            index =c.find(boundary)
            if index ==-1:
                pass
            else:
                c = c[:index]
            l = c.split('\r\n')
            print(l)
            attribute=l[0].split('; ')
            da={}
            la =attribute[0].split(':')
            da.update({la[0]:la[1]})
            for a in attribute[1:]:
                la=a.split('=')
                da.update({la[0]:la[1].replace('"','').replace('\'','')})
            data = '\r\n'.join(l[3:-1])
            filename = da['filename']
            if filename.find('\\')!=-1:
                filename=filename[filename.rfind('\\')+1:]
            else:
                filename=filename[filename.rfind('/')+1:]
            return (da['name'],filename,data)
        else:
            print('not match')
            return None










    def do_POST(self):
        content_len = int(self.headers['Content-Length'])
        #self.queryString
        self.path
        s = self.rfile.read(content_len)
        encoded=''
        try:
            s=str(s)
            import urlparse
            req = urlparse.parse_qs(urlparse.unquote(s))
            script = req['script'][0]
            arg = req['arg'][0]
            if self.path =='/RunCase':
                print(os.getcwd())
                encoded=self.RunScript('t.py', [script, arg])





        except Exception as e:
            print(e)

            response = self.ParseFormData(s)
            if response:
                type, filename, data =response

                encoded = self.onUploadFile(type, filename, data)
            else:
                encoded ='ERROR: %s, Can\'t parse Form data: %s'%(str(e),s)
                encoded= encoded.encode(encoding='utf_8')
            try:
                requestline = self.requestline
                import re
                reScript=re.compile('POST\s+(.+)\s+HTTP.*', re.DOTALL)
                m= re.match(reScript, requestline)
                if m:
                    returncode =self.RunScript(m.group(1),[])
                    encoded ='script %s completed with return code %d!'%(m.group(1), returncode)
            except Exception as e:
                encoded ='can\'t run script!'
                encoded = encoded.encode(encoding='utf_8', errors='strict')

        self.send_response(200)
        self.send_header("Content-type", "text/html")#; charset=%s" % enc)
        self.end_headers()
        self.wfile.write(encoded)



class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass