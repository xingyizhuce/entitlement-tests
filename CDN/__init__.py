import os

try:
    manifest_url = os.environ["Manifest_URL"]
except KeyError as e:
    pass

try:
    variant = os.environ["Variant"]
except KeyError as e:
    pass

try:
    arch = os.environ["Arch"]
except KeyError as e:
    pass

try:
    cdn = os.environ["CDN"]
except KeyError as e:
    pass

try:
    product_type = os.environ['Product_Type']
except KeyError as e:
    pass

try:
    test_type = os.environ["Test_Type"]
except KeyError as e:
    pass

try:
    release_ver = os.environ["Release_Version"]
except KeyError as e:
    pass

try:
    candlepin = os.environ["Candlepin"]
except KeyError as e:
    pass

try:
    master_release = os.environ["master_release"]
except KeyError as e:
    pass

try:
    minor_release = os.environ["minor_release"]
except KeyError as e:
    pass

try:
    openshift_version = os.environ["Openshift_Version"]
except KeyError as e:
    pass

# RHEL Variant:
# 68  client
# 69  server-x86_64
# 71  workstation
# 72  server-s390x
# 74  server-ppc64
# 76  computenode-x86_64
# 135 server-x86_64         - RHEL6 HTB
# 155 workstation-x86_64    - RHEL6 HTB
# 279 server-ppc64le    - RHEL7
# 294 server-aarch64    - RHEL7

