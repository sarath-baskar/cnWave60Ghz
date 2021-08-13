# To run the job:
# pyats run job $VIRTUAL_ENV/examples/steps/job/steps_example_job.py
# Description: This example shows the basic functionality of pyats 
#              with few passing tests

import os
from pyats.easypy import run
from pyats.datastructures.logic import And, Or, Not

def main():
    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testscript = os.path.join(test_path, 'VLAN/vlan_verify.py')


    run(testscript=testscript,
    ctrl_alias='CTRL',
    server_alias='SERVER',
    client_alias='CLIENT',
    client2_alias='CLIENT2',
    dn_alias='DN'
    )
