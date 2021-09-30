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



global lis
lis=[]
global lis1
lis1=[]



class common_setup(aetest.CommonSetup): 

    @aetest.subsection
    def initial_configs(self,steps, testbed, **param):
        
        ref_pp = self.parent.parameters
        ref_pp['ctrl'] = testbed.devices[param['ctrl_alias']]
        ref_pp['dn'] = testbed.devices[param['dn_alias']]
        ref_pp['server'] = testbed.devices[param['server_alias']]
        ref_pp['client'] = testbed.devices[param['client_alias']]
        ref_pp['client2'] = testbed.devices[param['client2_alias']]
        ref_pp['client3'] = testbed.devices[param['client3_alias']]

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


        ref_pp['server_inf']=ref_pp['server'].custom['inf']
        ref_pp['server_data_ipv6']=ref_pp['server'].custom['ipv6']
        ref_pp['server_data_ipv4']=ref_pp['server'].custom['ipv4']
        ref_pp['server_mgmt_ipv4']=ref_pp['server'].custom['mgmt_ipv4']
        ref_pp['server_file']=ref_pp['server'].custom['capture_file']
        ref_pp['client_inf']=ref_pp['client'].custom['inf']
        ref_pp['client_data_ipv4']=ref_pp['client'].custom['ipv4']
        ref_pp['client2_inf']=ref_pp['client2'].custom['inf']
        ref_pp['client2_data_ipv4']=ref_pp['client2'].custom['ipv4']
        ref_pp['client3_inf']=ref_pp['client3'].custom['inf']
        ref_pp['client3_data_ipv4']=ref_pp['client3'].custom['ipv4']
        
        vlan=int(ref_pp['dn1_cvlan'])
        #global lis
        #lis=[]
        for i in range(0,5):
            lis.append(vlan+i)
            
        svlan=int(ref_pp['dn1_svlan'])
        #global lis1
        #lis1=[]
        for i in range(0,5):
            lis1.append(svlan+i)    
            
        ref_pp['ctrl'].connect()
        ref_pp['server'].connect()
        ref_pp['client'].connect()


        
    @aetest.subsection
    def create_site(self,steps,ctrl,server,client,**param):

        misc.execute_command(server,'sudo ifconfig {} mtu 1492'.format(param['server_inf']))
        misc.execute_command(client,'sudo ifconfig {} mtu 1492'.format(param['client_inf']))

        log.info('Creating Site')
        assert cli.add_site(ctrl,param['dn1_site'],param['dn1_lat'],param['dn1_lon'],param['dn1_alt'],param['dn1_acc'])
        log.info('Successful in adding site')
            
    @aetest.subsection
    def Adding_node(self,steps,ctrl,server,client,**param):

        #Adding dn
        log.info('Adding dn1')
        assert cli.add_dn(ctrl,param['dn1_name'],param['dn1_site'],param['dn1_mac']) 
        log.info('Successful in adding dn1')
    
    @aetest.subsection
    def Adding_link(self,steps,ctrl,server,client,**param):

        #Adding link POP to dn1 link
        log.info('Adding link from controller')
        assert cli.add_link(ctrl,param['pop_name'],param['dn1_name'],param['pop_mac'],param['dn1_mac'],init_radio='radio1',resp_radio='radio1')
        log.info('Successful in Adding link')                
        log.info('Verify link status')

    @aetest.subsection
    def configuring_mgmt_ip(self,steps,ctrl,server,client,**param):
        with steps.start('Configuring Management ip on POP',continue_=True) as step:
            assert cli.config_management_ip(ctrl,param['pop_name'],param['pop_management_ip'])
            log.info('Successful in configuring Mgmt ip on POP')

        with steps.start('Configuring Management ip on DN',continue_=True) as step:
            assert cli.config_management_ip(ctrl,param['dn1_name'],param['dn1_management_ip'])
            log.info('Successful in configuring Mgmt ip on DN1')


    
    @aetest.subsection
    def start_iperf_server(self,steps,ctrl,server,client,**param):
        misc.config_iperf_server(server)

    @aetest.subsection
    def verify_links(self,steps,ctrl,server,client,**param):       
        log.info('Verify link status')

        for i in range(0,3):
                sleep(100)
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
            
        
        log.info('Successful in bringing up')
                

    @aetest.subsection
    def configure_l2_bridge(self,steps,ctrl,server,client,**param):
        #configuring l2bridge
        log.info('configuring l2bridge')
        
        assert cli.modify_network_l2bridge(ctrl,state='enable')
        log.info('Successful in configuring l2bridge')
        ctrl.disconnect()
        sleep(150)
        ctrl.connect()

    @aetest.subsection
    def verify_links(self,steps,ctrl,server,client,**param):
        log.info('Verify link status')

        for i in range(0,3):
                sleep(100)
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:
                    break
                elif i == 2:
                    assert verify

        log.info('Successful in bringing up')    

        
    
       
