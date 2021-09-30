# system imports
from os import chdir
from time import sleep
from datetime import datetime
import logging
import binascii
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
        ref_pp['network_name'] = ref_pp['dn'].custom['network_name']


        ref_pp['server_inf']=ref_pp['server'].custom['inf']
        ref_pp['server_data_ipv6']=ref_pp['server'].custom['ipv6']
        ref_pp['server_data_ipv4']=ref_pp['server'].custom['ipv4']
        ref_pp['server_mgmt_ipv4']=ref_pp['server'].custom['mgmt_ipv4']
        ref_pp['server_file']=ref_pp['server'].custom['capture_file']
        ref_pp['client_inf']=ref_pp['client'].custom['inf']
        ref_pp['client_data_ipv4']=ref_pp['client'].custom['ipv4']

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
                sleep(100)
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
        sleep(150)
        ctrl.connect()

    @aetest.subsection
    def verify_links(self,steps,ctrl):
        log.info('Verify link status')

        for i in range(0,3):
                sleep(100)
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:
                    break
                elif i == 2:
                    assert verify

        log.info('Successful in bringing up')


        
@aetest.loop(cid = ['\$nodeMac\$', '\$nodeName\$', '\$siteName\$', '\$networkName\$'])
class Option82_cid(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self,steps,server,ctrl,cid,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid=cid)      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,server,client,cid,**param):


        with steps.start('Initiate dhclient on client and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:

            mac=param['dn1_mac'].replace(':','')
            fin_rid=self.filter_generator(mac)

            if cid == '\$nodeMac\$':
                fin_cid=fin_rid

            elif cid == '\$nodeName\$':
                fin_cid=self.filter_generator(param['dn1_name'])
            
            elif cid == '\$siteName\$':
                fin_cid=self.filter_generator(param['dn1_site'])

            else:
                fin_cid=self.filter_generator(param['network_name'])

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')
        

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')

        

@aetest.loop(rid = ['\$nodeMac\$', '\$nodeName\$', '\$siteName\$', '\$networkName\$'])
class Option82_rid(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self, steps,ctrl,rid,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],remoteid=rid)      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,ctrl,server,client,rid,**param):

        with steps.start('Initiate dhclient on client and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:

            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)

            if rid == '\$nodeMac\$':
                fin_rid=fin_cid

            elif rid == '\$nodeName\$':
                fin_rid=self.filter_generator(param['dn1_name'])
            
            elif rid == '\$siteName\$':
                fin_rid=self.filter_generator(param['dn1_site'])

            else:
                fin_rid=self.filter_generator(param['network_name'])

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')


class Option82_custom_rid_cid(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self, steps,ctrl,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid=param['custom_cid'],remoteid=param['custom_rid'])      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,server,client,**param):

        with steps.start('Initiate dhclient on client and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:

            
            fin_cid=self.filter_generator(param['custom_cid'])

            fin_rid=self.filter_generator(param['custom_rid'])

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')
        

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')


@aetest.loop(rid = ['\$nodeMac\$', '\$nodeName\$', '\$siteName\$', '\$networkName\$'])
class Option82_custom_cid_defined_rid(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self, steps,ctrl,server,rid,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid=param['custom_cid'],remoteid=rid)      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,server,client,rid,**param):

        with steps.start('Initiate dhclient on client and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:

            fin_cid=self.filter_generator(param['custom_cid'])

            if rid == '\$nodeMac\$':
                mac=param['dn1_mac'].replace(':','')
                fin_rid=self.filter_generator(mac)

            elif rid == '\$nodeName\$':
                fin_rid=self.filter_generator(param['dn1_name'])
            
            elif rid == '\$siteName\$':
                fin_rid=self.filter_generator(param['dn1_site'])

            else:
                fin_rid=self.filter_generator(param['network_name'])

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')

@aetest.loop(cid = ['\$nodeMac\$', '\$nodeName\$', '\$siteName\$', '\$networkName\$'])
class Option82_custom_rid_defined_cid(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self,steps,server,ctrl,cid,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid=cid,remoteid=param['custom_rid'])      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,server,client,cid,**param):

        
        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])

            if cid == '\$nodeMac\$':
                mac=param['dn1_mac'].replace(':','')
                fin_cid=self.filter_generator(mac)

            elif cid == '\$nodeName\$':
                fin_cid=self.filter_generator(param['dn1_name'])
            
            elif cid == '\$siteName\$':
                fin_cid=self.filter_generator(param['dn1_site'])

            else:
                fin_cid=self.filter_generator(param['network_name'])

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,server,ctrl,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')
        

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')

