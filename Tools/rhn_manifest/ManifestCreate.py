#!/usr/bin/python
'''
Created on Mar 20, 2016

@author: yanpliu@redhat.com

'''

import json
import commands
import logging.handlers
import shutil
import sys
import getopt
import datetime
import RestAPIProperties
import copy
import os


#[Parameters]
Path_Key = "path"
Format = "rpm"
Rpms_Key = "rpms"
Name_Key = "name"
Release_Key = "release"
Channels = "channels"
Content_Category = "content_category"
Channel_arch = "arch"
Channel_Name_Key = "name"
Channel_variant = "variant_uid"
#Shadow = True
Rpm_category = "category"


"""Method to collect all the rpms to a list"""
def list_all_rpms(dict_a,key,rpmsl):
    if isinstance(dict_a,dict) : #Use instance to dict type
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            logging.debug("%s : %s" %(temp_key,temp_value))
            if key == temp_key:
                rpm_value = temp_value.split("/")[-1]
                rpmsl.append(rpm_value)
            list_all_rpms(temp_value,key,rpmsl)  #realize self recursive call


"""Method to Analyse rpms Json files"""
def rpms_Json(dict_a,gRpmsdict):
    if isinstance(dict_a,dict) : #Use instance to dict type
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            if temp_key == Rpms_Key:
                gRpmsdict[temp_key] = temp_value
                logging.debug(gRpmsdict)
                break
            else:
                rpms_Json(temp_value,gRpmsdict)
        return gRpmsdict


"""Method to collect all the channels to a list"""
def list_all_channels(dict_a,key,gChannelslist):
    if isinstance(dict_a,dict) : #Use instance to dict type
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            if key == temp_key:
                logging.debug(temp_value)
                logging.debug(gChannelslist.append(temp_value))
                logging.debug(gChannelslist)
            list_all_channels(temp_value,key)#realize self recursive call
    elif isinstance(dict_a,list) :
        for x in range(len(dict_a)):
            if isinstance(dict_a[x],dict):
                list_all_channels(dict_a[x],key)


"""Method to collect all the releases to a list"""
def list_all_releases(dict_a,Release_Key,release):
    if isinstance(dict_a,dict) : #Use instance to dict type
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            if Release_Key == temp_key:
                logging.debug(release.append(temp_value))
            list_all_releases(temp_value,Release_Key)#realize self recursive call
    elif isinstance(dict_a,list) :
        for x in range(len(dict_a)):
            if isinstance(dict_a[x],dict):
                list_all_releases(dict_a[x],Release_Key)


"""Method to get all the rpms package"""
def get_Rpms(gRpmsdict,composeid):
    """Use Rest API "/rest_api/v1/compose-rpms/" to get all the rpms to a list"""
    logging.info("##################Get the all the rpm packages of the compose begin")
    ComposerpmDemo_Jsonfile = RestAPIProperties.pathdir + composeid +'/log/' + RestAPIProperties.ComposerpmDemo_Jsonfile
    cmd_compose_rpms = 'curl  -H "%s" -H "%s"  -X GET -k  %s | python -mjson.tool > %s' % (RestAPIProperties.token_header, RestAPIProperties.content_header, RestAPIProperties.REST_API_Compose_rpms + composeid + "/", ComposerpmDemo_Jsonfile)
    result,output_rpms = commands.getstatusoutput(cmd_compose_rpms)
    logging.info(cmd_compose_rpms)
    logging.info("%s" % output_rpms)
    logging.info("%s" % result)
    if(result == 0):
        f = open(ComposerpmDemo_Jsonfile,'r')
        dict1 = json.load(f)
        f.close()
        gRpmsdict = copy.deepcopy(rpms_Json(dict1,gRpmsdict))

    """
    Analyze the RpmsJsonfile
    Generate RestAPIProperties.Rpms_Jsonfile
    """
    Rpms_Jsonfile = RestAPIProperties.pathdir+ composeid +'/log/' + RestAPIProperties.Rpms_Jsonfile
    f = open(Rpms_Jsonfile,'w')

    json.dump(gRpmsdict,f)
    f.close()

    logging.info("##################After rpms:##################")
    logging.debug(gRpmsdict)
    return gRpmsdict


