#!/usr/bin/python
'''
Created on June 8, 2016

@author: yanpliu@redhat.com

'''

import logging.handlers
import sys
import getopt
import datetime
import Properties
import os
import UtilSat5
import traceback
import logging.config



#########Install Satellite5.7 Server#########################
#########created by yanpliu###########################
#########Stop Satellite Server###################

def setUp(rhn):
    # Set logging config file
    log_path = os.path.join(os.getcwd(), "log")
    logging.info(log_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logging.info("--------------- Begin Init ---------------")
    try:

        if rhn == "Live":
            server_url = Properties.server_url.get("Live")
        elif rhn == "QA":
            server_url = Properties.server_url.get("QA")
        # Update sslCACert and serverUrl in file up2date on SAT5 Server
        UtilSat5.update_up2date(server_url)

    except Exception, e:
        logging.error(str(e))
        logging.error("Test Failed - Raised error when setup environment before RHN Entitlement testing!")
        logging.error(traceback.format_exc())

    logging.info("--------------- End Init ---------------")

def SatelliteSetup(rhn):
    logging.info("--------------- Begin install Satellite5.7 server --------------- ")
    # get server_Url username,password
    try:
        if rhn == "Live":
            server_url = Properties.server_url.get("Live")
            username = Properties.account_rhn.get("Live").get("username")
            password = Properties.account_rhn.get("Live").get("password")
        elif rhn == "QA":
            server_url = Properties.server_url.get("QA")
            username = Properties.account_rhn.get("QA").get("username")
            password = Properties.account_rhn.get("QA").get("password")

        # Register to RHN
        UtilSat5.register(username, password, server_url)

        test_result = True
        # Install Satellite Server5.7
        if rhn == "Live":
            test_result = UtilSat5.sateliteInstall()
        elif rhn == "QA":
            test_result = UtilSat5.activate_certificate_file()
            test_result &= UtilSat5.sateliteInstall()
        if test_result == False:
                logging.error("Test Failed - Failed to Install Satellite Server!")
    except Exception, e:
        logging.error(str(e))
        logging.error("Test Failed - Raised error when install Satellite Server!")
        logging.error(traceback.format_exc())

    logging.info("--------------- End Install Satellite Server --------------- ")


def Usage():
    print 'SatelliteSetup.py usage:'
    print '-h,--help: print help message.'
    print '-v, --version: print script version'
    print '-r, --rhn=QA,Live: input an rhn type, this is mandatory option'

def Version():
    print 'SatelliteSetup.py 1.0.0.0.1'

def ArgsMethod(argv):
    opts, args = getopt.getopt(argv[1:], 'hvdr:',['help','version','debug','rhn='])
    if len(argv) < 2:
        Usage()
        sys.exit(2)
    debugflag = 0
    rhn = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        elif o in ('-v', '--version'):
            Version()
            sys.exit(0)
        elif o in ('-d', '--debug'):
            debugflag = 1
        elif o in ('-r', '--rhn'):
            rhn = a
        else:
            print 'unhandled option'
            sys.exit(3)
    return rhn,debugflag


def log_file(logginglevel,rhn):
    # Write log into specified files
    if not os.path.exists(Properties.pathdir  + rhn +'/log/'):
        os.makedirs(Properties.pathdir + rhn +'/log/')
    logging.basicConfig(level=logginglevel,
                        format='%(asctime)s %(levelname)5s|%(filename)18s:%(lineno)3d|: %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename=Properties.pathdir + rhn +'/log/' + Properties.SatelliteSetup_Log,
                        filemode='w'
                        )


def log_console(logginglevel):
    # print log on the console
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logginglevel)
    formatter = logging.Formatter('%(asctime)s %(levelname)5s|%(filename)18s:%(lineno)3d|: %(message)s')
    consolehandler.setFormatter(formatter)
    logging.getLogger('').addHandler(consolehandler)


def main(argv):

    begintime = datetime.datetime.now()
    rhn = ArgsMethod(argv)[0]
    debugflag = ArgsMethod(argv)[1]
    #Output the log both to console and file
    if debugflag == 0:
        log_file(logging.INFO,rhn)
        log_console(logging.INFO)
    elif debugflag == 1:
        log_file(logging.DEBUG,rhn)
        log_console(logging.DEBUG)

    #####SetUP environment######
    setUp(rhn)

    ###########Install Satellite server 5.7####
    SatelliteSetup(rhn)

    endtime = datetime.datetime.now()
    logging.info("##################Begin time is:")
    logging.info(begintime)
    logging.info("##################End time is:")
    logging.info(endtime)


if __name__ == "__main__":
    main(sys.argv)