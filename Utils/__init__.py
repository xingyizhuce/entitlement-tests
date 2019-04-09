import os

# Get username and password for testing system
try:
    system_ip = os.environ["System_IP"]
except KeyError as e:
    pass

try:
    system_password = os.environ["Password"]
except KeyError as e:
    system_password = "QwAo2U6GRxyNPKiZaOCx"

system_username = "root"
