#!/usr/bin/python

import json
import commands
import RestAPIProperties
import copy
import os
import sys
import getopt

def getArgsValue(argv):
    if len(argv) < 2:
        Usage()
        sys.exit(2)

    opts, args = getopt.getopt(argv[1:], 'hr:s:t:',['help','rhelcomposeid=','suppcomposeid=','test-type='])
    
    rhelcompose_id = ''
    suppcompose_id = ''
    test_type = ''
    
    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif o in ('-r', '--rhelcomposeid'):
            rhelcompose_id = a
        elif o in ('-s', '--suppcomposeid'):
            suppcompose_id = a
        elif o in ('-t', '--test-type'):
            test_type = a
        else:
            print 'unhandled option'
            sys.exit(3)
    return rhelcompose_id, suppcompose_id, test_type

def Usage():
    print 'MergeRHELSuppManifest.py usage:'
    print '-h,--help: print help message.'
    print '-r, --rhelcomposeid=rhelcompose_id: input the rhel compose id, this is mandatory option'
    print '-s, --suppcomposeid=suppcompose_id: input the supplementary compose id, this is mandatory option'
    print '-t, --test-type=test_type: input one of the test types: Beta, HTB, GA'

if __name__ == "__main__":

    # RHELComposeId = "RHEL-7.5-20180322.0"
    # SuppComposeId = "Supp-7.5-RHEL-7-20180308.0"

    # Get the RHEL Compose Id Supplementary Compose Id from command line arguments
    RHELComposeId = getArgsValue(sys.argv)[0]
    SuppComposeId = getArgsValue(sys.argv)[1]
    
    # Get the test type from command line argument or env variable, which will be set as the value of the variable 'repo_family'
    test_type = getArgsValue(sys.argv)[2]

    if test_type.capitalize() == "Beta":
        repo_family = "beta"
    elif test_type.upper() == "HTB":
        repo_family = "htb"
    elif test_type.upper() == "GA":
        repo_family = "dist"
    
    # Read RHEL manifest json file into a dict 'dictRhel'
    RHELmanifestJsonFile = './' + RHELComposeId +"/" + repo_family + "/" + RestAPIProperties.manifestDirectory + "/" + RHELComposeId + "_RHN" +"_manifest.json"
    fRhel = open(RHELmanifestJsonFile,'r')
    dictRhel = json.load(fRhel)
    fRhel.close()
    #print dictRhel
    
    # Read Supp manifest json file into a dict 'dictSupp'
    SuppmanifestJsonFile = './' + SuppComposeId +"/" + repo_family + "/" + RestAPIProperties.manifestDirectory + "/" + SuppComposeId + "_RHN" +"_manifest.json"
    fsupp = open(SuppmanifestJsonFile,'r')
    dictSupp = json.load(fsupp)
    fsupp.close()
    #print dictSupp
    
    # Merge the content of 'dictSupp' into 'dictRhel'
    for k,v in dictSupp[RestAPIProperties.Service]["channels"].iteritems():
        print k
        dictRhel[RestAPIProperties.Service]["channels"][k] = v
        #print dictRhel[RestAPIProperties.Service]["channels"][k]

    # Create a json file with merged manifest content in 'dictRhel'
    manifestMerge = './' + RHELComposeId +"/" + repo_family + "/" + RestAPIProperties.manifestDirectory + "/" + "RHEL_Supp_manifest.json"
    fmanifest = open(manifestMerge, 'w')
    json.dump(dictRhel, fmanifest)
    fmanifest.close()
    
    # Create a new json file with json format of the merged manifest content in above json file 'manifestMerge'
    manifestMergeJson = './' + RHELComposeId +"/" + repo_family + "/" + RestAPIProperties.manifestDirectory  + "/" + RHELComposeId + "_" + SuppComposeId+ "_manifest.json"
    cmd_manifest = 'cat %s | python -m json.tool >%s ' % (manifestMerge,manifestMergeJson)
    result,output_repos = commands.getstatusoutput(cmd_manifest)
    
    # Remove above temporarily created json file 'manifestMerge'
    cmd_removemanifest = 'rm -rf %s' % (manifestMerge)
    commands.getstatusoutput(cmd_removemanifest)

