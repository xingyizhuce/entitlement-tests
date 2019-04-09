#!/usr/bin/python

import json
import sys
import getopt

def usage():
    print '''Usage: this script is used to generate rhn package manifest from the mapping file rhn_cdn_mappings.json of Satellite 5.8 server, and please be noted that this script is only supporting to generate rhn manifest for rhel 8 currently. For example: 
python generate_rhn_manifest.py -i "RHEL-8.0-20181220.1" \\
 -t "GA" \\
 -m "rhn_cdn_mappings(2.31-1).json" \\
 -c "rhel8.0-snapshot3.1-ga-stage-cdn.json" \\
 -r "rhel8-ga-package-manifest-rhn-sat5.json"'''
    print '-h, --help, print help message.'
    print '-i, --rhelcomposeid, input the rhel compose id, this is mandatory option'
    print '-t, --testtype, input the test type the rhn package manifest will be used for: Beta, HTB, GA, this is mandatory option'
    print '-m, --mappingfile, input the path of the mapping file rhn_cdn_mappings.json, this is mandatory option'
    print '-c, --cdnpackagemanifest, input the file path of the cdn package manifest, this is mandatory option'
    print '-r, --rhnpackagemanifest, input the file path of the generated rhn package manifest, this is optional option'

def get_args_value(argv):
    if len(argv) < 9:
        usage()
        sys.exit(3)

    opts, args = getopt.getopt(argv[1:], 'hi:t:m:c:r:', ['help', 'rhelcomposeid=','testtype=', 
                    'mappingfile=', 'cdnpackagemanifest=', 'rhnpackagemanifest='])

    rhelcompose_id = ''
    test_type=''
    mapping_file = ''
    cdn_package_manifest = ''
    rhn_package_manifest = ''
    
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(1)
        elif o in ('-i', '--rhelcomposeid'):
            rhelcompose_id = a
        elif o in ('-t', '--testtype'):
            test_type = a
        elif o in ('-m', '--mappingfile'):
            mapping_file = a
        elif o in ('-c', '--cdnpackagemanifest'):
            cdn_package_manifest = a
        elif o in ('-r', '--rhnpackagemanifest'):
            rhn_package_manifest = a
        else:
            print "Unknown option '{0}'.".format(o)
            sys.exit(3)
    return rhelcompose_id, test_type, mapping_file, cdn_package_manifest, rhn_package_manifest

def get_cdn_pkg(repo_name, json_cdn_manifest):
    # Get packages from cdn package manifest for certain repo
    
    repo_pkgs = []
    for pid in json_cdn_manifest["cdn"]["products"]:
        for repo_path in json_cdn_manifest["cdn"]["products"][pid]["Repo Paths"].keys():
            if repo_name == json_cdn_manifest["cdn"]["products"][pid]["Repo Paths"][repo_path]["Label"]:
                repo_pkgs = json_cdn_manifest["cdn"]["products"][pid]["Repo Paths"][repo_path]["RPMs"]
                return repo_pkgs

def generate_rhn_manifest():
    
    # Get parameter values from command line
    rhelcompose_id = ''
    test_type = ''
    mapping_file = ''
    cdn_package_manifest = ''
    rhn_package_manifest = ''

    rhelcompose_id, test_type, mapping_file, cdn_package_manifest, rhn_package_manifest = get_args_value(sys.argv)
    
    # Get the content of the mapping file rhn_cdn_mappings.json
    file_mapping = open(mapping_file,'r')
    json_mapping = json.load(file_mapping)
    file_mapping.close()

    # Get the content of the cdn package manifest file    
    file_cdn_manifest = open(cdn_package_manifest,'r')
    json_cdn_manifest = json.load(file_cdn_manifest)
    file_cdn_manifest.close()

    # Translate the test type to repo type
    repo_type = ""
    if test_type.lower() == "beta":
        repo_type = "beta"
    elif test_type.lower() == "htb":
        repo_type = "htb"
    elif test_type.lower() == "ga":
        repo_type = "dist"
    else:
        print "Unknown test type '{0}'.".format(test_type)
        sys.exit(3)
    
    # Generate the rhn package manifest content
    json_rhn_channel_pkg = dict()
    
    for channel_name in json_mapping.keys():
        for repo in json_mapping[channel_name]:
        
            relative_url_value = repo["relative_url"]
            if "RHEL-8" in rhelcompose_id:
            # Note: for now, this script is only supporting to generate rhn manifest for rhel 8.

                if (repo_type + "/rhel8/8" in relative_url_value) and ("/source" not in relative_url_value):
                
                    # Get the cdn repo name
                    repo_name = ""
                    pulp_repo_label_v2_value = repo["pulp_repo_label_v2"]
                    if "__" in pulp_repo_label_v2_value:
                        repo_name = pulp_repo_label_v2_value.split("__")[0]
                    else:
                        repo_name = pulp_repo_label_v2_value
                            
                    # Get the packages of the repo 'repo_name' from cdn package manifest and add them to corresponding rhn channel
                    json_rhn_channel_pkg[channel_name] = get_cdn_pkg(repo_name, json_cdn_manifest)

            else:
                break

    # Write the content of the rhn channels and packages into the rhn package manifest json file
    json_rhn_manifest = {"compose": rhelcompose_id, "rhn": { "channels": json_rhn_channel_pkg }}
    if rhn_package_manifest == "":
        rhn_package_manifest = "rhn_package_manifest.json"
        
    with open(rhn_package_manifest, 'w') as file_rhn_manifest:
        file_rhn_manifest.write(json.dumps(json_rhn_manifest, indent=4))


if __name__ == "__main__":
    generate_rhn_manifest()

