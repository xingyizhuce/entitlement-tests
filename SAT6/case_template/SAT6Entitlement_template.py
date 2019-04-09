import os
import sys
import json
import unittest
import traceback
import logging
import logging.config

from Utils import system_username
from Utils import system_password
from Utils import system_ip
from CDN import master_release
from CDN import minor_release
from CDN import cdn ## It indicates what CDN the SAT6 content is sync'ed from

from CDN import release_ver
from CDN import product_type
from CDN import test_type
from CDN import variant
from CDN import arch
from CDN import manifest_url
from CDN import candlepin ## It indicates what Candlepin the SAT6 manifest is downloaded from
from CDN import base_repo
from CDN import default_repo
from CDN import optional_repo

from SAT6 import sat6_server_hostname
from SAT6 import sat6_server_ip
from SAT6 import sat6_server_username
from SAT6 import sat6_server_password
from SAT6 import sat6_server_orglabel

from CDN.CDNParseManifestXML import CDNParseManifestXML
from CDN.CDNVerification import CDNVerification as CDN

from Utils.RemoteSSH import RemoteSSH

reload(sys)  
sys.setdefaultencoding('utf8')

pid = "PID"

# Create logger
logger = logging.getLogger("entLogger")


def get_account_info():
    with open('./CDN/json/account_info_cdn.json', 'r') as f:
        account_info = json.load(f)

    if pid in account_info[master_release].keys():
        """
        ## Below is not applicable for SAT6
        username = account_info[master_release][pid][candlepin]["username"]
        password = account_info[master_release][pid][candlepin]["password"]
        """
        
        # Get the username and password and orglable of SAT6 server
        username = sat6_server_username
        password = sat6_server_password
        orglabel = sat6_server_orglabel
        
        sku = account_info[master_release][pid][candlepin]["sku"]
        base_sku = account_info[master_release][pid][candlepin]["base_sku"]
        base_pid = account_info[master_release][pid]["base_pid"]
        return username, password, orglabel, sku, base_sku, base_pid
    else:
        raise AssertionError("Failed to get product id {0} in account_info_cdn.json.".format(pid))

"""
## Below is not applicable for SAT6
def get_hostname():
    if candlepin == "Stage":
        return "subscription.rhsm.stage.redhat.com"
    return "subscription.rhsm.redhat.com"


def get_baseurl():
    if cdn == "QA":
        baseurl = "https://cdn.qa.redhat.com"
    elif cdn == "Stage":
        baseurl = "https://cdn.stage.redhat.com"
    else:
        baseurl = "https://cdn.redhat.com"
    return baseurl
"""

def get_default_pid():
    with open('./CDN/json/default_pid.json', 'r') as f:
        default_pid = json.load(f)
    return default_pid[variant][product_type][test_type][arch]

def _config_sat6_testing_environment():
    # Get ip, username and password of beaker testing system
    system_info = {
        "ip": system_ip,
        "username": system_username,
        "password": system_password
    }

    # Back up the rhsm.conf
    cmd = "cp /etc/rhsm/rhsm.conf /etc/rhsm/rhsm-cp.conf"
    RemoteSSH().run_cmd(system_info, cmd, "Trying to back up the config file /etc/rhsm/rhsm.conf")

    # If needed, add SAT6 server hostname analysis in /etc/hosts file, e.g.: 10.8.243.120 sat62-server.redhat.com
    if sat6_server_ip != "":
        cmd = "echo '{0} {1}' >> /etc/hosts".format(sat6_server_ip, sat6_server_hostname)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to add satellite 6 server ip and hostname info into '/etc/hosts'")

    # Install SAT6 rpm cert package
    cmd = "yum localinstall -y http://{0}/pub/katello-ca-consumer-latest.noarch.rpm".format(sat6_server_hostname)
    RemoteSSH().run_cmd(system_info, cmd, "Trying to install satellite 6 rpm cert package")

def _register_sat6(system_info, username, password, orglabel):
    # Register with SAT6 server
    cmd = "subscription-manager register --username={0} --password='{1}' --org={2}".format(username, password, orglabel)

    if CDN().check_registered(system_info):
        logger.info("The system is already registered, need to unregister first!")
        if not CDN().unregister(system_info):
            logger.info("Failed to unregister, try to use '--force'!")
            cmd += " --force"

    ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to register with sat 6 server...")
    if ret == 0:
        logger.info("It's successful to register.")
        return True
    else:
        logger.error("Test Failed - Failed to register.")
        return False