class Q_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Setup(self, steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
                    

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
        
        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False


    @aetest.cleanup
    def Disabling_Q_VLAN(self,steps,ctrl,server,client,**param):
    
        log.info('Disabling Single VLAN in dn')
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in Enabling Single VLAN on dn')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')

        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
            

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Configure_QinQ_Vlan(self, etype, steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')

        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')


        
        
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            if etype =='0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id == {}&&vlan.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in QinQ VLAN tagging')
            else:
                assert False
 
            
            
    @aetest.cleanup
    def Disabling_QinQ_VLAN(self,etype,steps,ctrl,server,client,**param):
    
        log.info('Disabling Double VLAN in dn')
        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
        with steps.start('Removing vlan configs from DN',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,status='disable')      
            log.info('sucessful in Removing QinQ VLAN on dn')
        
        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')

class Allowed_Q_Vlan(aetest.Testcase):

        
    @aetest.setup
    def Configure_Q_Vlan_allowed_list(self, steps,ctrl,server,client,**param):
        vlans='{},{}-{}'.format(lis[0],lis[1],lis[3])

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=str(int(param['dn1_cvlan'])-1),status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')

        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='enable')      
            log.info('sucessful in configuring allowed q VLAN on dn')
            

    
    def test_untagged_packets(self,steps,ctrl,server,client,**param):

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        log.info('Starting iperf client')
        #sleep(20)
        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')


    @ aetest.test.loop(c_vlan=lis)
    def test_single_tagged_packets(self,c_vlan,steps,ctrl,server,client,**param):
    
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],c_vlan,param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
            
        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],c_vlan,param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        

        log.info('Starting iperf client')
        sleep(20) 
        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            if c_vlan==int(param['dn1_cvlan'])+4:
                if result == False:
                    log.info('No traffic due to unallowed vlan')
                else:
                    assert False
            else:
                assert result
                
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],c_vlan,param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')
            
        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],c_vlan,param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')
                      
                        
            
        
            
            
    @aetest.cleanup
    def VLAN_config_cleanup(self,steps,ctrl,server,client,**param):
        vlans='{},{}-{}'.format(lis[0],lis[1],lis[3])
    
        with steps.start('Remove Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='disable')      
            log.info('sucessful in Removing Single VLAN on dn')

        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='disable')      
            log.info('sucessful in Removing allowed q VLAN on dn')

        sleep(60)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

