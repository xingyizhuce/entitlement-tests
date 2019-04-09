import sys
import os
import json
import logging

def filter_manifest(eus_manifest_dir):
    """
    Filter out those PIDs described in Polarion cases from manifest.
    
    :eus_manifest_dir: directory stores manifest
    """

    # Open account_info_eus.json to get PIDs described in Poloarion cases
    polarion_content = json.load(open("../../CDN/json/account_info_eus.json"))
    polarion_keys = polarion_content.keys()
    print "EUS PIDs in Polarion cases: ", polarion_keys
    
    # Open the eus manifest
    eus_content = json.load(open("{0}/eus_manifest.json".format(eus_manifest_dir)))
    eus_keys = eus_content['cdn']['products'].keys()
    print "EUS PIDs got from errata: ", eus_keys
    
    filter_content = products = dict()
    
    for pid in eus_keys:
        if pid in polarion_keys:
            filter_content[pid] = eus_content['cdn']['products'][pid]

    with open('{0}/eus_filter_manifest.json'.format(eus_manifest_dir), 'w') as json_file:
        filter_manifest_content = {'cdn': {'products': filter_content}}
        json_file.write(json.dumps(filter_manifest_content, indent=4))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='merge_manifest.log',
                filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    if len(sys.argv) < 2:
        logging.info("python <script_name.py> <eus_manifest_dir>")
        sys.exit(1)

    eus_manifest_dir = sys.argv[1]
    filter_manifest(eus_manifest_dir)
