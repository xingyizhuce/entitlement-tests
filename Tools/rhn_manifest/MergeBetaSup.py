#!/usr/bin/python
'''
Created on April 15, 2016

@author: yanpliu@redhat.com

'''

import json
import commands
import RestAPIProperties
import copy
import os


if __name__ == "__main__":

    BetaComposeId = "RHEL-6.8-20160308.0"
    SuppComposeId = "Supp-6.8-RHEL-6-20160308.0"
    BetamanifestJsonFile = './' + BetaComposeId +"/" + "beta" + "/" + RestAPIProperties.manifestDirectory + "/" + BetaComposeId + "_RHN" +"_manifest.json"
    fbeta = open(BetamanifestJsonFile,'r')
    dictBeta = json.load(fbeta)
    fbeta.close()
    #print dictBeta
    SuppmanifestJsonFile = './' + SuppComposeId +"/" + "beta" + "/" + RestAPIProperties.manifestDirectory + "/" + SuppComposeId + "_RHN" +"_manifest.json"
    fsup = open(SuppmanifestJsonFile,'r')
    dictSupp = json.load(fsup)
    fsup.close()
    #print dictSupp
    for k,v in dictSupp[RestAPIProperties.Service]["channels"].iteritems():
        print k
        dictBeta[RestAPIProperties.Service]["channels"][k] = v
        print dictBeta[RestAPIProperties.Service]["channels"][k]

    #print dictBeta
    manifestMerge = './' + BetaComposeId +"/" + "beta" + "/" + RestAPIProperties.manifestDirectory + "/" + "Beta_Supp_manifest.json"
    fmanifest = open(manifestMerge, 'w')
    json.dump(dictBeta, fmanifest)
    fmanifest.close()
    manifestMergeJson = './' + BetaComposeId +"/" + "beta" + "/" + RestAPIProperties.manifestDirectory  + "/" + BetaComposeId + "_" + SuppComposeId+ "_manifest.json"

    cmd_manifest = 'cat %s | python -m json.tool >%s ' % (manifestMerge,manifestMergeJson)
    result,output_repos = commands.getstatusoutput(cmd_manifest)
    print output_repos
    cmd_removemanifest = 'rm -rf %s' % (manifestMerge)
    commands.getstatusoutput(cmd_removemanifest)
