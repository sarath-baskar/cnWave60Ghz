import re
import logging
import sys
from datetime import datetime



logger = logging.getLogger('config')

class fetch():
                        
    def link_status(node,kv='OFFLINE'):
        j = str(node)
        if kv in j:
            return False
        else:
            return True

    def fetch_topology(device,type_='Link'):
        return device.execute('tg topology ls')
        ''' print(raw_output)         
        #del raw_output[-1]
        raw_output[-1]=raw_output[-1].replace('\n','')
        s=''
        table_data={}
        Node={}
        Link={}
        Site={}
        for line in raw_output:
            if not line.strip():
              continue
            else:
              s += line
              
        lines = s.split('\n')
        logger.info(s)
        NodeName=0
        LinkName=0
        SiteName=0
        for line in lines:
            x=line.split()

            if line.startswith('NodeName') or line.startswith('-') or line.startswith('  '):
              NodeName=NodeName+1
              continue
            if line.startswith('LinkName'):
              LinkName=LinkName+1
              continue
            if line.startswith('SiteName'):
              SiteName=SiteName+1
              continue
            
            
            if NodeName >= 1 and LinkName == 0 and SiteName == 0:
              Node[x[0]]={}
              Node[x[0]]['MacAddr']=x[1]
              Node[x[0]]['PopNode']=x[2]
              Node[x[0]]['NodeType']=x[3]
              Node[x[0]]['Status']=x[4]
              Node[x[0]]['IsPrimary']=x[5]
              Node[x[0]]['SiteName']=x[6]

            
            if LinkName == 1 and SiteName == 0:
              Link[x[0]]={}
              Link[x[0]]['ANodeName']=x[1]
              Link[x[0]]['ZNodeName']=x[2]
              Link[x[0]]['Alive']=x[3]
              Link[x[0]]['LinkType']=x[4]
              Link[x[0]]['LinkupAttempts']=x[5]
              
            
            if SiteName == 1:
              Site[x[0]]={}
              Site[x[0]]['Latitude']=x[1]
              Site[x[0]]['Longitude']=x[2]
              Site[x[0]]['Altitude']=x[3]
              Site[x[0]]['Accuracy']=x[4]

        table_data['Node']=Node
        table_data['Link']=Link
        table_data['Site']=Site
        return table_datai'''

if __name__ == '__main__':
    fetch = Fetch()
