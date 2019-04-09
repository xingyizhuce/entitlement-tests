import os

# Not set container after KeyError exception, as Container should be specified, or the testing cannot be continued.
try:
    container = os.environ["Container"]
except KeyError as e:
    pass

try:
    docker_image_id = os.environ["Docker_image_id"]
except KeyError as e:
    docker_image_id = ""

try:
    sat6_server_hostname = os.environ["SAT6_Server_Hostname"]
except KeyError as e:
    sat6_server_hostname = ""

try:
    sat6_server_ip = os.environ["SAT6_Server_IP"]
except KeyError as e:
    sat6_server_ip = ""

try:
    sat6_server_username = os.environ["SAT6_Server_Username"]
except KeyError as e:
    sat6_server_username = ""

try:
    sat6_server_password = os.environ["SAT6_Server_Password"]
except KeyError as e:
    sat6_server_password = ""

try:
    sat6_server_orglabel = os.environ["SAT6_Server_OrgLabel"]
except KeyError as e:
    sat6_server_orglabel = ""

extra_repos = {
    "RHEL7": {
        "x86_64": "rhel-7-server-extras-rpms",
        "s390x": "rhel-7-for-system-z-extras-rpms",
        "ppc64le": "rhel-7-for-power-le-extras-rpms",
    },
    "RHEL-ALT": {
        "s390x": "rhel-7-for-system-z-a-extras-rpms",
        "ppc64le": "rhel-7-for-power-9-extras-rpms",
        "aarch64": "rhel-7-for-arm-64-extras-rpms",
    }
}


