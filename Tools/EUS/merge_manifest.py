import sys
import os
import json
import logging

def merge_manifest(eus_manifest_dir):
    """
    Merge manifests.
    
    Merge all the manifests under $eus_manifest_dir directory into one new json file eus_manifest.json.
    :param eus_manifest_dir: stores all the manifest needs to be merged.
    """
    
    os.chdir(eus_manifest_dir)
    products = dict()
    
    for manifest_file in os.listdir(os.getcwd()):
        logging.info("=== Handle manifest {0} ===".format(manifest_file))
        with open(manifest_file) as json_file:
            data = json.load(json_file)['cdn']['products']
            # if products is {}, merge the first manifest content totally into products
            if not products:
                logging.info("Write the first manifest into total manifest file... ")
                products = data
                continue

            # merge other manifest
            for pid in data:
                # if pid is new, write it in total_manifest directly
                # if pid is existing, merge it into total_manifest
                if pid not in products.keys():
                    logging.info("Write all the pid {0} part of file {1}...".format(pid, manifest_file))
                    products[pid] = data[pid]
                else:
                    logging.info("Trying to merge pid {0} of file {1}...".format(pid, manifest_file))
                    for repo_path in data[pid]['Repo Paths'].keys():
                        # If repo_path exists in products, merge the rpms part(['RPMs']) of data into products
                        # If not exist, set the repo_path content of data to products directly
                        if repo_path in products[pid]['Repo Paths'].keys():
                            rpms = list(set(products[pid]['Repo Paths'][repo_path]['RPMs'] + data[pid]['Repo Paths'][repo_path]['RPMs']))
                            products[pid]['Repo Paths'][repo_path]['RPMs'] = rpms
                        else:
                            products[pid]['Repo Paths'][repo_path] = data[pid]['Repo Paths'][repo_path]
                
    with open('eus_manifest.json', 'w') as json_file:
        total_manifest_content = {'cdn': {'products': products}}
        json_file.write(json.dumps(total_manifest_content, indent=4))     
    
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
        logging.info("python <script_name.py> <EUS_Manifest_DIR>")
        sys.exit(1)

    eus_manifest_dir = sys.argv[1]
    merge_manifest(eus_manifest_dir)
