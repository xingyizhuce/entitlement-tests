import os
import unittest
import traceback
import logging
import logging.config

from Utils import system_username
from Utils import system_password
from Utils import system_ip
import json
import commands
from RHN import rhn
from RHN import variant
from RHN import arch
from RHN import manifest_url
from RHN import server_url
from RHN import account_rhn
from RHN import test_level
from RHN import distro
from RHN.RHNParseManifestXML import RHNParseManifestXML
from RHN.RHNVerification import RHNVerification


# Create logger
logger = logging.getLogger("entLogger")


def get_username_password():
    if rhn == "Live":
        return account_rhn["Live"]["username"], account_rhn["Live"]["password"]
    elif rhn == "QA":
        return account_rhn["QA"]["username"], account_rhn["QA"]["password"]

def get_server_url():
    if rhn == "QA":
        return server_url["QA"]
    else:
        return server_url["Live"]

class RHNEntitlement(unittest.TestCase):
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

            # Get testing params passed by Jenkins
            self.rhn = rhn
            self.variant = variant
            self.arch = arch
            self.distro = distro

            # Get Testing Level
            self.test_level = test_level

            # Get manifest url, set json and xml manifest local path
            self.manifest_url = manifest_url
            self.manifest_path = os.path.join(os.getcwd(), "manifest")
            self.manifest_json = os.path.join(self.manifest_path, "rhn_test_manifest.json")
            self.manifest_xml = os.path.join(self.manifest_path, "rhn_test_manifest.xml")
            self.failed_manifest_json = os.path.join(self.manifest_path, "sat5_failed_test_manifest.json")

            # Get username, password and serverUrl
            self.username, self.password = get_username_password()
            self.server_url = get_server_url()

            # Update sslCACert and serverUrl in file up2date on SAT5 Server
            result = RHNVerification().update_up2date(self.system_info, self.server_url)
            self.assertTrue(result, msg="Test Failed - Failed to set sslCACert or sslServerUrl in up2date file!")


            # Get system release version and arch
            self.current_rel_version = RHNVerification().get_os_release_version(self.system_info)
            self.current_arch = RHNVerification().get_os_base_arch(self.system_info)

            # Download and parse manifest
            RHNParseManifestXML(self.manifest_url, self.manifest_path, self.manifest_json, self.manifest_xml).parse_json_to_xml()

            # Remove non-redhat.repo
            RHNVerification().remove_non_redhat_repo(self.system_info)

            # Generate file polarion.prop for Polarion case properties to create run automatically
            #RHNVerification().write_polarion_props(self.system_info)
            RHNVerification().write_polarion_props(variant, arch, self.manifest_json)

            # Extend system reservation time
            RHNVerification().extend_reservation_time(self.system_info, self.test_level)

            # Space extend
            #RHNVerification().extend_system_space(self.system_info)
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when setup environment before RHN Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End Init ---------------")

    def testRHNEntitlement_VARIANT_ARCH(self):
        logger.info("--------------- Begin testRHNEntitlement --------------- ")

        try:
            # Register
            result = RHNVerification().register(self.system_info, self.username, self.password, self.server_url)
            self.assertTrue(result, msg="Test Failed - Failed to Register with RHN server!")

            # Get and print all testing channels
            # If 0 channel, exit
            channel_list = RHNVerification().get_channels_from_manifest(self.manifest_xml, self.current_arch, self.variant)
            self.assertNotEqual(channel_list, [], msg="Test Failed - There is no any channel.")

            if '6.5' in self.current_rel_version or "5" not in self.current_rel_version:
                result = RHNVerification().verify_channels(self.system_info, self.manifest_xml, self.username, self.password, self.current_arch, self.variant)
                self.assertTrue(result, msg="Test Failed - Failed to verify channels!")

            # Add base channel, such as rhel-x86_64-server-6
            master_release, minor_release = RHNVerification().get_release_version(self.manifest_json, "RHN")
            #base_channel = "rhel-{0}-{1}-{2}".format(self.arch, self.variant.lower(), master_release)
            if "shadow" in channel_list[0]:
                    if self.variant == "ComputeNode":
                        base_channel = "rhel-{0}-{1}-{2}-{3}".format(self.arch, "hpc-node", master_release,"shadow")
                    else:
                        base_channel = "rhel-{0}-{1}-{2}-{3}".format(self.arch, self.variant.lower(), master_release,"shadow")
            else:
                    if self.variant == "ComputeNode":
                        base_channel = "rhel-{0}-{1}-{2}".format(self.arch, "hpc-node", master_release)
                    else:
                        base_channel = "rhel-{0}-{1}-{2}".format(self.arch, self.variant.lower(), master_release)
            result = RHNVerification().add_channels(self.system_info, self.username, self.password, base_channel)
            self.assertTrue(result, msg="Test Failed - Failed to add base channel {0}!".format(base_channel))

            test_result = True
            manifestfaileddict = dict()
            manifestfaileddict = {"rhn":{"channels":{}}}
            for channel in channel_list:
                # Add test channel
                if channel != base_channel:
                    result = RHNVerification().add_channels(self.system_info, self.username, self.password, channel)
                    if not result:
                        logger.error("Test Failed - Failed to add test channel {0}".format(channel))
                        test_result &= result
                        continue
                # Installation testing
                logging.info("#############Please print test.level###############")
                logging.info(self.test_level)
                if self.test_level == "Basic":
                    # Product id certificate installation
                    test_result &= RHNVerification().smoke_installation(self.system_info, self.manifest_xml, channel, manifestfaileddict)
                elif self.test_level == "Advanced":
                    # All package installation
                    test_result &= RHNVerification().installation(self.system_info, self.manifest_xml, channel, manifestfaileddict)
                # Remove test channel
                if channel != base_channel:
                    test_result &= RHNVerification().remove_channels(self.system_info, self.username, self.password, channel)
            manifestfaileddict["compose"] = self.distro
            failed_rpm = self.manifest_path+"/manifest_failed.json"
            failedmanifest = open(failed_rpm, 'w')
            json.dump(manifestfaileddict, failedmanifest)
            failedmanifest.close()
            cmd_manifest = 'cat %s | python -m json.tool >%s ' % (failed_rpm,self.failed_manifest_json)
            result,output_repos = commands.getstatusoutput(cmd_manifest)
            logging.debug(cmd_manifest)
            logging.debug("%s" % output_repos)
            cmd_removemanifest = 'rm -rf %s' % (failed_rpm)
            commands.getstatusoutput(cmd_removemanifest)
            self.assertTrue(test_result, msg="Test Failed - Failed to do RHN Entitlement testing!")
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when do RHN Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End testRHNEntitlement --------------- ")

    def tearDown(self):
        logger.info("--------------- Begin tearDown ---------------")
        try:
            # Unregister
            RHNVerification().unregister(self.system_info)

            # Restore non-redhat.repo
            RHNVerification().restore_non_redhat_repo(self.system_info)
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when tear down after RHN Entitlement testing!")
            logger.error(traceback.format_exc())
            assert False, str(e)

        logger.info("--------------- End tearDown ---------------")


if __name__ == '__main__':
    unittest.main()