properties = {
    "RHEL8": {  # product_type for host
        "RHEL8": {  # container_version
            "Beta": {  # Need to subscribe Beta to test RHEL8 Beta containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",
                    "container_pid": "486",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-x86_64-appstream-beta-rpms,rhel-8-for-x86_64-baseos-beta-rpms"
                },
                "s390x": {
                    "host_pid": "433",
                    "container_pid": "433",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "362",
                    "container_pid": "362",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                },
                "aarch64": {
                    "host_pid": "363",
                    "container_pid": "363",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-aarch64-appstream-beta-rpms,rhel-8-for-aarch64-baseos-beta-rpms"
                }
            },
            "HTB_Beta": {  # Need to subscribe Beta to test RHEL8 Beta containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",
                    "container_pid": "486",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-x86_64-appstream-beta-rpms,rhel-8-for-x86_64-baseos-beta-rpms"
                },
                "s390x": {
                    "host_pid": "433",
                    "container_pid": "433",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "362",
                    "container_pid": "362",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                },
                "aarch64": {
                    "host_pid": "363",
                    "container_pid": "363",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-aarch64-appstream-beta-rpms,rhel-8-for-aarch64-baseos-beta-rpms"
                }
            },
            "HTB_Snapshot": {
                "x86_64": {
                    "host_pid": "230",
                    "container_pid": "230",
                    "sku": "RH00076",
                    "repo": "rhel-8-for-x86_64-appstream-htb-rpms,rhel-8-for-x86_64-baseos-htb-rpms"
                },
                "s390x": {
                    "host_pid": "232",
                    "container_pid": "232",
                    "sku": "RH00076",
                    "repo": "rhel-8-for-s390x-appstream-htb-rpms,rhel-8-for-s390x-baseos-htb-rpms"
                },
                "ppc64le": {
                    "host_pid": "233",
                    "container_pid": "233",
                    "sku": "RH00076",
                    "repo": "rhel-8-for-ppc64le-appstream-htb-rpms,rhel-8-for-ppc64le-baseos-htb-rpms"
                },
                "aarch64": {
                    "host_pid": "489",
                    "container_pid": "489",
                    "sku": "RH00076",
                    "repo": "rhel-8-for-aarch64-appstream-htb-rpms,rhel-8-for-aarch64-baseos-htb-rpms"
                }
            },
            "GA": {  # Need to subscribe GA skus to test RHEL8 GA containers in RHEL8 GA phase
                "x86_64": {
                    "host_pid": "479",
                    "container_pid": "479",
                    "sku": "RH00003,RH00025,RH00026,RH00394,INSTR633200",
                    "repo": "rhel-8-for-x86_64-appstream-rpms,rhel-8-for-x86_64-baseos-rpms",
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "72",
                    "sku": "RH0451709,RH00545,RH00546",
                    "repo": "rhel-8-for-s390x-appstream-rpms,rhel-8-for-s390x-baseos-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "279",
                    "sku": "RH00284,RH00742,RH00748",
                    "repo": "rhel-8-for-ppc64le-appstream-rpms,rhel-8-for-ppc64le-baseos-rpms"
                },
                "aarch64": {
                    "host_pid": "419",
                    "container_pid": "419",
                    "sku": "RH00784",
                    "repo": "rhel-8-for-aarch64-appstream-rpms,rhel-8-for-aarch64-baseos-rpms"
                }
            }
        },
        "RHEL7": {  # container_version
            "Beta": {  # Need to subscribe GA skus to test RHEL7 GA Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",  # Beta pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH00003",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-server-rpms"
                },
                "s390x": {
                    "host_pid": "433",  # Beta pid in RHEL8 host
                    "container_pid": "72",  # GA pid in RHEL7 GA Container
                    "sku": "RH0451709",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-system-z-rpms"
                },
                "ppc64le": {
                    "host_pid": "362",  # Beta pid in RHEL8 host
                    "container_pid": "279",  # GA pid in RHEL7 GA Container
                    "sku": "RH00284",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-power-le-rpms"
                },
                "aarch64": {  # This is for RHEL-ALT aarch64
                    "host_pid": "363",  # Beta pid in RHEL8 host
                    "container_pid": "419",  # GA pid in RHEL7 GA Container
                    "sku": "RH00784",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-arm-64-rpms"
                }
            },
            "HTB_Beta": {  # Need to subscribe GA skus to test RHEL7 GA Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",  # Beta pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH00003",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-server-rpms"
                },
                "s390x": {
                    "host_pid": "433",  # Beta pid in RHEL8 host
                    "container_pid": "72",  # GA pid in RHEL7 GA Container
                    "sku": "RH0451709",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-system-z-rpms"
                },
                "ppc64le": {
                    "host_pid": "362",  # Beta pid in RHEL8 host
                    "container_pid": "279",  # GA pid in RHEL7 GA Container
                    "sku": "RH00284",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-power-le-rpms"
                },
                "aarch64": {  # This is for RHEL-ALT aarch64
                    "host_pid": "363",  # Beta pid in RHEL8 host
                    "container_pid": "419",  # GA pid in RHEL7 GA Container
                    "sku": "RH00784",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-7-for-arm-64-rpms"
                }
            },
            "HTB_Snapshot": {
                "x86_64": {
                    "host_pid": "230",  # HTB pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH0103708,RH00076",
                    "repo": "rhel-7-server-rpms"
                },
                "s390x": {
                    "host_pid": "232",  # HTB pid in RHEL8 host
                    "container_pid": "72",  # GA pid in RHEL7 GA Container
                    "sku": "RH0451709,RH00076",
                    "repo": "rhel-7-for-system-z-rpms"
                },
                "ppc64le": {
                    "host_pid": "233",  # HTB pid in RHEL8 host
                    "container_pid": "279",     # GA pid in RHEL7 GA Container
                    "sku": "RH00284,RH00076",
                    "repo": "rhel-7-for-power-le-rpms"
                },
                "aarch64": {  # This is for RHEL-ALT aarch64
                    "host_pid": "489",  # HTB pid in RHEL8 host
                    "container_pid": "419",     # GA pid in RHEL7 GA Container
                    "sku": "RH00784,RH00076",
                    "repo": "rhel-7-for-arm-64-rpms"
                }
            },
            "GA": {  # Need to subscribe GA skus to test RHEL7 GA Containers in RHEL8 GA phase
                "x86_64": {
                    "host_pid": "479",
                    "container_pid": "69",
                    "sku": "RH00003",
                    "repo": "rhel-7-server-rpms"
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "72",
                    "sku": "RH0451709",
                    "repo": "rhel-7-for-system-z-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "279",
                    "sku": "RH00284",
                    "repo": "rhel-7-for-power-le-rpms"
                },
                "aarch64": {  # This is for RHEL-ALT aarch64
                    "host_pid": "419",
                    "container_pid": "419",
                    "sku": "RH00784",
                    "repo": "rhel-7-for-arm-64-rpms"
                }
            }
        },
        "RHEL6": {  # container_version
            "Beta": {  # Need to subscribe GA skus to test RHEL6 GA Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",  # Beta pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH00003",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-6-server-rpms"
                }
            },
            "HTB_Beta": {  # Need to subscribe GA skus to test RHEL6 GA Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "486",  # Beta pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH00003",  # Need GA sku to get repos in RHEL7 GA Container
                    "repo": "rhel-6-server-rpms"
                }
            },
            "HTB_Snapshot": {
                "x86_64": {
                    "host_pid": "230",  # Beta pid in RHEL8 host
                    "container_pid": "69",  # GA pid in RHEL7 GA Container
                    "sku": "RH0103708,RH00076",
                    "repo": "rhel-6-server-rpms"
                }
            },
            "GA": {  # Need to subscribe GA skus to test RHEL6 GA Containers in RHEL8 GA phase
                "x86_64": {
                    "host_pid": "479",
                    "container_pid": "69",
                    "sku": "RH00003",
                    "repo": "rhel-6-server-rpms"
                }
            }
        }
    },
    "RHEL7": {  # product_type for host
        "RHEL8": {  # container_version
            "Beta": {  # Need to subscribe Beta skus to test RHEL8 Beta Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "69",
                    "container_pid": "486",
                    "sku": "RH0103708,RH00069",
                    "repo": "rhel-8-for-x86_64-appstream-beta-rpms,rhel-8-for-x86_64-baseos-beta-rpms"
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "433",
                    "sku": "RH0451709",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "362",
                    "sku": "RH00284",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                }
            },
            "HTB_Beta": {  # Need to subscribe Beta skus to test RHEL8 Beta Containers in RHEL8 Beta phase
                "x86_64": {
                    "host_pid": "69",
                    "container_pid": "486",
                    "sku": "RH0103708,RH00069",
                    "repo": "rhel-8-for-x86_64-appstream-beta-rpms,rhel-8-for-x86_64-baseos-beta-rpms"
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "433",
                    "sku": "RH0451709",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "362",
                    "sku": "RH00284",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                }
            },
            "HTB_Snapshot": {
                "x86_64": {
                    "host_pid": "69",
                    "container_pid": "230",
                    "sku": "RH0103708,RH00076",
                    "repo": "rhel-8-for-x86_64-appstream-htb-rpms,rhel-8-for-x86_64-baseos-htb-rpms"
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "232",
                    "sku": "RH0451709,RH00076",
                    "repo": "rhel-8-for-s390x-appstream-htb-rpms,rhel-8-for-s390x-baseos-htb-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "233",
                    "sku": "RH00284,RH00076",
                    "repo": "rhel-8-for-ppc64le-appstream-htb-rpms,rhel-8-for-ppc64le-baseos-htb-rpms"
                }
            },
            "GA": {  # Need to subscribe GA skus to test RHEL8 GA Containers in RHEL8 GA phase
                "x86_64": {
                    "host_pid": "69",
                    "container_pid": "479",
                    "sku": "RH0103708,RH00003,RH00025,RH00026,RH00394",
                    "repo": "rhel-8-for-x86_64-appstream-rpms,rhel-8-for-x86_64-baseos-rpms"
                },
                "s390x": {
                    "host_pid": "72",
                    "container_pid": "72",
                    "sku": "RH0451709,RH00545,RH00546",
                    "repo": "rhel-8-for-s390x-appstream-rpms,rhel-8-for-s390x-baseos-rpms"
                },
                "ppc64le": {
                    "host_pid": "279",
                    "container_pid": "279",
                    "sku": "RH00284,RH00742,RH00748",
                    "repo": "rhel-8-for-ppc64le-appstream-rpms,rhel-8-for-ppc64le-baseos-rpms"
                }
            }
        }
    },
    "RHEL-ALT": {  # product_type for host
        "RHEL8": {  # container_version
            "Beta": {  # Need to subscribe Beta skus to test RHEL8 Beta Containers in RHEL8 Beta phase
                "s390x": {
                    "host_pid": "434",
                    "container_pid": "433",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "420",
                    "container_pid": "362",
                    "sku": "RH00284,RH00069",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                },
                "aarch64": {
                    "host_pid": "419",
                    "container_pid": "363",
                    "sku": "RH00784",
                    "repo": "rhel-8-for-aarch64-appstream-beta-rpms,rhel-8-for-aarch64-baseos-beta-rpms"
                }
            },
            "HTB_Beta": {  # Need to subscribe Beta skus to test RHEL8 Beta Containers in RHEL8 Beta phase
                "s390x": {
                    "host_pid": "434",
                    "container_pid": "433",
                    "sku": "RH00069",
                    "repo": "rhel-8-for-s390x-appstream-beta-rpms,rhel-8-for-s390x-baseos-beta-rpms"
                },
                "ppc64le": {
                    "host_pid": "420",
                    "container_pid": "362",
                    "sku": "RH00284",
                    "repo": "rhel-8-for-ppc64le-appstream-beta-rpms,rhel-8-for-ppc64le-baseos-beta-rpms"
                },
                "aarch64": {
                    "host_pid": "419",
                    "container_pid": "363",
                    "sku": "RH00784",
                    "repo": "rhel-8-for-aarch64-appstream-beta-rpms,rhel-8-for-aarch64-baseos-beta-rpms"
                }
            },
            "HTB_Snapshot": {
                "s390x": {
                    "host_pid": "434",
                    "container_pid": "232",
                    "sku": "RH0416249,RH00076",
                    "repo": "rhel-8-for-s390x-appstream-htb-rpms,rhel-8-for-s390x-baseos-htb-rpms"
                },
                "ppc64le": {
                    "host_pid": "420",
                    "container_pid": "233",
                    "sku": "RH00284,RH00076",
                    "repo": "rhel-8-for-ppc64le-appstream-htb-rpms,rhel-8-for-ppc64le-baseos-htb-rpms"
                },
                "aarch64": {
                    "host_pid": "419",
                    "container_pid": "489",
                    "sku": "RH00784,RH00076",
                    "repo": "rhel-8-for-aarch64-appstream-htb-rpms,rhel-8-for-aarch64-baseos-htb-rpms"
                }
            },
            "GA": {  # Need to subscribe GA skus to test RHEL8 GA Containers in RHEL8 GA phase
                "s390x": {
                    "host_pid": "434",
                    "container_pid": "72",
                    "sku": "RH0416249",
                    "repo": "rhel-8-for-s390x-appstream-rpms,rhel-8-for-s390x-baseos-rpms"
                },
                "ppc64le": {
                    "host_pid": "420",
                    "container_pid": "279",
                    "sku": "RH00284",
                    "repo": "rhel-8-for-ppc64le-appstream-rpms,rhel-8-for-ppc64le-baseos-rpms"
                },
                "aarch64": {
                    "host_pid": "419",
                    "container_pid": "419",
                    "sku": "RH00784",
                    "repo": "rhel-8-for-aarch64-appstream-rpms,rhel-8-for-aarch64-baseos-rpms"
                }
            }
        }
    }
}