class Q_Vlan_Remarking(aetest.Testcase):
        
    @aetest.setup
    def Configure_Q_Vlan_allowed_list(self, steps,ctrl,server,client,**param):
        remark=int(param['dn1_cvlan'])+1

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=str(int(param['dn1_cvlan'])-1),status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='enable')      
            log.info('sucessful in configuring allowed q VLAN on dn')
            
        with steps.start('Configuring Remark VLAN',continue_=True) as step:
            assert cli.config_vlan_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_cvlan'],remark)
            log.info('sucessful in Configuring Single VLAN Remarking on dn')


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,**param):

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')    


        with steps.start('Starting client iperf',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
                
        
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,**param):
        remark=int(param['dn1_cvlan'])+1
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],remark,param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')

        with steps.start('Starting client iperf',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],remark,param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client') 

    @aetest.cleanup
    def Removing_configs_from_node_and_PCs(self,steps,ctrl,server,client,**param):
        remark=int(param['dn1_cvlan'])+1

        with steps.start('Removing Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='disable')      
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in Removing allowed q VLAN on dn')
            
        with steps.start('Removing Remark VLAN',continue_=True) as step:
            assert cli.config_vlan_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_cvlan'],remark,status='disable')
            log.info('sucessful in Removing Single VLAN Remarking on dn')

class Q_Vlan_Drop_Untag(aetest.Testcase):

        
    @aetest.setup
    def Configure_Q_Vlan(self, steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=str(int(param['dn1_cvlan'])-1),status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
        with steps.start('Configure drop untag packets in Q VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='enable')      
            log.info('sucessful in configuring Drop untag VLAN')
            
        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='enable')      
            log.info('sucessful in configuring allowed q VLAN on dn') 
        
    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,**param):
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        

        
        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            if result == False:
                log.info('Traffic Failed due to drop untag')
            else:
                log.info('Failed to drop untagged packets')
                assert False
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))            
            
        
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')
           
    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,**param):
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')

        
        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))
            log.info('througput numbers up={} down={}'.format(up,down)) 
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')
       
        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')

    @aetest.cleanup
    def Disabling_Q_VLAN_configs(self,steps,ctrl,server,client,**param):
    
        log.info('Disabling Single VLAN in dn')
        with steps.start('Removing drop untag packets in Q VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in Removing Drop untag VLAN')
        with steps.start('Removing vlan configs from dn',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in Enabling Single VLAN on dn')
        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in Removing allowed q VLAN on dn')

class Q_Vlan_Priority_Remarking(aetest.Testcase):
   
    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Configure_Q_Vlan(self, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=str(int(param['dn1_cvlan'])-1),status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='enable')      
            log.info('sucessful in configuring allowed q VLAN on dn')
            
        with steps.start('Configuring Remark VLAN priority',continue_=True) as step:
            assert cli.config_vlan_prio_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_cvlan'],'7')
            log.info('sucessful in Configuring Single VLAN priority Remarking on dn')

    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,**param):
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
           
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()
        
        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==0'.format(ip,str(int(param['dn1_cvlan'])-1))    
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in priority remarking')
            else:
                assert False
        
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client') 
    
    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,**param):
        
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
            sleep(20)
        
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in priority remarking')
            else:
                assert False

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')
     
        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')

    @aetest.cleanup
    def Removing_configs_from_node_and_PCs(self,steps,ctrl,server,client,**param):

        with steps.start('Removing Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='disable')      
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_cvlan'],status='enable')      
            log.info('sucessful in Removing allowed q VLAN on dn')
            
        with steps.start('Removing Remark VLAN prio',continue_=True) as step:
            assert cli.config_vlan_prio_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_cvlan'],'7',status='disable')
            log.info('sucessful in Removing Single VLAN priority Remarking on dn')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Q_port_Behaviour_When_QinQ_Ingress(aetest.Testcase):

    @aetest.setup
    def Configure_Q_Vlan(self, steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed q VLAN on dn')

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

    @ aetest.test
    def Verify_traffic(self,steps,ctrl,server,client,**param):

        log.info('Starting iperf client')
        sleep(20)
        up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
        result=((up != 0.0) and (down != 0.0))
        if result == False:
            log.info('Traffic dropped due to double tagged packets')
        else:
            log.info('Failed to drop double tagged packets')
            assert False
        log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

    @aetest.cleanup
    def Removing_Vlan_configs(self, steps,ctrl,server,client,etype,**param):

        with steps.start('Removing Q VLAN in dn',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed q VLAN on dn')

        with steps.start('Remonving QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Allowed_QinQ_Vlan(aetest.Testcase):

    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self, steps,ctrl,server,client,etype,**param):
        vlans='{},{}-{}'.format(lis1[0],lis1[1],lis1[3])

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**parm):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20)
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test.loop(s_vlan=lis1)
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):
        
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')


        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            if s_vlan==int(param['dn1_svlan'])+4:
                if result == False:
                    log.info('No traffic due to unallowed vlan')
                else:
                    assert False
            else:
                assert result

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test.loop(s_vlan=lis1)
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],s_vlan,param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],s_vlan,param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        log.info('Starting iperf client')
        sleep(20)
        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            if s_vlan==int(param['dn1_svlan'])+4:
                if result == False:
                    log.info('No traffic due to unallowed vlan')
                else:
                    assert False
            else:
                assert result

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],s_vlan,param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],s_vlan,param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')





    @aetest.cleanup
    def VLAN_config_cleanup(self,steps,ctrl,server,client,etype,**param):
        vlans='{},{}-{}'.format(lis1[0],lis1[1],lis1[3])

        with steps.start('Remove QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan='1',cvlan='1',ethertype=etype,status='disable')
            log.info('sucessful in Removing Double VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Allowed_QinQ_Vlan(aetest.Testcase):

    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self, steps,ctrl,server,client,etype,**param):
        vlans='{},{}-{}'.format(lis1[0],lis1[1],lis1[3])

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20)
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test.loop(s_vlan=lis1)
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):
        
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')


        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            if s_vlan==int(param['dn1_svlan'])+4:
                if result == False:
                    log.info('No traffic due to unallowed vlan')
                else:
                    assert False
            else:
                assert result

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test.loop(s_vlan=lis1)
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],s_vlan,param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],s_vlan,param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        log.info('Starting iperf client')
        sleep(20)
        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            if s_vlan==int(param['dn1_svlan'])+4:
                if result == False:
                    log.info('No traffic due to unallowed vlan')
                else:
                    assert False
            else:
                assert result

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],s_vlan,param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],s_vlan,param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')





    @aetest.cleanup
    def VLAN_config_cleanup(self,steps,ctrl,server,client,etype,**param):
        vlans='{},{}-{}'.format(lis1[0],lis1[1],lis1[3])

        with steps.start('Remove QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan='1',cvlan='1',ethertype=etype,status='disable')
            log.info('sucessful in Removing Double VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Vlan_Remarking(aetest.Testcase):
        
    @aetest.setup
    def Configure_Q_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        remark=int(param['dn1_svlan'])+1

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=param['dn1_svlan'],cvlan=param['dn1_cvlan'],ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configuring Remark VLAN',continue_=True) as step:
            assert cli.config_vlan_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_svlan'],remark)
            log.info('sucessful in Configuring Single VLAN Remarking on dn')

    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20)
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        remark=int(param['dn1_svlan'])+1
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],remark,param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')


        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],remark,param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        remark=int(param['dn1_svlan'])+1
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],remark,param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        log.info('Starting iperf client')
        sleep(20)
        with steps.start('Verifying Traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0.0) and (down != 0.0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],remark,param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')
    

    @aetest.cleanup
    def Removing_configs_from_node_and_PCs(self,steps,ctrl,server,client,etype,**param):
        remark=int(param['dn1_svlan'])+1
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing QinQ VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')
            
        with steps.start('Removing Remark VLAN',continue_=True) as step:
            assert cli.config_vlan_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_svlan'],remark,status='disable')
            log.info('sucessful in Removing Single VLAN Remarking on dn')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Vlan_Prio_Remarking(aetest.Testcase):
     
    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configuring Remark VLAN Priority',continue_=True) as step:
            assert cli.config_vlan_prio_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_svlan'],'7')
            log.info('sucessful in Configuring Single VLAN prirotiy Remarking on dn')

    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        sleep(20)
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            if etype == '0x8100':
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id== {}&&vlan.priority==0'.format(ip,str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1))
               
            else:
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==0&&vlan.priority==0'.format(ip,str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1))
                
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()


        with steps.start('Analyse Capture',continue_=True) as step:
            if etype == '0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id== {}&&vlan.priority==0'.format(ip,str(int(param['dn1_svlan'])-1),param['dn1_svlan'])
               
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==0&&vlan.priority==7'.format(ip,param['dn1_svlan'],int(param['dn1_svlan'])-1)
                
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            if etype == '0x8100':                
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id== {}&&vlan.priority==7&&vlan.priority==0'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])

            else:
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==7&&vlan.priority==0'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])

            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False



        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing QiNQ vlan in client')

    @aetest.cleanup
    def Removing_configs_from_node(self,steps,ctrl,server,client,etype,**param):
    
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')
            
        with steps.start('Removing Remark VLAN Priority',continue_=True) as step:
            assert cli.config_vlan_prio_remarking(ctrl,param['dn1_name'],param['dn1_inf'],param['dn1_svlan'],'7',status='disable')
            log.info('sucessful in Removing Single VLAN prirotiy Remarking on dn')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Allow_untag_Allow_Singe_Tag(aetest.Testcase):
        
    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client.disconnect()
        client.connect()
        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configure drop untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in configuring Drop untag VLAN')
            
        
            


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
        with steps.start('Starting client iperf',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
        
        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        
        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing QiNQ vlan in client')
    

    @aetest.cleanup
    def Removing_configs_from_node(self,steps,ctrl,server,client,etype,**param):
    
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')

        
        client.disconnect()
        client.connect()

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Drop_untag_Allow_Singe_Tag(aetest.Testcase):
        
    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configure drop untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='enable')      
            log.info('sucessful in configuring Drop untag VLAN')
            
        
            


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
       
        with steps.start('Starting iperf in client',continue_=True) as step:
            sleep(20) 
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0.0) and (down != 0.0))
            log.info(result)
            if result == False:
                log.info('Traffic Failed due to drop untag')
            else:
                log.info('Failed to drop untagged packets')
                assert False
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        
        with steps.start('Starting client iperf',continue_=True) as step:
            sleep(20)
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')
    

    @aetest.cleanup
    def Removing_configs_from_node(self,steps,ctrl,server,client,etype,**param):
    
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')
            
        with steps.start('Removing drop untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in Removing Drop untag VLAN')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Allow_untag_Drop_Singe_Tag(aetest.Testcase):
        
    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configure Allow untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in configuring Allow untag ')
        
        with steps.start('Configure Drop Single packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_drop_single_tag(ctrl,param['dn1_name'],param['dn1_inf'],status='enable')      
            log.info('sucessful in configuring Drop Singletag')
            
        
            


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
       
        with steps.start('Starting client iperf',continue_=True) as step:
            sleep(20)
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
            
        

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        
        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0) and (down != 0))
            if result == False:
                log.info('Packets dropped due to drop config')
            else:
                assert False


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')
    

    @aetest.cleanup
    def Removing_configs_from_node(self,steps,ctrl,server,client,etype,**param):
    
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')
            
        with steps.start('Removing drop Single tag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_drop_single_tag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in Removing Drop Single tag')
            