"""Method to get all the channels"""
def get_Channels(gChannelslist,release,Repo_family,compose_id,Shadow):
    '''Use Rest API /rest_api/v1/content-delivery-repos/ to get the channels to a list'''
    logging.info("##################Get  the channels begin##################")
    if Shadow == True:
        if os.path.exists(RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "_shadow"):
            shutil.rmtree(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "_shadow")
            os.makedirs(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "_shadow")
        else:
            os.makedirs(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "_shadow")
    else:
        if os.path.exists(RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family):
            shutil.rmtree(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family)
            os.makedirs(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family )
        else:
            os.makedirs(RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family )
    if Shadow == True:
        ChannelsDemo_Jsonfile = RestAPIProperties.pathdir + compose_id + '/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.ChannelsDemo_Jsonfile
    else:
        ChannelsDemo_Jsonfile = RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "/" + RestAPIProperties.ChannelsDemo_Jsonfile
    cmd_repos = 'curl  -H "%s" -H "%s" -d "release_id=%s&service=%s&content_format=%s&repo_family=%s&shadow=%s"  -G -k  %s | python -mjson.tool > %s'  % (RestAPIProperties.token_header, RestAPIProperties.content_header, release, RestAPIProperties.Service,Format,Repo_family, Shadow,RestAPIProperties.REST_API_Content_delivery_repos,ChannelsDemo_Jsonfile)
    re,output = commands.getstatusoutput(cmd_repos)
    logging.info(cmd_repos)
    logging.info("%s" % output)
    logging.info("%s" % re)

    if re == 0:
        f = open(ChannelsDemo_Jsonfile,'r')
        dictprevious = json.load(f)
        f.close()
        gChannelslistTotal = dictprevious["results"]
        flag = 1
        while dictprevious["next"] != None:
            flag = flag + 1
            cmd_channel = 'curl  -H "%s" -H "%s" -d "release_id=%s&service=%s&content_format=%s&repo_family=%s&shadow=%s&page=%s"  -G -k  %s | python -mjson.tool > %s'  % (RestAPIProperties.token_header, RestAPIProperties.content_header, release, RestAPIProperties.Service,Format,Repo_family, Shadow,flag,RestAPIProperties.REST_API_Content_delivery_repos,ChannelsDemo_Jsonfile)
            logging.info(cmd_channel)
            result,output = commands.getstatusoutput(cmd_channel)
            logging.info(output)
            if result == 0:
                f = open(ChannelsDemo_Jsonfile,'r')
                dictnext = json.load(f)
                f.close()
                gChannelslistTotal.extend(dictnext["results"])
                dictprevious = dictnext

    #Generate Channels Count file
    if Shadow == True:
        Channels_CountListfile = RestAPIProperties.pathdir + compose_id + '/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.Channels_CountListfile
    else:
        Channels_CountListfile = RestAPIProperties.pathdir + compose_id + '/log/' + Repo_family + "/" + RestAPIProperties.Channels_CountListfile
    flist = open(Channels_CountListfile,'w')
    clist = []
    for x in range(len(gChannelslistTotal)):
        # RHEL6.8 HTB support x86.64 only workaround
        logging.debug(gChannelslistTotal[x])
        logging.debug(gChannelslistTotal[x]["arch"])
        if gChannelslistTotal[x]["repo_family"] == "htb":
            if gChannelslistTotal[x]["product_id"] != None and gChannelslistTotal[x]["arch"] != RestAPIProperties.invalid_repo:
                gChannelslist.append(gChannelslistTotal[x])
                channel = gChannelslistTotal[x]["name"]
                if channel not in clist:
                    clist.append(channel)
            #elif gChannelslistTotal[x]["arch"] == RestAPIProperties.miss_repo:
            else:
                gChannelslist.append(gChannelslistTotal[x])
                channel = gChannelslistTotal[x]["name"]
                if channel not in clist:
                    clist.append(channel)
        else:
            gChannelslist.append(gChannelslistTotal[x])
            channel = gChannelslistTotal[x]["name"]
            if channel not in clist:
                clist.append(channel)
    logging.debug(gChannelslist)
    for channel in clist:
        flist.write(channel+"\n")
    flist.close()
    #Generate Channels List File
    if Shadow == True:
        gChannelslistFile = RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "_shadow" + "/" + "gChannelslist.json"
    else:
        gChannelslistFile = RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "/" + "gChannelslist.json"
    filechannel = open(gChannelslistFile, 'w')
    json.dump(gChannelslist, filechannel)
    filechannel.close()
    return gChannelslist

