# system imports
from os import chdir
from time import sleep
from datetime import datetime
import logging
import yaml
import csv
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

global node_list
global link_list
node_list = []
link_list = []

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
        ref_pp['node_list'] = ref_pp['ctrl'].custom['node_list']
        ref_pp['link_list'] = ref_pp['ctrl'].custom['link_list']

        
        global node_list
        global link_list
        node_list = []
        link_list = []

        node_list=list(ref_pp['node_list'].split(","))
        link_list=list(ref_pp['link_list'].split(","))


        ref_pp['pop_name'] = ref_pp['pop'].custom['name']
        ref_pp['pop_mac'] = ref_pp['pop'].custom['mac']
        ref_pp['path']=ref_pp['pop'].custom['location']
    

        ref_pp['server_inf']=ref_pp['server'].custom['inf']
        ref_pp['server_data_ipv6']=ref_pp['server'].custom['ipv6']
        ref_pp['server_ipv6_GW']=ref_pp['server'].custom['GW']
        ref_pp['server_data_ipv4']=ref_pp['server'].custom['ipv4']
        ref_pp['result_file']=ref_pp['server'].custom['file_name']
        ref_pp['client_inf']=ref_pp['client'].custom['inf']
        ref_pp['client_data_ipv4']=ref_pp['client'].custom['ipv4']
        ref_pp['client_BW']=ref_pp['client'].custom['BW']

        ref_pp['switch_inf']=ref_pp['switch'].custom['inf']
        ref_pp['switch_os'] = ref_pp['switch'].os
        ref_pp['vlan'] = ref_pp['switch'].custom['vlan']
        ref_pp['cpe_inf'] =ref_pp['switch'].custom['cpe_inf']
        
      
        ref_pp['server'].connect()
        ref_pp['client'].connect()
        ref_pp['switch'].connect()


        
   

    @aetest.subsection
    def start_iperf_server_and_config_vlan(self,steps,ctrl,server,switch,client,**param):
        misc.config_iperf_server(server)
        misc.config_access_vlan(switch,param['switch_os'],param['switch_inf'],param['vlan'])

    