# The base repo of RHEL 7 Beta is rhel-7-desktop-beta-rpms
# The base repo of RHEL 7 HTB is rhel-7-server-htb-rpms
# The base repo of RHEL 7 GA is rhel-7-desktop-rpms
# Base on the base repo url when verify arch and release listing
# That is, test beta dirs/listing when Beta, test dist dir/listing when GA/Snapshot
base_repo = {
    "6": {
        "Beta": {
            "68": "rhel-6-desktop-beta-rpms",
            "69": "rhel-6-server-beta-rpms",
            "71": "rhel-6-workstation-beta-rpms",
            "72": "rhel-6-for-system-z-beta-rpms",
            "74": "rhel-6-for-power-beta-rpms",
            "76": "rhel-6-hpc-node-beta-rpms",
            },
        "HTB_Beta": {
            "135": "rhel-6-server-htb-rpms",
            "155": "rhel-6-workstation-htb-rpms"
        },
        "HTB_Snapshot": {
            "135": "rhel-6-server-htb-rpms",
            "155": "rhel-6-workstation-htb-rpms"
        },
        "GA": {
            "68": "rhel-6-desktop-rpms",
            "69": "rhel-6-server-rpms",
            "71": "rhel-6-workstation-rpms",
            "72": "rhel-6-for-system-z-rpms",
            "74": "rhel-6-for-power-rpms",
            "76": "rhel-6-hpc-node-rpms",
            "248": "rhel-6-server-rpms"
        }
    },
    "7": {
        "Beta": {
            "68": "rhel-7-desktop-beta-rpms",
            "69": "rhel-7-server-beta-rpms",
            "71": "rhel-7-workstation-beta-rpms",
            "72": "rhel-7-for-system-z-beta-rpms",
            "74": "rhel-7-for-power-beta-rpms",
            "76": "rhel-7-hpc-node-beta-rpms",
            "279": "rhel-7-for-power-le-beta-rpms",
            "294": "rhel-7-server-for-arm-beta-rpms",
            "420": "rhel-7-for-power-9-beta-rpms",
            "419": "rhel-7-for-arm-64-beta-rpms",
            "434": "rhel-7-for-system-z-a-beta-rpms"
        },
        "HTB_Beta": {
            "230": "rhel-7-server-htb-rpms",
            "231": "rhel-7-workstation-htb-rpms",
        },
        "HTB_Snapshot": {
            "230": "rhel-7-server-htb-rpms",
            "231": "rhel-7-workstation-htb-rpms",
        },
        "GA": {
            "68": "rhel-7-desktop-rpms",
            "69": "rhel-7-server-rpms",
            "71": "rhel-7-workstation-rpms",
            "72": "rhel-7-for-system-z-rpms",
            "74": "rhel-7-for-power-rpms",
            "76": "rhel-7-hpc-node-rpms",
            "279": "rhel-7-for-power-le-rpms",
            "294": "rhel-7-for-arm-rpms",
            "420": "rhel-7-for-power-9-rpms",
            "419": "rhel-7-for-arm-64-rpms",
            "434": "rhel-7-for-system-z-a-rpms",
        }
    },
    "8": {
        "Beta": {
            "486": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "363": "rhel-8-for-aarch64-baseos-beta-rpms,rhel-8-for-aarch64-appstream-beta-rpms",
            "362": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
            "433": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
            "495": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "496": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
            "497": "rhel-8-for-aarch64-baseos-beta-rpms,rhel-8-for-aarch64-appstream-beta-rpms",
            "498": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
            "499": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "501": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "487": {
                "x86_64": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
                "s390x": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
            },
            "488": {
                "x86_64": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
                "s390x": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
            }
        },
        "HTB_Beta": {
            "230": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "489": {
                "aarch64": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
            },
            "233": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "232": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "542": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
            "543": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms",
            "544": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
            "545": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms"
        },
        "HTB_Snapshot": {
            "230": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "489": {
                "aarch64": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
            },
            "233": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "232": {
                "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
                "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
                "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
            "542": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
            "543": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms",
            "544": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
            "545": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms"
        },
        "GA": {
            "479": "rhel-8-for-x86_64-baseos-rpms,rhel-8-for-x86_64-appstream-rpms",
            "419": "rhel-8-for-aarch64-baseos-rpms,rhel-8-for-aarch64-appstream-rpms",
            "279": "rhel-8-for-ppc64le-baseos-rpms,rhel-8-for-ppc64le-appstream-rpms",
            "72": "rhel-8-for-system-z-baseos-rpms,rhel-8-for-system-z-appstream-rpms",
        }
    }
}

# default_repo is for repos enabled by default after subscribe suitable pool.
# Generally, GA repo is enabled by default, others(such as beta repo) need to be disabled
default_repo = {
    "6": {
        "68": "rhel-6-desktop-rpms",
        "69": "rhel-6-server-rpms",
        "71": "rhel-6-workstation-rpms",
        "72": "rhel-6-for-system-z-rpms",
        "74": "rhel-6-for-power-rpms",
        "76": "rhel-6-hpc-node-rpms",
        "135": "rhel-6-server-htb-rpms",
        "155": "rhel-6-workstation-htb-rpms",
        "248": "rhel-6-server-rpms"
    },
    "7": {
        "68": "rhel-7-desktop-rpms",
        "69": "rhel-7-server-rpms",
        "71": "rhel-7-workstation-rpms",
        "72": "rhel-7-for-system-z-rpms",
        "74": "rhel-7-for-power-rpms",
        "76": "rhel-7-hpc-node-rpms",
        "279": "rhel-7-for-power-le-rpms",
        "294": "rhel-7-for-arm-rpms",
        "230": "rhel-7-server-htb-rpms",
        "231": "rhel-7-workstation-htb-rpms",
        "420": "rhel-7-for-power-9-rpms",
        "419": "rhel-7-for-arm-64-rpms",
        "434": "rhel-7-for-system-z-a-rpms"
    },
    "8": {
        "486": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
        "363": "rhel-8-for-aarch64-baseos-beta-rpms,rhel-8-for-aarch64-appstream-beta-rpms",
        "362": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
        "433": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
        "495": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
        "496": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
        "497": "rhel-8-for-aarch64-baseos-beta-rpms,rhel-8-for-aarch64-appstream-beta-rpms",
        "498": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
        "499": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
        "501": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
        "487": {
            "x86_64": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "s390x": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
            "ppc64le": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
        },
        "488": {
            "x86_64": "rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms",
            "s390x": "rhel-8-for-s390x-baseos-beta-rpms,rhel-8-for-s390x-appstream-beta-rpms",
            "ppc64le": "rhel-8-for-ppc64le-baseos-beta-rpms,rhel-8-for-ppc64le-appstream-beta-rpms",
        },
        "230": {
            "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
            "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
            "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
            },
        "489": {
            "aarch64": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
        },
        "233": {
            "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
            "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
            "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
        },
        "232": {
            "x86_64": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
            "s390x": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
            "ppc64le": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms"
        },
        "542": "rhel-8-for-x86_64-baseos-htb-rpms,rhel-8-for-x86_64-appstream-htb-rpms",
        "543": "rhel-8-for-ppc64le-baseos-htb-rpms,rhel-8-for-ppc64le-appstream-htb-rpms",
        "544": "rhel-8-for-aarch64-baseos-htb-rpms,rhel-8-for-aarch64-appstream-htb-rpms",
        "545": "rhel-8-for-s390x-baseos-htb-rpms,rhel-8-for-s390x-appstream-htb-rpms",
        "479": "rhel-8-for-x86_64-baseos-rpms,rhel-8-for-x86_64-appstream-rpms",
        "419": "rhel-8-for-aarch64-baseos-rpms,rhel-8-for-aarch64-appstream-rpms",
        "279": "rhel-8-for-ppc64le-baseos-rpms,rhel-8-for-ppc64le-appstream-rpms",
        "72": "rhel-8-for-system-z-baseos-rpms,rhel-8-for-system-z-appstream-rpms",
    }
}


# RHEL Beta relies on RHEL GA, and some beta packages also rely on optional repo, so set ga optional repo for Beta
# testing phase

# RHEL HTB is standalone, it doesn't rely on RHEL ga repos, so set its own htb base repo for Beta and Snapshot phase
# RHEL HTB needs testing on Beta and Snapshot Phase

optional_repo = {
    "6": {
        "68": "rhel-6-desktop-optional-rpms",
        "69": "rhel-6-server-optional-rpms",
        "71": "rhel-6-workstation-optional-rpms",
        "72": "rhel-6-for-system-z-optional-rpms",
        "74": "rhel-6-for-power-optional-rpms",
        "76": "rhel-6-hpc-node-optional-rpms",
        "135": "rhel-6-server-optional-htb-rpms",
        "155": "rhel-6-workstation-optional-htb-rpms",
        "248": "rhel-6-server-optional-rpms"
    },
    "7": {
        "68": "rhel-7-desktop-optional-rpms",
        "69": "rhel-7-server-optional-rpms",
        "71": "rhel-7-workstation-optional-rpms",
        "72": "rhel-7-for-system-z-optional-rpms",
        "74": "rhel-7-for-power-optional-rpms",
        "76": "rhel-7-hpc-node-optional-rpms",
        "279": "rhel-7-for-power-le-optional-rpms",
        "294": "rhel-7-server-for-arm-optional-rpms",
        "420": "rhel-7-for-power-9-optional-rpms",
        "419": "rhel-7-for-arm-64-optional-rpms",
        "434": "rhel-7-for-system-z-a-optional-rpms",
        "230": "rhel-7-server-optional-htb-rpms",
        "231": "rhel-7-workstation-optional-htb-rpms"
    }
}

openshift_repo = {
    "3.11": {
        "69": "rhel-7-server-extras-rpms --enable=rhel-7-server-ansible-2.6-rpms --enable=rhel-7-fast-datapath-rpms",
        "420": "rhel-7-for-power-9-extras-rpms --enable=rhel-7-server-ansible-2.6-for-power-9-rpms --enable=rhel-7-server-for-power-9-rhscl-rpms --enable=rhel-7-for-power9-fast-datapath-rpms",
        "279": "rhel-7-for-power-le-extras-rpms --enable=rhel-7-server-ansible-2.6-for-power-le-rpms --enable=rhel-7-server-for-power-le-rhscl-rpms --enable=rhel-7-for-power-le-fast-datapath-rpms",
    },
    "3.10": {
        "69": "rhel-7-server-extras-rpms --enable=rhel-7-server-ansible-2.4-rpms --enable=rhel-7-fast-datapath-rpms",
        "420": "rhel-7-for-power-9-extras-rpms --enable=rhel-7-server-ansible-2.6-for-power-9-rpms --enable=rhel-7-server-for-power-le-rhscl-rpms --enable=rhel-7-for-power9-fast-datapath-rpms",
        "279": "rhel-7-for-power-le-extras-rpms --enable=rhel-7-server-ansible-2.6-for-power-le-rpms --enable=rhel-7-server-for-power-le-rhscl-rpms --enable=rhel-7-for-power-le-fast-datapath-rpms",
    },
    "3.9": {
        "69": "rhel-7-server-extras-rpms --enable=rhel-7-fast-datapath-rpms --enable=rhel-7-server-ansible-2.4-rpms",
    }
}