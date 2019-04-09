import os
import sys
import unittest
import traceback
import logging
import logging.config

from Utils import system_username
from Utils import system_password
from Utils import system_ip
from CDN import test_type
from CDN import product_type
from CDN import master_release
from CDN import arch
from CDN.Container_Tests import repos
from CDN.Container_Tests import docker_image_id
from CDN.Container_Tests import container
from CDN.Container_Tests import properties
from CDN.Container_Tests import sat6_server_hostname
from CDN.Container_Tests import sat6_server_ip
from CDN.Container_Tests import sat6_server_username
from CDN.Container_Tests import sat6_server_password
from CDN.Container_Tests import sat6_server_orglabel


from CDN.CDNVerification import CDNVerification as CDN
from CDN.ContainerUtils import ContainerUtils as CU

from Utils.RemoteSSH import RemoteSSH

reload(sys)
sys.setdefaultencoding('utf8')

# Create logger
logger = logging.getLogger("entLogger")


def get_username_password():
    username = "entitlement_testing"
    password = "redhat"
    return username, password


def get_properties(container_version):
    sku = properties[product_type][container_version][test_type][arch]["sku"]
    default_repo = properties[product_type][container_version][test_type][arch]["repo"]
    return sku, default_repo


def register_sat6(system_info, username, password, orglabel):
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


class Container(unittest.TestCase):

    def __config_sat6_testing_environment(self, system_info):
        # Back up the rhsm.conf
        cmd = "cp /etc/rhsm/rhsm.conf /etc/rhsm/rhsm-cp.conf"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to back up the config file /etc/rhsm/rhsm.conf")

        # If needed, add SAT6 server hostname analysis in /etc/hosts file, e.g.: 10.8.243.120 sat62-server.redhat.com
        if sat6_server_ip != "":
            cmd = "echo '{0} {1}' >> /etc/hosts".format(sat6_server_ip, sat6_server_hostname)
            RemoteSSH().run_cmd(system_info, cmd,
                                "Trying to add satellite 6 server ip and hostname info into '/etc/hosts'")

        # Install SAT6 rpm cert package
        cmd = "yum localinstall -y http://{0}/pub/katello-ca-consumer-latest.noarch.rpm".format(sat6_server_hostname)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to install satellite 6 rpm cert package")

    def __remove_katello_ca_consumer(self, system_info):
        cmd = "yum remove -y `rpm -qa | grep katello-ca-consumer`"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to install satellite 6 rpm cert package")

    def setUp(self):
        # Set system ip and password
        self.system_info = {
            "ip": system_ip,
            "username": system_username,
            "password": system_password
        }

        # Get username and password of testing account
        self.username = sat6_server_username
        self.password = sat6_server_password
        self.orglabel = sat6_server_orglabel

    def tearDown(self):
        CDN().unregister(self.system_info)
        CDN().restore_non_redhat_repo(self.system_info)
        self.__remove_katello_ca_consumer(self.system_info)

    def Container(self, container_version):
        try:
            # Install needed packages
            CDN().install_packages(self.system_info)

            # Config SAT6 testing env
            self.__config_sat6_testing_environment(self.system_info)

            # Remove non-redhat.repo
            CDN().remove_non_redhat_repo(self.system_info)

            # Get sku to subscribe and default repo of container
            skus, default_repo = get_properties(container_version)
            default_repo = default_repo.split(",")
            default_repo.sort()

            # Register
            result = register_sat6(self.system_info, self.username, self.password, self.orglabel)
            self.assertTrue(result, msg="Test Failed - Failed to register with SAT 6 server!")

            sku_pool_dict = CDN().get_sku_pool(self.system_info)
            self.assertNotEqual(sku_pool_dict, {}, msg="Test Failed - Failed to get subscription pool list!")

            for sku in skus.split(","):
                subscribe_result = CDN().subscribe_pool(self.system_info, sku_pool_dict[sku][0])
                self.assertTrue(subscribe_result, msg="Test Failed - Failed to subscribe sku {0}!".format(sku))

            CU().list_default_pid_host(self.system_info)
            CU().yum_repolist_host(self.system_info)

            # Install and start the podman package at the first loop
            # Think about how to install podman on RHEL7
            if not CU().check_installed(self.system_info, "podman"):
                install_result = CU().install_package(self.system_info, "podman")
                self.assertTrue(install_result, msg="Test Failed - Failed to install package podman!")

            # Remove non-redhat.repo
            CDN().remove_non_redhat_repo(self.system_info)

            config_result = CU().config_podman_registry(self.system_info)
            self.assertTrue(config_result, msg="Test Failed - Failed to config container registry!")

            image_name = CU().pull_image(self.system_info, container_version, docker_image_id)
            self.assertNotEqual(image_name, False, msg="Test Failed - Failed to pull container image!")

            podman_cname = "container_testing_name"
            create_result = CU().create_container(self.system_info, podman_cname, image_name)
            self.assertTrue(create_result, msg="Test Failed - Failed to create container!")

            CU().list_default_pid_container(self.system_info, podman_cname)

            result &= CU().check_yum_repolist_all(self.system_info, podman_cname, True)

            result &= CU().check_image_deafult_repo(self.system_info, podman_cname, default_repo)

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
                result &= CU().check_yum_repolist_all(self.system_info, podman_cname, False)

            result &= CDN().unregister(self.system_info)
            result &= CU().check_yum_repolist_all(self.system_info, podman_cname, False)
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
