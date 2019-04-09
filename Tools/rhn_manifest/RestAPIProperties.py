'''
Created on Mar 23, 2016

@author: yanpliu@redhat.com

'''

import sys
#from Tools.rhn_manifest import test_type
sys.path.append("../../")
#from Tools import test_type

#[Env]
defaultencoding = 'utf-8'


#[Token]
token_header = "Authorization: Token ea5ac42c87d01cc42962b99966c3a9b430206bfc"
content_header = "Content-Type: application/json"
invalid_repo = "i386"
miss_repo = "TBD"



#[Buid Info]
#compose_id = "RHEL-6.8-20160308.0"
#compose_id = "RHEL-6.8-20160414.0"
#compose_id = "Supp-6.8-RHEL-6-20160308.0"

#if test_type == "Beta":
#    repo_family = "beta"
#elif test_type == "HTB":
#    repo_family = "htb"
#elif test_type == "GA":
#    repo_family = "dist"

Service = "rhn"


#[OutputFile]
pathdir = './'
#pathdir = './' + compose_id +"/"
#pathdirlog = './' + compose_id +'/log/'
manifestDirectory = Service + "-" + "package-manifest"
ComposerpmDemo_Jsonfile = "composerpm.json"
Rpms_Jsonfile = "rpms.json"
Rpms_Resultsfile = 'rpms_counts.txt'
RepoDemo_Jsonfile = "repo.json"
ReleaseDemo_Jsonfile = "release.json"
ChannelsDemo_Jsonfile = "channels.json"
Channels_CountListfile = "channels_count.txt"
ManifestCreate_Log = 'ManifestCreate.log'
rpm_map_channelflagFile = 'rpm_map_channelflag.json'
#manifestJsonfile = compose_id + "_RHN" +"_manifest.json"
manifestJsonfile = "RHN_manifest.json"



#[REST_API]
REST_API_Url = "https://pdc.engineering.redhat.com"
#REST_API_Compose_rpms = REST_API_Url + "/rest_api/v1/compose-rpms/" + compose_id + "/"
REST_API_Compose_rpms = REST_API_Url + "/rest_api/v1/compose-rpms/"
REST_API_Content_delivery_repos =  REST_API_Url + "/rest_api/v1/content-delivery-repos/"
REST_API_Compose =  REST_API_Url + "/rest_api/v1/composes/"


