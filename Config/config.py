from time import sleep
import sys
import json
import logging
from Fetch.fetch import *
from API.request import *

logger = logging.getLogger('config')

class cli():
    
   
       
    def add_dn(device,name,site,eth,primary='True'):

        ''' This function is used to add DN to the controller

            input:
            =====
            device = controller ip <required>
            dn_ip = dn ip <required>
            name = Name of the DN <required>
            site = siteName to which DN is to be added <required>
            primary = 'True' or 'False' <optional> by default it is True
            
            output:
            ======
            returns the status of the execution as True or False
        '''
        

        radio1 = eth.replace(eth[0:2],'12')
        radio2 = eth.replace(eth[0:2],'22') 
        if primary == True:
            
            return device.execute('tg2 node add -n {0} -m {1} --wlan_mac_addrs {2},{3} -s {4} --node_type dn  --is_primary'.format(name,eth,radio1,radio2,site))
        else:
            
            return device.execute('tg2 node add -n {0} -m {1} --wlan_mac_addrs {2},{3} -s {4} --node_type dn'.format(name,eth,radio1,radio2,site))

    def add_cn(device,name,site,eth):

        ''' This function is used to add CN to the controller

            input:
            =====
            device = controller ip <required>
            cn_ip = cn ip <required>
            name = Name of the CN <required>
            site = siteName to which CN is to be added <required>
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        radio1 = eth.replace(eth[0:2],'12')
        return device.execute('tg2 node add -n {0} -m {1} --wlan_mac_addrs {2} -s {3} --node_type cn'.format(name,eth,radio1,site))


    def del_node(device,name,to_do='force'):

        ''' This function is used to delete node to the controller

            input:
            =====
            device = controller ip <required>
            name = Name of the node <required>
            to_do = '' or 'force' <optional> by default it is ''
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        
        if to_do == 'force':
            return device.execute('tg2 node del -n {0} --force'.format(name))
        else:
            return device.execute('tg2 node del -n {0}'.format(name))

    def add_site(device,site,lat,lon,alt,acc):

        ''' This function is used to add site to the controller

            input:
            =====
            device = controller ip <required>
            site = Name of the site <required>
            lat = latitude of the site <required>
            lon = longitude of the site <required>
            alt = altitude of the site <required>
            acc = accuracy of the site <required>
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        
        return device.execute('tg2 site add -n {0} --lon {1} --lat {2} --alt {3} --acc {4}'.format(site,lon,lat,alt,acc))

    def del_site(device,site):

        ''' This function is used to delete site to the controller

            input:
            =====
            device = controller ip <required>
            site = Name of the site <required>
            lat = latitude of the site <required>
            lon = longitude of the site <required>
            alt = altitude of the site <required>
            acc = accuracy of the site <required>
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        
        return device.execute('tg2 site del -n {}'.format(site))
       
            

    def add_link( device, init_name, resp_name, init_mac, resp_mac, init_radio='radio1', resp_radio='radio1', link_type='wireless'):

        ''' This function is used to add a link to the controller

            input:
            =====
            device = controller ip <required>
            init_ip = initiator ip <required>
            init_name = initiator name <required>
            resp_ip = responder ip <required>
            resp_name = responder name <required>
            link_type = 'wireless' or 'wired' <optional> by default it is wireless
            
          
            output:
            ======
            returns the status of the execution as True or False
        '''

        if init_radio == 'radio1':
            init_mac = init_mac.replace(init_mac[0:2],'12') 
        else:
            init_mac = init_mac.replace(init_mac[0:2],'22') 
        if resp_radio == 'radio1':
            resp_mac = resp_mac.replace(resp_mac[0:2],'12') 
        else:
            resp_mac = resp_mac.replace(resp_mac[0:2],'22') 
        return device.execute('tg2 link add -a {0} --a_node_mac {1} -z {2} --z_node_mac {3} --{4}'.format(init_name,init_mac,resp_name,resp_mac,link_type))
        
        
    def del_link(device,init_name,resp_name,to_do='force'):

        ''' This function is used to delete a link from the controller

            input:
            =====
            device = controller ip <required>
            init_ip = initiator ip <required>
            init_name = initiator name <required>
            resp_ip = responder ip <required>
            resp_name = responder name <required>
            to_do = '' or 'force' <optional> by default it is ''
            
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        
        if to_do == 'force':
            return device.execute('tg2 link del -a {0}  -z {1} --force'.format(init_name,resp_name))
        else:
            return device.execute('tg2 link del -a {0}  -z {1}'.format(init_name,resp_name))

    def link_state(device,iname,rname,state='up'):

        ''' This function is used to make chages in the link state

            input:
            =====
            device = controller ip <required>
            iname = initiator name <required>
            rname = responder name <required>
            state = 'up' or 'down' <optional> by default it is up
            
          
            output:
            ======
            returns the status of the execution as True or False
        '''
        
        return device.execute('tg2 link {0} -i {1} -r {2}'.format(state,iname,rname))

    def config_pop_node(device,pop_name,ip,iface,gw,routing):

        device.execute('tg2 config modify node -n {} -s popParams.POP_ADDR "{}"'.format(pop_name,ip))
        device.execute('tg2 config modify node -n {} -s popParams.POP_IFACE "{}"'.format(pop_name,iface))
        device.execute('tg2 config modify node -n {} -s popParams.GW_ADDR "{}"'.format(pop_name,gw))
        if routing == 'STATIC':
            device.execute('tg2 config modify node -n {} -s popParams.POP_STATIC_ROUTING "1"'.format(pop_name)) 
        return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        
    def modify_network_GPS(device,state='1'):
        return device.execute('tg2 config modify network -i radioParamsBase.fwParams.forceGpsDisable {}'.format(state))
        
    def modify_network_l2bridge(device,state='enable'):
        if state == 'enable':
            device.execute('tg2 config modify network -s envParams.CAMBIUM_L2_BRIDGE_IFACE "nic1"')
            return device.execute('tg2 config set network overrides --overrides_file /data/cfg/network_config_overrides.json')
            
        if state == 'disable':
            device.execute('tg2 config modify network -s envParams.CAMBIUM_L2_BRIDGE_IFACE ""')
            return device.execute('tg2 config set network overrides --overrides_file /data/cfg/network_config_overrides.json')
        
        
        

    def modify_network_mngd_config(device,state='true'):
        return device.execute('tg2 config modify network -b sysParams.managedConfig  {}'.format(state))

    def modify_network_wsec(device,state='0'):
        return device.execute('tg2 config modify network -i radioParamsBase.fwParams.wsecEnable  {}'.format(state))
        
    def modify_node_CPE(device,node_name,interface,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s envParams.CPE_INTERFACE "{}"'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json') 
        elif status == 'disable':
            device.execute('tg2 config modify node -n {} -s envParams.CPE_INTERFACE ""'.format(node_name))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        
    def config_relay(device,node_name,interface):
        device.execute('tg2 config modify node -n {} -s envParams.OPENR_IFACE_PREFIXES "terra,{}"'.format(node_name,interface))
        return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        
    def config_management_ip(device,node_name,management_ip):
        device.execute('tg2 config modify node -n {} -s  envParams.CAMBIUM_MGMT_IPV4_ADDR "{}"'.format(node_name,management_ip))
        return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        
    def config_management_vlan(device,node_name,vlan_id,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s  envParams.CAMBIUM_MGMT_VLAN_ID "{}"'.format(node_name,vlan_id))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        if status == 'disable':
            device.execute(device, 'tg2 config modify node -n {} -s  envParams.CAMBIUM_MGMT_VLAN_ID ""'.format(node_name))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
    
    def config_single_vlan(device,node_name,interface,vlan_id='',vlan_prio='0',status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.nativeVID "{}"'.format(node_name,interface,vlan_id))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.vlanPortType 1'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.nativePri {}'.format(node_name,interface,vlan_prio))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
            
        else:
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.nativeVID ""'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.vlanPortType 0'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.nativePri 0'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        
    def config_double_vlan(device,node_name,interface,svlan='',cvlan='',svlan_prio='0',cvlan_prio='0',ethertype='0x8100',status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.nativeVID "{}"'.format(node_name,interface,cvlan))
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.svlanId "{}"'.format(node_name,interface,svlan))
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.svlanEtherType "{}"'.format(node_name,interface,ethertype))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.nativePri {}'.format(node_name,interface,cvlan_prio))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.svlanPri {}'.format(node_name,interface,svlan_prio))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.vlanPortType 2'.format(node_name,interface))        
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
            
        else:
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.nativeVID ""'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.svlanId ""'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.svlanEtherType "0x8100"'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.nativePri 0'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.svlanPri 0'.format(node_name,interface))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.{}.vlanPortType 0'.format(node_name,interface))        
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
    
    def config_vlan_allowed_list(device,node_name,interface,vlan_list='',status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.vlanMembership "{}"'.format(node_name,interface,vlan_list))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
            
        else:
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.vlanMembership ""'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')


    def config_vlan_remarking(device,node_name,interface,ingress_vlan,remark_vlan,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.perVlanParams.{}.ingressRemarkVID "{}"'.format(node_name,interface,ingress_vlan,remark_vlan))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
    
        else:
            device.execute('tg2 config modify node -n {} -s  vlanParams.vlanPortParams.{}.perVlanParams.{}.ingressRemarkVID ""'.format(node_name,interface,ingress_vlan)) 
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

    def config_vlan_prio_remarking(device,node_name,interface,ingress_vlan,remark_prio,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -i  vlanParams.vlanPortParams.{}.perVlanParams.{}.ingressRemarkPri {}'.format(node_name,interface,ingress_vlan,remark_prio))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
    
        else:
            device.execute('tg2 config modify node -n {} -i  vlanParams.vlanPortParams.{}.perVlanParams.{}.ingressRemarkPri 0'.format(node_name,interface,ingress_vlan)) 
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

    def config_drop_single_tag(device,node_name,interface,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -i  vlanParams.vlanPortParams.{}.vlanAcceptFrameType 2'.format(node_name,interface))  
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        else:
            device.execute('tg2 config modify node -n {} -i  vlanParams.vlanPortParams.{}.vlanAcceptFrameType 1'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
    
    def config_vlan_drop_untag(device,node_name,interface,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -b  vlanParams.vlanPortParams.{}.dropUntaggedPkt true'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        else:
            device.execute('tg2 config modify node -n {} -b  vlanParams.vlanPortParams.{}.dropUntaggedPkt false'.format(node_name,interface))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

    def config_single_mvlan(device,node_name,vid,vid_prio=0,status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s envParams.CAMBIUM_MGMT_VLAN_ID "{}"'.format(node_name,vid))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.nativePri {}'.format(node_name,vid_prio))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

        else:
            device.execute('tg2 config modify node -n {} -s envParams.CAMBIUM_MGMT_VLAN_ID ""'.format(node_name))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.nativePri 0'.format(node_name))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

    def config_QinQ_mvlan(device,node_name,cvlan,svlan,cvlan_prio=0,svlan_prio=0,ethertype='0x8100',status='enable'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -s envParams.CAMBIUM_MGMT_VLAN_ID "{}"'.format(node_name,cvlan))
            device.execute('tg2 config modify node -n {} -s vlanParams.vlanPortParams.mgmt.svlanId "{}"'.format(node_name,svlan))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.nativePri {}'.format(node_name,cvlan_prio))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.svlanPri {}'.format(node_name,svlan_prio))
            device.execute('tg2 config modify node -n {} -s vlanParams.vlanPortParams.mgmt.svlanEtherType "{}"'.format(node_name,ethertype))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

        else:
            device.execute('tg2 config modify node -n {} -s envParams.CAMBIUM_MGMT_VLAN_ID ""'.format(node_name))
            device.execute('tg2 config modify node -n {} -s vlanParams.vlanPortParams.mgmt.svlanId ""'.format(node_name))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.nativePri 0'.format(node_name))
            device.execute('tg2 config modify node -n {} -i vlanParams.vlanPortParams.mgmt.svlanPri 0'.format(node_name))
            device.execute('tg2 config modify node -n {} -s vlanParams.vlanPortParams.mgmt.svlanEtherType "0x8100" '.format(node_name))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')

    def config_option82(device,node_name,status='enable',circuitid='None',remoteid='None'):
        if status == 'enable':
            device.execute('tg2 config modify node -n {} -b  dhcpParams.dhcpOpt82.opt82Enabled true'.format(node_name))
            if circuitid != 'None':
                device.execute('tg2 config modify node -n {} -s  dhcpParams.dhcpOpt82.circuitID "{}"'.format(node_name,circuitid))
            if remoteid != 'None':
                device.execute('tg2 config modify node -n {} -s  dhcpParams.dhcpOpt82.remoteID "{}"'.format(node_name,remoteid))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
        else:
            device.execute('tg2 config modify node -n {} -b  dhcpParams.dhcpOpt82.opt82Enabled false'.format(node_name))
            device.execute('tg2 config modify node -n {} -s  dhcpParams.dhcpOpt82.circuitID ""'.format(node_name))
            device.execute('tg2 config modify node -n {} -s  dhcpParams.dhcpOpt82.remoteID ""'.format(node_name))
            return device.execute('tg2 config set node overrides --overrides_file /data/cfg/node_config_overrides.json')
            
    def config_interface(device,inf,status):
        return device.execute('ifconfig {0} {1}'.format(inf,status))

class api():

    

    def set_ignition_state(ctrl_ip,link_name,status='true'):
        url = "https://{}/api/v2/setIgnitionState".format(ctrl_ip)
        string = '{\"linkAutoIgnite\": {\"dummy\": status}}'
        payload=string.replace("dummy",str(link_name)).replace("status",str(status))
        return request(str(url),payload,"POST")

    def set_link_state(ctrl_ip,iname, rname,action = '1'):
        url = "https://{}/api/v2/setLinkStatus".format(ctrl_ip)
        string = "{\"action\": state, \"initiatorNodeName\": \"iname\", \"responderNodeName\": \"rname\"}"
        
        payload=string.replace("state",str(action)).replace("iname",str(iname)).replace("rname",str(rname))
        return request(str(url),payload,"POST")

    def get_link_state(ctrl_ip,link_name):
        url = "https://{}/api/v2/getLink".format(ctrl_ip)
        string = "{\"name\": \"dummy\"}"
        payload=string.replace("dummy",str(link_name))
        return request(str(url),payload,"POST")
             
    def config_l2_bridge(ctrl_ip,status='true'):
        url =  "https://{}/api/v2/modifyNetworkOverridesConfig".format(ctrl_ip)
        if status=='true':
            payload=r'{"overrides": "{\"envParams\":{\"CAMBIUM_L2_BRIDGE_IFACE\":\"nic1\"}}"}'
        else:
            payload=r'{"overrides": "{\"envParams\":{\"CAMBIUM_L2_BRIDGE_IFACE\":\"\"}}"}'
        return request(str(url),payload,"POST")

    def config_cpe(ctrl_ip,node_name,inf,status='true'):
        url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
        if status=='true':
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CPE_INTERFACE\":\"inf\"}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(inf))


        else:
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CPE_INTERFACE\":\"\"}}}"}'
            payload=string.replace("node_name",str(node_name))
        return request(str(url),payload,"POST")

    def config_management_ip(ctrl_ip,node_name,management_ip):
        url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
        string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_IPV4_ADDR\":\"mgmt_ip\"}}}"}'
        payload=string.replace("node_name",str(node_name)).replace("mgmt_ip",str(management_ip))
        return request(str(url),payload,"POST")

    def config_management_vlan(ctrl_ip,node_name,vlan_id,status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"mgmt_vlan\"}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("mgmt_vlan",str(vlan_id))
            return request(str(url),payload,"POST")
        if status == 'disable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"\"}}}"}'
            payload=string.replace("node_name",str(node_name))
            return request(str(url),payload,"POST")

    def config_single_vlan(ctrl_ip,node_name,interface,vlan_id='',vlan_prio='0',status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"nativePri\": vlan_prio,\"nativeVID\": \"vlan_id\",\"vlanPortType\": 1}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("vlan_id",str(vlan_id)).replace("vlan_prio",str(vlan_prio))
            logger.info(payload)
            return request(str(url),payload,"POST")
            
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"nativePri\": 0,\"nativeVID\": \"\",\"vlanPortType\": 0}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_double_vlan(ctrl_ip,node_name,interface,svlan='',cvlan='',svlan_prio='0',cvlan_prio='0',ethertype='0x8100',status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"svlanId\": \"s_vlan\",\"svlanPri\": svlan_prio,\"svlanEtherType\": \"ether\",\"nativePri\": cvlan_prio,\"nativeVID\": \"c_vlan\",\"vlanPortType\": 2}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("s_vlan",str(svlan)).replace("svlan_prio",str(svlan_prio)).replace("ether",str(ethertype)).replace("cvlan_prio",str(cvlan_prio)).replace("c_vlan",str(cvlan))
            logger.info(payload)
            return request(str(url),payload,"POST")
            
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"svlanId\": \"\",\"svlanPri\": 0,\"svlanEtherType\": \"0x8100\",\"nativePri\": 0,\"nativeVID\": \"\",\"vlanPortType\": 0}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_vlan_allowed_list(ctrl_ip,node_name,interface,vlan_list='',status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"vlanMembership\": \"vlan_list\"}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("vlan_list",str(vlan_list))
            logger.info(payload)
            return request(str(url),payload,"POST")
            
            
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"vlanMembership\": \"\"}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_vlan_remarking(ctrl_ip,node_name,interface,ingress_vlan,remark_vlan,status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"perVlanParams\": {\"ingress_vlan\": {\"ingressRemarkVID\": \"remark_vlan\"}}}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("ingress_vlan",str(ingress_vlan)).replace("remark_vlan",str(remark_vlan))
            logger.info(payload)
            return request(str(url),payload,"POST")
    
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"perVlanParams\": {\"ingress_vlan\": {\"ingressRemarkVID\": \"\"}}}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("ingress_vlan",str(ingress_vlan))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_vlan_prio_remarking(ctrl_ip,node_name,interface,ingress_vlan,remark_prio,status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"perVlanParams\": {\"ingress_vlan\": {\"ingressRemarkPri\": remark_prio}}}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("ingress_vlan",str(ingress_vlan)).replace("remark_prio",str(remark_prio))
            logger.info(payload)
            return request(str(url),payload,"POST")
          
    
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"perVlanParams\": {\"ingress_vlan\": {\"ingressRemarkPri\": 0}}}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface)).replace("ingress_vlan",str(ingress_vlan)).replace("remark_prio",str(remark_prio))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_drop_single_tag(ctrl_ip,node_name,interface,status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"vlanAcceptFrameType\": 2}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")
            
           
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"vlanAcceptFrameType\": 1}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_vlan_drop_untag(device,node_name,interface,status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"dropUntaggedPkt\": true}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")
           
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"inf\": {\"dropUntaggedPkt\": false}}}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("inf",str(interface))
            logger.info(payload)
            return request(str(url),payload,"POST")

    def config_single_mvlan(ctrl_ip,node_name,vid,vid_prio=0,status='enable'):

        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"mgmt_vlan\"}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("mgmt_vlan",str(vid))
            string1=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"mgmt\": {\"nativePri\": vid_prio}}}}}"}'
            payload1=string1.replace("node_name",str(node_name)).replace("vid_prio",vid_prio)
            logger.info(payload)
            logger.info(payload1)
            request(str(url),payload,"POST")
            return request(str(url),payload1,"POST")

        if status == 'disable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"\"}}}"}'
            payload=string.replace("node_name",str(node_name))
            string1=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"mgmt\": {\"nativePri\": 0}}}}}"}'
            payload1=string1.replace("node_name",str(node_name))
            logger.info(payload)
            logger.info(payload1)
            request(str(url),payload,"POST")
            return request(str(url),payload1,"POST")

    def config_QinQ_mvlan(ctrl_ip,node_name,cvlan,svlan,cvlan_prio=0,svlan_prio=0,ethertype='0x8100',status='enable'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"mgmt_vlan\"}}}"}'
            payload=string.replace("node_name",str(node_name)).replace("mgmt_vlan",str(cvlan))
            string1=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"mgmt\": {\"nativePri\": vid_prio,\"svlanId\": \"svlan\",\"svlanPri\": svlan_prio,\"svlanEthertype\":\"ether\"}}}}}"}'
            payload1=string1.replace("node_name",str(node_name)).replace("vid_prio",str(cvlan_prio)).replace("svlan",str(svlan)).replace("svlan_prio",svlan_prio).replace("ether",ethertype)
            logger.info(payload)
            logger.info(payload1)
            request(str(url),payload,"POST")
            return request(str(url),payload1,"POST")
            

        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\":{\"envParams\":{\"CAMBIUM_MGMT_VLAN_ID\":\"\"}}}"}'
            payload=string.replace("node_name",str(node_name))
            string1=r'{"overrides": "{\"node_name\": {\"vlanParams\": {\"vlanPortParams\": {\"mgmt\": {\"nativePri\": 0,\"svlanId\": \"\",\"svlanPri\": 0,\"svlanEthertype\":\"0x8100\"}}}}}"}'
            payload1=string1.replace("node_name",str(node_name))
            logger.info(payload)
            logger.info(payload1)
            request(str(url),payload,"POST")
            return request(str(url),payload1,"POST")

    def config_option82(ctrl_ip,node_name,status='enable',circuitid='None',remoteid='None'):
        if status == 'enable':
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"dhcpParams\": {\"dhcpOpt82\": {\"opt82Enabled\": true}}}}"}'
            payload=string.replace("node_name",str(node_name))
            logger.info(payload)
            request(str(url),payload,"POST")

            if circuitid != 'None':
                string1=r'{"overrides": "{\"node_name\": {\"dhcpParams\": {\"dhcpOpt82\": {\"circuitID\": \"circuitid\"}}}}"}'
                payload1=string1.replace("node_name",str(node_name)).replace("circuitid",str(circuitid))
                logger.info(payload1)
                request(str(url),payload1,"POST")
            if remoteid != 'None':
                string2=r'{"overrides": "{\"node_name\": {\"dhcpParams\": {\"dhcpOpt82\": {\"remoteID\": \"remoteid\"}}}}"}'
                payload2=string2.replace("node_name",str(node_name)).replace("remoteid",str(remoteid))
                logger.info(payload2)
                request(str(url),payload2,"POST")
            return True
            
        else:
            url =  "https://{}/api/v2/modifyNodeOverridesConfig".format(ctrl_ip)
            string=r'{"overrides": "{\"node_name\": {\"dhcpParams\": {\"dhcpOpt82\": {\"opt82Enabled\": true,\"circuitID\": \"\",\"remoteID\": \"\"}}}}"}'
            payload=string.replace("node_name",str(node_name))
            logger.info(payload)
            return request(str(url),payload,"POST")
            
            
       
            
          
            
    

if __name__ == '__main__':
       config = Config()
