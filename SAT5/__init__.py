import os

manifest_url = os.environ["Manifest_URL"]
distro = os.environ["Distro"]
variant = os.environ["Variant"]
arch = os.environ["Arch"]
product_type = os.environ['Product_Type']
test_level = os.environ["Test_Level"]
test_type = os.environ["Test_Type"]
sat5_server = os.environ["SAT5_Server"]
sat5_server_username = os.environ["SAT5_Server_Username"]
sat5_server_password = os.environ["SAT5_Server_Password"]

# Only RHEL8 and the HTB of other RHEL version needs to use Activation Key to register
try:
    sat5_activation_key = os.environ["SAT5_Activation_Key"]
except KeyError as e:
    pass