"""Method to get the Release information"""
def get_Release(compose_id):
    """Use Rest API /rest_api/v1/composes/ to get the release"""
    ReleaseDemo_Jsonfile = RestAPIProperties.pathdir+ compose_id +'/log/' + RestAPIProperties.ReleaseDemo_Jsonfile
    cmd_release = 'curl  -H "%s" -H "%s" -d "compose_id=%s"  -G -k  %s | python -mjson.tool > %s'  % (RestAPIProperties.token_header, RestAPIProperties.content_header, compose_id, RestAPIProperties.REST_API_Compose, ReleaseDemo_Jsonfile)
    result,output_repos = commands.getstatusoutput(cmd_release)
    logging.info(cmd_release)
    logging.info("%s" % output_repos)
    if result == 0:
        f = open(ReleaseDemo_Jsonfile,'r')
        dictrelease = json.load(f)
        f.close()
        release = dictrelease["results"][0][Release_Key]
        logging.info(release)
        return release


"""Method to write rpm mapping channel to manifest file"""
def writeToManifest(gChannelslist,rpm_variant,rpm_arch,rpm_name,rpm_category,manifestdict,rpm_map_channelflagdict):
    for y in range(len(gChannelslist)):
        channelsdict = gChannelslist[y]
        flag = 0
        logging.debug(channelsdict)
        if channelsdict[Channel_arch] == rpm_arch and channelsdict[Content_Category] == rpm_category and channelsdict[Channel_variant] == rpm_variant:
            manifestdict[RestAPIProperties.Service][Channels].setdefault(channelsdict[Channel_Name_Key], [ ]).append(rpm_name)
            logging.debug("add " +rpm_variant+ "." +rpm_arch+ "." + rpm_name + " to " + "channel " +  channelsdict[Channel_Name_Key])
            flag = 1
            rpm_map_channelflagdict[rpm_variant +"."+ rpm_arch +"."+ rpm_name] = True
        else:
            rpm_map_channelflagdict[rpm_variant +"."+ rpm_arch +"."+ rpm_name] = False
        if flag == 1:
            break;


"""Method to count the nummber of rpms which map to channel"""
def ChannelContainRpmsCalculate(Repo_family,compose_id,Shadow):
    if Shadow == True:
        ManifestJsonfile = RestAPIProperties.pathdir + compose_id + "/" + Repo_family + "/" + RestAPIProperties.manifestDirectory+ "_shadow" + "/" + "shadow_" +compose_id+ "_" + RestAPIProperties.manifestJsonfile
    elif Shadow == False:
        ManifestJsonfile = RestAPIProperties.pathdir + compose_id +"/"+ Repo_family + "/" + RestAPIProperties.manifestDirectory + "/" + compose_id +"_" +RestAPIProperties.manifestJsonfile
    fdict = open(ManifestJsonfile, 'r')
    manifestdict = json.load(fdict)
    fdict.close()
    manifestchannelsdict = manifestdict[RestAPIProperties.Service][Channels]
    for x in range(len(manifestchannelsdict)):
        channelslistKey = manifestchannelsdict.keys()[x]
        channelslist = manifestchannelsdict[channelslistKey]
        logging.info(channelslistKey + " contains rpm packages number is:")
        logging.info(len(channelslist))

