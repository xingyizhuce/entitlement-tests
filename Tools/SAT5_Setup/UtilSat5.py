#!/usr/bin/python
'''
Created on June 8, 2016

@author: yanpliu@redhat.com

'''

import json
import commands
import logging.handlers
import shutil
import sys
import getopt
import Properties
import copy
import os
import logging.config


def log_file(rhn):
    # Write log into specified files
    if not os.path.exists(Properties.pathdir  + rhn +'/log/'):
        os.makedirs(Properties.pathdir + rhn +'/log/')
    logging.basicConfig(level=Properties.logginglevel,
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


def update_up2date(server_url):
    # sslCACert default value:
    # RHEL6: sslCACert=/usr/share/rhn/RHNS-CA-CERT
    # RHEL7: sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
    up2date_path = "/etc/sysconfig/rhn/up2date"
    #cert = "/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT"
    cert = "/usr/share/rhn/RHNS-CA-CERT"
    cmd = "sed -i -e '/sslCACert=/d' -e '/^sslCACert/a\sslCACert={0}' {1}".format(cert, up2date_path)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set sslCACert in {0}...".format(up2date_path))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set sslCACert to {0} in {1}.".format(cert, up2date_path))
    else:
        logging.error("Test Failed - Failed to set sslCACert to {0} in {1}.".format(cert, up2date_path))
        return False

    cmd = "sed -i -e '/serverURL=/d' -e '/^serverURL/a\serverURL={0}' {1}".format(server_url, up2date_path)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set serverUrl in {0}...".format(up2date_path))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set serverURL to {0} in {1}.".format(server_url, up2date_path))
    else:
        logging.error("Test Failed - Failed to set serverURL to {0} in {1}.".format(server_url, up2date_path))
        return False

    return True