class L3(aetest.Testcase):
  
    @aetest.setup
    def Setup(self, steps,server,client,switch,**param):

        logger.info(link_list)

        with steps.start('Enabling L3',continue_=True) as step:     
            assert api.config_l2_bridge(param['ctrl_ip'],status='false')
            logger.info('Successful in Enabling L3')
            sleep(600)

        with steps.start('Configuring CPE',continue_=True) as step:

            api.set_ignition_state(param['ctrl_ip'],link_list[0],status='true')
            for i in range(0,5):
                api.set_link_state(param['ctrl_ip'],param['pop_name'],node_list[0],action='1')
                sleep(3)
                data = fetch_api.get_link_state(param['ctrl_ip'],link_list[0])
                logger.info(data)
                if data["is_alive"] == True:  
                    logger.info('Link is up')             
                    break
                elif i == 4:
                    if data["is_alive"] == True:
                        logger.info('Link is Up')
                    else:
                        assert False

            assert api.config_cpe(param['ctrl_ip'],node_list[0],param['cpe_inf'])
            sleep(200)
            for i in range(0,5):
                sleep(3)
                data = fetch_api.get_link_state(param['ctrl_ip'],link_list[0])
                logger.info(data)
                if data["is_alive"] == True:  
                    logger.info('Link is up')             
                    break
                elif i == 4:
                    if data["is_alive"] == True:
                        logger.info('Link is Up')
                    else:
                        assert False


        with steps.start('Disassociating link in Sector',continue_=True) as step:
            for (a,b) in zip (node_list,link_list):
                api.set_ignition_state(param['ctrl_ip'],b,status='false')
                logger.info('Successfully Disabled ingition for link {}'.format(b))
                sleep(1)
                api.set_link_state(param['ctrl_ip'],param['pop_name'],a,action='2')
                logger.info('Successfully Sent Disassoc for node {}'.format(b))
                for i in range(0,5):
                    sleep(3)
                    data = fetch_api.get_link_state(param['ctrl_ip'],b)
                    logger.info(data)
                    if data["is_alive"] == False:  
                        logger.info('Link is down')             
                        break
                    elif i == 4:
                        if data["is_alive"] == 'false':
                            logger.info('Link is down')
                        else:
                            assert False

        
        with steps.start('Configure IP & GW in Server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv6'],version='6')
            log.info('Successful in configuring IP in Server')
            misc.execute_command(server,'ip -6 route add default via {}'.format(param['server_ipv6_GW']))

        
        #Cleaning IP on client PC
        with steps.start('Cleaning IP in client',continue_=True) as step: 
            misc.config_client_interface(client,param['client_inf'])
            log.info('Successful in configuring IP in Client')

        
    @ aetest.test
    def test_section(self,steps,ctrl,server,client,**param):

        with steps.start('Sending Assoc',continue_=True) as step:
            dummy = 1
            fields = ['No.of.Active.Links','L3 TCP UL(Mbps)','L3 TCP DL(Mbps)','L3 UDP UL(Mbps)','L3 UDP DL(Mbps)']
            filename = param['result_file']
            with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(fields)


            for (a,b) in zip (node_list,link_list):
                        
                for i in range(0,5):
                    assert api.set_link_state(param['ctrl_ip'],param['pop_name'],a,action='1')
                    sleep(5)
                    data = fetch_api.get_link_state(param['ctrl_ip'],b)
                    logger.info(data)
                    if data["is_alive"] == True:  
                        logger.info('Link is Up')             
                        break
                    elif i == 4:
                        if data["is_alive"] == True:
                            logger.info('Link is Up')
                        else:
                            assert False
                sleep(20)
                tcp_up=misc.config_iperf_client(client,param['server_data_ipv6'],direction='uplink',type='tcp',time='60')
                assert ((tcp_up != 0.0))
                log.info('Successful in Running Uplink TCP traffic')
                sleep(5)
                tcp_down=misc.config_iperf_client(client,param['server_data_ipv6'],direction='downlink',type='tcp',time='60')
                assert ((tcp_down != 0.0))
                log.info('Successful in Running Downlink TCP traffic')
                sleep(5)
                udp_up=misc.config_iperf_client(client,param['server_data_ipv6'],direction='uplink',type='udp',bw=param['client_BW'],time='60')
                assert ((udp_up != 0.0))
                log.info('Successful in Running Uplink UDP traffic')
                sleep(5)
                udp_down=misc.config_iperf_client(client,param['server_data_ipv6'],direction='downlink',type='udp',bw=param['client_BW'],time='60')
                assert ((udp_down != 0.0))
                log.info('Successful in Running Downlink UDP traffic')

                rows = [[dummy,tcp_up,tcp_down,udp_up,udp_down]]
                
                with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

                dummy = dummy+1

            rows = [['','','','','']]
            with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

        
    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):
        with steps.start('Disabling CPE ',continue_=True) as step:
            api.set_ignition_state(param['ctrl_ip'],link_list[0],status='true')
            assert api.config_cpe(param['ctrl_ip'],node_list[0],param['cpe_inf'],status='False')
            sleep(300)
            for i in range(0,5):
                api.set_link_state(param['ctrl_ip'],param['pop_name'],node_list[0],action='1')
                sleep(3)
                data = fetch_api.get_link_state(param['ctrl_ip'],link_list[0])
                logger.info(data)
                if data["is_alive"] == True:  
                    logger.info('Link is up')             
                    break
                elif i == 4:
                    if data["is_alive"] == True:
                        logger.info('Link is Up')
                    else:
                        assert False