"""Method to calculate the nummber of rpms which contains to a channel"""
def ChannelsRpmMapCalculate(rpmlist,Repo_family,compose_id,Shadow):
    """Calculate the successful and failed rpms mapped to channels"""
    if Shadow == True:
        rpm_map_channelflagFile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.rpm_map_channelflagFile
    else:
        rpm_map_channelflagFile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "/" + RestAPIProperties.rpm_map_channelflagFile
    f = open(rpm_map_channelflagFile,'r')
    mapdict = json.load(f)
    f.close()
    failedcount = 0
    for x in range(len(mapdict)):
        mapkey = mapdict.keys()[x]
        if mapdict[mapkey] == False:
            logging.info("Add rpm " + mapkey + " failed")
            failedcount += 1

    #print "The number of failed RPM package is: "
    logging.info("##################The number of RPM package from compose " + compose_id+ " failed to map channels is:")
    logging.info(failedcount)

    #print "The number of successful RPM package is: "
    logging.info("##################The number of RPM package from compose " + compose_id+ " sucessed to map channels is:")
    logging.info(len(rpmlist)-failedcount)


def log_file(logginglevel,compose_id):
    # Write log into specified files
    if not os.path.exists(RestAPIProperties.pathdir  + compose_id +'/log/'):
        os.makedirs(RestAPIProperties.pathdir + compose_id +'/log/')
    logging.basicConfig(level=logginglevel,
                        format='%(asctime)s %(levelname)5s|%(filename)18s:%(lineno)3d|: %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename=RestAPIProperties.pathdir + compose_id +'/log/' + RestAPIProperties.ManifestCreate_Log,
                        filemode='w'
                        )


def log_console(logginglevel):
    # print log on the console
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logginglevel)
    formatter = logging.Formatter('%(asctime)s %(levelname)5s|%(filename)18s:%(lineno)3d|: %(message)s')
    consolehandler.setFormatter(formatter)
    logging.getLogger('').addHandler(consolehandler)


"""Method to create manifest file"""
def manifestCreate(gRpmsdict,gChannelslist,Repo_family,compose_id,Shadow):
    # Generate Manifest file
    logging.info("##################Creating Manifest file Begin##################")
    logging.debug(gRpmsdict[Rpms_Key])
    manifestdict = dict()
    rpm_map_channelflagdict = dict()
    manifestdict = {RestAPIProperties.Service:{Channels:{}}}
    rpmlist = []
    if Shadow == True:
        manifestfile = RestAPIProperties.pathdir + compose_id + '/log/' + Repo_family + "_shadow" + "/" + "manifest.json"
    else:
        manifestfile = RestAPIProperties.pathdir + compose_id + '/log/' + Repo_family + "/" + "manifest.json"
    fmanifest = open(manifestfile, 'w')
    if Shadow == True:
        rpm_map_channelflagFile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.rpm_map_channelflagFile
    else:
        rpm_map_channelflagFile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "/" + RestAPIProperties.rpm_map_channelflagFile
    fmap = open(rpm_map_channelflagFile, 'w')
    for x in range(len(gRpmsdict[Rpms_Key])):
        variant = gRpmsdict[Rpms_Key].keys()[x]
        variantdict = gRpmsdict[Rpms_Key][variant]
        for y in range(len(variantdict)):
            arch = variantdict.keys()[y]
            archdict = variantdict[arch]
            for z in range(len(archdict)):
                srpmdict = archdict[archdict.keys()[z]]
                for n in range(len(srpmdict)):
                    rpmdict = srpmdict[srpmdict.keys()[n]]
                    for m in range(len(rpmdict)):
                        temp_key = rpmdict.keys()[m]
                        temp_value = rpmdict[temp_key]
                        if temp_key == Path_Key:
                            rpm_name = temp_value.split("/")[-1]
                            rpmlist.append(rpm_name)
                            rpm_category = rpmdict[Rpm_category]
                            #logging.debug(variant,arch,rpm_name,rpm_category)
                            if rpm_category == "binary":
                                writeToManifest(gChannelslist,variant,arch,rpm_name,rpm_category,manifestdict,rpm_map_channelflagdict)
    manifestdict["compose"] = compose_id
    json.dump(manifestdict, fmanifest)
    json.dump(rpm_map_channelflagdict, fmap)
    fmanifest.close()
    fmap.close()
    if Shadow == True:
        ManifestJsonFile = RestAPIProperties.pathdir + compose_id + "/" + Repo_family + "/" + RestAPIProperties.manifestDirectory+ "_shadow" + "/" + "shadow_" +compose_id+ "_" + RestAPIProperties.manifestJsonfile
        manifestpath = RestAPIProperties.pathdir + compose_id +"/" + Repo_family + "/" + RestAPIProperties.manifestDirectory+ "_shadow"
    elif Shadow == False:
        ManifestJsonFile = RestAPIProperties.pathdir + compose_id + "/" + Repo_family + "/" + RestAPIProperties.manifestDirectory + "/" +compose_id+ "_" + RestAPIProperties.manifestJsonfile
        manifestpath = RestAPIProperties.pathdir + compose_id +"/" + Repo_family + "/" + RestAPIProperties.manifestDirectory
    if not os.path.exists(manifestpath):
        os.makedirs(manifestpath)
    cmd_manifest = 'cat %s | python -m json.tool >%s ' % (manifestfile,ManifestJsonFile)
    result,output_repos = commands.getstatusoutput(cmd_manifest)
    logging.debug(cmd_manifest)
    logging.debug("%s" % output_repos)
    cmd_removemanifest = 'rm -rf manifestfile'
    commands.getstatusoutput(cmd_removemanifest)

    #Create rpms pacakges results file
    if Shadow == True:
        Rpms_Resultsfile = RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.Rpms_Resultsfile
    else:
        Rpms_Resultsfile = RestAPIProperties.pathdir+ compose_id +'/log/' + Repo_family + "/" + RestAPIProperties.Rpms_Resultsfile
    f = open(Rpms_Resultsfile,'w')
    for i in rpmlist:
        f.write(i)
        f.write("\n")
    f.close()
    logging.info("##################Creating Manifest file End##################")