class Option82_multiple_wildcard(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final

    @aetest.setup
    def Setup(self, steps,ctrl,server,**param):

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid="\$nodeName\$:\$nodeMac\$",remoteid="\$siteName\$:\$nodeMac\$")      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')

        with steps.start('configure ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'])
            log.info('Successful in configuring IP in Server')

    @ aetest.test
    def Test(self,steps,server,client,**param):

        with steps.start('Initiate dhclient on client and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:

            fin_cid_1=self.filter_generator(param['dn1_name'])
            fin_cid_2=self.filter_generator(param['dn1_mac'])


            fin_rid_1=self.filter_generator(param['dn1_site'])
            fin_rid_2=self.filter_generator(param['dn1_mac'])
            

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {}:{} && bootp.option.agent_information_option.agent_remote_id == {}:{}'.format(fin_cid_1,fin_cid_2,fin_rid_1,fin_rid_2)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down)) 

    @aetest.cleanup
    def cleanup(self,steps,ctrl,server,client,**param):


        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        
        with steps.start('Removing ip on server',continue_=True) as step:
            assert misc.config_ip(server,param['server_inf'],param['server_data_ipv4'],status='disable')
            log.info('Successful in Removing IP in Server')

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')


class Q_Vlan_option82(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final
    
    @aetest.setup
    def Configure_Q_Vlan_allowed_list(self, steps,ctrl,server,client,**param):
        vlans='{},{}-{}'.format(lis[0],lis[1],lis[3])

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
                if verify == True:               
                    break
                elif i == 2: 
                    assert verify
                sleep(100)
        
        with steps.start('Configure Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id=str(int(param['dn1_cvlan'])-1),status='enable')      
            log.info('sucessful in Enabling Single VLAN on dn')

        with steps.start('Configure Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='enable')      
            log.info('sucessful in configuring allowed q VLAN on dn')

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],circuitid='\$nodeMac\$',remoteid=param['custom_rid'])      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')
            

    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,server,client,**param):

        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Restarting DHCP server',continue_=True) as step:
            assert misc.execute_server_command(server,'systemctl restart isc-dhcp-server.service')

        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])
            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)

    

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {} && vlan.id =={}'.format(fin_cid,fin_rid,str(int(param['dn1_cvlan'])-1))
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')


        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

    @ aetest.test.loop(c_vlan=lis)
    def test_single_tagged_packets(self,c_vlan,steps,ctrl,server,client,**param):
    
        with steps.start('Configure Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],c_vlan,param['server_data_ipv4'])
            log.info('Successful in configuring vlan in Server')

        with steps.start('Restarting DHCP server',continue_=True) as step:
            assert misc.execute_server_command(server,'systemctl restart isc-dhcp-server.service')
            
        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],c_vlan,param['client_data_ipv4'],assign_ip='no')
            log.info('Successful in configuring vlan in client')

        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,str(param['client_inf']+'.'+str(c_vlan))))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])
            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)
            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if c_vlan==int(param['dn1_cvlan'])+4:
                if res < 4:
                    log.info('IP failed due to unallowed VLAN')
                else:
                    assert False
            elif res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        

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

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,str(param['client_inf']+'.'+str(c_vlan)),status='disable')
                
        with steps.start('Removing Q VLAN in Server',continue_=True) as step:
            assert misc.config_Q(server,param['server_inf'],c_vlan,param['server_data_ipv4'],status='disable')
            log.info('Removing Q vlan in Server')

        
            
        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],c_vlan,param['client_data_ipv4'],assign_ip='no',status='disable')
            log.info('Removing Q vlan in client')
                      
                            
            
    @aetest.cleanup
    def VLAN_config_cleanup(self,steps,ctrl,server,client,**param):
        vlans='{},{}-{}'.format(lis[0],lis[1],lis[3])
    
        with steps.start('Remove Q VLAN in dn',continue_=True) as step:

            assert cli.config_single_vlan(ctrl,param['dn1_name'],param['dn1_inf'],vlan_id='1',status='disable')      
            log.info('sucessful in Removing Single VLAN on dn')

        with steps.start('Removing Allowed Q VLAN in dn',continue_=True) as step:

            assert cli.config_vlan_allowed_list(ctrl,param['dn1_name'],param['dn1_inf'],vlan_list=vlans,status='disable')      
            log.info('sucessful in Removing allowed q VLAN on dn')

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')