@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Drop_untag_Drop_Singe_Tag(aetest.Testcase):
        
    @aetest.setup
    def Configure_QinQ_Vlan_allowed_list(self,etype, steps,ctrl,server,client,**param):
        

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client.disconnect()
        client.connect()
        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='enable')
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='enable')
            log.info('sucessful in configuring allowed QinQ VLAN on dn')
            
        with steps.start('Configure Drop untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='enable')      
            log.info('sucessful in configuring Drop untag ')
        
        with steps.start('Configure Drop Single packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_drop_single_tag(ctrl,param['dn1_name'],param['dn1_inf'],status='enable')      
            log.info('sucessful in configuring Drop Singletag')
            
        
            


    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
       
        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0) and (down != 0))
            if result == False:
                log.info('Packets dropped due to drop config')
            else:
                assert False
            
        

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')        




    @ aetest.test
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
        
        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            result=((up != 0) and (down != 0))
            if result == False:
                log.info('Packets dropped due to drop config')
            else:
                assert False


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing Q vlan in client')




    @ aetest.test
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')


        with steps.start('Starting client iperf',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))


        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],status='disable')
            log.info('Removing QinQ vlan in Server')

        with steps.start('Removing QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],status='disable')
            log.info('Removing QiNQ vlan in client')
    

    @aetest.cleanup
    def Removing_configs_from_node(self,steps,ctrl,server,client,etype,**param):
    
        
        with steps.start('Removing QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],svlan=str(int(param['dn1_svlan'])-1),cvlan=str(int(param['dn1_cvlan'])-1),ethertype=etype,status='disable')
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed QinQ VLAN in dn',continue_=True) as step:
            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=param['dn1_svlan'],status='disable')
            log.info('sucessful in Removing allowed QinQ VLAN on dn')

        with steps.start('Removing drop untag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_vlan_drop_untag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in Removing Drop untag')        
        
        with steps.start('Removing drop Single tag packets in QinQ VLAN',continue_=True) as step:
            assert cli.config_drop_single_tag(ctrl,param['dn1_name'],param['dn1_inf'],status='disable')      
            log.info('sucessful in Removing Drop Single tag')


@aetest.loop(etype = ['0x8100', '0x88A8'])
class Same_S_And_C_QinQ_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Configure_QinQ_Vlan(self, etype, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_svlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
        
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            if etype =='0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id == {}&&vlan.priority==5&&vlan.priority==3'.format(ip,param['dn1_svlan'],param['dn1_svlan'])
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==5&&vlan.priority==3'.format(ip,param['dn1_svlan'],param['dn1_svlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in QinQ VLAN tagging')
            else:
                assert False
 
            
            
    @aetest.cleanup
    def Disabling_QinQ_VLAN(self,etype,steps,ctrl,server,client,**param):
    
        log.info('Disabling Double VLAN in dn')
        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_svlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_svlan'],svlan=param['dn1_svlan'],ethertype=etype,status='disable')      
            log.info('sucessful in Removing QinQ VLAN on dn')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')

@aetest.skip(reason = 'Failure in client3 reachability')
class POP_Bridge_Q_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        #log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))
    
    @aetest.setup
    def Setup(self, steps,ctrl,server,client3,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
                    
        client3.connect()
        with steps.start('Configure Q VLAN in POP',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['pop_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on POP')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client3,param['client3_inf'],param['client3_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    
        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client3,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False


    @aetest.cleanup
    def Disabling_Q_VLAN(self,steps,ctrl,server,client3,**param):
    
        log.info('Disabling Single VLAN in POP')
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['pop_name'],param['pop_inf1'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in Enabling Single VLAN on POP')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client3,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')
        client3.disconnect()
    


class Transparent_Port(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Transparent in dn',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent on dn')
                 
        with steps.start('Configure IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,**param):
        sleep(20) 
        up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
        assert ((up != 0) and (down != 0))
        log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,**param):
    
                 
        with steps.start('Removing IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')


class Transparent_Port_With_Q_Packets(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent_port(self, steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Transparent port',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent port on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'])
            log.info('Successful in configuring vlan in client')
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,**param):
        sleep(20) 
        up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
        assert ((up != 0) and (down != 0))
        log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))    

    @aetest.cleanup
    def Disabling_VLAN_in_Server(self,steps,ctrl,server,client,**param):
    
   
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')
        
        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],param['dn1_cvlan'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in client')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Transparent_Port_With_QinQ_Packets(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent_Port(self, etype, steps,ctrl,server,client,**param):
        
        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure Transparent port',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent port on dn')
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
       
        with steps.start('Configure QinQ VLAN in Client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in client')       
        
       
    @ aetest.test
    def verify_traffic(self,etype,steps,ctrl,server,client,**param):
        sleep(20) 
        up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
        assert ((up != 0) and (down != 0))
        log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))        
            
    @aetest.cleanup
    def Removing_VLAN(self,etype,steps,ctrl,server,client,**param):
    
        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
       
        with steps.start('Removnig QinQ VLAN in Client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['client_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in client')


class Two_Interface_Transaprent(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,**param):

        client2.connect()
        misc.execute_command(client2,'sudo ifconfig {} mtu 1492'.format(param['client2_inf']))

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        
        with steps.start('Configure Transparent in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent on dn')

        with steps.start('Configure Transparent in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent on dn')
                 
        with steps.start('Configure IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,**param):
        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,**param):
    
                 
        with steps.start('Removing IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        misc.execute_command(client2,'sudo ifconfig {} mtu 1500'.format(param['client2_inf']))
        client2.disconnect()


class Two_Interface_Transaprent_Q(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure Transparent in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent on dn')

        with steps.start('Configure Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')
                 
        
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,**param):

        with steps.start('Configure IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('Removing IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        
        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,**param):
    
                 
        with steps.start('Configure Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Qvlan on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Two_Interface_Transaprent_QinQ(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure Transparent in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Enabling Transparent on dn')

        with steps.start('Configure QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Configure IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('Removing IP in Server',continue_=True) as step: 
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        
        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')
        

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,etype,**param):
    

        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

class Two_Interface_Same_Q_Vlan(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')

        with steps.start('Configure Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')
                 
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,**param):

        

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 


        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

       

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,**param):

        with steps.start('Removing Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Removing Qvlan on dn')
    
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Removing Qvlan on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

class Two_Interface_Different_Q_Vlan(aetest.Testcase):

    

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,**param):

      

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')

        with steps.start('Configure Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=str(int(param['dn1_cvlan'])+1),vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')
                 
        
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,**param):

      

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])+1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')


        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])+1),param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

       

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,**param):

        with steps.start('Removing Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Removing Qvlan on dn')
    
        

        with steps.start('Removing Qvlan in dn port2',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Removing Qvlan on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Two_Interface_Q_QinQ(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Qvlan on dn')

        with steps.start('Configure QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        
        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')
        

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,etype,**param):
    
        with steps.start('Removing Qvlan in dn port1',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='disable')      
            log.info('sucessful in Removing Qvlan on dn')

        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()


@aetest.loop(etype = ['0x8100', '0x88A8'])
class Two_Interface_Same_QinQ(aetest.Testcase):

    @aetest.setup
    def Configure_QinQ(self, steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure QinQ VLAN in dn port1',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')

        with steps.start('Configure QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,etype,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        '''with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')'''

        '''with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')'''

        
        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')
        

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,etype,**param):
    
        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')

        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Two_Interface_Different_QinQ(aetest.Testcase):

    @aetest.setup
    def Configure_Transparent(self, steps,ctrl,server,client,client2,etype,**param):

       

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        client2.connect()
        with steps.start('Configure QinQ VLAN in dn port1',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')

        with steps.start('Configure QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=str(int(param['dn1_cvlan'])+1),svlan=str(int(param['dn1_svlan'])+1),ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        with steps.start('Configure IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'])
            log.info('Successful in configuring IP in Client')

        
    
    @ aetest.test
    def verify_traffic(self,steps,ctrl,server,client,client2,etype,**param):

     

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        sleep(20) 
        with steps.start('client1 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])+1),str(int(param['dn1_svlan'])+1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        
        sleep(20)
        with steps.start('client2 traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client2,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])+1),str(int(param['dn1_svlan'])+1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Removing  vlan in Server')
        

    @aetest.cleanup
    def Removing_Ips(self,steps,ctrl,server,client,client2,etype,**param):

    
    
        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')

        with steps.start('Removing QinQ VLAN in dn port2',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf1'],cvlan=str(int(param['dn1_cvlan'])+1),svlan=str(int(param['dn1_svlan'])+1),ethertype=etype,svlan_prio='5',cvlan_prio='3',status='disable')      
            log.info('sucessful in Removing Double VLAN on dn')
        
        #Configure IP on client PC
        with steps.start('Removing IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

        with steps.start('Removing IP in client2',continue_=True) as step: 
            assert misc.config_ip(client2,param['client2_inf'],param['client2_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client2')

        client2.disconnect()

class Same_Mvlan(aetest.Testcase):
    @aetest.setup
    def setup_management_vlan(self,steps,ctrl,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,**param):
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,**param):
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')

class Different_Mvlan(aetest.Testcase):
    @aetest.setup
    def setup_management_vlan(self,steps,ctrl,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
    
        

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,**param):
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')
        sleep(10)
        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')
            
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,**param):
        

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')    

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Same_Mqinq_Vlan(aetest.Testcase):
    @aetest.setup
    def config_qinq_vlan(self,steps,ctrl,server,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')

    @ aetest.test
    def test_QinQ_management_vlan(self,steps,ctrl,server,etype,**param):
        sleep(10)
        with steps.start('Verifying POP GUI access',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

    @aetest.cleanup
    def removing_vlan_configs(self,steps,ctrl,server,etype,**param):

        with steps.start('Removing QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Removing QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Different_Mqinq_Vlan(aetest.Testcase):
    @aetest.setup
    def config_qinq_vlan(self,steps,ctrl,server,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],param['pop_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on POP')

        

    @ aetest.test
    def test_QinQ_management_vlan(self,steps,ctrl,server,etype,**param):
        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['pop_mcvlan'],param['pop_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')
        sleep(10)
        with steps.start('Verifying POP GUI access',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['pop_mcvlan'],param['pop_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')
        sleep(10)
        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable')

    @aetest.cleanup
    def removing_vlan_configs(self,steps,ctrl,server,etype,**param):

        with steps.start('Removing QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],param['pop_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on POP')


class Single_Data_Vlan_Single_Same_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))

    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,client,**param):
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')
        sleep(10)
        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,**param):
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')       

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from ctrl',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in removing Single VLAN on dn')
        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

class Single_Data_Vlan_Single_Different_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))

    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    

    @ aetest.test
    def verification(self,steps,ctrl,server,client,**param):
        
        sleep(10)

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')
        
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,**param):
        

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')       

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from ctrl',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in removing Single VLAN on dn')
        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')


@aetest.loop(etype = ['0x8100', '0x88A8'])
class Single_Data_Vlan_Double_Same_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))

    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,client,etype,**param):
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Removing QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Removing QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable') 

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from ctrl',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in removing Single VLAN on dn')
        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')