def ManifestTotal(Repo_family,gRpmsdict,release,compose_id,Shadow):
    '''Get the channels to a list'''
    gChannelslist = []
    gChannelslist = copy.deepcopy(get_Channels(gChannelslist,release,Repo_family,compose_id,Shadow))
    logging.info("##################The Channels List is:##################")
    logging.debug(gChannelslist)
    '''Generate Manifest file'''
    manifestCreate(gRpmsdict,gChannelslist,Repo_family,compose_id,Shadow)

    #The total number of rpm packages
    logging.info("##################The number of RPM package from compose " + compose_id+ " is:")
    if Shadow == True:
        Rpms_Resultsfile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "_shadow" + "/" + RestAPIProperties.Rpms_Resultsfile
    else:
        Rpms_Resultsfile = RestAPIProperties.pathdir + compose_id +'/log/' + Repo_family + "/" + RestAPIProperties.Rpms_Resultsfile
    f = open(Rpms_Resultsfile,'r')
    rpmlist = []
    for line in f.readlines():
        rpmlist.append(line.split(','))
    f.close
    logging.info(len(rpmlist))

    #print "The number of channels is:"
    logging.info("##################The number of channels from compose " + compose_id+ " is:")
    logging.info(len(gChannelslist))

    # Channel Contain Rpms number
    ChannelContainRpmsCalculate(Repo_family,compose_id,Shadow)
    # Channels Rpm Map results count
    ChannelsRpmMapCalculate(rpmlist,Repo_family,compose_id,Shadow)


def Usage():
    print 'ManifestCreate.py usage:'
    print '-h,--help: print help message.'
    print '-v, --version: print script version'
    print '-c, --composeid=compose_id: input an compose id, this is mandatory option'
    print '-t, --test-type=test_type: input one of the test types: Beta, HTB, GA'
    print '-d, --debug: Run python script using debug mode'
    print '-s, --shadow: Run shadow type'
def Version():
    print 'ManifestCreate.py.py 1.0.0.0.1'

def OutPut(args):
    Compose_id = args