class CDNEntitlement_PID(unittest.TestCase):
    def setUp(self):
        # Set our logging config file
        log_path = os.path.join(os.getcwd(), "log/{0}".format(pid))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        """
        #logger = logging.getLogger()
        #logger.setLevel(logging.DEBUG)
        self.file_handler_debug, self.file_handler_info, self.file_handler_error, self.console_handler = CDN().log_setting(variant, arch, cdn, pid)
        logger.addHandler(self.file_handler_debug)
        logger.addHandler(self.file_handler_info)
        logger.addHandler(self.file_handler_error)
        logger.addHandler(self.console_handler)
        """
        logger.info("--------------- Begin Init for product {0} ---------------".format(pid))
        try:
            # Get ip, username and password of beaker testing system
            self.system_info = {
                "ip": system_ip,
                "username": system_username,
                "password": system_password
            }

            # Get default pid
            self.default_pid = get_default_pid()

            # Get testing params passed by Jenkins
            self.release_ver = release_ver
            self.cdn = cdn

            # Get manifest url, set json and xml manifest local path
            self.manifest_url = manifest_url
            self.manifest_path = os.path.join(os.getcwd(), "manifest")
            self.manifest_json = os.path.join(self.manifest_path, "cdn_test_manifest.json")
            self.manifest_xml = os.path.join(self.manifest_path, "cdn_test_manifest.xml")

            # Get pid under testing
            self.pid = pid

            # Get base pid, sku, base sku, username, password
            #for k, v in get_username_password().items():
            #    setattr(self, k, v)
            username, password, orglabel, sku, base_sku, base_pid = get_account_info()
            self.sku = sku
            self.base_sku = base_sku
            self.base_pid = base_pid
            self.username = username
            self.password = password
            self.orglabel = orglabel

            """
            ## Below is not applicable for SAT6
            # Config hostname and baseurl in /etc/rhsm/rhsm.conf
            self.hostname = get_hostname()
            self.baseurl = get_baseurl()
            CDN().config_testing_environment(self.system_info, self.hostname, self.baseurl)
            """

            # Config SAT6 testing env
            _config_sat6_testing_environment()

            # Install needed packages
            CDN().install_packages(self.system_info)

            # Get system release version and arch
            if master_release == "8":
                self.current_release_ver = CDN().get_os_release_version_by_dnf(self.system_info)
                self.current_arch = CDN().get_os_base_arch_by_dnf(self.system_info)                
            else:
                self.current_release_ver = CDN().get_os_release_version(self.system_info)
                self.current_arch = CDN().get_os_base_arch(self.system_info)
            if self.release_ver == "":
                self.release_ver = self.current_release_ver

            rhel_8_addon_ids = ["487", "488", "230", "489", "233", "232"] # These ids are different with others, different arches have
            # the same id, so list them here to handle specially.
            if self.pid in rhel_8_addon_ids:
                # Get default enabled repo
                self.default_repo = default_repo[master_release][self.pid][self.current_arch]
                # Get base repo of product
                self.base_repo = base_repo[master_release][test_type][self.pid][self.current_arch]
            else:
                # Get default enabled repo
                self.default_repo = default_repo[master_release][self.base_pid]
                # Get base repo of product
                self.base_repo = base_repo[master_release][test_type][self.base_pid]

            if master_release != "8":
                # Get optional repo of RHEL
                self.optional_repo = optional_repo[master_release][self.base_pid]

            # Get platform version - the release version of the testing system
            self.platform_version = CDN().get_platform_version(master_release, minor_release, test_type)

            # Stop rhsmcertd service. As headling(autosubscribe) operation will be run every 2 mins after start up system,
            # then every 24 hours after that, which will influence our subscribe test.
            result = CDN().stop_rhsmcertd(self.system_info)
            self.assertTrue(result, msg="Test Failed - Failed to stop service rhsmcertd!")

            # Synchronize system time with clock.redhat.com, it's a workaround when system time is not correct,
            # commands "yum repolist" and "subscription-manager repos --list" return nothing
            if master_release == "8":
                CDN().sync_system_time_by_chrony(self.system_info)
            else:
                CDN().ntpdate_redhat_clock(self.system_info)

            # Download and parse manifest
            CDNParseManifestXML(self.manifest_url, self.manifest_path, self.manifest_json, self.manifest_xml).parse_json_to_xml()

            # Remove non-redhat.repo
            CDN().remove_non_redhat_repo(self.system_info)

            # Space extend
            # CDN().extend_system_space(self.system_info, self.manifest_json, master_release)
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when setup environment before CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End Init for product {0} ---------------".format(pid))

    def testCDNEntitlement_VARIANT_ARCH_PID(self):
        logger.info("--------------- Begin testCDNEntitlement for product {0} ---------------".format(pid))
        test_result = True
        try:
            # Check default product cert under /etc/pki/product-default before any testing operation
            test_result &= CDN().check_default_pid_cert(self.system_info, self.manifest_xml, self.default_pid, self.current_arch, self.platform_version)

            # Register
            result = _register_sat6(self.system_info, self.username, self.password, self.orglabel)
            self.assertTrue(result, msg="Test Failed - Failed to register with SAT 6 server!")

            # Get subscription list
            if self.current_arch == 'i386' and self.pid in ["92", "94", "132", "146"]:
                # Products SF, SAP, HPN are not supported on i386, and keep them pass currently.
                logger.info("Product {0} could not be supported on arch i386.".format(self.pid))
                return
            else:
                sku_pool_dict = CDN().get_sku_pool(self.system_info)
                self.assertNotEqual(sku_pool_dict, {}, msg="Test Failed - Failed to get subscription pool list!")
                logger.info("Subscription pool list:")
                CDN().print_list(sku_pool_dict)

            # Eg. sku_pool_dict:
            # {
            # 'MCT3115': ['8a99f984508e9fbf01509432f2e9054c'],
            # 'RH0103708': ['8a99f9865154360c015156e8a8250f6e', '8a99f9865154360c015156e8a7c20f57'],
            # 'RH00284': ['8a99f984508e9fbf01509432f3b80561']
            # }

            # Subscribe base sku firstly, and then subscribe layered sku
            # Trying to subscribe base product, and then check the sku, pid and arches got from manifest are included in the entitlement cert
            if self.base_sku in sku_pool_dict.keys():
                result = CDN().subscribe_pool(self.system_info, sku_pool_dict[self.base_sku][0])
                self.assertTrue(result, msg="Test Failed - Failed to subscribe with base sku {0}!".format(self.base_sku))
                
                ent_cert = CDN().get_certificate(self.system_info, self.base_sku)
                if ent_cert != "":
                    result &= CDN().verify_pid_in_ent_cert(self.system_info, ent_cert, self.base_pid)
                    result &= CDN().verify_sku_in_ent_cert(self.system_info, ent_cert, self.base_sku)
                    result &= CDN().verify_arch_in_ent_cert(self.system_info, ent_cert, self.manifest_xml, 
                                self.base_pid, self.current_release_ver)
                else:
                    test_result = False
                    logger.error("Test Failed - Failed to get entitlement certificate after subscribe base sku {0}.".format(self.base_sku))
            else:
                raise AssertionError("No suitable subscription for base sku {0}.".format(self.base_sku))

            # Trying to subscribe layered product, and then check the sku, pid and arches got from manifest are included in the entitlement cert
            if self.base_sku != self.sku:
                if self.sku in sku_pool_dict.keys():
                    result = CDN().subscribe_pool(self.system_info, sku_pool_dict[self.sku][0])
                    self.assertTrue(result, msg="Test Failed - Failed to subscribe with base sku {0}!".format(self.sku))
                
                    ent_cert = CDN().get_certificate(self.system_info, self.sku)
                    if ent_cert != "":
                        result &= CDN().verify_pid_in_ent_cert(self.system_info, ent_cert, self.pid)
                        result &= CDN().verify_sku_in_ent_cert(self.system_info, ent_cert, self.sku)
                        result &= CDN().verify_arch_in_ent_cert(self.system_info, ent_cert, self.manifest_xml, self.pid, self.current_release_ver)
                    else:
                        test_result = False
                        logger.error(
                            "Test Failed - Failed to get entitlement certificate after subscribe layered sku {0}.".format(self.sku))
                else:
                    raise AssertionError("No suitable subscription for layered sku {0}".format(self.sku))


            # Backup /etc/yum.repos.d/redhat.repo, and archive it in Jenkins job
            CDN().redhat_repo_backup(self.system_info)

            """
            ## Below get_release_list testing is not applicable for SAT6
            # Get release list with rhsm command
            test_result &= CDN().get_release_list(self.system_info)
            """

            # Set system release
            releasever_set = ""
            if test_type == "GA":
                # Set option --releasever for yum/repoquery command
                if self.release_ver != self.current_release_ver:
                    releasever_set = CDN().set_release(self.system_info, self.release_ver, self.manifest_json, master_release)
                    self.assertNotEqual(releasever_set, False, msg="Test Failed - Failed to set system release!")
            
            # Clear yum cache
            test_result &= CDN().clean_yum_cache(self.system_info, releasever_set)

            # Test the default enabled repo
            test_enabled_repo = CDN().test_default_enable_repo(self.system_info, self.default_repo, master_release)
            test_result &= test_enabled_repo
            if not test_enabled_repo:
                CDN().disable_all_repo(self.system_info)
                if master_release == "8":
                    default_repo_1 = self.default_repo.split(',')[0].strip()
                    default_repo_2 = self.default_repo.split(',')[1].strip()
                
                    result = CDN().enable_repo(self.system_info, default_repo_1)
                    self.assertTrue(result, msg="Test Failed - Failed to enable default repo: {0}".format(default_repo_1))

                    result = CDN().enable_repo(self.system_info, default_repo_2)
                    self.assertTrue(result, msg="Test Failed - Failed to enable default repo: {0}".format(default_repo_2))
                else:
                    result = CDN().enable_repo(self.system_info, self.default_repo)
                    self.assertTrue(result, msg="Test Failed - Failed to enable default repo!")

            # Get and print repo list from package manifest
            # If 0 repo, exit
            repo_list = CDN().get_repo_list_from_manifest(self.manifest_xml, self.pid, self.current_arch, self.release_ver)
            self.assertNotEqual(repo_list, [], msg="Test Failed - There is no any repository for pid {0} in release {1}.".format(self.pid, self.release_ver))

            # Make sure all test repos listed in manifest can be retrieved successfully
            test_result &= CDN().test_repos(self.system_info, repo_list, releasever_set, self.release_ver, self.current_arch)

            """
            ## Below testing is not applicable for SAT6
            # Change gpgkey for all test repos for rhel snapshot testing against QA CDN
            if test_type == 'GA' and self.cdn == "QA":
                # NOTICE: it's very dangerous if it's tested on Prod CDN, so add option self.cdn == "QA"
                test_result &= CDN().change_gpgkey(self.system_info, repo_list)
            """

            # Need enable GA and Beta base repo for RHEL Beta. RCM pushes only Beta rpms to Beta repos, rpms from previous release remains only in GA repository.
            if master_release == "7":
                if test_type == "Beta":
                    result = CDN().enable_repo(self.system_info, self.base_repo)
                    self.assertTrue(result, msg="Test Failed - Failed to enable beta base repo!")

                # Enable ga optional repo(eg. rhel-7-server-optional-rpms) for GA testing, as some packages rely optional repo
                # For now, optional repo is not enabled for Beta testing, will add it if needed.
                if test_type == "GA":
                    result = CDN().enable_repo(self.system_info, self.optional_repo)
                    self.assertTrue(result, msg="Test Failed - Failed to enable GA optional repo!")

            # Now the enabled repos are like:
            # RHEL 7 Server x86_64 Beta: rhel-7-server-beta-rpms, rhel-7-server-rpms
            # RHEL 7 Server x86_64 GA: rhel-7-server-rpms, rhel-7-server-optional-rpms
            # RHEL 8 x86_64 Beta: rhel-8-for-x86_64-baseos-beta-rpms,rhel-8-for-x86_64-appstream-beta-rpms
            # RHEL 8 x86_64 GA: rhel-8-for-x86_64-baseos-rpms,rhel-8-for-x86_64-appstream-rpms

            for repo in repo_list:
                # Enable the test repo
                result = CDN().enable_repo(self.system_info, repo)
                if not result:
                    logger.error("Test Failed - Failed to enable test repo {0}".format(repo))
                    test_result &= result
                    continue

                # Product id certificate installation
                test_result &= CDN().package_smoke_installation(self.system_info, repo, releasever_set, self.manifest_xml, self.pid, self.base_pid, self.default_pid, self.current_arch, self.release_ver, self.platform_version, master_release)

                # Disable the test repo, but keep the default repo, the base repo and the optional repo enabled.
                if master_release == "8":
                    if repo not in [self.default_repo, self.base_repo]:
                        test_result &= CDN().disable_repo(self.system_info, repo)
                else:
                    if repo not in [self.optional_repo, self.default_repo, self.base_repo]:
                        test_result &= CDN().disable_repo(self.system_info, repo)

            self.assertTrue(test_result, msg="Test Failed - Failed to do CDN Entitlement testing!")
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End testCDNEntitlement for product {0} ---------------".format(pid))

    def tearDown(self):
        logger.info("--------------- Begin tearDown for product {0} ---------------".format(pid))

        try:
            # Unregister
            CDN().unregister(self.system_info)

            # Restore non-redhat.repo
            #CDN().restore_non_redhat_repo(self.system_info)
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when tear down after CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End tearDown for product {0} ---------------".format(pid))

        """
        # Remove log handlers from current logger
        logger.removeHandler(self.file_handler_debug)
        logger.removeHandler(self.file_handler_info)
        logger.removeHandler(self.file_handler_error)
        logger.removeHandler(self.console_handler)
        """

if __name__ == '__main__':
    unittest.main()