def update_rhnconf(rhn):
    ###########Modify satellite information and mount point##########
    if rhn == "Live":
        rhn_parent = "satellite.rhn.qa.redhat.com"
    elif rhn == "QA":
        rhn_parent = "satellite.rhn.redhat.com"
    ca_chain = '/usr/share/rhn/RHNS-CA-CERT'
    mount_point = Properties.mount_point
    kickstart_mount_point = Properties.kickstart_mount_point
    repomd_cache_mount_point = Properties.repomd_cache_mount_point
    ceback_mail = Properties.ceback_mail
    rhn_conf = Properties.rhn_conf

    cmd = "sed -i -e '/mount_point = /d' -e '/^mount_point/a\mount_point={0}' {1}".format(mount_point, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set mount_point in {0}...".format(rhn_conf))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set mount_point to {0} in {1}.".format(mount_point, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set mount_point to {0} in {1}.".format(mount_point, rhn_conf))
        return False

    cmd = "sed -i -e '/kickstart_mount_point = /d' -e '/^kickstart_mount_point/a\kickstart_mount_point={0}' {1}".format(kickstart_mount_point, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set kickstart_mount_point in {0}...".format(rhn_conf))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set kickstart_mount_point to {0} in {1}.".format(kickstart_mount_point, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set kickstart_mount_point to {0} in {1}.".format(kickstart_mount_point, rhn_conf))
        return False

    cmd = "sed -i -e '/repomd_cache_mount_point = /d' -e '/^repomd_cache_mount_point/a\/repomd_cache_mount_point={0}' {1}".format(repomd_cache_mount_point, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set repomd_cache_mount_point in {0}...".format(rhn_conf))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set repomd_cache_mount_point to {0} in {1}.".format(repomd_cache_mount_point, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set repomd_cache_mount_point to {0} in {1}.".format(repomd_cache_mount_point, rhn_conf))
        return False


    cmd = "sed -i -e '/ceback_mail = /d' -e '/^ceback_mail/a\ceback_mail={0}' {1}".format(ceback_mail, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set repomd_cache_mount_point in {0}...".format(rhn_conf))
    if ret == 0:
        logging.info("It's successful to set ceback_mail to {0} in {1}.".format(ceback_mail, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set ceback_mail to {0} in {1}.".format(ceback_mail, rhn_conf))
        return False

    cmd = "sed -i -e '/server.satellite.rhn_parent = /d' -e '/^server.satellite.rhn_parent/a\server.satellite.rhn_parent={0}' {1}".format(rhn_parent, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set server.satellite.rhn_parent in {0}...".format(rhn_conf))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set server.satellite.rhn_parent to {0} in {1}.".format(rhn_parent, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set server.satellite.rhn_parent to {0} in {1}.".format(rhn_parent, rhn_conf))
        return False

    cmd = "sed -i -e '/server.satellite.ca_chain = /d' -e '/^server.satellite.ca_chain/a\server.satellite.ca_chain={0}' {1}".format(ca_chain, rhn_conf)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set server.satellite.ca_chain in {0}...".format(rhn_conf))
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to set server.satellite.ca_chain to {0} in {1}.".format(ca_chain, rhn_conf))
    else:
        logging.error("Test Failed - Failed to set server.satellite.ca_chain to {0} in {1}.".format(ca_chain, rhn_conf))
        return False
    return True



def register(username, password, server_url):
    cmd = "rhnreg_ks --username=%s --password=%s --serverUrl=%s" % (username, password, server_url)

    if isregistered():
        if not unregister():
            logging.info("The system is failed to unregister from rhn server, try to use '--force'!")
            cmd += " --force"

    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to register to rhn server...")
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("It's successful to register to rhn server.")
        cmd = "rm -rf /var/cache/yum/*"
        #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to clean the yum cache after register...")
        ret, output = commands.getstatusoutput(cmd)
        if ret == 0:
            logging.info("It's successful to clean the yum cache.")
        else:
            logging.warning("Failed to clean the yum cache.")
        return True
    else:
        # Error Message:
        # Invalid username/password combination
        logging.error("Test Failed - Failed to register with rhn server.")
        return False

def stopsat():
    logging.info("###########Stop Satellite Server Begin##########")
    which_cmd = 'which rhn-satellite'
    ret,output = commands.getstatusoutput(which_cmd)
    logging.info(which_cmd)
    logging.info("%s" % output)
    if ret == 0:
        logging.info('#############There is a old satellite server need to clean###########')
        logging.info('###########Stop satellite server############')
        stop_sat_cmd = 'rhn-satellite stop'
        result,output_stop = commands.getstatusoutput(stop_sat_cmd)
        #result,output_stop = RemoteSSH().run_cmd(system_info, stop_sat_cmd, "Trying to stop satellite server...")
        logging.info(stop_sat_cmd)
        logging.info("%s" % output_stop)
        if result == 0:
            logging.info('#############Stop satellite server successfully###########')
        else:
            logging.info('#############Stop satellite server failed###########')
    else:
        logging.info('###########There is no satellite server.###########')

def satellite_check():
    satellite_flag = False
    logging.info("###########Check Satellite Server Install or not##########")
    which_cmd = 'which rhn-satellite'
    ret,output = commands.getstatusoutput(which_cmd)
    #ret,output = RemoteSSH().run_cmd(system_info, which_cmd, "Trying to check satellite server install or not...")
    logging.info(which_cmd)
    logging.info("%s" % output)
    if ret == 0:
        logging.info('#############There is a old satellite server need to clean###########')
        satellite_flag = True
    else:
        logging.info('###########There is no satellite server.###########')
    return satellite_flag

def startsat():
    logging.info("###########Start Satellite Server Begin##########")
    which_cmd = 'which rhn-satellite'
    ret,output = commands.getstatusoutput(which_cmd)
    #ret,output = RemoteSSH().run_cmd(system_info, which_cmd, "Trying to check satellite server install or not...")
    logging.info(which_cmd)
    logging.info("%s" % output)
    if ret == 0:
        logging.info('#############There is a old satellite server need to clean###########')
        logging.info('###########Start satellite server############')
        start_sat_cmd = 'rhn-satellite start'
        result,output_stop = commands.getstatusoutput(start_sat_cmd)
        #result,output_stop = RemoteSSH().run_cmd(system_info, start_sat_cmd, "Trying to start satellite server...")
        logging.info(start_sat_cmd)
        logging.info("%s" % output_stop)
        if result == 0:
            logging.info('#############Start satellite server successfully###########')
        else:
            logging.info('#############Start satellite server failed###########')
    else:
        logging.info('###########There is no satellite server.###########')

def sateliteInstall():
    logging.info("###########Install Satellite Server Begin##########")
    create_cmd = 'mkdir -p  %s' % (Properties.mount_directory)
    ret,output = commands.getstatusoutput(create_cmd)
    #ret,output = RemoteSSH().run_cmd(system_info, create_cmd, "Trying to create mount directory...")
    logging.info(create_cmd)
    logging.info("%s" % output)
    if ret == 0:
        logging.info('#############create mount directory successfully###########')
    else:
        logging.info('###########create mount directory failed###########')

    mount_cmd = 'mount -o loop %s %s'  % (Properties.satellite_ISO, Properties.mount_directory)
    retmount,outputmount = commands.getstatusoutput(mount_cmd)
    #retmount,outputmount = RemoteSSH().run_cmd(system_info, mount_cmd, "Trying to mount ISO...")
    logging.info(mount_cmd)
    logging.info("%s" % outputmount)
    if ret == 0:
        logging.info('#############mount ISO successfully###########')
    else:
        logging.info('###########mount ISO failed###########')

    if satellite_check() == False:
        install_cmd = '%s --answer-file=%s' % (Properties.satellite_installfile, Properties.answerfile)
        ret,output = commands.getstatusoutput(install_cmd)
        #ret,output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to Install satellite...")
        logging.info(install_cmd)
        logging.info("%s" % output)
        if ret == 0:
            logging.info('#############Install Satellite server successfully###########')
            satellite_satus()
        else:
            logging.info('###########Install Satellite server Failed###########')
    elif satellite_check() == True:
        startsat()
        install_cmd = '%s --clear-db --answer-file=%s' % (Properties.satellite_installfile, Properties.answerfile)
        ret,output = commands.getstatusoutput(install_cmd)
        #ret,output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to Install satellite with --clear-db ...")
        logging.info(install_cmd)
        logging.info("%s" % output)
        if ret == 0:
            logging.info('#############Install Satellite server successfully###########')
            logging.info('Satellite Server Status is:')
            satellite_satus()
        else:
            logging.info('###########Install Satellite server Failed###########')

def satellite_satus():
    logging.info("###########Check Satellite Server Status##########")
    satellite_check()
    check_cmd = 'rhn-satellite status'
    ret,output = commands.getstatusoutput(check_cmd)
    #ret,output = RemoteSSH().run_cmd(system_info, check_cmd, "Trying to check Satellite Server Status...")
    if ret == 0:
        logging.info(check_cmd)
        logging.info("%s" % output)


def isregistered():
    cmd = "ls /etc/sysconfig/rhn/systemid"
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check if registered to rhn...")
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("The system is registered to rhn server now.")
        return True
    else:
        logging.info("The system is not registered to rhn server now.")
        return False

def unregister():
    cmd = "rm -rf /etc/sysconfig/rhn/systemid"
    #(ret1, output1) = RemoteSSH().run_cmd(system_info, cmd, "Trying to unregister from rhn - delete systemid...")
    ret1, output1 = commands.getstatusoutput(cmd)
    cmd = "sed -i 's/enabled = 1/enabled = 0/' /etc/yum/pluginconf.d/rhnplugin.conf"
    #(ret2, output2) = RemoteSSH().run_cmd(system_info, cmd, "Trying to unregister from rhn - modify rhnplugin.conf...")
    ret2, output2 = commands.getstatusoutput(cmd)
    if ret1 == 0 and ret2 == 0:
        logging.info("It's successful to unregister from rhn server.")
        return True
    else:
        logging.error("Test Failed - Failed to unregister from rhn server.")
        return False

def activate_certificate_file():
    cmd = "rhn-satellite-activate --rhn-cert %s -vv" % (Properties.QA_satellite_cert)
    #ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to activate certificate file...")
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        logging.info("The system is activated certificate file to RHN sucessfully.")
        return True
    else:
        logging.info("The system is activated certificate file to RHN failed.")
        return False










