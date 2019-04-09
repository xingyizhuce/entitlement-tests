import random
import logging

from Utils.RemoteSSH import RemoteSSH

# Create logger
logger = logging.getLogger("entLogger")


class ContainerUtils(object):
    def yum_repolist_host(self, system_info):
        cmd = "yum repolist"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to yum clean all for RHEL8 container...")

    def list_default_pid_host(self, system_info):
        cmd = "ls /etc/pki/product-default/"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to get default pid on host...")

    def list_default_pid_container(self, system_info, podman_cname):
        cmd = "podman exec {0} ls /etc/pki/product-default/".format(podman_cname)
        RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to get default pid in container...")

    def refresh_rhsm(self, system_info):
        for i in range(0, 5):
            ret, output = RemoteSSH().run_cmd(system_info, "subscription-manager refresh", "Trying to refresh rhsm.")
            if ret == 0:
                break
        # clean all yum old cache repos
        RemoteSSH().run_cmd(system_info, "yum clean all", "Trying to clean old cache repos.")

    def check_installed(self, system_info, package_name):
        cmd = "rpm -q {0}".format(package_name)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to install package".format(package_name))
        if "not installed" in output:
            return False
        else:
            return True

    def check_installed(self, system_info, package_name):
        cmd = "rpm -q {0}".format(package_name)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to install package".format(package_name))
        if "not installed" in output:
            return False
        else:
            return True

    def install_package(self, system_info, package_name):
        logger.info("--------------- Begin to install {0} on host ---------------".format(package_name))
        result = True
        installed = self.check_installed(system_info, package_name)
        if not installed:
            cmd = "yum install -y {0}".format(package_name)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to install package".format(package_name))
            if ret == 0:
                logger.info("It's successful to install package {0}".format(package_name))
            else:
                logger.error("Failed to install package {0}".format(package_name))
                result = False
        else:
            logger.info("Package {0} has been installed.".format(package_name))
        logger.info("--------------- End to install {0} on host ---------------".format(package_name))
        return result

    def config_podman_registry(self, system_info):
        logger.info("--------------- Begin to config podman on host ---------------")
        result = True

        # Config the docker register for RHEL8 images
        # No need to update the registry for RHEL7 images
        cmd = '''sed -i "/^\[registries.search\]$/{n;s/^registries = .*$/registries = ['registry.access.redhat.com','registry.stage.redhat.io']/}" /etc/containers/registries.conf'''
        RemoteSSH().run_cmd(system_info, cmd, "Trying to config registries.search domain in registries file...")
        cmd = '''sed -i "/^\[registries.insecure\]$/{n;s/^registries = .*$/registries = ['brewregistry.stage.redhat.io']/}" /etc/containers/registries.conf'''
        RemoteSSH().run_cmd(system_info, cmd, "Trying to config registries.insecure domain in registries file...")

        cmd = "cat /etc/containers/registries.conf"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check podman config file /etc/containers/registries.conf....")
        #if "brew-pulp-docker01" in output and "registry.access." in output and "brewregistry.stage." and "registry.stage." in output:
        if "brewregistry.stage." in output:
            logger.info("It's successful to config podman registry!")
        else:
            logger.error("Failed to config podman registry!")
            result = False
        logger.info("--------------- End to config podman on host ---------------")
        return result

    def podman_login(self, system_info, username, password, registry):
        logger.info("--------------- Begin to login into the registries with 'podman login' ---------------")
        result = False
        cmd = "podman login {0} --username={1} --password={2}".format(registry, username, password)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Login to the registries  with podman command")
        if ret == 0 and "Login Succeeded" in output:
            result = True
        return result

    def pull_image(self, system_info, image, podman_image_id):
        logger.info("--------------- Begin to pull container image ---------------")
        if image == "RHEL6":
            image_name = "registry.redhat.io/rhel6"
            #image_name = "registry.access.redhat.com/rhel6"
        elif image == "RHEL7":
            image_name = "registry.redhat.io/rhel7"
            #image_name = "registry.access.redhat.com/rhel7"
        else:
            #image_name = "brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888/rhel8:{0}".format(podman_image_id)
            image_name = "brewregistry.stage.redhat.io/ubi8:{0}".format(podman_image_id)

        cmd = "podman pull {0}".format(image_name)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to pull container image...")
        if ret == 0:
            logger.info("It's successful to pull {0} container image!".format(image))
        else:
            logger.error("Failed to pull {0} container image!".format(image))
            image_name = False
        logger.info("--------------- End to pull podman image ---------------")
        return image_name

    def create_container(self, system_info, podman_cname, image_name):
        logger.info("--------------- Begin to create container ---------------")
        result = True
        create_cmd = "podman create -t --name {0} {1} ".format(podman_cname, image_name)
        ret1, output = RemoteSSH().run_cmd(system_info, create_cmd, "Trying to to create container used for testing...")
        if "already in use" in output:
            # Temporally comment below code since the pre-GA testing needs to
            # manually update the rhel 8 snaphsot container HTB product cert with GA product cert
            delete_cmd = "podman stop {0}; podman rm -f {0}".format(podman_cname)
            RemoteSSH().run_cmd(system_info, delete_cmd, "Trying to to remove container that is already in use...")
            ret1, output = RemoteSSH().run_cmd(system_info, create_cmd, "Trying to to create container used for testing...")

        start_cmd = "podman start {0}".format(podman_cname)
        ret2, output = RemoteSSH().run_cmd(system_info, start_cmd, "Trying to to start container used for testing...")
        if ret1 == 0 and ret2 == 0:
            logger.info("It's successful to create and start container.")
        else:
            result = False
            logger.error("Test Failed - Failed to create and start containers.")
        logger.info("--------------- End to create and start container ---------------")
        return result

    def replace_pid_container(self, system_info, podman_cname, arch):
        # Replace default pid on RHEL8 Container
        if arch == "x86_64":
            cmd = "podman exec {0} bash -c 'rm -rf /etc/pki/product-default/*; curl http://git.app.eng.bos.redhat.com/git/rcm/rcm-metadata.git/plain/product_ids/rhel-8.0/AppStream-x86_64-c8f82759f4be-479.pem > /etc/pki/product-default/479.pem'".format(podman_cname)
        elif arch == "aarch64":
            cmd = "podman exec {0} bash -c 'rm -rf /etc/pki/product-default/*; curl http://git.app.eng.bos.redhat.com/git/rcm/rcm-metadata.git/plain/product_ids/rhel-8.0/BaseOS-aarch64-5865bf01958b-419.pem > /etc/pki/product-default/419.pem'".format(podman_cname)
        elif arch == "ppc64le":
            cmd = "podman exec {0} bash -c 'rm -rf /etc/pki/product-default/*; curl http://git.app.eng.bos.redhat.com/git/rcm/rcm-metadata.git/plain/product_ids/rhel-8.0/BaseOS-ppc64le-4640dfa4c9b0-279.pem > /etc/pki/product-default/279.pem'".format(podman_cname)
        elif arch == "s390x":
            cmd = "podman exec {0} bash -c 'rm -rf /etc/pki/product-default/*; curl http://git.app.eng.bos.redhat.com/git/rcm/rcm-metadata.git/plain/product_ids/rhel-8.0/BaseOS-s390x-a1cf8c4dcb59-72.pem > /etc/pki/product-default/72.pem'".format(podman_cname)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to to start container used for testing...")

    def check_container(self, system_info, podman_cname):
        logger.info("--------------- Begin to check container ---------------")
        result = True
        cmd = "podman exec {0} ls /etc/yum.repos.d/".format(podman_cname)
        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to check container...")
        if ret == 0 and "redhat.repo" in output:
            logger.info("It's successful to check container!")
        else:
            logger.error("Failed to check container!")
            result = False
        logger.info("--------------- End to check container ---------------")
        return result

    def install_repoquery(self, system_info, podman_cname):
        logger.info("--------------- Begin to install command repoquery ---------------")
        result = True
        cmd = "podman exec {0} yum install -y yum-utils".format(podman_cname)
        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to install package repoquery...")
        if ret == 0:
            logger.info("It's successful to install command repoquery!")
        else:
            logger.error("Failed to install command repoquery!")
            result = False
        logger.info("--------------- End to install command repoquery ---------------")
        return result

    def check_ubi_repo(self, system_info, podman_cname,):
        # Check ubi repos
        result = False
        ubi_repos = ["ubi-8-appstream", "ubi-8-appstream-debug", "ubi-8-appstream-source", "ubi-8-baseos", "ubi-8-baseos-debug", "ubi-8-baseos-source"]
        cmd = "podman exec {0} yum repolist all".format(podman_cname)
        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to to get the result of command yum repolist...")
        repos_get = [i.split(" ")[0] for i in output.splitlines()]

        repos_error = []
        for repo in ubi_repos:
            if repo not in repos_get:
                repos_error.append(repo)
        if len(repos_error):
            logger.error("Failed to check ubi repos: {0}".format(repos_error))
        else:
            result = True
            logger.info("It's successful to check ubi repos.")
        return result

    def check_yum_repolist_all(self, system_info, podman_cname, repolist):
        logger.info("--------------- Begin to check yum repolist all in container ---------------")
        result = True
        # Run 'yum repolist' firstly to get the result of this command
        cmd = "podman exec {0} yum repolist all".format(podman_cname)
        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to to get the result of command yum repolist...")

        if repolist == True and "repolist: 0" not in output:
            logger.info("It's successful to get repo list with yum repolist all command.")
        elif repolist == False and "repolist: 0" in output:
            logger.info("It's successful to check there is no repo with yum repolist all command.")
        else:
            logger.error("Failed to get repos with yum repolist all command.")
            result = False
        logger.info("--------------- End to check yum repolist all in container ---------------")
        return result

    def check_image_deafult_repo(self, system_info, podman_cname, default_repo, container_version):
        logger.info("--------------- Begin to check default repo in container ---------------")
        result = True
        # To get all default enabled repos
        if container_version == "RHEL6":
            cmd = "podman exec {0} yum repolist | grep -A 100 'repo id' | egrep -v 'repo id|repolist'".format(podman_cname)
        else:
            cmd = "podman exec {0} yum repolist --quiet | grep -A 100 'repo id' | egrep -v 'repo id|repolist'".format(podman_cname)
        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to get all default enabled repos...")

        repo_list_all = [i.split(' ')[0].split('/')[0] for i in output.splitlines()]
        
        # Remove the ubi repos from the default repos
        repo_list = []
        for i in repo_list_all:
            if "rhubi" not in i:
                repo_list.append(i)
        repo_list.sort()

        if default_repo == repo_list:
            logger.info("It's successful to check the default enabled repo!")
        else:
            logger.error("Failed to check the default enabled repo: {0}.".format(repo_list))
            logger.info("The correct default repos should be: {0}".format(default_repo))
            result = False

        logger.info("--------------- End to check default repo in container ---------------")
        return result

    def get_one_package(self, system_info, podman_cname, repo, type="binary"):
        if type == "source":
            formatstr = "%{name}-%{version}-%{release}.src"
            cmd = '''podman exec {0} bash -c "repoquery --quiet --all --repoid={1} --archlist=src --qf '{2}'"'''.format(podman_cname, repo, formatstr)
        else:
            formatstr = "%{name}"
            cmd = '''podman exec {0} bash -c "repoquery --quiet --all --repoid={1} --qf '{2}'"'''.format(podman_cname, repo, formatstr)

        ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to repoquery available packages in container...")
        package_list = output.splitlines()

        # Up to 5 times for repoquery command
        if 'Could not match packages' in output:
            for i in range(0, 5):
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to repoquery available packages...")
                if ret == 0 and 'Could not match packages' not in output:
                    break
        if ret == 0:
            if package_list:
                #package_name = package_list[0]
                package_name = random.sample(package_list, 1)[0]
                logger.info("It's successful to repoquery available packages for repo {0} in container.".format(repo))
            else:
                package_name = ""
                logger.warning("There is no available package for repo {0} after repoquery command.".format(repo))
        else:
            package_name = "False"
            logger.error("Test Failed - Failed to repoquery available packages for repo {0} in container.".format(repo))

        logger.info("--------------- End to get packages via repoquery for repo {0}---------------".format(repo))
        return package_name

    def check_one_repo(self, system_info, podman_cname, repo):
        result = True
        if "source" in repo:
            logger.info("--------------- Begin to download one package from source repo in container ---------------")
            package_name = self.get_one_package(system_info, podman_cname, repo, "source")
            if package_name:
                cmd = "podman exec %s yumdownloader --source --enablerepo=%s --destdir /tmp %s" % (podman_cname, repo, package_name)
                ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to yumdownloader source package {0}...".format(package_name))
                if ret == 0 and ("Trying other mirror" not in output):
                    logger.info("It's successful to yumdownloader source package {0} of repo {1}.".format(package_name, repo))
                else:
                    logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(package_name, repo))
                    result = False
            elif package_name == "False":
                result = False
            logger.info("--------------- End to download one package from source repo in container ---------------")
        else:
            logger.info("--------------- Begin to install one package from binary repo in container ---------------")
            package_name = self.get_one_package(system_info, podman_cname, repo)
            if package_name:
                cmd = "podman exec %s yum -y install --skip-broken --enablerepo=%s %s" % (podman_cname, repo, package_name)
                ret, output = RemoteSSH().run_cmd_interact(system_info, cmd, "Trying to install package {0} of repo {1}...".format(package_name, repo))
                if ret == 0:
                    logger.info("It's successful to install package {0} of repo {1}.".format(package_name, repo))
                else:
                    logger.error("Test Failed - Failed to install package {0} of repo {1}.".format(package_name, repo))
                    result = False
            elif package_name == "False":
                result = False
            logger.info("--------------- End to install one package from binary repo in container ---------------")
        return result

    def restart_container(self, system_info, podman_cname):
        logger.info("--------------- Begin to restart container ---------------")
        result = True
        cmd = "podman restart {0}".format(podman_cname)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to restart container...")
        if ret == 0:
            logger.info("It's successful to restart container.")
        else:
            result = False
            logger.error("Failed to restart container")
        logger.info("--------------- End to restart container ---------------")
        return result

    def unsubscribe(self, system_info):
        logger.info("--------------- Begin to unsubscribe on host ---------------")
        result = True
        cmd = "subscription-manager unsubscribe --all"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to unsubscribe...")
        if ret == 0:
            logger.info("It's successful to unsubscribe.")
        else:
            result = False
            logger.error("Failed to unsubscribe")
        logger.info("--------------- Begin to unsubscribe on host ---------------")
        return result
















