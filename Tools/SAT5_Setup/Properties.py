'''
Created on June 06, 2016

@author: yanpliu@redhat.com

'''
import logging

#[Env]
systemid_path = '/etc/sysconfig/rhn/systemid'
up2date_path = '/etc/sysconfig/rhn/up2date'
cert = '/usr/share/rhn/RHNS-CA-CERT'

#[conf]
mount_point = '/home/var/satellite'
kickstart_mount_point = '/home/var/satellite'
repomd_cache_mount_point = '/home/var/cache'
ceback_mail = 'yanpliutest@redhat.com'
rhn_conf = '/etc/rhn/rhn.conf'

#[Installtion]
satellite_ISO = '/root/Satellite_Software/satellite-5.7.0-20150108-rhel-6-x86_64.iso'
mount_directory = '/media/cdrom/'
pathdir = './'
satellite_installfile = mount_directory + "/install.pl"
satellite_cert = "/home/Satellite_Software/satellite5.7_cert.crt"
QA_satellite_cert = "/home/Satellite_Software/sat57QARHN-test-resigned.cert"
answerfile_path = "/root/entitlement-tests/Tools/SAT5_Setup/"
answerfile = answerfile_path + '/answers.txt'

#[RHN information]
account_rhn = {
    "Live": {
        "username": "qa@redhat.com",
        "password": "5ZZaEeysLP5Fb9PM"
    },
    "QA": {
        "username": "qa@redhat.com",
        "password": "redhatqa"
    }
}


server_url = {
    "QA": "https://xmlrpc.rhn.qa.redhat.com/XMLRPC",
    "Live": "https://xmlrpc.rhn.redhat.com/XMLRPC"
}


#[OutputFile]
SatelliteSetup_Log = "SatelliteSetup.log"