repos = {
    "RHEL6": {
        "Beta": {
            "x86_64": [
                "rhel-6-server-supplementary-beta-debuginfo",
                "rhel-6-server-supplementary-beta-rpms",
                "rhel-6-server-optional-beta-source-rpms",
                "rhel-6-server-supplementary-beta-source-rpms",
                "rhel-6-server-optional-beta-rpms",
                "rhel-6-server-beta-debug-rpms",
                "rhel-6-server-optional-beta-debug-rpms",
                "rhel-6-server-beta-source-rpms",
                "rhel-6-server-beta-rpms"
            ]
        },
        "HTB_Beta": {
            "x86_64": [
                "rhel-6-server-supplementary-beta-debuginfo",
                "rhel-6-server-supplementary-beta-rpms",
                "rhel-6-server-optional-beta-source-rpms",
                "rhel-6-server-supplementary-beta-source-rpms",
                "rhel-6-server-optional-beta-rpms",
                "rhel-6-server-beta-debug-rpms",
                "rhel-6-server-optional-beta-debug-rpms",
                "rhel-6-server-beta-rpms",
                "rhel-6-server-beta-source-rpms"
            ]
        },
        "HTB_Snapshot": {
            "x86_64": [
                "rhel-6-server-supplementary-beta-debuginfo",
                "rhel-6-server-supplementary-beta-rpms",
                "rhel-6-server-optional-beta-source-rpms",
                "rhel-6-server-supplementary-beta-source-rpms",
                "rhel-6-server-optional-beta-rpms",
                "rhel-6-server-beta-debug-rpms",
                "rhel-6-server-optional-beta-debug-rpms",
                "rhel-6-server-beta-source-rpms",
                "rhel-6-server-beta-rpms"
            ]
        },
        "GA": {
            "x86_64": [
                "rhel-6-server-debug-rpms",
                "rhel-6-server-optional-source-rpms",
                "rhel-6-server-supplementary-rpms",
                "rhel-6-server-supplementary-debuginfo",
                "rhel-6-server-optional-rpms",
                "rhel-6-server-source-rpms",
                "rhel-6-server-supplementary-source-rpms",
                "rhel-6-server-optional-debug-rpms",
                "rhel-6-server-rpms"
            ]
        }
    },
    "RHEL7": {
        "Beta": {
            "x86_64": [
                "rhel-7-server-supplementary-beta-source-rpms",
                "rhel-7-server-optional-beta-rpms",
                "rhel-7-server-beta-rpms",
                "rhel-7-server-supplementary-beta-debug-rpms",
                "rhel-7-server-beta-source-rpms",
                "rhel-7-server-beta-debug-rpms",
                "rhel-7-server-optional-beta-source-rpms",
                "rhel-7-server-optional-beta-debug-rpms",
                "rhel-7-server-supplementary-beta-rpms"
            ],
            "s390x": [
                "rhel-7-for-system-z-optional-beta-debug-rpms",
                "rhel-7-for-system-z-beta-debug-rpms",
                "rhel-7-for-system-z-supplementary-beta-source-rpms",
                "rhel-7-for-system-z-beta-rpms",
                "rhel-7-for-system-z-supplementary-beta-debug-rpms",
                "rhel-7-for-system-z-optional-beta-source-rpms",
                "rhel-7-for-system-z-optional-beta-rpms",
                "rhel-7-for-system-z-beta-source-rpms",
                "rhel-7-for-system-z-supplementary-beta-rpms"
            ],
            "ppc64le": [
                "rhel-7-for-power-le-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-debug-rpms",
                "rhel-7-for-power-le-optional-beta-rpms",
                "rhel-7-for-power-le-beta-source-rpms",
                "rhel-7-for-power-le-supplementary-beta-rpms",
                "rhel-7-for-power-le-optional-beta-source-rpms",
                "rhel-7-for-power-le-optional-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-source-rpms",
                "rhel-7-for-power-le-beta-rpms"
            ]
        },
        "HTB_Beta": {
            "x86_64": [
                "rhel-7-server-supplementary-beta-source-rpms",
                "rhel-7-server-optional-beta-rpms",
                "rhel-7-server-beta-rpms",
                "rhel-7-server-supplementary-beta-debug-rpms",
                "rhel-7-server-beta-source-rpms",
                "rhel-7-server-beta-debug-rpms",
                "rhel-7-server-optional-beta-source-rpms",
                "rhel-7-server-optional-beta-debug-rpms",
                "rhel-7-server-supplementary-beta-rpms"
            ],
            "s390x": [
                "rhel-7-for-system-z-optional-beta-debug-rpms",
                "rhel-7-for-system-z-beta-debug-rpms",
                "rhel-7-for-system-z-supplementary-beta-source-rpms",
                "rhel-7-for-system-z-beta-rpms",
                "rhel-7-for-system-z-supplementary-beta-debug-rpms",
                "rhel-7-for-system-z-optional-beta-source-rpms",
                "rhel-7-for-system-z-optional-beta-rpms",
                "rhel-7-for-system-z-beta-source-rpms",
                "rhel-7-for-system-z-supplementary-beta-rpms"
            ],
            "ppc64le": [
                "rhel-7-for-power-le-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-debug-rpms",
                "rhel-7-for-power-le-optional-beta-rpms",
                "rhel-7-for-power-le-beta-source-rpms",
                "rhel-7-for-power-le-supplementary-beta-rpms",
                "rhel-7-for-power-le-optional-beta-source-rpms",
                "rhel-7-for-power-le-optional-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-source-rpms",
                "rhel-7-for-power-le-beta-rpms"
            ]
        },
        "HTB_Snapshot": {
            "x86_64": [
                "rhel-7-server-supplementary-beta-source-rpms",
                "rhel-7-server-optional-beta-rpms",
                "rhel-7-server-beta-rpms",
                "rhel-7-server-supplementary-beta-debug-rpms",
                "rhel-7-server-beta-source-rpms",
                "rhel-7-server-beta-debug-rpms",
                "rhel-7-server-optional-beta-source-rpms",
                "rhel-7-server-optional-beta-debug-rpms",
                "rhel-7-server-supplementary-beta-rpms"
            ],
            "s390x": [
                "rhel-7-for-system-z-optional-beta-debug-rpms",
                "rhel-7-for-system-z-beta-debug-rpms",
                "rhel-7-for-system-z-supplementary-beta-source-rpms",
                "rhel-7-for-system-z-beta-rpms",
                "rhel-7-for-system-z-supplementary-beta-debug-rpms",
                "rhel-7-for-system-z-optional-beta-source-rpms",
                "rhel-7-for-system-z-optional-beta-rpms",
                "rhel-7-for-system-z-beta-source-rpms",
                "rhel-7-for-system-z-supplementary-beta-rpms"
            ],
            "ppc64le": [
                "rhel-7-for-power-le-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-debug-rpms",
                "rhel-7-for-power-le-optional-beta-rpms",
                "rhel-7-for-power-le-beta-source-rpms",
                "rhel-7-for-power-le-supplementary-beta-rpms",
                "rhel-7-for-power-le-optional-beta-source-rpms",
                "rhel-7-for-power-le-optional-beta-debug-rpms",
                "rhel-7-for-power-le-supplementary-beta-source-rpms",
                "rhel-7-for-power-le-beta-rpms"
            ]
        },
        "GA": {
            "x86_64": [
                "rhel-7-server-supplementary-source-rpms",
                "rhel-7-server-optional-rpms",
                "rhel-7-server-rpms",
                "rhel-7-server-supplementary-debug-rpms",
                "rhel-7-server-source-rpms",
                "rhel-7-server-debug-rpms",
                "rhel-7-server-optional-source-rpms",
                "rhel-7-server-optional-debug-rpms",
                "rhel-7-server-supplementary-rpms"
            ],
            "s390x": [
                "rhel-7-for-system-z-optional-debug-rpms",
                "rhel-7-for-system-z-debug-rpms",
                "rhel-7-for-system-z-supplementary-source-rpms",
                "rhel-7-for-system-z-rpms",
                "rhel-7-for-system-z-supplementary-debug-rpms",
                "rhel-7-for-system-z-optional-source-rpms",
                "rhel-7-for-system-z-optional-rpms",
                "rhel-7-for-system-z-source-rpms",
                "rhel-7-for-system-z-supplementary-rpms"
            ],
            "ppc64le": [
                "rhel-7-for-power-le-debug-rpms",
                "rhel-7-for-power-le-supplementary-debug-rpms",
                "rhel-7-for-power-le-optional-rpms",
                "rhel-7-for-power-le-source-rpms",
                "rhel-7-for-power-le-supplementary-rpms",
                "rhel-7-for-power-le-optional-source-rpms",
                "rhel-7-for-power-le-optional-debug-rpms",
                "rhel-7-for-power-le-supplementary-source-rpms",
                "rhel-7-for-power-le-rpms"
            ]
        }
    },
    "RHEL8": {
        "Beta": {
            "x86_64": [
                "rhel-8-for-x86_64-appstream-beta-debug-rpms",
                "rhel-8-for-x86_64-appstream-beta-rpms",
                "rhel-8-for-x86_64-appstream-beta-source-rpms",
                "rhel-8-for-x86_64-baseos-beta-debug-rpms",
                "rhel-8-for-x86_64-baseos-beta-rpms",
                "rhel-8-for-x86_64-baseos-beta-source-rpms"
            ],
            "s390x": [
                "rhel-8-for-s390x-appstream-beta-debug-rpms",
                "rhel-8-for-s390x-appstream-beta-rpms",
                "rhel-8-for-s390x-appstream-beta-source-rpms",
                "rhel-8-for-s390x-baseos-beta-debug-rpms",
                "rhel-8-for-s390x-baseos-beta-rpms",
                "rhel-8-for-s390x-baseos-beta-source-rpms"
            ],
            "ppc64le": [
                "rhel-8-for-ppc64le-appstream-beta-debug-rpms",
                "rhel-8-for-ppc64le-appstream-beta-rpms",
                "rhel-8-for-ppc64le-appstream-beta-source-rpms",
                "rhel-8-for-ppc64le-baseos-beta-debug-rpms",
                "rhel-8-for-ppc64le-baseos-beta-rpms",
                "rhel-8-for-ppc64le-baseos-beta-source-rpms"
            ],
            "aarch64": [
                "rhel-8-for-aarch64-appstream-beta-debug-rpms",
                "rhel-8-for-aarch64-appstream-beta-rpms",
                "rhel-8-for-aarch64-appstream-beta-source-rpms",
                "rhel-8-for-aarch64-baseos-beta-debug-rpms",
                "rhel-8-for-aarch64-baseos-beta-rpms",
                "rhel-8-for-aarch64-baseos-beta-source-rpms"

            ]
        },
        "HTB_Beta": {
            "x86_64": [
                "rhel-8-for-x86_64-appstream-beta-debug-rpms",
                "rhel-8-for-x86_64-appstream-beta-rpms",
                "rhel-8-for-x86_64-appstream-beta-source-rpms",
                "rhel-8-for-x86_64-baseos-beta-debug-rpms",
                "rhel-8-for-x86_64-baseos-beta-rpms",
                "rhel-8-for-x86_64-baseos-beta-source-rpms"
            ],
            "s390x": [
                "rhel-8-for-s390x-appstream-beta-debug-rpms",
                "rhel-8-for-s390x-appstream-beta-rpms",
                "rhel-8-for-s390x-appstream-beta-source-rpms",
                "rhel-8-for-s390x-baseos-beta-debug-rpms",
                "rhel-8-for-s390x-baseos-beta-rpms",
                "rhel-8-for-s390x-baseos-beta-source-rpms"
            ],
            "ppc64le": [
                "rhel-8-for-ppc64le-appstream-beta-debug-rpms",
                "rhel-8-for-ppc64le-appstream-beta-rpms",
                "rhel-8-for-ppc64le-appstream-beta-source-rpms",
                "rhel-8-for-ppc64le-baseos-beta-debug-rpms",
                "rhel-8-for-ppc64le-baseos-beta-rpms",
                "rhel-8-for-ppc64le-baseos-beta-source-rpms"
            ],
            "aarch64": [
                "rhel-8-for-aarch64-appstream-beta-debug-rpms",
                "rhel-8-for-aarch64-appstream-beta-rpms",
                "rhel-8-for-aarch64-appstream-beta-source-rpms",
                "rhel-8-for-aarch64-baseos-beta-debug-rpms",
                "rhel-8-for-aarch64-baseos-beta-rpms",
                "rhel-8-for-aarch64-baseos-beta-source-rpms"
            ]
        },
        "HTB_Snapshot": {
            "x86_64": [
                "rhel-8-for-x86_64-appstream-htb-debug-rpms",
                "rhel-8-for-x86_64-appstream-htb-rpms",
                "rhel-8-for-x86_64-appstream-htb-source-rpms",
                "rhel-8-for-x86_64-baseos-htb-debug-rpms",
                "rhel-8-for-x86_64-baseos-htb-rpms",
                "rhel-8-for-x86_64-baseos-htb-source-rpms"
            ],
            "s390x": [
                "rhel-8-for-s390x-appstream-htb-debug-rpms",
                "rhel-8-for-s390x-appstream-htb-rpms",
                "rhel-8-for-s390x-appstream-htb-source-rpms",
                "rhel-8-for-s390x-baseos-htb-debug-rpms",
                "rhel-8-for-s390x-baseos-htb-rpms",
                "rhel-8-for-s390x-baseos-htb-source-rpms"
            ],
            "ppc64le": [
                "rhel-8-for-ppc64le-appstream-htb-debug-rpms",
                "rhel-8-for-ppc64le-appstream-htb-rpms",
                "rhel-8-for-ppc64le-appstream-htb-source-rpms",
                "rhel-8-for-ppc64le-baseos-htb-debug-rpms",
                "rhel-8-for-ppc64le-baseos-htb-rpms",
                "rhel-8-for-ppc64le-baseos-htb-source-rpms"
            ],
            "aarch64": [
                "rhel-8-for-aarch64-appstream-htb-debug-rpms",
                "rhel-8-for-aarch64-appstream-htb-rpms",
                "rhel-8-for-aarch64-appstream-htb-source-rpms",
                "rhel-8-for-aarch64-baseos-htb-debug-rpms",
                "rhel-8-for-aarch64-baseos-htb-rpms",
                "rhel-8-for-aarch64-baseos-htb-source-rpms"
            ]
        },
        "GA": {
            "x86_64": [
                "rhel-8-for-x86_64-appstream-debug-rpms",
                "rhel-8-for-x86_64-appstream-rpms",
                "rhel-8-for-x86_64-appstream-source-rpms",
                "rhel-8-for-x86_64-baseos-debug-rpms",
                "rhel-8-for-x86_64-baseos-rpms",
                "rhel-8-for-x86_64-baseos-source-rpms",
                "rhel-8-for-x86_64-supplementary-debug-rpms",
                "rhel-8-for-x86_64-supplementary-rpms",
                "rhel-8-for-x86_64-supplementary-source-rpms",
                # Red Hat Enterprise Linux for Real Time, PID: 287
                "rhel-8-for-x86_64-rt-debug-rpms",
                "rhel-8-for-x86_64-rt-rpms",
                "rhel-8-for-x86_64-rt-source-rpms",
                # Red Hat Enterprise Linux for Real Time for NFV, PID: 313
                "rhel-8-for-x86_64-nfv-debug-rpms",
                "rhel-8-for-x86_64-nfv-rpms",
                "rhel-8-for-x86_64-nfv-source-rpms",
                # Red Hat CodeReady Linux Builder for x86_64, PID: 491
                "codeready-builder-for-rhel-8-x86_64-debug-rpms",
                "codeready-builder-for-rhel-8-x86_64-rpms",
                "codeready-builder-for-rhel-8-x86_64-source-rpms",
                # Red Hat Enterprise Linux High Availability for x86_64, PID: 83
                "rhel-8-for-x86_64-highavailability-debug-rpms",
                "rhel-8-for-x86_64-highavailability-rpms",
                "rhel-8-for-x86_64-highavailability-source-rpms",
                # Red Hat Enterprise Linux Resilient Storage for x86_64, PID: 90
                "rhel-8-for-x86_64-resilientstorage-debug-rpms",
                "rhel-8-for-x86_64-resilientstorage-rpms",
                "rhel-8-for-x86_64-resilientstorage-source-rpms",
            ],
            "s390x": [
                "rhel-8-for-s390x-appstream-debug-rpms",
                "rhel-8-for-s390x-appstream-rpms",
                "rhel-8-for-s390x-appstream-source-rpms",
                "rhel-8-for-s390x-baseos-debug-rpms",
                "rhel-8-for-s390x-baseos-rpms",
                "rhel-8-for-s390x-baseos-source-rpms",
                "rhel-8-for-s390x-supplementary-debug-rpms",
                "rhel-8-for-s390x-supplementary-rpms",
                "rhel-8-for-s390x-supplementary-source-rpms",
                # Red Hat Enterprise Linux Resilient Storage for IBM z Systems, PID: 299
                "rhel-8-for-s390x-resilientstorage-debug-rpms",
                "rhel-8-for-s390x-resilientstorage-rpms",
                "rhel-8-for-s390x-resilientstorage-source-rpms",
                # Red Hat Enterprise Linux High Availability for IBM z Systems, PID: 300
                "rhel-8-for-s390x-highavailability-debug-rpms",
                "rhel-8-for-s390x-highavailability-rpms",
                "rhel-8-for-s390x-highavailability-source-rpms",
                # Red Hat CodeReady Linux Builder for IBM z Systems, PID: 494
                "codeready-builder-for-rhel-8-s390x-debug-rpms",
                "codeready-builder-for-rhel-8-s390x-rpms",
                "codeready-builder-for-rhel-8-s390x-source-rpms",
            ],
            "ppc64le": [
                "rhel-8-for-ppc64le-appstream-debug-rpms",
                "rhel-8-for-ppc64le-appstream-rpms",
                "rhel-8-for-ppc64le-appstream-source-rpms",
                "rhel-8-for-ppc64le-baseos-debug-rpms",
                "rhel-8-for-ppc64le-baseos-rpms",
                "rhel-8-for-ppc64le-baseos-source-rpms",
                "rhel-8-for-ppc64le-supplementary-debug-rpms",
                "rhel-8-for-ppc64le-supplementary-rpms",
                "rhel-8-for-ppc64le-supplementary-source-rpms",
                # Red Hat Enterprise Linux Resilient Storage for Power, little endian, PID: 376
                "rhel-8-for-ppc64le-resilientstorage-debug-rpms",
                "rhel-8-for-ppc64le-resilientstorage-rpms",
                "rhel-8-for-ppc64le-resilientstorage-source-rpms",
                # Red Hat Enterprise Linux High Availability for Power, little endian, PID: 380
                "rhel-8-for-ppc64le-highavailability-debug-rpms",
                "rhel-8-for-ppc64le-highavailability-rpms",
                "rhel-8-for-ppc64le-highavailability-source-rpms",
                # Red Hat CodeReady Linux Builder for Power, little endian, PID: 492
                "codeready-builder-for-rhel-8-ppc64le-debug-rpms",
                "codeready-builder-for-rhel-8-ppc64le-rpms",
                "codeready-builder-for-rhel-8-ppc64le-source-rpms",
            ],
            "aarch64": [
                "rhel-8-for-aarch64-appstream-debug-rpms",
                "rhel-8-for-aarch64-appstream-rpms",
                "rhel-8-for-aarch64-appstream-source-rpms",
                "rhel-8-for-aarch64-baseos-debug-rpms",
                "rhel-8-for-aarch64-baseos-rpms",
                "rhel-8-for-aarch64-baseos-source-rpms",
                "rhel-8-for-aarch64-supplementary-debug-rpms",
                "rhel-8-for-aarch64-supplementary-rpms",
                "rhel-8-for-aarch64-supplementary-source-rpms",
                # Red Hat CodeReady Linux Builder for ARM 64, PID: 493
                "codeready-builder-for-rhel-8-aarch64-debug-rpms",
                "codeready-builder-for-rhel-8-aarch64-rpms",
                "codeready-builder-for-rhel-8-aarch64-source-rpms",
            ]
        }
    },
    "RHEL7-ALT": {
        "Beta": {
            "aarch64": [
                "rhel-7-for-arm-64-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-rpms",
                "rhel-7-for-arm-64-optional-beta-source-rpms",
                "rhel-7-for-arm-64-beta-rpms",
                "rhel-7-for-arm-64-beta-source-rpms"
            ]
        },
        "HTB_Beta": {
            "aarch64": [
                "rhel-7-for-arm-64-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-rpms",
                "rhel-7-for-arm-64-optional-beta-source-rpms",
                "rhel-7-for-arm-64-beta-rpms",
                "rhel-7-for-arm-64-beta-source-rpms"
            ]
        },
        "HTB_Snapshot": {
            "aarch64": [
                "rhel-7-for-arm-64-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-debug-rpms",
                "rhel-7-for-arm-64-optional-beta-rpms",
                "rhel-7-for-arm-64-optional-beta-source-rpms",
                "rhel-7-for-arm-64-beta-rpms",
                "rhel-7-for-arm-64-beta-source-rpms"
            ]
        },
        "GA": {
            "aarch64": [
                "rhel-7-for-arm-64-debug-rpms",
                "rhel-7-for-arm-64-optional-debug-rpms",
                "rhel-7-for-arm-64-optional-rpms",
                "rhel-7-for-arm-64-optional-source-rpms",
                "rhel-7-for-arm-64-rpms",
                "rhel-7-for-arm-64-source-rpms"
            ]
        }
    }
}
