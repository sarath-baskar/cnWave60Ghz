# system imports
from os import chdir
from time import sleep
from datetime import datetime
import logging
import yaml
import sys
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
class common_setup(aetest.CommonSetup): 

    @aetest.subsection
    def initial_configs(self,steps, testbed, **param):
        
        ref_pp = self.parent.parameters
        ref_pp['ctrl'] = testbed.devices[param['ctrl_alias']]
        ref_pp['dn'] = testbed.devices[param['dn_alias']]
        ref_pp['server'] = testbed.devices[param['server_alias']]
        ref_pp['client'] = testbed.devices[param['client_alias']]
        ref_pp['pop_name'] = ref_pp['ctrl'].custom['name']
        ref_pp['pop_mac'] = ref_pp['ctrl'].custom['mac']
        ref_pp['pop_iface'] = ref_pp['ctrl'].custom['iface']
        ref_pp['pop_iface'] = ref_pp['ctrl'].custom['iface']
        ref_pp['pop_mcvlan'] = ref_pp['ctrl'].custom['mcvlan']
        ref_pp['pop_msvlan'] = ref_pp['ctrl'].custom['msvlan']
        ref_pp['pop_management_ip']=ref_pp['ctrl'].custom['management_ip']
        ref_pp['path']=ref_pp['ctrl'].custom['location']
        
        ref_pp['dn1_name']=ref_pp['dn'].custom['name']
        ref_pp['dn1_site']=ref_pp['dn'].custom['site']
        ref_pp['dn1_lat'] = ref_pp['dn'].custom['lat']
        ref_pp['dn1_lon'] = ref_pp['dn'].custom['lon']
        ref_pp['dn1_alt'] = ref_pp['dn'].custom['alt']
        ref_pp['dn1_acc'] = ref_pp['dn'].custom['acc']
        ref_pp['dn1_inf'] = ref_pp['dn'].custom['inf']
        ref_pp['dn1_inf1'] = ref_pp['dn'].custom['inf1']    
        ref_pp['dn1_mac'] = ref_pp['dn'].custom['mac']
        ref_pp['dn1_management_ip']=ref_pp['dn'].custom['management_ip']
        ref_pp['dn1_cvlan'] = ref_pp['dn'].custom['cvlan']
        ref_pp['dn1_svlan'] = ref_pp['dn'].custom['svlan']
        ref_pp['dn1_mcvlan'] = ref_pp['dn'].custom['mcvlan']
        ref_pp['dn1_msvlan'] = ref_pp['dn'].custom['msvlan']
        ref_pp['custom_rid'] = ref_pp['dn'].custom['custom_rid']
        ref_pp['custom_cid'] = ref_pp['dn'].custom['custom_cid']


        ref_pp['server_inf']=ref_pp['server'].custom['inf']
        ref_pp['server_data_ipv6']=ref_pp['server'].custom['ipv6']
        ref_pp['server_data_ipv4']=ref_pp['server'].custom['ipv4']
        ref_pp['server_mgmt_ipv4']=ref_pp['server'].custom['mgmt_ipv4']
        ref_pp['server_file']=ref_pp['server'].custom['capture_file']
        ref_pp['client_inf']=ref_pp['client'].custom['inf']
        ref_pp['client_data_ipv4']=ref_pp['client'].custom['ipv4']
 
            
        ref_pp['ctrl'].connect()
        ref_pp['server'].connect()
        ref_pp['client'].connect()
    
    @aetest.subsection
    def create_site(self,ctrl,**param):

        log.info('Creating Site')
        assert cli.add_site(ctrl,param['dn1_site'],param['dn1_lat'],param['dn1_lon'],param['dn1_alt'],param['dn1_acc'])
        log.info('Successful in adding site')
            
    @aetest.subsection
    def Adding_node(self,ctrl,**param):

        #Adding dn
        log.info('Adding dn1')
        assert cli.add_dn(ctrl,param['dn1_name'],param['dn1_site'],param['dn1_mac']) 
        log.info('Successful in adding dn1')
    
    @aetest.subsection
    def Adding_link(self,ctrl,**param):

        #Adding link POP to dn1 link
        log.info('Adding link from controller')
        assert cli.add_link(ctrl,param['pop_name'],param['dn1_name'],param['pop_mac'],param['dn1_mac'],init_radio='radio1',resp_radio='radio1')
        log.info('Successful in Adding link')                
        log.info('Verify link status')

    @aetest.subsection
    def start_iperf_server(self,server):
        misc.config_iperf_server(server)

    @aetest.subsection
    def verify_links(self,steps,ctrl):       
        log.info('Verify link status')

        for i in range(0,3):
                #sleep(100)
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
            
        
        log.info('Successful in bringing up')
                

    @aetest.subsection
    def configure_l2_bridge(self,ctrl):
        #configuring l2bridge
        log.info('configuring l2bridge')
        
        assert cli.modify_network_l2bridge(ctrl,state='enable')
        log.info('Successful in configuring l2bridge')
        ctrl.disconnect()
        #sleep(150)
        ctrl.connect()

    @aetest.subsection
    def verify_links(self,steps,ctrl):
        log.info('Verify link status')

        for i in range(0,3):
                #sleep(100)
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:
                    break
                elif i == 2:
                    assert verify

        log.info('Successful in bringing up')


class common_cleanup(aetest.CommonCleanup):  
    @aetest.subsection
    def Disabling_L2bridge(self,steps,ctrl,server,client,**param):
        log.info('configuring l2bridge')
        '''with steps.start('Disabling L2 bridge',continue_=True) as step:
            assert cli.modify_network_l2bridge(ctrl,state='disable')
            log.info('Successful in configuring l2bridge')

        sleep(150)'''      
        ctrl.disconnect()
        ctrl.connect()
        with steps.start('Verify link status',continue_=True) as step:
            for i in range(0,3):
                #sleep(100)
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                   
    @aetest.subsection
    def deleting_node(self,steps,ctrl,server,client,**param):
        assert cli.del_node(ctrl,param['dn1_name']) 
        log.info('Successful in deleting dn1')
      

    @aetest.subsection
    def deleting_Site(self,steps,ctrl,server,client,**param):
        assert cli.del_site(ctrl,param['dn1_site'])
        log.info('Successful in Deleting site')
    
    @aetest.subsection
    def stopping_iperf_server(self,server,ctrl,client,**param):
        assert misc.config_iperf_server(server,status='disable')
        log.info('Successful in stopping iperf server')
        ctrl.disconnect()
        server.disconnect()
        client.disconnect()
        
       
if __name__ == '__main__': # pragma: no cover
    aetest.main()


