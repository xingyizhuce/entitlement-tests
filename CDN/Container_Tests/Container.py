import os
import sys
import unittest
#from ddt import ddt, file_data
import traceback
import logging
import logging.config

from Utils import system_username
from Utils import system_password
from Utils import system_ip
from CDN import test_type
from CDN import product_type
from CDN import master_release
from CDN import cdn
from CDN import arch
from CDN import candlepin
from CDN.Container_Tests import extra_repos
from CDN.Container_Tests import repos
from CDN.Container_Tests import docker_image_id
from CDN.Container_Tests import container
from CDN.Container_Tests import properties

from CDN.CDNVerification import CDNVerification as CDN
from CDN.ContainerUtils import ContainerUtils as CU

reload(sys)
sys.setdefaultencoding('utf8')

# Create logger
logger = logging.getLogger("entLogger")


def get_username_password():
    username = "entitlement_testing"
    password = "redhat"
    return username, password


def get_podman_userpass_registry(container_version):
    if container_version == "RHEL8":
        username = "entitlement_testing"
        password = "redhat"
        registry = "brewregistry.stage.redhat.io"
    else:
        username = "QualityAssurance"
        password = "VHVFhPS5TEG8dud9"
        registry = "registry.redhat.io"
    return username, password, registry


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


def get_properties(container_version):
    sku = properties[product_type][container_version][test_type][arch]["sku"]
    default_repo = properties[product_type][container_version][test_type][arch]["repo"]
    return sku, default_repo


