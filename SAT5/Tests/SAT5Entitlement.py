import os
import unittest
import traceback
import logging
import logging.config
import json
import commands
import datetime

from Utils import system_username
from Utils import system_password
from Utils import system_ip
from SAT5 import distro
from SAT5 import variant
from SAT5 import arch
from SAT5 import manifest_url
from SAT5 import sat5_server
from SAT5 import sat5_server_username
from SAT5 import sat5_server_password
from SAT5 import sat5_activation_key
from SAT5 import product_type
from SAT5 import test_level
from SAT5 import test_type

from SAT5.SAT5ParseManifestXML import SAT5ParseManifestXML
from SAT5.SAT5Verification import SAT5Verification

# Create logger
logger = logging.getLogger("entLogger")

def get_server_url():
    return "https://" + sat5_server + "/XMLRPC"

class SAT5Entitlement(unittest.TestCase):
    def setUp(self):
        # Set logging config file
        log_path = os.path.join(os.getcwd(), "log")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        logger.info("--------------- Begin Init ---------------")
        try:
            # Get ip, username and password of beaker testing system
            self.system_info = {
                "ip": system_ip,
                "username": system_username,
                "password": system_password
            }

            # Get sat5 server name, url, username, password and activation key.
            self.sat5_server = sat5_server
            self.server_url = get_server_url()
            
            self.username = sat5_server_username
            self.password = sat5_server_password
            self.activation_key = sat5_activation_key

            # Get testing parameters
            self.distro = distro
            self.variant = variant
            self.arch = arch
            self.test_level = test_level
            self.test_type = test_type
            self.product_type = product_type
            
            # Get manifest url, set json and xml manifest local path
            self.manifest_url = manifest_url
            self.manifest_path = os.path.join(os.getcwd(), "manifest")
            self.manifest_json = os.path.join(self.manifest_path, "sat5_test_manifest.json")
            self.manifest_xml = os.path.join(self.manifest_path, "sat5_test_manifest.xml")
            self.failed_manifest_json = os.path.join(self.manifest_path, "sat5_failed_test_manifest.json")
            self.notrun_manifest_json = os.path.join(self.manifest_path, "sat5_notrun_test_manifest.json")
            self.pass_manifest_json = os.path.join(self.manifest_path, "sat5_pass_test_manifest.json")
            self.failed_manifest_log = os.path.join(self.manifest_path, "sat5_failed_test_manifest.log")
            self.notrun_manifest_log = os.path.join(self.manifest_path, "sat5_notrun_test_manifest.log")
            self.pass_manifest_log = os.path.join(self.manifest_path, "sat5_pass_test_manifest.log")

            # Install needed packages for RHEL8
            if self.product_type == "RHEL8":
                SAT5Verification().install_packages(self.system_info)

            # Download certificate from SAT5 Server
            result = SAT5Verification().download_cert(self.system_info, self.sat5_server)
            self.assertTrue(result, msg="Test Failed - Failed to download certificate from SAT5 Server!")

            # Update sslCACert and serverUrl in file up2date on SAT5 Server
            result = SAT5Verification().update_up2date(self.system_info, self.server_url)
            self.assertTrue(result, msg="Test Failed - Failed to set sslCACert or sslServerUrl in up2date file!")

            # Get system release version and arch
            if self.product_type == "RHEL8":
                self.current_release_ver = SAT5Verification().get_os_release_version_by_dnf(self.system_info)
                self.current_arch = SAT5Verification().get_os_base_arch_by_dnf(self.system_info)                
            else:
                self.current_release_ver = SAT5Verification().get_os_release_version(self.system_info)
                self.current_arch = SAT5Verification().get_os_base_arch(self.system_info)

            # Download and parse manifest
            SAT5ParseManifestXML(self.manifest_url, self.manifest_path, self.manifest_json, self.manifest_xml).parse_json_to_xml()

            # Remove non-redhat.repo
            SAT5Verification().remove_non_redhat_repo(self.system_info)

            # Space extend
            #SAT5Verification().extend_system_space(self.system_info, self.manifest_json)

            # Extend system reservation time
            #SAT5Verification().extend_reservation_time(self.system_info, self.test_level)

        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when setup environment before SAT5 Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End Init ---------------")

    def testSAT5Entitlement_VARIANT_ARCH(self):
        logger.info("--------------- Begin testSAT5Entitlement --------------- ")

        try:
            # Check if the testing system is registered
            if SAT5Verification().isregistered(self.system_info):
                logger.info("The system is already registered, need to unregister first!")
                
                result = SAT5Verification().unregister(self.system_info, self.product_type)
                self.assertTrue(result, msg="Test Failed - Failed to unregister from Satellite 5 server!")

            # Register the testing system
            if self.product_type == "RHEL8":
                result = SAT5Verification().register_by_activationkey(self.system_info, self.activation_key)
                self.assertTrue(result, msg="Test Failed - Failed to Register with SAT5 server by activation key!")
            else:
                if test_type == "HTB":
                    result = SAT5Verification().register_by_activationkey(self.system_info, self.activation_key)
                    self.assertTrue(result, msg="Test Failed - Failed to Register with SAT5 server by activation key!")
                else:
                    result = SAT5Verification().register(self.system_info, self.username, self.password, self.server_url)
                    self.assertTrue(result, msg="Test Failed - Failed to Register with SAT5 server by username and password!")

            # Trying to clean the yum cache after register
            SAT5Verification().clean_yum_cache(self.system_info)
            self.assertTrue(result, msg="Test Failed - Failed to clean yum cache.")
            
            # Get and print all testing channels
            # If 0 channel, exit
            channel_list = SAT5Verification().get_channels_from_manifest(self.manifest_xml, 
                                self.current_arch, self.variant, self.product_type)
            self.assertNotEqual(channel_list, [], msg="Test Failed - There is no any channel.")
            
            Test_Result = True
            if self.current_release_ver.split()[0] != "5":
                # Check if all channels listed in manifest are available in SAT5
                ret = SAT5Verification().verify_channels(self.system_info, self.manifest_xml, 
                            self.username, self.password, self.current_arch, self.variant, self.product_type)
                result = ret[0]
                Test_Result &= result

                # Remove the failed-to-verify channels from the testing channels list if have
                failed_channellist = ret[1]
                if len(failed_channellist) > 0:
                    logger.error("--------------- Remove channels which are failed to be verfied ---------------")
                    for channelmiss in failed_channellist:
                        if channelmiss in channel_list:
                            logger.error("Test Failed - Remove the channel '{0}' from testing channels list for now so that it won't interrupt the testing.".format(channelmiss))
                            channel_list.remove(channelmiss)

                logger.info("--------------- The channels to be tested are:")
                SAT5Verification().print_list(channel_list)

            # Get base channel, such as rhel-x86_64-server-6
            master_release, minor_release = SAT5Verification().get_release_version(self.manifest_json, "SAT5")
            base_channel_str = SAT5Verification().get_base_channel(self.test_type, self.variant, self.arch, master_release)
            base_channel = base_channel_str.split(",")

            # Add base channel, such as rhel-x86_64-server-6
            logger.info("--------------- Add base channels '{0}' ---------------".format(base_channel))
            result = SAT5Verification().add_channels(self.system_info, self.username, self.password, base_channel)
            #self.assertTrue(result, msg="Test Failed - Failed to add base channel {0}!".format(base_channel))
            
            Test_Result &= result
            extendtime_flag = False

            ffailedmanifest_log = open(self.failed_manifest_log, 'w')
            fpassmanifest_log = open(self.pass_manifest_log, 'w')
            # fnotrunmanifest_log = open(self.notrun_manifest_log, 'w')
            #
            #
            # fmanifest = open(self.manifest_json,'r')
            # notrundictmanifest = json.load(fmanifest)
            # notrunlist = notrundictmanifest["rhn"]["channels"]
            # for x in range(len(notrunlist)):
            #     channel = notrunlist.keys()[x]
            #     channellist = notrunlist[channel]
            #     for y in range(channellist):
            #         fnotrunmanifest_log.write("{0}:{1}".format(channel, y))

            #manifestfaileddict = dict()
            manifestfaileddict = {"rhn":{"channels":{}}}

            #manifestpassdict = dict()
            manifestpassdict = {"rhn":{"channels":{}}}

            #manifestnotrundict = dict()
            manifestnotrundict = {"rhn":{"channels":{}}}

            for channel in channel_list:
                # Add test channel
                if channel not in base_channel:
                    result = SAT5Verification().add_channels(self.system_info, self.username, self.password, channel)
                    if not result:
                        logger.error("Test Failed - Failed to add test channel {0}".format(channel))
                        Test_Result &= result
                        continue

                # Installation testing
                logger.info("Test level: {0}".format(self.test_level))
                if self.test_level == "Basic":
                    # Product id certificate installation
                    Test_Result &= SAT5Verification().smoke_installation(self.system_info, self.manifest_xml, channel, manifestfaileddict)
                elif self.test_level == "Advanced":
                    # All package installation
                    #test_result &= SAT5Verification().installation(self.system_info, self.manifest_xml, channel, manifestfaileddict, starttime)
                    starttime = datetime.datetime.now()
                    test_re = SAT5Verification().installation(self.system_info, self.manifest_xml, channel, manifestfaileddict, manifestpassdict, manifestnotrundict, ffailedmanifest_log, fpassmanifest_log, starttime)
                    Test_Result &= test_re[0]
                    extendtime_flag = test_re[1]
                    if extendtime_flag == True:
                        starttime = datetime.datetime.now()

                # Remove test channel
                if channel not in base_channel:
                    Test_Result &= SAT5Verification().remove_channels(self.system_info, self.username, self.password, channel)


            # Generate failed rpm manifest file
            manifestfaileddict["compose"] = self.distro
            failed_rpm = self.manifest_path+"/manifest_failed.json"
            ffailedmanifest = open(failed_rpm, 'w')
            json.dump(manifestfaileddict, ffailedmanifest)
            ffailedmanifest.close()
            cmd_manifest = 'cat %s | python -m json.tool >%s ' % (failed_rpm,self.failed_manifest_json)
            result,output_repos = commands.getstatusoutput(cmd_manifest)
            logger.debug(cmd_manifest)
            logger.debug("%s" % output_repos)
            cmd_removemanifest = 'rm -rf %s' % (failed_rpm)
            commands.getstatusoutput(cmd_removemanifest)

            # Generate pass rpm manifest file
            manifestpassdict["compose"] = self.distro
            pass_rpm = self.manifest_path+"/manifest_pass.json"
            fpassmanifest = open(pass_rpm, 'w')
            json.dump(manifestpassdict, fpassmanifest)
            fpassmanifest.close()
            cmd_manifest = 'cat %s | python -m json.tool >%s ' % (pass_rpm,self.pass_manifest_json)
            result,output_repos = commands.getstatusoutput(cmd_manifest)
            logger.debug(cmd_manifest)
            logger.debug("%s" % output_repos)
            cmd_removemanifest = 'rm -rf %s' % (pass_rpm)
            commands.getstatusoutput(cmd_removemanifest)

            # Generate not run rpm manifest file
            manifestnotrundict["compose"] = self.distro
            notrun_rpm = self.manifest_path+"/manifest_pass.json"
            fnotrunmanifest = open(notrun_rpm, 'w')
            json.dump(manifestnotrundict, fnotrunmanifest)
            fnotrunmanifest.close()
            cmd_manifest = 'cat %s | python -m json.tool >%s ' % (notrun_rpm,self.notrun_manifest_json)
            result,output_repos = commands.getstatusoutput(cmd_manifest)
            logger.debug(cmd_manifest)
            logger.debug("%s" % output_repos)
            cmd_removemanifest = 'rm -rf %s' % (notrun_rpm)
            commands.getstatusoutput(cmd_removemanifest)

            self.assertTrue(Test_Result, msg="Test Failed - Failed to do SAT5 Entitlement testing!")
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when do SAT5 Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End testSAT5Entitlement --------------- ")

    def tearDown(self):
        logger.info("--------------- Begin tearDown ---------------")
        try:
            # Unregister
            SAT5Verification().unregister(self.system_info, self.product_type)

            # Restore non-redhat.repo
            #SAT5Verification().restore_non_redhat_repo(self.system_info)
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when tear down after SAT5 Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End tearDown ---------------")


if __name__ == '__main__':
    unittest.main()
