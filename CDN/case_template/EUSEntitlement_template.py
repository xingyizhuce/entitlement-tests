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
from CDN import cdn
from CDN import release_ver
from CDN import variant
from CDN import arch
from CDN import manifest_url
from CDN import candlepin
from CDN import base_repo
from CDN import default_repo
from CDN import optional_repo
from CDN import product_type

from CDN.CDNParseManifestXML import CDNParseManifestXML
from CDN.CDNVerification import CDNVerification as EUS


reload(sys)  
sys.setdefaultencoding('utf8')

pid = "PID"

# Create logger
logger = logging.getLogger("entLogger")


def get_username_password():
    with open('./CDN/json/account_info_eus.json', 'r') as f:
        account_info = json.load(f)
    if pid in account_info.keys():
        username = account_info[pid][candlepin]["username"]
        password = account_info[pid][candlepin]["password"]
        sku = account_info[pid][candlepin]["sku"]
        eus_base_sku = account_info[pid][candlepin]["eus_base_sku"]
        rhel_base_sku = account_info[pid][candlepin]["rhel_base_sku"]
        eus_base_pid = account_info[pid]["eus_base_pid"]
        rhel_base_pid = account_info[pid]["rhel_base_pid"]
        return username, password, sku, eus_base_sku, rhel_base_sku, eus_base_pid, rhel_base_pid
    else:
        raise AssertionError("Failed to get product id {0} in account_info_cdn.json.".format(pid))


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


def get_default_pid():
    with open('./CDN/json/default_pid.json', 'r') as f:
        default_pid = json.load(f)
    return default_pid[variant][product_type]["GA"][arch]


