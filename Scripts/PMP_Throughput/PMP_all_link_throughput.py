# system imports
from os import chdir
from time import sleep
from datetime import datetime
import logging
import yaml
import csv
import sys
import pdb
from pyats import aetest
from pyats.log.utils import banner
from genie import testbed
#from pyats.topology import loader
from multiprocessing import Process
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)




#importing custom modules
from Config.config import *
from Fetch.fetch import *
from Misc.misc import misc



#Fetching input values from input.yaml

global node_list
global link_list
vlan_list = []
link_list = []

class ForkedPdb(pdb.Pdb):
    """A Pdb subclass that may be used
    from a forked multiprocessing child

    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

class common_setup(aetest.CommonSetup): 

    @aetest.subsection
    def initial_configs(self,steps, testbed, **param):
        
        ref_pp = self.parent.parameters
        ref_pp['ctrl'] = testbed.devices[param['ctrl_alias']]
        ref_pp['pop'] = testbed.devices[param['pop_alias']]
        ref_pp['server'] = testbed.devices[param['server_alias']]
        ref_pp['client'] = testbed.devices[param['client_alias']]
        ref_pp['switch'] = testbed.devices[param['switch_alias']]

        ref_pp['ctrl_ip'] = ref_pp['ctrl'].custom['ip']
        ref_pp['vlan_list'] = ref_pp['ctrl'].custom['vlan_list']
        ref_pp['link_list'] = ref_pp['ctrl'].custom['link_list']

        
        global vlan_list
        global link_list
        vlan_list = []
        link_list = []

        vlan_list=list(ref_pp['vlan_list'].split(","))
        link_list=list(ref_pp['link_list'].split(","))


        ref_pp['pop_name'] = ref_pp['pop'].custom['name']
        ref_pp['pop_mac'] = ref_pp['pop'].custom['mac']
        ref_pp['path']=ref_pp['pop'].custom['location']
    

        ref_pp['server_inf']=ref_pp['server'].custom['inf']
        ref_pp['server_data_ipv6']=ref_pp['server'].custom['ipv6']
        ref_pp['server_data_ipv4']=ref_pp['server'].custom['ipv4']
        ref_pp['result_file']=ref_pp['server'].custom['file_name']
        ref_pp['client_inf']=ref_pp['client'].custom['inf']
        ref_pp['client_data_ipv4']=ref_pp['client'].custom['ipv4']

        ref_pp['switch_inf']=ref_pp['switch'].custom['inf']
        ref_pp['switch_os'] = ref_pp['switch'].os
        

        
        #ForkedPdb().set_trace()
        ref_pp['server'].connect()
        ref_pp['client'].connect()
        #ForkedPdb().set_trace()
        ref_pp['switch'].connect()


    @aetest.subsection
    def start_iperf_server(self,steps,ctrl,server,client,**param):
        misc.config_iperf_server(server)

class L2(aetest.Testcase):
  
    @aetest.setup
    def Setup(self, steps,server,client,**param):

        logger.info(link_list)

        with steps.start('Enabling L2',continue_=True) as step:     
            assert api.config_l2_bridge(param['ctrl_ip'],status='true')
            logger.info('Successful in Enabling L2 bridge')
            #sleep(300)
        
        
        with steps.start('Configure IP in Server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    @ aetest.test
    def test_section(self,steps,ctrl,server,switch,client,**param):

        with steps.start('Verifying Throughput',continue_=True) as step:
            
            fields = ['Link Names','TCP UL(Mbps)','TCP DL(Mbps)','UDP UL(Mbps)','UDP DL(Mbps)']
            filename = param['result_file']
            with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(fields)


            for (a,b) in zip (link_list,vlan_list):
                misc.config_access_vlan(switch,param['switch_os'],param['switch_inf'],b)
                sleep(5)
                for i in range(0,3):
                    sleep(3)
                    data = fetch_api.get_link_state(param['ctrl_ip'],a)
                    logger.info(data)
                    if data["is_alive"] == True:  
                        logger.info('Link is up')             
                        break
                    elif i == 2:
                        if data["is_alive"] == 'True':
                            logger.info('Link is Up')
                        else:
                            assert False
                tcp_up=misc.config_iperf_client(client,param['server_data_ipv4'],direction='uplink',type='tcp',time='20')
                assert ((tcp_up != 0.0))
                log.info('Successful in Running Uplink TCP traffic')

                tcp_down=misc.config_iperf_client(client,param['server_data_ipv4'],direction='downlink',type='tcp',time='20')
                assert ((tcp_down != 0.0))
                log.info('Successful in Running Downlink TCP traffic')

                udp_up=misc.config_iperf_client(client,param['server_data_ipv4'],direction='uplink',type='udp',time='20')
                assert ((udp_up != 0.0))
                log.info('Successful in Running Uplink UDP traffic')

                udp_down=misc.config_iperf_client(client,param['server_data_ipv4'],direction='downlink',type='udp',time='20')
                assert ((udp_down != 0.0))
                log.info('Successful in Running Downlink UDP traffic')

                rows = [[a,tcp_up,tcp_down,udp_up,udp_down]]
                
                with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)


        
    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):
        pass
    
        
    
if __name__ == '__main__': # pragma: no cover
    aetest.main(pdb = True)