@aetest.loop(etype = ['0x8100', '0x88A8'])
class QinQ_Vlan_option82(aetest.Testcase):

    def Capturing_Server_interface(self,server,server_inf,server_file):
        assert misc.capture_interface(server,server_inf,server_file)

    def obtain_ip(self,client,client_inf):
        assert misc.run_dhclient(client,client_inf)

    def filter_generator(self,value):
        my_str_as_bytes = str.encode(value)
        bin=(binascii.hexlify(my_str_as_bytes))
        fin=(str(bin).replace("'",'').replace('b',''))
        final=':'.join(re.findall('..', fin))
        return final
    
    @aetest.setup
    def setup(self, steps,ctrl,server,client,etype,**param):
        vlans='{},{}-{}'.format(lis1[0],lis1[1],lis1[3])

        with steps.start('Verifying links',continue_=True) as step:     
            log.info('Verify link status')

            for i in range(0,3):
                    
                data = fetch.fetch_topology(ctrl)
                verify = fetch.link_status(data)
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

        with steps.start('Configure option 82 in DN/CN',continue_=True) as step:

            assert cli.config_option82(ctrl,param['dn1_name'],remoteid=param['custom_rid'])      
            log.info('sucessful in Enabling DHCP option 82 with circuitid on DN/CN')
            

    @ aetest.test
    def test_untagged_packets(self,steps,ctrl,etype,server,client,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Restarting DHCP server',continue_=True) as step:
            assert misc.execute_server_command(server,'systemctl restart isc-dhcp-server.service')

        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,param['client_inf']))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])
            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)

    

            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {} && vlan.id =={}'.format(fin_cid,fin_rid,str(int(param['dn1_cvlan'])-1))
            res=misc.analyse_capture(server,filter,param['server_file'])
            if res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        with steps.start('Verify_traffic',continue_=True) as step:
            up,down=misc.config_iperf_client(client,param['server_data_ipv4'])
            assert ((up != 0) and (down != 0))
            log.info('Successful in Running Bidirectional traffic up {}, down {}'.format(up,down))

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],str(int(param['dn1_cvlan'])-1),str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disbale')
            log.info('Successful in configuring vlan in Server')

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,param['client_inf'],status='disable')

    @ aetest.test.loop(s_vlan=lis1)
    def test_single_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):
        
        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring vlan in Server')

        with steps.start('Restarting DHCP server',continue_=True) as step:
            assert misc.execute_server_command(server,'systemctl restart isc-dhcp-server.service')
            
        with steps.start('Configure Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'],assign_ip='no')
            log.info('Successful in configuring vlan in client')

        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,str(param['client_inf']+'.'+str(s_vlan))))
            p2.start()
            p1.join()
            p2.join()

        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])
            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)
            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if s_vlan==int(param['dn1_svlan'])+4:
                if res < 4:
                    log.info('No IP due to unallowed vlan')
                else:
                    assert False
            elif res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False

        

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

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,str(param['client_inf']+'.'+str(s_vlan)),status='disable')
                
        with steps.start('Removing QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],s_vlan,str(int(param['dn1_svlan'])-1),param['server_data_ipv4'],ethertype=etype,status='disable')
            log.info('Successful in Removing vlan in Server')

        with steps.start('Removing Q VLAN in client',continue_=True) as step:
            assert misc.config_Q(client,param['client_inf'],s_vlan,param['client_data_ipv4'],assign_ip='no',status='disable')
            log.info('Removing Q vlan in client')


    @ aetest.test.loop(s_vlan=lis1)
    def test_double_tagged_packets(self,steps,ctrl,server,client,etype,s_vlan,**param):

        with steps.start('Configure QinQ VLAN in Server',continue_=True) as step:
            assert misc.config_QinQ(server,param['server_inf'],param['dn1_cvlan'],s_vlan,param['server_data_ipv4'],ethertype=etype)
            log.info('Successful in configuring QinQ vlan in Server')

        with steps.start('Restarting DHCP server',continue_=True) as step:
            assert misc.execute_server_command(server,'systemctl restart isc-dhcp-server.service')

        with steps.start('Configure QinQ VLAN in client',continue_=True) as step:
            assert misc.config_QinQ(client,param['client_inf'],param['dn1_cvlan'],s_vlan,param['client_data_ipv4'],assign_ip='no',ethertype=etype)
            log.info('Successful in configuring QinQ vlan in client')

        with steps.start('Initiate dhclient and capture on Server',continue_=True) as step:
            p1 = Process(target=self.Capturing_Server_interface,args=(server,param['server_inf'],param['server_file']))
            p1.start()
            sleep(5)
            p2 = Process(target=self.obtain_ip,args=(client,str(param['client_inf']+'.'+str(s_vlan)+'.'+param['dn1_cvlan'])))
            p2.start()
            p1.join()
            p2.join()


        with steps.start('Analyzing packets',continue_=True) as step:


            fin_rid=self.filter_generator(param['custom_rid'])
            mac=param['dn1_mac'].replace(':','')
            fin_cid=self.filter_generator(mac)
            filter = 'bootp.option.agent_information_option.agent_circuit_id == {} && bootp.option.agent_information_option.agent_remote_id == {}'.format(fin_cid,fin_rid)
            res=misc.analyse_capture(server,filter,param['server_file'])
            if s_vlan==int(param['dn1_svlan'])+4:
                if res < 4:
                    log.info('No IP due to unallowed vlan')
                else:
                    assert False
            elif res >= 4:
                log.info('Successful in Verifying option 82 packets')
            else:
                assert False


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

        with steps.start('Release ip',continue_=True) as step:
            assert misc.run_dhclient(client,(param['client_inf']+'.'+str(s_vlan)+'.'+param['dn1_cvlan']),status='disable')

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

        with steps.start('Removing option 82 config',continue_=True) as step:
            assert cli.config_option82(ctrl,param['dn1_name'],status='disable')      
            log.info('sucessful in Removing DHCP option 82 on DN/CN')

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
                sleep(100)
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