def ArgsMethod(argv):
    if len(argv) < 2:
        Usage()
        sys.exit(2)
    opts, args = getopt.getopt(argv[1:], 'hvdsc:t:',['help','version','debug','shadow','composeid=','test-type='])
    debugflag = 0
    Shadow = False
    compose_id = ''
    test_type = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif o in ('-v', '--version'):
            Version()
            sys.exit(0)
        elif o in ('-d', '--debug'):
            debugflag = 1
        elif o in ('-s', '--shadow'):
            Shadow = True
        elif o in ('-c', '--composeid'):
            compose_id = a
        elif o in ('-t', '--test-type'):
            test_type = a
        else:
            print 'unhandled option'
            sys.exit(3)
    return compose_id,debugflag,Shadow,test_type


def main(argv):
    begintime = datetime.datetime.now()
    compose_id = ArgsMethod(argv)[0]
    debugflag = ArgsMethod(argv)[1]
    Shadow = ArgsMethod(argv)[2]
    test_type = ArgsMethod(argv)[3]

    # Output the log both to console and file
    if debugflag == 0:
        log_file(logging.INFO,compose_id)
        log_console(logging.INFO)
    elif debugflag == 1:
        log_file(logging.DEBUG,compose_id)
        log_console(logging.DEBUG)

    # Use Rest API "/rest_api/v1/compose-rpms/" to get all the rpms to a list
    gRpmsdict = dict()
    gRpmsdict = copy.deepcopy(get_Rpms(gRpmsdict,compose_id))
    logging.debug(gRpmsdict)
    rpmtime = datetime.datetime.now()

    # Use Rest API /rest_api/v1/composes/ to get the release
    release = get_Release(compose_id)
    logging.info(release)

    # Get the test type from command line argument or env variable, which will be set as the value of the variable 'repo_family'
    if test_type.capitalize() == "Beta":
        repo_family = "beta"
    elif test_type.upper() == "HTB":
        repo_family = "htb"
    elif test_type.upper() == "GA":
        repo_family = "dist"

    logging.info("###########Generate Manifest" + repo_family +" Begin##########")
    ManifestTotal(repo_family,gRpmsdict,release,compose_id,Shadow)
    logging.info("###########Generate Manifest" + repo_family +" End##########")


    #logging.info("###########Generate Manifest" + RestAPIProperties.htbrepo_family +" Begin##########")
    #ManifestTotal(RestAPIProperties.htbrepo_family,gRpmsdict,release,compose_id,Shadow)
    #logging.info("###########Generate Manifest" + RestAPIProperties.htbrepo_family +" End##########")

    endtime = datetime.datetime.now()
    logging.info("##################Begin time is:")
    logging.info(begintime)
    logging.info("##################Rpm finish time is:")
    logging.info(rpmtime)
    logging.info("##################End time is:")
    logging.info(endtime)


if __name__ == "__main__":

    main(sys.argv)
    # begintime = datetime.datetime.now()
    # #Output the log both to console and file
    # log_file()
    # log_console()
    #
    #
    # # Use Rest API "/rest_api/v1/compose-rpms/" to get all the rpms to a list
    # gRpmsdict = dict()
    # gRpmsdict = copy.deepcopy(get_Rpms(gRpmsdict))
    # logging.debug(gRpmsdict)
    # rpmtime = datetime.datetime.now()
    #
    # """Use Rest API /rest_api/v1/composes/ to get the release"""
    # release = get_Release()
    # logging.info(release)
    #
    #
    # logging.info("###########Generate Manifest" + RestAPIProperties.repo_family +" Begin##########")
    # ManifestTotal(RestAPIProperties.repo_family)
    # logging.info("###########Generate Manifest" + RestAPIProperties.repo_family +" End##########")
    #
    #
    # logging.info("###########Generate Manifest" + RestAPIProperties.htbrepo_family +" Begin##########")
    # #ManifestTotal(RestAPIProperties.htbrepo_family)
    # logging.info("###########Generate Manifest" + RestAPIProperties.htbrepo_family +" End##########")
    #
    # endtime = datetime.datetime.now()
    # logging.info("##################Begin time is:")
    # logging.info(begintime)
    # logging.info("##################Rpm finish time is:")
    # logging.info(rpmtime)
    # logging.info("##################End time is:")
    # logging.info(endtime)