class EUSEntitlement_PID(unittest.TestCase):
    def setUp(self):
        # Set our logging config file
        log_path = os.path.join(os.getcwd(), "log/{0}".format(pid))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        logger.info("--------------- Begin Init for product {0} ---------------".format(pid))
        try:
            # Get ip, username and password of beaker testing system
            self.system_info = {
                "ip": system_ip,
                "username": system_username,
                "password": system_password
            }

            # Get testing params passed by Jenkins
            self.release_ver = release_ver
            self.variant = variant
            self.arch = arch
            self.cdn = cdn

            # Get manifest url, set json and xml manifest local path
            self.manifest_url = manifest_url
            self.manifest_path = os.path.join(os.getcwd(), "manifest")
            self.manifest_json = os.path.join(self.manifest_path, "eus_test_manifest.json")
            self.manifest_xml = os.path.join(self.manifest_path, "eus_test_manifest.xml")

            # Get pid
            self.pid = pid

            # Get platform version - the release version of the testing system
            self.platform_version = EUS().get_platform_version(master_release, minor_release)

            # Get username, password, sku, base rhel sku, base eus sku, base rhel pid, base eus pid
            username, password, sku, eus_base_sku, rhel_base_sku, eus_base_pid, rhel_base_pid = get_username_password()
            self.username = username
            self.password = password
            self.sku = sku
            self.eus_base_sku = eus_base_sku
            self.rhel_base_sku = rhel_base_sku
            self.eus_base_pid = eus_base_pid
            self.rhel_base_pid = rhel_base_pid

            # Get default pid
            self.default_pid = get_default_pid()

            self.rhel_base_repo = base_repo[master_release]["GA"][self.rhel_base_pid]
            self.default_repo = default_repo[master_release][self.rhel_base_pid]
            self.optional_repo = optional_repo[master_release][self.rhel_base_pid]

            # Config hostname and baseurl in /etc/rhsm/rhsm.conf
            self.hostname = get_hostname()
            self.baseurl = get_baseurl()
            EUS().config_testing_environment(self.system_info, self.hostname, self.baseurl)

            # Get system release version and arch
            self.current_release_ver = EUS().get_os_release_version(self.system_info)
            self.current_arch = EUS().get_os_base_arch(self.system_info)
            if self.release_ver == "":
                self.release_ver = self.current_release_ver

            # Stop rhsmcertd service. As headling(autosubscribe) operation will be run every 2 mins after start up system,
            # then every 24 hours after that, which will influence our subscribe test.
            result = EUS().stop_rhsmcertd(self.system_info)
            self.assertTrue(result, msg="Test Failed - Failed to stop service rhsmcertd!")

            # Synchronize system time with clock.redhat.com, it's a workaround when system time is not correct,
            # commands "yum repolist" and "subscription-manager repos --list" return nothing
            EUS().ntpdate_redhat_clock(self.system_info)

            # Download and parse manifest
            CDNParseManifestXML(self.manifest_url, self.manifest_path, self.manifest_json, self.manifest_xml).parse_json_to_xml()

            # Install needed packages
            EUS().install_packages(self.system_info)

            # Remove non-redhat.repo
            EUS().remove_non_redhat_repo(self.system_info)
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when setup environment before CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End Init for product {0} ---------------".format(pid))

    def testEUSEntitlement_VARIANT_ARCH_PID(self):
        logger.info("--------------- Begin testEUSEntitlement for product {0} ---------------".format(pid))
        test_result = True
        try:
            # Register
            result = EUS().register(self.system_info, self.username, self.password)
            self.assertTrue(result, msg="Test Failed - Failed to register with CDN server!")

            # Get subscription list
            sku_pool_dict = EUS().get_sku_pool(self.system_info)
            self.assertNotEqual(sku_pool_dict, {}, msg="Test Failed - Failed to get subscription pool list!")
            logger.info("Subscription pool list:")
            EUS().print_list(sku_pool_dict)
            # sku_pool_dict:
            # {
            # 'MCT3115': ['8a99f984508e9fbf01509432f2e9054c'],
            # 'RH0103708': ['8a99f9865154360c015156e8a8250f6e', '8a99f9865154360c015156e8a7c20f57'],
            # 'RH00284': ['8a99f984508e9fbf01509432f3b80561']
            # }

            # Try to subscribe base product, and then check the sku, pid and arches got from manifest are included in the entitlement cert
            if self.rhel_base_sku in sku_pool_dict.keys():
                result = EUS().subscribe_pool(self.system_info, sku_pool_dict[self.rhel_base_sku][0])
                self.assertTrue(result, msg="Test Failed - Failed to subscribe with base sku {0}!".format(self.rhel_base_sku))

                ent_cert = EUS().get_certificate(self.system_info, self.rhel_base_sku)
                if ent_cert != "":
                    result &= EUS().verify_pid_in_ent_cert(self.system_info, ent_cert, self.rhel_base_pid)
                    result &= EUS().verify_sku_in_ent_cert(self.system_info, ent_cert, self.rhel_base_sku)
                else:
                    test_result = False
                    logger.error("Test Failed - Failed to generate entitlement certificate after subscribe base sku {0}".format(self.rhel_base_sku))
            else:
                raise AssertionError("No suitable subscription for base rhel sku  {0}".format(self.rhel_base_sku))
                    
            # Try to subscribe eus base product, and then check the sku, pid and arches got from manifest are included in the entitlement cert
            if self.rhel_base_sku != self.eus_base_sku:
                if self.eus_base_sku in sku_pool_dict.keys():
                    result = EUS().subscribe_pool(self.system_info, sku_pool_dict[self.eus_base_sku][0])
                    self.assertTrue(result, msg="Test Failed - Failed to subscribe with base sku {0}!".format(self.eus_base_sku))

                    ent_cert = EUS().get_certificate(self.system_info, self.eus_base_sku)
                    if ent_cert != "":
                        result &= EUS().verify_pid_in_ent_cert(self.system_info, ent_cert, self.eus_base_pid)
                        result &= EUS().verify_sku_in_ent_cert(self.system_info, ent_cert, self.eus_base_sku)
                        if self.sku == self.eus_base_sku:
                            result &= EUS().verify_pid_in_ent_cert(self.system_info, ent_cert, self.pid)
                            result &= EUS().verify_sku_in_ent_cert(self.system_info, ent_cert, self.sku)
                            result &= EUS().verify_arch_in_ent_cert(self.system_info, ent_cert, self.manifest_xml, self.pid, self.current_release_ver)
                    else:
                        test_result = False
                        logger.error("Test Failed - Failed to generate entitlement certificate after subscribe eus base sku {0}".format(self.eus_base_sku))
                else:
                    raise AssertionError("No suitable subscription for eus base sku {0}".format(self.eus_base_sku))

            # Try to subscribe layered product, and then check the sku, pid and arches got from manifest are included in the entitlement cert
            if self.sku != self.eus_base_sku:
                if self.sku in sku_pool_dict.keys():
                    result = EUS().subscribe_pool(self.system_info, sku_pool_dict[self.sku][0])
                    self.assertTrue(result, msg="Test Failed - Failed to subscribe with sku {0}!".format(self.sku))

                    ent_cert = EUS().get_certificate(self.system_info, self.sku)
                    if ent_cert != "":
                        result &= EUS().verify_pid_in_ent_cert(self.system_info, ent_cert, self.pid)
                        result &= EUS().verify_sku_in_ent_cert(self.system_info, ent_cert, self.sku)
                        result &= EUS().verify_arch_in_ent_cert(self.system_info, ent_cert, self.manifest_xml, self.pid, self.current_release_ver)
                    else:
                        test_result = False
                        logger.error("Test Failed - Failed to generate entitlement certificate after subscribe sku {0}".format(self.sku))
                else:
                    raise AssertionError("No suitable subscription for sku {0}".format(self.sku))

            # Backup /etc/yum.repos.d/redhat.repo, and archive it in Jenkins job
            EUS().redhat_repo_backup(self.system_info)

            # Set system release
            releasever_set = ""
            if self.release_ver != self.current_release_ver:
                releasever_set = EUS().set_release(self.system_info, self.release_ver, self.manifest_json, master_release)
                self.assertNotEqual(releasever_set, False, msg="Test Failed - Failed to set system release!")

            # Clear yum cache
            test_result &= EUS().clean_yum_cache(self.system_info, releasever_set)

            # Test the default enabled repo
            test_enabled_repo = EUS().test_default_enable_repo(self.system_info, self.default_repo, master_release)
            test_result &= test_enabled_repo
            if not test_enabled_repo:
                EUS().disable_all_repo(self.system_info)
                result = EUS().enable_repo(self.system_info, self.default_repo)
                self.assertTrue(result, msg="Test Failed - Failed to enable rhel default repo!")

            # Enable ga optional repo, such as rhel-7-server-optional-rpms, as beta packages also rely optional repo
            result = EUS().enable_repo(self.system_info, self.optional_repo)
            self.assertTrue(result, msg="Test Failed - Failed to enable rhel optional repo!")

            # Get and print repo list from package manifest
            # If 0 repo, exit
            repo_list = EUS().get_repo_list_from_manifest(self.manifest_xml, self.pid, self.current_arch, self.release_ver)
            self.assertNotEqual(repo_list, [], msg="Test Failed - There is no any repository for pid {0} in release {1}.".format(self.pid, self.release_ver))

            # Enable all test repos listed in manifest to ensure the repo correctness
            test_result &= EUS().test_repos(self.system_info, repo_list, releasever_set, self.release_ver, self.current_arch)

            for repo in repo_list:
                # Enable the test repo
                result = EUS().enable_repo(self.system_info, repo)
                if not result:
                    logger.error("Test Failed - Failed to enable test repo {0}".format(repo))
                    test_result &= result

                # Product id certificate installation
                test_result &= EUS().package_smoke_installation(self.system_info, repo, releasever_set, self.manifest_xml, self.pid, self.rhel_base_pid, self.default_pid, self.current_arch, self.release_ver, self.platform_version, master_release)

                # Disable the test repo, but keep the default repo, the base repo and the optional repo enabled.
                if repo not in [self.optional_repo, self.default_repo, self.rhel_base_repo]:
                    test_result &= EUS().disable_repo(self.system_info, repo)

            self.assertTrue(test_result, msg="Test Failed - Failed to do CDN Entitlement testing!")
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End testEUSEntitlement for product {0} ---------------".format(pid))

    def tearDown(self):
        logger.info("--------------- Begin tearDown for product {0} ---------------".format(pid))

        try:
            # Unregister
            EUS().unregister(self.system_info)

            # Restore non-redhat.repo
            #EUS().restore_non_redhat_repo(self.system_info)
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when tear down after CDN Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

        logger.info("--------------- End tearDown for product {0} ---------------".format(pid))


if __name__ == '__main__':
    unittest.main()