class L2(aetest.Testcase):
  
    @aetest.setup
    def Setup(self, steps,server,client,switch,**param):

        logger.info(link_list)

        with steps.start('Enabling L2 ',continue_=True) as step:     
            assert api.config_l2_bridge(param['ctrl_ip'],status='true')
            logger.info('Successful in Enabling L2 bridge')
            sleep(600)


        with steps.start('Disassociating link in Sector',continue_=True) as step:
            for (a,b) in zip (node_list,link_list):
                api.set_ignition_state(param['ctrl_ip'],b,status='false')
                logger.info('Successfully Disabled ingition for link {}'.format(b))
                sleep(1)
                api.set_link_state(param['ctrl_ip'],param['pop_name'],a,action='2')
                logger.info('Successfully Sent Disassoc for node {}'.format(b))
                for i in range(0,5):
                    sleep(3)
                    data = fetch_api.get_link_state(param['ctrl_ip'],b)
                    logger.info(data)
                    if data["is_alive"] == False:  
                        logger.info('Link is down')             
                        break
                    elif i == 4:
                        if data["is_alive"] == 'false':
                            logger.info('Link is down')
                        else:
                            assert False
          
        
        
        with steps.start('Configure IP in Server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    @ aetest.test
    def test_section(self,steps,ctrl,server,client,**param):

        with steps.start('Sending Assoc',continue_=True) as step:
            dummy = 1
            fields = ['No.of.Active.Links','L2 TCP UL(Mbps)','L2 TCP DL(Mbps)','L2 UDP UL(Mbps)','L2 UDP DL(Mbps)']
            filename = param['result_file']
            with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(fields)


            for (a,b) in zip (node_list,link_list):
                
                
                for i in range(0,5):
                    assert api.set_link_state(param['ctrl_ip'],param['pop_name'],a,action='1')
                    sleep(5)
                    data = fetch_api.get_link_state(param['ctrl_ip'],b)
                    logger.info(data)
                    if data["is_alive"] == True:  
                        logger.info('Link is Up')             
                        break
                    elif i == 4:
                        if data["is_alive"] == True:
                            logger.info('Link is Up')
                        else:
                            assert False
                sleep(20)
                tcp_up=misc.config_iperf_client(client,param['server_data_ipv4'],direction='uplink',type='tcp',time='60')
                assert ((tcp_up != 0.0))
                log.info('Successful in Running Uplink TCP traffic')
                sleep(5)
                tcp_down=misc.config_iperf_client(client,param['server_data_ipv4'],direction='downlink',type='tcp',time='60')
                assert ((tcp_down != 0.0))
                log.info('Successful in Running Downlink TCP traffic')
                sleep(5)
                udp_up=misc.config_iperf_client(client,param['server_data_ipv4'],direction='uplink',type='udp',bw=param['client_BW'],time='60')
                assert ((udp_up != 0.0))
                log.info('Successful in Running Uplink UDP traffic')
                sleep(5)
                udp_down=misc.config_iperf_client(client,param['server_data_ipv4'],direction='downlink',type='udp',bw=param['client_BW'],time='60')
                assert ((udp_down != 0.0))
                log.info('Successful in Running Downlink UDP traffic')

                rows = [[dummy,tcp_up,tcp_down,udp_up,udp_down]]
                
                with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

                dummy = dummy+1

            

        
    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):
        with steps.start('Disabling L2 ',continue_=True) as step:     
            assert api.config_l2_bridge(param['ctrl_ip'],status='false')
            logger.info('Successful in Disabling L2 bridge')
            #sleep(600)

class common_cleanup(aetest.CommonCleanup):  

    @aetest.subsection
    def Enabling_links(self,steps,server,ctrl,client,**param):
        with steps.start('Enabling link Igintion ',continue_=True) as step:
            for link in link_list:
                api.set_ignition_state(param['ctrl_ip'],link,status='true')
                logger.info('Successfully Enabled ingition for link {}'.format(link))
                sleep(1)
                
              
    
    @aetest.subsection
    def stopping_iperf_server(self,server,ctrl,client,**param):
        assert misc.config_iperf_server(server,status='disable')
        log.info('Successful in stopping iperf server')
        server.disconnect()
        client.disconnect()
    
        
    
if __name__ == '__main__': # pragma: no cover
    aetest.main()

