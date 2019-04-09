#!/bin/python

import sys
import json

"""
Product 238 on RHEL 7.5 _ {u'7.5': [u'x86_64']}
Product 236 on RHEL 7.5 _ {u'7.5': [u'x86_64']}
Product 230 on RHEL 7.5 _ {u'7.5': [u'x86_64']}
Product 231 on RHEL 7.5 _ {u'7.5': [u'x86_64']}
"""

if len(sys.argv)>=2:
    with open(sys.argv[1],"r") as f:
        data = f.read()
else:
    data = sys.stdin.read()

data = json.loads(data)["cdn"]["products"]

for productid in data.keys():
    PID = data[productid]["Product ID"]
    platform = data[productid]["Platform"]
    platform_version = data[productid]["Platform Version"]

    arch = {}
    for repo in data[productid]["Repo Paths"].keys():
        item = data[productid]["Repo Paths"][repo]
        if item["releasever"] not in arch:
            arch[item["releasever"]] = []
        if item["basearch"] not in arch[item["releasever"]]:
            arch[item["releasever"]].append(item["basearch"])

    print("Product {0} on {1} {2} _ {3}".format(PID, platform, platform_version, arch))