@aetest.loop(etype = ['0x8100', '0x88A8'])
class Single_Data_Vlan_Double_Different_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))

    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],param['pop_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        
    

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,client,etype,**param):
        sleep(10)
        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Removing QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable') 

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['pop_mcvlan'],param['pop_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Removing QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['pop_mcvlan'],param['pop_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable') 

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_cvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Removing QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on POP')

        

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_cvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from ctrl',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_cvlan'],status='disable')      
            log.info('sucessful in removing Single VLAN on dn')
        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

class Same_Single_Vlan_On_Data_Management(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))

    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

        
    

    @ aetest.test
    def verify_gui_page(self,steps,ctrl,server,client,**param):
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_mcvlan'],vlan_prio='7',status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')
            
         
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')
        

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            ip = param['client_data_ipv4'].rsplit('/', 1)[0]
            filter = 'ip.src == {}&&vlan.id == {}&&vlan.priority==7'.format(ip,param['dn1_mcvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,**param):
        

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')       

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_data_ipv4'],status='disable')
            log.info('Successful in configuring vlan in Server')
        with steps.start('Removing vlan configs from ctrl',continue_=True) as step:
            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=param['dn1_mcvlan'],status='disable')      
            log.info('sucessful in removing Single VLAN on dn')
        with steps.start('Removing IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Client')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Double_Data_Vlan_Single_Same_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        
    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')


        
        
        
        
    

    @ aetest.test
    def verifyication(self,steps,ctrl,server,client,etype,**param):
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            if etype =='0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id == {}&&vlan.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in QinQ VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')       

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,status='disable')      
            log.info('sucessful in Removing QinQ VLAN on dn')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Double_Data_Vlan_Single_Different_Management_Vlan(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        
    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'])
            log.info('Successful in configuring mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'])
            log.info('Successful in configuring mvlan in POP')
    
        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')



    @ aetest.test
    def verifyication(self,steps,ctrl,server,client,etype,**param):
        
        sleep(10)
        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['dn1_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Configuring MVLAN on Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'])
            log.info('Successful in configuring vlan in Server')
        sleep(10)
        with steps.start('Verifying GUI page of POP',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],param['pop_mcvlan'],param['server_mgmt_ipv4'],status='disable')
            log.info('Successful in Removing vlan in Server')
        

        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            if etype =='0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id == {}&&vlan.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==5&&vlan.priority==3'.format(ip,param['dn1_cvlan'],param['dn1_svlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in QinQ VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,etype,**param):
        
        with steps.start('Removing MVLAN on POP and DN',continue_=True) as step:
            assert cli.config_single_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in DN')
            assert cli.config_single_mvlan(ctrl,param['pop_name'],param['pop_mcvlan'],status='disable')
            log.info('Successful in Removing mvlan in POP')       

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],param['dn1_svlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_cvlan'],svlan=param['dn1_svlan'],ethertype=etype,status='disable')      
            log.info('sucessful in Removing QinQ VLAN on dn')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class Same_Double_Vlan_On_Data_Management(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)
        
    def Verify_traffic(self,client,server_data_ipv4):

        log.info('Starting iperf client')
        up,down=misc.config_iperf_client(client,server_data_ipv4)
        assert ((up != 0.0) and (down != 0.0))
        
    @aetest.setup
    def setup_vlan(self,steps,ctrl,server,client,etype,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configuring QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='enable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Configuring QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='enable')

    

    @ aetest.test
    def verifyication(self,steps,ctrl,server,client,etype,**param):

        sleep(10)
        with steps.start('Verifying POP GUI access',continue_=True) as step:
            assert misc.verify_web_page(server,param['pop_management_ip'])
            log.info('Successful in verifying POP GUI with MVLAN')

        with steps.start('Verifying GUI page of DN',continue_=True) as step:
            assert misc.verify_web_page(server,param['dn1_management_ip'])
            log.info('Successful in verifying DN1 GUI with MVLAN')

        with steps.start('Removing QinQ Vlan in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_mgmt_ipv4'],ethertype=etype,status='disable')

        with steps.start('Configure QinQ VLAN in dn',continue_=True) as step:

            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_mcvlan'],svlan=param['dn1_msvlan'],ethertype=etype,svlan_prio='5',cvlan_prio='3',status='enable')      
            log.info('sucessful in Enabling Double VLAN on dn')
            
         
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')
        
        #Configure IP on client PC
        with steps.start('Configure IP in client',continue_=True) as step: 
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'])
            log.info('Successful in configuring IP in Client')


        with steps.start('Capturing and verifying traffic',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            p2 = Process(target=self.Verify_traffic,args=(client,param['server_data_ipv4']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyse Capture',continue_=True) as step:
            if etype =='0x8100':
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&vlan.id == {}&&vlan.priority==5&&vlan.priority==3'.format(ip,param['dn1_mcvlan'],param['dn1_msvlan'])
            else:
                ip = param['client_data_ipv4'].rsplit('/', 1)[0]
                filter = 'ip.src == {}&&vlan.id == {}&&ieee8021ad.id == {}&&ieee8021ad.priority==5&&vlan.priority==3'.format(ip,param['dn1_mcvlan'],param['dn1_msvlan'])
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res > 0:
                log.info('Successful in QinQ VLAN tagging')
            else:
                assert False

    @aetest.cleanup
    def removing_vlan_config(self,steps,ctrl,server,client,etype,**param):
        with steps.start('Removing QinQ Management VLAN on POP and DN',continue_=True) as step:
            assert cli.config_QinQ_mvlan(ctrl,param['dn1_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on DN1')
            assert cli.config_QinQ_mvlan(ctrl,param['pop_name'],param['dn1_mcvlan'],param['dn1_msvlan'],ethertype=etype,status='disable')
            log.info('Successful in configuring QinQ mvlan on POP')

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_mcvlan'],param['dn1_msvlan'],param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')
        with steps.start('Removing vlan configs from server',continue_=True) as step:
            assert cli.config_double_vlan(ctrl,param['dn1_name'],param['dn1_inf'],cvlan=param['dn1_mcvlan'],svlan=param['dn1_msvlan'],ethertype=etype,status='disable')      
            log.info('sucessful in Removing QinQ VLAN on dn')
        with steps.start('Configure IP in client',continue_=True) as step:
            assert misc.config_ip(client,param['client_inf'],param['client_data_ipv4'],status='disable')
            log.info('Successful in configuring IP in Client')



class common_cleanup(aetest.CommonCleanup):  
    @aetest.subsection
    def Disabling_L2bridge(self,steps,ctrl,server,client,**param):
        log.info('configuring l2bridge')
        with steps.start('Disabling L2 bridge',continue_=True) as step:
            assert cli.modify_network_l2bridge(ctrl,state='disable')
            log.info('Successful in configuring l2bridge')

        sleep(150)        
        ctrl.disconnect()
        ctrl.connect()
        with steps.start('Verify link status',continue_=True) as step:
            for i in range(0,3):
                sleep(100)
                data = fetch_cli.fetch_topology(ctrl)
                verify = fetch_cli.link_status(data)
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
        misc.execute_command(server,'rm index.html*')
        misc.execute_command(server,'sudo ifconfig {} mtu 1500'.format(param['server_inf']))
        misc.execute_command(client,'sudo ifconfig {} mtu 1500'.format(param['client_inf']))
        server.disconnect()
        client.disconnect()
        
       
    
if __name__ == '__main__': # pragma: no cover
    aetest.main()

