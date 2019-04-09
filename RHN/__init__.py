import os

manifest_url = os.environ["Manifest_URL"]
variant = os.environ["Variant"]
arch = os.environ["Arch"]
rhn = os.environ["RHN"]
distro = os.environ["Distro"]
test_level = os.environ["Test_Level"]

# rhn server url
server_url = {
    "QA": "https://xmlrpc.rhn.qa.redhat.com/XMLRPC",
    "Live": "https://xmlrpc.rhn.redhat.com/XMLRPC"
}

# accounts used for rhn testing
account_rhn = {
    "Live": {
        "username": "qa@redhat.com",
        "password": "a85xH8a5w8EaZbdS"
    },
    "QA": {
        "username": "qa@redhat.com",
        "password": "redhatqa"
    }
}