#@ddt
class Container(unittest.TestCase):

    def setUp(self):
        # Set system ip and password
        self.system_info = {
            "ip": system_ip,
            "username": system_username,
            "password": system_password
        }

    def tearDown(self):
        CDN().unregister(self.system_info)

    #@file_data('test_data_dict.yml')
    def Container(self, container_version):
        #username = kwargs.get('username')
        #password = kwargs.get('password')
        #sku = kwargs.get('sku')
        #pid = kwargs.get('pid')

        try:
            # Config hostname and baseurl in /etc/rhsm/rhsm.conf
            hostname = get_hostname()
            baseurl = get_baseurl()
            CDN().config_testing_environment(self.system_info, hostname, baseurl)

            # Get username and password of testing account
            username, password = get_username_password()

            podman_username, podman_password, podman_registy = get_podman_userpass_registry(container_version)

            # Get sku to subscribe and default repo of container
            skus, default_repo = get_properties(container_version)
            default_repo = default_repo.split(",")
            default_repo.sort()

            # To get the extra repo to install podman on RHEL7 and RHEL-ALT host
            if product_type != "RHEL8":
                extra_repo = extra_repos[product_type][arch]

            result = CDN().register(self.system_info, username, password)
            self.assertTrue(result, msg="Test Failed - Failed to register with CDN server!")

            sku_pool_dict = CDN().get_sku_pool(self.system_info)
            self.assertNotEqual(sku_pool_dict, {}, msg="Test Failed - Failed to get subscription pool list!")

            for sku in skus.split(","):
                subscribe_result = CDN().subscribe_pool(self.system_info, sku_pool_dict[sku][0])
                self.assertTrue(subscribe_result, msg="Test Failed - Failed to subscribe sku {0}!".format(sku))

            CU().list_default_pid_host(self.system_info)
            CU().yum_repolist_host(self.system_info)

            # Install and start the podman package at the first loop
            if not CU().check_installed(self.system_info, "podman"):
                if master_release == '7':
                    CDN().enable_repo(self.system_info, extra_repo)
                    if 'qa' in baseurl or 'stage' in baseurl:
                        CDN().config_testing_environment(self.system_info, hostname, "https://cdn.redhat.com")
                        CU().refresh_rhsm(self.system_info)

                install_result = CU().install_package(self.system_info, "podman")
                self.assertTrue(install_result, msg="Test Failed - Failed to install package podman!")

                if master_release == '7':
                    CDN().disable_repo(self.system_info, extra_repo)
                    if 'qa' in baseurl or 'stage' in baseurl:
                        CDN().config_testing_environment(self.system_info, hostname, baseurl)
                        CU().refresh_rhsm(self.system_info)

            # Remove non-redhat.repo
            CDN().remove_non_redhat_repo(self.system_info)

            config_result = CU().podman_login(self.system_info, podman_username, podman_password, podman_registy)
            self.assertTrue(config_result, msg="Test Failed - Failed to config container registry!")

            image_name = CU().pull_image(self.system_info, container_version, docker_image_id)
            self.assertNotEqual(image_name, False, msg="Test Failed - Failed to pull container image!")

            podman_cname = "container_testing_{0}".format(container_version)
            create_result = CU().create_container(self.system_info, podman_cname, image_name)
            self.assertTrue(create_result, msg="Test Failed - Failed to create container!")

            # Workaround for Pre GA testing
            #if container_version == "RHEL8":
            #    CU().replace_pid_container(self.system_info, podman_cname, arch)

            CU().list_default_pid_container(self.system_info, podman_cname)

            if container_version == "RHEL8":
                result &= CU().check_ubi_repo(self.system_info, podman_cname)

            result &= CU().check_yum_repolist_all(self.system_info, podman_cname, True)

            result &= CU().check_image_deafult_repo(self.system_info, podman_cname, default_repo, container_version)

            install_repoquery = CU().install_repoquery(self.system_info, podman_cname)
            self.assertTrue(install_repoquery, msg="Test Failed - Failed to install package repoquery!")

            check_container = CU().check_container(self.system_info, podman_cname)
            self.assertTrue(check_container, msg="Test Failed - Failed to check container!")

            # Assume that always test GA repos for RHEL6 and RHEL7 Container
            if container_version == 'RHEL8':
                repo_list = repos[container_version][test_type][arch]
            else:
                repo_list = repos[container_version]['GA'][arch]

            for repo in repo_list:
                result &= CU().check_one_repo(self.system_info, podman_cname, repo)

            result &= CU().unsubscribe(self.system_info)
            result &= CU().check_yum_repolist_all(self.system_info, podman_cname, True)
            restart_result = CU().restart_container(self.system_info, podman_cname)
            result &= restart_result
            if restart_result:
                result &= CU().check_yum_repolist_all(self.system_info, podman_cname, True)

            result &= CDN().unregister(self.system_info)

            # Re-create container to check yum repolist after unregister
            podman_cname_after = "container_testing_after_{0}".format(container_version)
            create_result = CU().create_container(self.system_info, podman_cname_after, image_name)
            self.assertTrue(create_result, msg="Test Failed - Failed to create container!")
            if container_version == "RHEL8":
                result &= CU().check_ubi_repo(self.system_info, podman_cname_after)
            else:
                result &= CU().check_yum_repolist_all(self.system_info, podman_cname_after, False)
            return result
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do Container Entitlement testing!")
            logger.error(traceback.format_exc())
            raise AssertionError(e)

    def test_Container_RHEL6(self):
        # Set our logging config file
        log_path = os.path.join(os.getcwd(), "log/Container-{0}/RHEL6".format(arch))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        try:
            logger.info("--------------- Begin testing for RHEL6 Container on Host {0} {1} ---------------".format(product_type, arch))
            result = True
            container_type = container.strip().split(",")
            if "RHEL6" not in container_type:
                logger.warning("RHEL6 CONTAINER TESTING IS NOT NEEDED.")
            else:
                result = self.Container("RHEL6")
            logger.info("--------------- End testing for RHEL6 Container on Host {0} {1} ---------------".format(product_type, arch))
            self.assertTrue(result, msg="Test Failed - Failed to do Container Entitlement testing!")
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do RHEL6 Container on Host {0} {1}!".format(product_type, arch))
            logger.error(traceback.format_exc())
            raise AssertionError(e)

    def test_Container_RHEL7(self):
        # Set our logging config file
        log_path = os.path.join(os.getcwd(), "log/Container-{0}/RHEL7".format(arch))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        try:
            logger .info("--------------- Begin testing for RHEL7 Container on Host {0} {1} ---------------".format(product_type, arch))
            result = True
            container_type = container.strip().split(",")
            if "RHEL7" not in container_type:
                logger.warning("RHEL7 CONTAINER TESTING IS NOT NEEDED.")
            else:
                result = self.Container("RHEL7")
            logger.info("--------------- End testing for RHEL7 Container on Host {0} {1} ---------------".format(product_type, arch))
            self.assertTrue(result, msg="Test Failed - Failed to do Container Entitlement testing!")
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do RHEL7 Container on Host {0} {1}!".format(product_type, arch))
            logger.error(traceback.format_exc())
            raise AssertionError(e)

    def test_Container_RHEL8(self):
        # Set our logging config file
        log_path = os.path.join(os.getcwd(), "log/Container-{0}/RHEL8".format(arch))
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        logging_conf_file = "{0}/logging.conf".format(os.getcwd())
        logging.config.fileConfig(logging_conf_file, defaults={'logfilepath': log_path})

        try:
            logger.info("--------------- Begin testing for RHEL8 Container on Host {0} {1} ---------------".format(product_type, arch))
            result = True
            container_type = container.strip().split(",")
            if "RHEL8" not in container_type:
                logger.warning("RHEL8 CONTAINER TESTING IS NOT NEEDED.")
            else:
                result = self.Container("RHEL8")
            logger.info("--------------- End testing for RHEL8 Container on Host {0} {1} ---------------".format(product_type, arch))
            self.assertTrue(result, msg="Test Failed - Failed to do Container Entitlement testing!")
        except Exception, e:
            logger.error(e)
            logger.error("Test Failed - Raised error when do RHEL8 Container on Host {0} {1}!".format(product_type, arch))
            logger.error(traceback.format_exc())
            raise AssertionError(e)
