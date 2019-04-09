import os

sat6_server_hostname = os.environ["SAT6_Server_Hostname"]
sat6_server_ip = ""
try:
    sat6_server_ip = os.environ["SAT6_Server_IP"]
except KeyError as e:
    pass
sat6_server_username = os.environ["SAT6_Server_Username"]
sat6_server_password = os.environ['SAT6_Server_Password']
sat6_server_orglabel = os.environ['SAT6_Server_OrgLabel']

