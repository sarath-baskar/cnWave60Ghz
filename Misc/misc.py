from time import sleep
import sys
import logging
import telnetlib
import pexpect
from re import compile
from Fetch.fetch import *

    
IPERF_PATTERN = compile(r' (\d{1,3}\S{0,4}\s{1}\S{1})bits/sec')

logger = logging.getLogger('misc')

class misc():
    

    
    def execute_command(device,cmd):
        device.execute(cmd)
        return True
    def config_access_vlan(device,os,int,vlan):
        if os == 'ngos':
           
            cmd1='''configure\n
                    interface {0}\n
                    switchport mode access\n
                    switchport access vlan {1}\n
                    end
                 '''.format(int,vlan)
            device.execute(cmd1)
        
        else:
            cmd='''
                   configure t\n
                   interface {0}\n
                   switchport mode access\n
                   switchport access vlan {1}\n
                   end
                '''.format(int,vlan)
         
    
    def config_iperf_server(device,status='enable'):
        if status == 'enable':
            device.execute(' killall iperf3') 
            return device.execute('iperf3 -s -i 1 > i.txt &')
        else:
            device.execute(' rm i.txt')
            return device.execute(' killall iperf3')

    def config_iperf_client(device,server_data_ip,direction='bidir',type='tcp',bw='1.8G',time='10'):
        server_data_ip=server_data_ip.rsplit('/', 1)[0]
        if direction == 'bidir':
            device.execute('killall iperf3')
            if type == 'tcp':
                raw_output=device.execute('iperf3 -c {0} -i 1 -t {1} --bidir | grep receiver'.format(server_data_ip,time),prompt_recovery=True)
            else:
                raw_output=device.execute('iperf3 -c {0} -i 1 -t {1} -u -b {2} --bidir | grep receiver'.format(server_data_ip,time,bw),prompt_recovery=True)

            if 'receiver' in raw_output:
                output = raw_output
                thr_Mbps = 0.0
                match = IPERF_PATTERN.search(output)
                raw_output=output.splitlines()
                if match:
                    thr_str = match.group(1)
                    if 'G' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) * 1e3
                    elif 'M' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0])
                    if 'K' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) / 1e3
                up=thr_Mbps
                output = str(raw_output[1])
                thr_Mbps = 0.0
                match = IPERF_PATTERN.search(output)
                if match:
                    thr_str = match.group(1)
                    if 'G' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) * 1e3
                    elif 'M' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0])
                    if 'K' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) / 1e3
                down=thr_Mbps
            else:
                up=0.0
                down=0.0
                return up,down
            return up,down

        else:
            device.execute('killall iperf3')
            if direction =='uplink':
                if type == 'tcp':
                    raw_output=device.execute('iperf3 -c {0} -i 1 -t {1}  | grep receiver'.format(server_data_ip,time),prompt_recovery=True,timeout=120)
                else:
                    raw_output=device.execute('iperf3 -c {0} -i 1 -t {1} -u -b {2}  | grep receiver'.format(server_data_ip,time,bw),prompt_recovery=True,timeout=120)
            else:
                if type == 'tcp':
                    raw_output=device.execute('iperf3 -c {0} -i 1 -t {1} -R | grep receiver'.format(server_data_ip,time),prompt_recovery=True,timeout=120)

                else:
                    raw_output=device.execute('iperf3 -c {0} -i 1 -t {1} -u -b {2} -R  | grep receiver'.format(server_data_ip,time,bw),prompt_recovery=True,timeout=120)

            if 'receiver' in raw_output:
                output = raw_output
                thr_Mbps = 0.0
                match = IPERF_PATTERN.search(output)
                raw_output=output.splitlines()
                if match:
                    thr_str = match.group(1)
                    if 'G' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) * 1e3
                    elif 'M' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0])
                    if 'K' in thr_str:
                        thr_Mbps = float(thr_str.split(' ')[0]) / 1e3
                return thr_Mbps
        

    def config_client_interface(device,inf):
        device.execute('ifconfig {} down'.format(inf))
        device.execute('ifconfig {} up'.format(inf))
        return device.execute('service network-manager restart')


    def capture_interface(device,inf,file):
        device.execute(' killall tcpdump')
        return device.execute(''' tcpdump -i {}  -G 10 -W 1 -w {} '''.format(inf,file))
        
    def analyse_capture(device,filter,file):
        device.execute('''tshark -r {} -2 -R '{}' | wc -l > dummy.txt'''.format(file,filter))
        string = device.execute('cat dummy.txt')
        device.execute(' rm {}'.format(file))
        device.execute(' rm dummy.txt')
        packet_count=str(string[0])
        return int(packet_count)

    def config_Q(device,inf,vlan_id,data_ip,assign_ip='yes',status='enable'):
        if status == 'enable':
            device.execute(' ip link add link {} {}.{} type vlan proto 802.1Q id {}'.format(inf,inf,vlan_id,vlan_id))
            if assign_ip == 'yes':
                device.execute(' ifconfig {}.{} {} up'.format(inf,vlan_id,data_ip))
                return True
            else:
                return True
        else:
            device.execute(' ip link del link {} {}.{}'.format(inf,inf,vlan_id))
            return True 

    def config_QinQ(device,inf,cvlan,svlan,data_ip,ethertype='0x8100',assign_ip='yes',status='enable'):
        if status == 'enable':
            if ethertype == '0x8100':
                device.execute(' ip link add link {} {}.{} type vlan proto 802.1Q id {}'.format(inf,inf,svlan,svlan)) 
            else:
                device.execute(' ip link add link {} {}.{} type vlan proto 802.1ad id {}'.format(inf,inf,svlan,svlan))

            device.execute(' ifconfig {}.{} up'.format(inf,svlan))
            device.execute(' ip link add link {}.{} {}.{}.{} type vlan proto 802.1Q id {}'.format(inf,svlan,inf,svlan,cvlan,cvlan))
            if assign_ip =='yes':
                device.execute(' ifconfig {}.{}.{} {} up'.format(inf,svlan,cvlan,data_ip))
                return True
            else:
                return True
        else:
            
            device.execute(' ip link del link {} {}.{}'.format(inf,inf,svlan))
            return True

    def config_ip(device,inf,data_ip,version='4',status='enable'):
        if version =='4':
            if status == 'enable':
            
                device.execute(' ifconfig {} {} up'.format(inf,data_ip))
                return True
            else:
                device.execute(' ifconfig {} 0.0.0.0 up'.format(inf))
                return True
        else:
            if status == 'enable':
            
                device.execute(' ifconfig {} inet6 add  {} up'.format(inf,data_ip))
                return True
            else:
                device.execute(' ifconfig {} inet6 del {} up'.format(inf,data_ip))
                return True


    def verify_web_page(device,mgmt_ip):
        output=device.execute('wget https://{} --no-check-certificate --timeout=10'.format(mgmt_ip))
        if '200 OK' in output:
            return True
        else:
            return False

    def run_dhclient(device,inf,version='4',status='enable'):
        device.execute('killall dhclient')
        if status == 'enable':
            device.execute('dhclient -{} {}'.format(version,inf),prompt_recovery=True)
            return True
        else:
            device.execute('dhclient -{} -r {}'.format(version,inf),prompt_recovery=True)
            return True



