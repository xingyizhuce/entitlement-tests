import os
import sys

sys.path.append(os.getcwd())
from Utils.RemoteSSH import RemoteSSH


def get_release_info():
    system_info = {
        "ip": os.environ["System_IP"],
        "username": "root",
        "password": os.environ["Password"]
        }
        
    Product_Type = os.environ["Product_Type"]
    variant = os.environ["Variant"].lower()
    
    if Product_Type == "RHEL8":
        cmd = "rpm -q --qf='%{VERSION}\n' redhat-release"
        ret, output = RemoteSSH().run_cmd(system_info, cmd)
        release = output
        print release
    elif Product_Type in ["RHEL7", "RHEL-ALT"]:
        qf = "%{VERSION}"
        cmd = "rpm -q --qf='{0}\n' redhat-release-{1}".format(qf, variant)
        ret, release = RemoteSSH().run_cmd(system_info, cmd)
        print release
    else:
        qf = "%{RELEASE}"
        cmd = "rpm -q --qf='{0}\n' redhat-release-{1}".format(qf, variant)
        ret, release = RemoteSSH().run_cmd(system_info, cmd)
        print release
    return release

if __name__ == '__main__':
    get_release_info()
