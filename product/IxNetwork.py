'''
@author: speng
'''
'''
2015/7/2 Sean,
        add logging of IxNetwork
        redirect tcl 'puts'
        derive IxNetwork from a common Tcl class
'''


import os
import sys
pardir =os.path.dirname(os.path.realpath(os.getcwd()))
#pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
sys.path.append(os.path.sep.join([pardir,'product']))
print('\n'.join(sys.path))
#
from TclInter import TclInter
class IxNetwork(TclInter):
    iphost = None

    def __init__(self, name,attrs,logger=None, logpath=None):#'10.245.34.201'
        TclInter.__init__(self, name, attrs, logger, logpath)
        if attrs.get('IP'):
            self.iphost = attrs['IP']

    def OpenTcl(self):
        super(IxNetwork,self).OpenTcl()
        self.tclInter.eval('source ../product/ixia_tcl_lib.tcl')
        cwd = os.path.abspath('../product').replace('\\','/')#os.getcwd().replace('\\','/')
        IxTclNetwork_path = '"' + cwd + '/IxTclNetwork' + '"'
        self.SendLine('set_tcl_env ' + IxTclNetwork_path + ' ' + self.iphost)
        self.Expect('::ixNet::OK')
#         self.tcl.eval('lappend auto_path ' + IxTclNetwork_path)
#         self.tcl.eval('package require IxTclNetwork')
#         return '::ixNet::OK' == self.tcl.eval('ixNet connect ' + host_ip + ' -port 8009 -version 6.0')

    def get_statis_item(self, item="{Tx Frames}"):
        # the variable item is the input argument of "monitor flow statistics.tcl", it can be any of the following:
        # {Tx Port} {Rx Port} {Traffic Item} {Ethernet II:Destination MAC Address}
        # {Ethernet II:Source MAC Address} {Tx Frames} {Rx Frames} {Frames Delta} {Loss %}
        # {Tx Frame Rate} {Rx Frame Rate} {Rx Bytes} {Tx Rate (Bps)} {Rx Rate (Bps)} {Tx Rate (bps)}
        # {Rx Rate (bps)} {Tx Rate (Kbps)} {Rx Rate (Kbps)} {Tx Rate (Mbps)} {Rx Rate (Mbps)} {Store-Forward Avg Latency (ns)}
        # {Store-Forward Min Latency (ns)} {Store-Forward Max Latency (ns)} {First TimeStamp} {Last TimeStamp}
        item_list = self.tclInter.eval('monitor_flow_statistics ' + item)
        item_list = item_list.split()
        int_type = ["{Tx Frames}", "{Rx Frames}", "{Frames Delta}", "{Rx Bytes}"]
        float_type = ["{Loss %}", "{Tx Frame Rate}", "{Rx Frame Rate}", "{Tx Rate (Bps)}",
                    "{Rx Rate (Bps)}", "{Tx Rate (bps)}", "{Rx Rate (bps)}", "{Tx Rate (Kbps)}",
                    "{Rx Rate (Kbps)}", "{Tx Rate (Mbps)}", "{Rx Rate (Mbps)}"]
        if item in float_type:
            for i in range(len(item_list)):
                item_list[i] = float(item_list[i])
        elif item in int_type:
            for i in range(len(item_list)):
                item_list[i] = int(item_list[i])
        return item_list

    def generate_traffic(self, config_file = 'ixia_config_files/MFF_PPPoE_config3.tcl'):
        #print self.eval('puts $auto_path')
        print "loading config from {} ...".format(config_file)
        self.eval('source "{}"'.format(config_file))
#         print self.check_status()
        print "generating traffic..."
        try:
            self.eval('generate_traffic')
        except Exception:
            print "ignoring failed sessions..."
        while self.check_status() != "stopped":
            self.tclInter.eval('after 50')
            status = self.check_status()
            print status

    def start_traffic(self):
        print "starting traffic..."
        status = self.check_status()
        if status == "stopped":
            self.tclInter.eval('start_traffic')
        elif status == "started":
            print "already started"
        elif status == "unapplied":
            print "trafffic has not been generated"
        return



    def stop_traffic(self):
        print "stopping traffic..."
        status = self.check_status()
        if status == "stopped":
            print "already stopped"
            return
        self.tclInter.eval('stop_traffic')
        while "stopped" != self.tclInter.eval('check_status'):
            self.tclInter.eval('after 100')
#         status = self.check_status()
#         print status
#         while status != "stopped":
#             self.tclInter.eval('after 100')
#             status = self.check_status()
#             print status
    def clear_statis(self):
        return '::ixNet::OK' == self.tclInter.eval('clear_statis')

    def check_status(self):
        return self.tclInter.eval('check_status')

    def cacul_delta(self, d2, d1):
        return [d2[i] - d1[i] for i in range(len(d1))]


if __name__ == "__main__":
    ixN = IxNetwork('ixiaNetwork', {'IP': '10.245.34.201'})
    ixN.OpenTcl()
    ixN.Expect('OK')
    ixN.SendLine('set a 1')
    ixN.SendLine('puts $a')

    print ixN.get_statis_item()
    print ixN.get_statis_item('{Rx Frames}')
    print ixN.get_statis_item()

    ixN2 = IxNetwork('ixiaNetwork', {'IP': '10.245.34.201'})
    ixN2.OpenTcl()
    print ixN2.get_statis_item()
    print ixN2.get_statis_item('{Rx Frames}')
    print ixN2.get_statis_item()

