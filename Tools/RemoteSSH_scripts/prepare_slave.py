import os
import sys

sys.path.append(os.getcwd())
from Utils.RemoteSSH import RemoteSSH

ip = os.environ["JSLAVEIP"]


def prepare_slave():
    system_info = {
        "ip": ip,
        "username": "root",
        "password": "redhat"
        }
    local_path = "CI/scripts/prepare_slave.sh"
    remote_path = "/tmp/prepare_slave.sh"
    RemoteSSH().upload_file(system_info, local_path, remote_path)
    ret, output = RemoteSSH().run_cmd(system_info, "bash {0}".format(remote_path))
    print output


if __name__ == '__main__':
    prepare_slave()
