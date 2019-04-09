import os
import time
import random
import logging
import ConfigParser

from Utils.RemoteSSH import RemoteSSH
from Utils.EntitlementBase import EntitlementBase
from CDN.CDNReadXML import CDNReadXML


# Create logger
logger = logging.getLogger("entLogger")


class CDNVerification(EntitlementBase):
    def install_packages(self, system_info):
        RemoteSSH().run_cmd(system_info, "yum install -y openssl")
        RemoteSSH().run_cmd(system_info, "yum install -y yum-utils")
        RemoteSSH().run_cmd(system_info, "yum install -y python3")

    def upload_file(self, system_info, local_path, remote_path):
        # Upload file to testing system
        logger.info("--------------- Begin to upload file ---------------")
        RemoteSSH().upload_file(system_info, local_path, remote_path)
        logger.info("--------------- End to upload file ---------------")

    def redhat_repo_backup(self, system_info):
        # Download content of file redhat.repo remotely, and save it locally
        remote_path = "/etc/yum.repos.d/redhat.repo"
        local_path = os.path.join(os.getcwd(), "redhat.repo")
        RemoteSSH().download_file(system_info, remote_path, local_path)
        ret, output = RemoteSSH().run_cmd(None, "ls {0}".format(local_path), "Trying to check {0}.".format(local_path))
        if "No such file or directory" in output:
            logger.warning("Failed to download {0} to {1}.".format(remote_path, local_path))
        else:
            logger.info("It's successful to download {0} to {1}.".format(remote_path, local_path))

    def stop_rhsmcertd(self, system_info):
        # Stop rhsmcertd service. As headling(autosubscribe) operation will be run every 2 mins after start up system,
        # then every 24 hours after that, which will influence our subscribe test.
        cmd = 'service rhsmcertd status'
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get status of service rhsmcertd...")
        if 'stopped' in output or 'Stopped' in output or 'inactive' in output:
            return True

        cmd = 'service rhsmcertd stop'
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to stop service rhsmcertd...")
        if ret == 0:
            cmd = 'service rhsmcertd status'
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get status of service rhsmcertd...")
            if 'stopped' in output or 'Stopped' in output:
                logger.info("It's successful to stop rhsmcertd service.")
                return True
            else:
                logger.error("Failed to stop rhsmcertd service.")
                return False
        else:
            logger.error("Failed to stop rhsmcertd service.")
            return False

    def get_platform_version(self, master_release, minor_release, test_type="GA"):
        if test_type == "GA":
            test_type = ""
        elif test_type == "HTB_Beta":
            test_type = "Beta"
        elif test_type == "HTB_Snapshot":
            test_type = "HTB"
        platform_version = "{0}.{1} {2}".format(master_release, minor_release, test_type)
        return platform_version.strip()

    def get_product_name(self, manifest, pid):
        return CDNReadXML().get_name(manifest, pid)

    def config_testing_environment(self, system_info, hostname, baseurl):
        # Config hostname and baseurl in /etc/rhsm/rhsm.conf
        cmd = "subscription-manager config --server.hostname={0}".format(hostname)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to set hostname in /etc/rhsm/rhsm.conf...")

        cmd = "subscription-manager config --rhsm.baseurl={0}".format(baseurl)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to set baseurl in /etc/rhsm/rhsm.conf...")

    def check_registered(self, system_info):
        # Check if registered
        cmd = "subscription-manager identity"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check if registered with server...")
        if ret == 0:
            logger.info("The system is registered with server now.")
            return True
        else:
            logger.info("The system is not registered with server now.")
            return False

    def unregister(self, system_info):
        # Unregister with server
        if self.check_registered(system_info):
            cmd = "subscription-manager unregister"
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to unregister...")

            if ret == 0:
                logger.info("It's successful to unregister.")
                return True
            else:
                logger.error("Test Failed - Failed to unregister.")
                return False
        else:
            logger.info("The system is not registered with server now.")
            return True

    def register(self, system_info, username, password):
        # Register with server
        cmd = "subscription-manager register --username={0} --password='{1}'".format(username, password)

        if self.check_registered(system_info):
            logger.info("The system is already registered, need to unregister first!")
            if not self.unregister(system_info):
                logger.info("Failed to unregister, try to use '--force'!")
                cmd += " --force"

        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to register with server...")
        if ret == 0:
            logger.info("It's successful to register.")
            return True
        else:
            logger.error("Test Failed - Failed to register.")
            return False

    def check_sys_role_usage(self, system_info):
        # Check role and usage setting
        cmd = "subscription-manager role"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to show role...")
        
        cmd = "subscription-manager usage"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to show usage...")

        cmd = "syspurpose show"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to show role/usage...")

    def set_role(self, system_info, variant):
        # Set role for RHEL 8 system, like:
        # subscription-manager role --set="Red Hat Enterprise Linux Compute Node"
        # subscription-manager usage --set="Production"
        # syspurpose show
        # {
        #   "role": "Red Hat Enterprise Linux Compute Node",
        #   "usage": "Production"
        # }

        role = ""
        if variant == "Workstation":
            role = "Red Hat Enterprise Linux Workstation"
        elif variant == "ComputeNode":
            role = "Red Hat Enterprise Linux Compute Node"
        elif variant == "Server":
            role = "Red Hat Enterprise Linux Server"

        cmd = "subscription-manager role --set \"{0}\"".format(role)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set role...")
        if ret == 0:
            logger.info("It's successful to set role.")
            return True
        else:
            logger.error("Test Failed - Failed to set role.")
            return False

    def set_usage(self, system_info):
        # Set usage for RHEL 8 system, like:
        # subscription-manager role --set="Red Hat Enterprise Linux Compute Node"
        # subscription-manager usage --set="Production"
        # syspurpose show
        # {
        #   "role": "Red Hat Enterprise Linux Compute Node",
        #   "usage": "Production"
        # }

        usage = "Production"

        cmd = "subscription-manager usage --set \"{0}\"".format(usage)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set usage...")
        if ret == 0:
            logger.info("It's successful to set usage.")
            return True
        else:
            logger.error("Test Failed - Failed to set usage.")
            return False

    def check_subscription(self, system_info, sku):
        cmd = "subscription-manager list --available --all | grep {0}".format(sku)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list sbuscription {0}...".format(sku))
        if ret == 0 and sku in output:
            logger.info("It's successful to get sku {0} in available list.".format(sku))
            return True
        else:
            logger.error("Test Failed - Failed to get sku {0} in available list.".format(sku))
            return False

    def get_sku_pool(self, system_info):
        # Get available entitlement pools
        time.sleep(5)
        cmd = "subscription-manager  list --avail --all| egrep 'SKU|Pool ID' | grep -v Subscription"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list all available SKU and Pool ID...")

        sku_pool_dict = {}
        if ret == 0:
            if output != "":
                i = 0
                sku = ""
                for line in output.splitlines():
                    if line != "":
                        if i % 2 == 0:
                            sku = line.split(":")[1].strip()
                        if i % 2 != 0:
                            pool = line.split(":")[1].strip()
                            if i != 0:
                                if sku in sku_pool_dict.keys():
                                    sku_pool_dict[sku].append(pool)
                                else:
                                    sku_pool_dict[sku] = [pool]
                        i += 1
            else:
                logger.error("No suitable pools!")
                logger.error("Test Failed - Failed to get available pools.")
        else:
            logger.error("Test Failed - Failed to get available pools.")

        sku_pool_available_suggested = self.get_sku_pool_available_suggested(system_info)
        sku_pool_dict = self.check_sku_pool(sku_pool_dict, sku_pool_available_suggested)
        
        return sku_pool_dict

    def check_sku_pool(self, sku_pool_dict, sku_pool_available_suggested):
        i = 0
        for sku in sku_pool_available_suggested.keys():
            for pool in sku_pool_available_suggested[sku]:
                if pool[1] != 'Unlimited' and int(pool[1]) < int(pool[2]):
                    sku_pool_dict[sku].remove(pool[0])
                    logger.info("Remove the pool '{0}' of SKU '{1}' due to available subscription '{2}' " \
                        "is less than suggested subscription '{3}'.".format(pool[0],sku,pool[1],pool[2]))
                    i += 1
        
        if i > 0:
            logger.info("Totally there are '{0}' pool(s) removed from the SKU '{1}' after check.".format(str(i),sku))
            logger.debug("The final sku/pool list is:\n'{0}'".format(sku_pool_dict))
        else:
            logger.info("There is no pool needed to remove after check.")

        return sku_pool_dict
        
    def get_sku_pool_available_suggested(self, system_info):
        # Get available entitlement pools
        time.sleep(5)
        cmd = "subscription-manager  list --avail --all| egrep 'SKU|Pool ID|Available:|Suggested:' | grep -v Subscription"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list all available SKU and Pool ID...")

        sku_pool_dict = {}
        if ret == 0:
            if output != "":
                i = 0
                while i < len(output.splitlines()):
                    sku = output.splitlines()[i].split(":")[1].strip()
                    pool = output.splitlines()[i+1].split(":")[1].strip()
                    available = output.splitlines()[i+2].split(":")[1].strip()
                    suggested = output.splitlines()[i+3].split(":")[1].strip()
                    
                    sku_list=[]
                    sku_list.append(pool)
                    sku_list.append(available)
                    sku_list.append(suggested)
                    if sku in sku_pool_dict.keys():
                        sku_pool_dict[sku].append(sku_list)
                    else:
                        sku_pool_dict[sku] = [sku_list]

                    i += 4
            else:
                logger.error("No suitable pools!")
                logger.error("Test Failed - Failed to get available pools.")
        else:
            logger.error("Test Failed - Failed to get available pools.")

        return sku_pool_dict

    def subscribe_pool(self, system_info, poolid):
        cmd = "subscription-manager subscribe --pool={0}".format(poolid)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to subscribe with poolid {0}".format(poolid))

        if ret == 0:
            logger.info("It's successful to subscribe.")
            return True
        else:
            logger.error("Test Failed - Failed to subscribe.")
            return False

    def clean_product_dir(self, system_info):
        cmd = "ls /etc/pki/product/"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list product id files under /etc/pki/product/...")

        cmd = "rm -rf /etc/pki/product/*"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to remove all product id files under /etc/pki/product/...")

        if ret:
            logger.error("Test Failed - Failed to remove all product id files under /etc/pki/product/.")
            return False
        else:
            logger.info("It's successful to remove all product id files under /etc/pki/product/.")
            return True

    def auto_subscribe(self, system_info):
        cmd = "subscription-manager attach --auto"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to auto subscribe for system...")

        if ret == 0:
            logger.info("It's successful to auto subscribe.")
            return True
        else:
            logger.error("Test Failed - Failed to auto subscribe.")
            return False

    def get_certificate_list(self, system_info):
        cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list all certificate files under /etc/pki/entitlement/...")
        return output.splitlines()

    def get_certificate(self, system_info, sku):
        cmd = "subscription-manager list --consumed"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list the consumed subscription...")

        cmd = "subscription-manager list --consumed --matches={0} | grep Serial".format(sku)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get the serial number for the consumed sku '{0}'...".format(sku))
        cert_filename = output.split(":")[1].strip() + ".pem"

        if cert_filename in self.get_certificate_list(system_info):
            return cert_filename
        else:
            logger.error("Test Failed - Failed to get the entitlement certificate of the sku '{0}'.".format(sku))
            return ""

    def test_default_enable_repo(self, system_info, default_repo, master_release):
        logger.info("--------------- Begin to verify default enabled repo ---------------")
        result = True

        # Display the default enabled repos to check it via log conveniently later
        cmd = "subscription-manager repos --list-enabled"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to get default enabled repo...")

        # Get the enabled repos
        cmd = "subscription-manager repos --list-enabled | grep 'Repo ID'"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get default enabled repo...")

        if output:
            repo = [i.split(':')[1].strip() for i in output.split('\n')]
            if len(repo) == 1:
                # Only one enabled repo
                if repo[0] == default_repo:
                    logger.info("Correct default enabled repo.")
                else:
                    logger.error("Test Failed - Incorrect default enabled repo - {0}.".format(repo))
                    result = False
            else:
                # more than one enabled repos
                if master_release == "8":
                    logger.info("Correct default enabled repo.")
                    result = True
                else:
                    logger.error("Test Failed - More than one enabled repo - {0}.".format(repo))
                    result = False
        else:
            # No default enabled repo
            logger.error("Test Failed - No default enabled repo.")
            result = False
        logger.info("--------------- End to verify default enabled repo ---------------")
        return result

    def verify_pid_in_ent_cert(self, system_info, ent_cert, pid):
        logger.info("--------------- Begin to verify pid {0} in entitlement cert ---------------".format(pid))
        result = True

        # Verify if one specific product id in one entitlement cert
        cmd = "rct cat-cert /etc/pki/entitlement/{0} | grep ID | egrep -v 'Stacking ID|Pool ID'".format(ent_cert)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check PID {0} in entitlement certificate {1} with rct...".format(pid, ent_cert))

        # Output:
        #    ID: 240
        #    ID: 281
        #    ID: 285
        #    ID: 286
        #    ID: 69
        #    ID: 83
        #    ID: 85
        if ret == 0:
            if pid in [i.split(":")[1].strip() for i in output.splitlines()]:
                logger.info("It's successful to verify PID {0} in entitlement certificate {1}.".format(pid, ent_cert))
            else:
                logger.error("Test Failed - Failed to verify PID {0} in entitlement certificate {1}.".format(pid, ent_cert))
                result = False
        else:
            # Output:
            # sh: rct: command not found
            prefix_str = '1.3.6.1.4.1.2312.9.1.'
            cmd = 'openssl x509 -text -noout -in /etc/pki/entitlement/{0} | grep --max-count=1 -A 1 {1}{2}'.format(ent_cert, prefix_str, pid)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check PID {0} in entitlement certificate {1} with openssl...".format(pid, ent_cert))
            if ret == 0 and output != '':
                logger.info("It's successful to verify PID {0} in entitlement certificate {1}.".format(pid, ent_cert))
            else:
                logger.error("Test Failed - Failed to verify PID {0} in entitlement certificate {1}.".format(pid, ent_cert))
                result = False
        logger.info("--------------- End to verify pid {0} in entitlement cert ---------------".format(pid))
        return result

    def verify_sku_in_ent_cert(self, system_info, ent_cert, sku):
        logger.info("--------------- Begin to verify sku {0} in entitlement cert ---------------".format(sku))
        result = True

        # Verify if one specific sku id in one entitlement cert
        cmd = "rct cat-cert /etc/pki/entitlement/{0} | grep SKU".format(ent_cert)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check SKU {0} in entitlement certificate {1} with rct...".format(sku, ent_cert))

        if ret == 0:
            # Output:
            # SKU: MCT2887
            if sku in [i.strip().split(":")[1].strip() for i in output.splitlines()]:
                logger.info("It's successful to verify sku {0} in entitlement certificate {1}.".format(sku, ent_cert))
            else:
                logger.error("Test Failed - Failed to verify sku {0} in entitlement cert {1}.".format(sku, ent_cert))
                result = False
        else:
            # Output:
            # sh: rct: command not found
            cmd = 'openssl x509 -text -noout -in /etc/pki/entitlement/{0} | grep {1}'.format(ent_cert, sku)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check SKU {0} in entitlement certificate {1} with openssl...".format(sku, ent_cert))
            if ret == 0 and output != '':
                logger.info("It's successful to verify sku {0} in entitlement cert {1}.".format(sku, ent_cert))
            else:
                logger.error("Test Failed - Failed to verify sku {0} in entitlement cert {1}." .format(sku, ent_cert))
                result = False
        logger.info("--------------- End to verify sku {0} in entitlement cert ---------------".format(sku))
        return result

    def verify_arch_in_ent_cert(self, system_info, ent_cert, manifest_xml, pid, current_release_ver):
        logger.info("--------------- Begin to verify arch in entitlement cert ---------------")
        result = True

        # Get arch list from manifest
        arch_manifest = self.get_arch_list_from_manifest(manifest_xml, pid)

        # Get supported arches in entitlement certificate
        cmd = "rct cat-cert /etc/pki/entitlement/{0}  | grep -A 3 'ID: {1}' | grep Arch".format(ent_cert, pid)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get supported arches for pid {0} in entitlement certificate {1} with rct cat-cert...".format(pid, ent_cert))
        if ret == 0:
            if output != "":
                # Output:
                # Arch: x86_64,x86
                arches = output.split(":")[1].strip().split(",")
                arch_cert = []
                for arch in arches:
                    if arch == 'x86':
                        arch_cert.append('i386')
                    elif arch == 'ppc' and current_release_ver.find('6') >= 0:
                        arch_cert.append('ppc64')
                    elif arch == 'ppc64' and current_release_ver.find('5') >= 0:
                        arch_cert.append('ppc')
                    elif arch == 's390':
                        arch_cert.append('s390x')
                    elif arch == 'ia64' and current_release_ver.find('6') >= 0:
                        continue
                    else:
                        arch_cert.append(arch)
                logger.info("Supported arch in entitlement cert are: {0}.".format(arch_cert))

                error_arch_list = self.cmp_arrays(arch_manifest, arch_cert)
                if len(error_arch_list) > 0:
                    logger.error("Failed to verify arches for product {0} in entitlement certificate.".format(pid))
                    logger.info('Below are arches got from in manifest but not in entitlement cert:')
                    self.print_list(error_arch_list)
                    logger.error("Test Failed - Failed to verify arch in entitlement certificate for product {0}.".format(pid))
                    result = False
                else:
                    logger.info("It's successful to verify arch in entitlement certificate for product {0}.".format(pid))
            else:
                logger.error("Test Failed - Failed to verify arch in entitlement certificate for product {0}.".format(pid))
                result = False
        else:
            # Output:
            # sh: rct: command not found
            str = '1.3.6.1.4.1.2312.9.1.{0}.3:'.format(pid)
            cmd = 'openssl x509 -text -noout -in /etc/pki/entitlement/{0} | grep {1} -A 2'.format(ent_cert, str)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get supported arches for pid {0} in entitlement certificate {1} with openssl...".format(pid, ent_cert))
            if ret == 0 and output != '':
                for i in arch_manifest:
                    if i in output:
                        continue
                    else:
                        logger.error("Test Failed - Failed to verify in entitlement certificate for product {0}.".format(pid))
                        result = False
                logger.info("It's successful to verify arch in entitlement certificate for product {0}.".format(pid))
            else:
                logger.error("Test Failed - Failed to verify in entitlement certificate for product {0}.".format(pid))
                result = False
        logger.info("--------------- End to verify arch in entitlement cert ---------------")
        return result

    def set_release(self, system_info, release_ver, manifest_json, master_release):
        releasever_set = ""
        cmd = "subscription-manager release --set={0}".format(release_ver)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set release version as {0}...".format(release_ver))

        if ret == 0 and 'Release set to' in output:
            logger.info("It's successful to set system release as {0}.".format(release_ver))
            cmd = "subscription-manager release"
            RemoteSSH().run_cmd(system_info, cmd, "Trying to check the release version after setting...".format(release_ver))
        elif 'No releases match' in output:
            releasever_set = '--releasever=%s' % release_ver
            logger.info("It's successfully to set option --releasever={0}.".format(release_ver))
        else:
            logger.error("Test Failed - Failed to set system release as {0}.".format(release_ver))
            return False
        return releasever_set

    def get_release_list(self, system_info):
        cmd = "subscription-manager release --list"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get release list with rhsm...")
        if ret:
            logger.error("Test Failed - Failed to get release list with rhsm command.")
            return False
        else:
            logger.info("It's successful to get release list with rhsm command.")
            return True

    def clean_yum_cache(self, system_info, releasever_set):
        # Clean yum cache
        cmd = 'yum clean all --enablerepo=* {0}'.format(releasever_set)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum clean cache...")
        if ret == 0:
            logger.info("It's successful to clean yum cache.")
            return True
        else:
            logger.error("Test Failed - Failed to clean yum cache.")
            return False

    def get_repo_list_from_manifest(self, manifest_xml, pid, current_arch, release_ver):
        # Get repo list from xml format manifest
        logger.info("--------------- Begin to get repo list from manifest: {0} {1} {2} ---------------".format(pid, current_arch, release_ver))
        repo_list = CDNReadXML().get_repo_list(manifest_xml, release_ver, pid, current_arch)
        if len(repo_list) == 0:
            logger.error("Got 0 repository from manifest for pid {0} on release {1}!".format(pid, release_ver))
            return []
        else:
            logger.info("Got {0} Repos from manifest for pid {1} on release {2}:".format(len(repo_list), pid, release_ver))
            self.print_list(repo_list)
        logger.info("--------------- End to get repo list from manifest: {0} {1} {2} ---------------".format(pid, current_arch, release_ver))
        return repo_list

    def get_package_list_from_manifest(self, manifest_xml, pid, repo, current_arch, release_ver, type="name"):
        # Get package list from manifest file
        logger.info("--------------- Begin to get package list from manifest: {0} {1} {2} {3} ---------------".format(pid, current_arch, repo, release_ver))
        package_list = CDNReadXML().get_package_list(manifest_xml, repo, release_ver, pid, current_arch)
        logger.info("It's successful to get {0} packages from package manifest.".format(len(package_list)))
        if len(package_list) != 0:
            if type == "name":
                package_list = [p.split()[0] for p in package_list]
            elif type == "full-name":
                # "%{name}-%{version}-%{release}.src"
                package_list = ["{0}-{1}-{2}.{3}".format(i.split()[0], i.split()[1], i.split()[2], i.split()[3]) for i in package_list]
            self.print_list(package_list)
        logger.info("--------------- End to get package list from manifest: PASS ---------------")
        return package_list

    def get_arch_list_from_manifest(self, manifest_xml, pid):
        # Get arch list from xml format manifest
        logger.info("--------------- Begin to get arch list for pid {0} from manifest ---------------".format(pid))
        arch_list = CDNReadXML().get_arch_list(manifest_xml, pid)
        if len(arch_list) == 0:
            logger.error("Got none arch from manifest for pid {0}!".format(pid))
            return []
        else:
            logger.info("Got {0} arch(es) from manifest for pid {1}:".format(len(arch_list), pid))
            self.print_list(arch_list)
        logger.info("--------------- End to get arch list for pid {0} from manifest ---------------".format(pid))
        return arch_list

    def test_repos(self, system_info, repo_list, releasever_set, release_ver, current_arch):
        # Check all enabled repos to see if there are broken repos
        repo_file = os.path.join(os.getcwd(), "redhat.repo")
        if not os.path.exists(repo_file):
            logger.error("There is no {0} backuped.".format(repo_file))
            return False

        config = ConfigParser.ConfigParser()
        config.read(repo_file)

        cmd = "yum repolist --enablerepo={0} {1}".format(",".join(repo_list), releasever_set)

        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to test enabled repos...")
        if "ERROR" in output:
            result = False
            # Get baseurl/repo pairs from redhat.repo file
            url_repo_dict = {}
            for s in config.sections():
                for i in config.items(s):
                    if i[0] == "baseurl":
                        url_repo_dict[i[1]] = s

            # Check $releasever $basearch in redhat.repo file, then replace the following error url according to it
            src_str = ""
            dest_str = ""
            if url_repo_dict.keys()[0].count("$") == 2:
                src_str = "%s/%s" % (release_ver, current_arch)
                dest_str = "$releasever/$basearch"
            elif url_repo_dict.keys()[0].count("$") == 1:
                src_str = current_arch
                dest_str = "$basearch"

            error_list = []
            while not result:
                disablerepo = []
                # Get error url
                # http://download.lab.bos.redhat.com/released/RHEL-6/6.7/Server/optional/x86_64/os3/repodata/repomd.xml: [Errno 14] PYCURL ERROR 22 - "The requested URL returned error: 404 Not Found"
                # Trying other mirror.
                start_position = output.index("http")
                error_end_position = output.index("Trying other mirror") - 1
                error_url = output[start_position:error_end_position]

                # Get repo url
                repo_url_end_position = output.index("/repodata/repomd.xml")
                repo_url = output[start_position:repo_url_end_position]

                # Get base url, and then get the repo name
                base_url = repo_url.replace(src_str, dest_str)
                repo_name = url_repo_dict[base_url]

                # Set error dict
                error_dict = {}
                error_dict['url'] = error_url
                error_dict["repo"] = repo_name

                error_list.append(error_dict)

                disablerepo.append(repo_name)
                cmd += " --disablerepo={0}".format(",".join(disablerepo))

                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to disablerepo {0}...".format(disablerepo))

                if "ERROR" not in output:
                    result = True

            logger.info("=========================Summary of repos and baseurls=======================================")
            logger.error("Followings are failed repos (total: {0})".format(len(error_list)))
            for i in error_list:
                logger.info("repo: {0}".format(i["repo"]))
                logger.info("      {1}".format(i["url"]))
            logger.error("Failed to do yum repolist.")
            return False
        else:
            logger.info("It's successful to do yum repolist.")
            return True

    def enable_ocprepo(self, system_info, repo):
        # Enable a repo before test this repo
        cmd = "subscription-manager repos --enable={0}".format(repo)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to enable ocp")
        if ret == 0:
            logger.info("It's successful to enable ocp repo")
            return True
        else:
            logger.error("Test Failed - Failed to enable ocp repo")
            return False

    def enable_repo(self, system_info, repo):
        # Enable a repo before test this repo
        cmd = "subscription-manager repos --enable={0}".format(repo)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to enable repo {0}...".format(repo))
        if ret == 0:
            logger.info("It's successful to enable repo {0}.".format(repo))
            return True
        else:
            logger.error("Test Failed - Failed to enable repo {0}.".format(repo))
            return False

    def disable_repo(self, system_info, repo):
        # Disable a repo after finish testing this repo
        cmd = "subscription-manager repos --disable={0}".format(repo)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to disable repo {0}...".format(repo))
        if ret == 0:
            logger.info("It's successful to disable repo {0}.".format(repo))
            return True
        else:
            logger.error("Test Failed - Failed to disable repo {0}.".format(repo))
            return False

    def disable_all_repo(self, system_info):
        # Disabling all default enabled repos
        cmd = "subscription-manager repos --disable=*"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to disable all repos...")
        if ret == 0:
            logger.info("It's sucessful to disable all repos.")
            return True
        else:
            logger.error("Test Failed - Failed to diable default enabled repo.")
            return False

    def change_gpgkey(self, system_info, repo_list):
        # Change gpgkey for all the test repos listed in manifest
        logger.info("--------------- Begin to change gpgkey for test repos ---------------")
        result = True

        for repo in repo_list:
            cmd = "subscription-manager repo-override --repo %s --add=gpgkey:file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release" % repo
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to change gpgkey for repo %s in /etc/yum.repos.d/redhat.repo...".format(repo))
            if ret == 0:
                logger.info("It's successful to change gpgkey for repo {0} in /etc/yum.repos.d/redhat.repo.".format(repo))
            else:
                logger.error("Test Failed - Failed to change gpgkey for repo {0} /etc/yum.repos.d/redhat.repo.".format(repo))
                result = False

        logger.info("--------------- End to change gpgkey for test repos ---------------")
        return result

    def get_pkgs_via_repoquery(self, system_info, repo, releasever_set, master_release, type="binary"):
        logger.info("--------------- Begin to get packages via repoquery for repo {0}---------------".format(repo))
        
        pkgnarrowstr = ""
        if master_release == "8":
            pkgnarrowstr = "--available"
        else:
            pkgnarrowstr = "--pkgnarrow=available"

        if type == "source":
            formatstr = "%{name}-%{version}-%{release}.src"
            cmd = '''repoquery %s --quiet --all --repoid=%s --archlist=src --qf "%s" %s''' % (pkgnarrowstr, repo, formatstr, releasever_set)
        else:
            formatstr = "%{name}"
            cmd = '''repoquery %s --quiet --all --repoid=%s --qf "%s" %s''' % (pkgnarrowstr, repo, formatstr, releasever_set)

        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to repoquery available packages...", timeout=3600)

        # Up to 5 times for repoquery command
        if 'Could not match packages' in output:
            for i in range(0, 5):
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to repoquery available packages...",
                                                  timeout=3600)
                if ret == 0 and 'Could not match packages' not in output:
                    break

        if ret == 0:
            logger.info("It's successful to repoquery available packages for the repo {0}.".format(repo))
            pkgs = output.strip().splitlines()
        else:
            logger.error("Test Failed - Failed to repoquery available packages for the repo {0}.".format(repo))
            pkgs = []
        logger.info("--------------- End to get packages via repoquery for repo {0}---------------".format(repo))
        return pkgs

    def yum_download_one_source_package(self, system_info, repo, releasever_set, manifest_xml, pid, current_arch, release_ver, master_release):
        logger.info("--------------- Begin to verify package downloadable of repo {0} of product {1} ---------------".format(repo, pid))
        download_result = True

        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, current_arch, release_ver, "full-name")
        if len(manifest_pkgs) == 0:
            logger.info("There is no package in manifest for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))

            # Trying to get available source packages via repoquery
            manifest_pkgs = self.get_pkgs_via_repoquery(system_info, repo, releasever_set, master_release, "source")

        if len(manifest_pkgs) == 0:
            logger.info("There is no available package for repo {0} from both manifest and repoquery!".format(repo))
        else:
            # Get one package randomly to download
            pkg_name = random.sample(manifest_pkgs, 1)[0]
            cmd = "yumdownloader --destdir /tmp --source %s %s" % (pkg_name, releasever_set)

            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yumdownloader source package {0}...".format(pkg_name))

            if ret == 0 and ("Trying other mirror" not in output):
                cmd = "ls /tmp/{0}*".format(pkg_name)
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check downloaded source package {0} just now...".format(pkg_name))

                if ret == 0 and pkg_name in output:
                    logger.info("It's successful to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                else:
                    logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                    download_result = False
            else:
                logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                download_result = False

        logger.info("--------------- End to verify package downloadable of repo {0} of product {1} ---------------".format(repo, pid))
        return download_result

    def yum_download_all_source_package(self, system_info, repo, releasever_set, manifest_xml, pid, current_arch, release_ver, master_release):
        logger.info("--------------- Begin to verify package downloadable of repo {0} of product {1} ---------------".format(repo, pid))
        download_result = True

        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, current_arch, release_ver, "full-name")
        if len(manifest_pkgs) == 0:
            logger.info("There is no package in manifest for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))

            # Trying to get available source packages via repoquery
            manifest_pkgs = self.get_pkgs_via_repoquery(system_info, repo, releasever_set, master_release, "source")

        if len(manifest_pkgs) == 0:
            logger.info("There is no available package for repo {0} from both manifest and repoquery!".format(repo))
        else:
            # Do a full download for the source rpms
            for pkg_name in manifest_pkgs:
                cmd = "yumdownloader --destdir /tmp --source %s %s" % (pkg_name, releasever_set)

                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yumdownloader source package {0}...".format(pkg_name))

                if ret == 0 and ("Trying other mirror" not in output):
                    cmd = "ls /tmp/{0}*".format(pkg_name)
                    ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check downloaded source package {0} just now...".format(pkg_name))

                    if ret == 0 and pkg_name in output:
                        logger.info("It's successful to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                    else:
                        logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                        download_result = False
                else:
                    logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                    download_result = False

        logger.info("--------------- End to verify package downloadable of repo {0} of product {1} ---------------".format(repo, pid))
        return download_result

    def verify_productid_in_product_cert(self, system_info, pid, base_pid):
        # Check product id in product entitlement certificate
        str = '1.3.6.1.4.1.2312.9.1.'

        time.sleep(20)
        ret, output = RemoteSSH().run_cmd(system_info, "ls /etc/pki/product/", "Trying to list all the product certificates...")
        product_ids = output.split()

        if "{0}.pem".format(pid) in product_ids:
            logger.info("It's successful to install the product cert {0}!".format(pid))

            cmd = 'openssl x509 -text -noout -in /etc/pki/product/{0}.pem | grep {1}{2}'.format(pid, str, pid)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to verify product id in product certificate...")

            if ret == 0 and output != '':
                logger.info("It's successful to verify PID {0} in product cert.".format(pid))
                return True
            else:
                logger.error("Test Failed - Failed to verify PID {0} in product cert.".format(pid))
                return False
        else:
            error_list = list(set(product_ids) - set([base_pid]))
            if len(error_list) == 0:
                logger.error("Test Failed - Failed to install the product cert {0}.pem.".format(pid))
            else:
                logger.error("Test Failed - Failed to install correct product cert {0}, but installed cert {1}.".format(pid, error_list))
            return False

    def check_info_in_product_cert(self, system_info, manifest_xml, pid, arch, platform_version, path):
        logger.info("--------------- Begin to check cert info listed in product cert ---------------")

        product_name = self.get_product_name(manifest_xml, pid)

        cmd = "rct cc {0}{1}.pem | grep -A 4 'ID:'".format(path, pid)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get the content of {0}{1}.pem...".format(path, pid))

        # data: {'Tags': 'rhel-6,rhel-6-server', 'Version': '6.10 Beta', 'Arch': 'x86_64', 'ID': '69', 'Name': 'Red Hat Enterprise Linux Server'}
        data = {}
        for item in output.splitlines():
            item_list = item.split(":")
            data[item_list[0].strip()] = item_list[1].strip()

        pid_got = data["ID"]
        version_got = data["Version"]
        arch_got = data["Arch"]
        name_got = data["Name"]
        result = True
        if pid_got == pid:
            logger.info("Correct PID '{0}' is listed in {1}{2}.pem.".format(pid_got, path, pid))
        else:
            logger.info("Correct PID: {0}".format(pid))
            logger.info("Incorrect PID: {0}".format(pid_got))
            logger.error("Test Failed - Incorrect PID is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if version_got == platform_version:
            logger.info("Correct Platform Version '{0}' is listed in {1}{2}.pem.".format(version_got, path, pid))
        else:
            logger.info("Correct Platform Version: {0}".format(platform_version))
            logger.info("Incorrect Platform Version: {0}".format(version_got))
            logger.error("Test Failed - Incorrect Platform Version is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if arch_got == arch:
            logger.info("Correct Arch '{0}' is listed in {1}{2}.pem.".format(arch_got, path, pid))
        else:
            logger.info("Correct Arch: {0}".format(arch))
            logger.info("Incorrect Arch: {0}".format(arch_got))
            logger.error("Test Failed - Incorrect Arch is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if product_name:
            if name_got == product_name:
                logger.info("Correct Product Name '{0}' is listed in {1}{2}.pem.".format(name_got, path, pid))
            else:
                logger.info("Correct Product Name: {0}".format(product_name))
                logger.info("Incorrect Product Name: {0}".format(name_got))
                logger.error("Test Failed - Incorrect Product Name is listed in {0}{1}.pem.".format(path, pid))
                result = False
        else:
            logger.info("The testing for 'Product Name' was ignored, as failed to get 'Product Name' from manifest for pid {0}.".format(pid))
        logger.info("--------------- End to check cert info listed in product cert ---------------")
        return result

    def check_openshift_info_in_product_cert(self, system_info, manifest_xml, pid, arch, openshift_version, path):
        logger.info("--------------- Begin to check cert info listed in product cert ---------------")

        product_name = self.get_product_name(manifest_xml, pid)

        cmd = "rct cc {0}{1}.pem | grep -A 4 'ID:'".format(path, pid)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get the content of {0}{1}.pem...".format(path, pid))

        # data: {'Tags': 'rhel-6,rhel-6-server', 'Version': '6.10 Beta', 'Arch': 'x86_64', 'ID': '69', 'Name': 'Red Hat Enterprise Linux Server'}
        data = {}
        for item in output.splitlines():
            item_list = item.split(":")
            data[item_list[0].strip()] = item_list[1].strip()

        pid_got = data["ID"]
        version_got = data["Version"]
        arch_got = data["Arch"]
        name_got = data["Name"]
        result = True
        if pid_got == pid:
            logger.info("Correct PID '{0}' is listed in {1}{2}.pem.".format(pid_got, path, pid))
        else:
            logger.info("Correct PID: {0}".format(pid))
            logger.info("Incorrect PID: {0}".format(pid_got))
            logger.error("Test Failed - Incorrect PID is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if version_got == openshift_version:
            logger.info("Correct Platform Version '{0}' is listed in {1}{2}.pem.".format(version_got, path, pid))
        else:
            logger.info("Correct Platform Version: {0}".format(openshift_version))
            logger.info("Incorrect Platform Version: {0}".format(version_got))
            logger.error("Test Failed - Incorrect Platform Version is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if arch_got == arch:
            logger.info("Correct Arch '{0}' is listed in {1}{2}.pem.".format(arch_got, path, pid))
        else:
            logger.info("Correct Arch: {0}".format(arch))
            logger.info("Incorrect Arch: {0}".format(arch_got))
            logger.error("Test Failed - Incorrect Arch is listed in {0}{1}.pem.".format(path, pid))
            result = False

        if product_name:
            if name_got == product_name:
                logger.info("Correct Product Name '{0}' is listed in {1}{2}.pem.".format(name_got, path, pid))
            else:
                logger.info("Correct Product Name: {0}".format(product_name))
                logger.info("Incorrect Product Name: {0}".format(name_got))
                logger.error("Test Failed - Incorrect Product Name is listed in {0}{1}.pem.".format(path, pid))
                result = False
        else:
            logger.info("The testing for 'Product Name' was ignored, as failed to get 'Product Name' from manifest for pid {0}.".format(pid))
        logger.info("--------------- End to check cert info listed in product cert ---------------")
        return result

    def curl_file_with_debug_cert(self,system_info, cert_path, key_path, proxy, productid_url, productid_path):
        if ".qa." in productid_url:
            cmd = "curl {0} > {1}".format(productid_url, productid_path)
        elif ".stage." in productid_url:
            cmd = "curl {0} > {1}".format(productid_url, productid_path)
        else:
            cmd = "curl -s --proxy {0} --cert {1} --key {2} -k {3} > {4}".format(proxy, cert_path, key_path, productid_url, productid_path)
        RemoteSSH().run_cmd(system_info, cmd, "Trying to download productid cert from CDN...")
        cmd = "cat {0}".format(productid_path)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check the downloaded productid cert from CDN...")
        if "Not Found" in output or "File not found" in output or "No such file or directory" in output:
            logger.error("Test Failed - Failed to download productid cert from CDN.")
            return False
        return True

    def check_default_pid_cert(self, system_info, manifest_xml, default_pid, arch, platform_version):
        logger.info("--------------- Begin to verify default pid cert under /etc/pki/product-default/ ---------------")
        logger.info("The default pid under /etc/pki/product-default/ should be {0}.".format(default_pid))

        cmd = "ls /etc/pki/product-default/"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get default pid cert...")

        if output == "":
            default_pids = []
        else:
            default_pids = [i.split(".")[0] for i in output.split(" ")]

        if len(default_pids) == 0:
            logger.error("Test Failed - There is no default product cert under /etc/pki/product-default/.")
            result = False
        elif len(default_pids) > 1:
            logger.error("Test Failed - There are more than one default product cert under /etc/pki/product-default/: {0}".format(default_pids))
            result = False
        else:
            if default_pids[0] == default_pid:
                logger.info("Correct product cert {0} is listed under /etc/pki/product-default/.".format(default_pids[0]))
                result = self.check_info_in_product_cert(system_info, manifest_xml, default_pid, arch, platform_version, "/etc/pki/product-default/")
            else:
                logger.error("Test Failed - Incorrect default cert is listed under /etc/pki/product-default/.")
                result = False
        logger.info("--------------- End to verify default pid cert under /etc/pki/product-default/ ---------------")
        return result

    def get_default_pid_cert(self, system_info):
        cmd = "ls /etc/pki/product-default/"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get default product id with rhsm...")
        if ret:
            logger.error("Test Failed - Failed to get default product id with rhsm command.")
            return False
        else:
            logger.info("It's successful to get default product id with rhsm command.")
            return output.split(".")[0]

    def yum_install_one_package(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, arch, release_ver, platform_version, master_release):
        logger.info("--------------- Begin to verify package installation for repo {0} of product {1} on release {2} ---------------".format(repo, pid, release_ver))
        checkresult = True

        # Get all packages list from packages manifest
        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, arch, release_ver, "name")
        pkgs = self.get_pkgs_via_repoquery(system_info, repo, releasever_set, master_release)

        if len(manifest_pkgs) == 0:
            logger.info("Got 0 package from manifest for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))
            avail_pkgs = pkgs
        elif len(pkgs) == 0:
            logger.info("Got 0 package via repoquery for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))
            avail_pkgs = manifest_pkgs
        else:
            # Get a available packages list which are uninstalled got from repoquery and also in manifest.
            avail_pkgs = list(set(pkgs) & set(manifest_pkgs))

        if len(avail_pkgs):
            # Get one package randomly to install
            pkg_name = random.sample(avail_pkgs, 1)[0]
            install_cmd = "yum -y install --skip-broken %s %s" % (pkg_name, releasever_set)
            ret, output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to yum install package {0}...".format(pkg_name))

            if "Nothing to do" in output and 'already installed' in output:
                remove_cmd = "rpm -e --nodeps {0}".format(pkg_name)
                ret, output = RemoteSSH().run_cmd(system_info, remove_cmd, "Trying to remove already installed package {0}...".format(pkg_name))
                ret, output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to install package {0} again...".format(pkg_name))
            elif "Nothing to do" in output and 'Complete!' in output:
            # In case some package can not be installed and skipped due to the para --skip-broken
            # So try to re-select another package randomly to install
                pkg_name = random.sample(avail_pkgs, 1)[0]
                install_cmd = "yum -y install --skip-broken %s %s" % (pkg_name, releasever_set)
                ret, output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to yum install another package {0}...".format(pkg_name))

            if "conflicts" in output:
                pass

            if "Complete!" in output:
                logger.info("It's successful to yum install package {0} of repo {1}.".format(pkg_name, repo))
                # Make sure default product cert is correct after package installation for all repos
                checkresult &= self.check_default_pid_cert(system_info, manifest_xml, default_pid, arch, platform_version)

                if ("optional" not in repo) and ("supplementary" not in repo) and ("debug" not in repo):
                    # For layered os repos, correct product cert should be installed, and no extra cert, and no missing cert
                    if default_pid != pid and base_pid != pid:
                        logger.info("The product certificate {0} should be installed under /etc/pki/product.".format(pid))
                        cmd = "ls /etc/pki/product/{0}.pem".format(pid)
                        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to install package {0} again...".format(pkg_name))
                        if "No such file or directory" not in output:
                            checkresult &= self.check_info_in_product_cert(system_info, manifest_xml, pid, arch, platform_version, "/etc/pki/product/")
                        else:
                            logger.error("Test Failed - Failed to install product certificate after package installation of repo {0}.".format(repo))
                            checkresult = False
            else:
                logger.error("Test Failed - Failed to install package {0} of repo {1}.".format(pkg_name, repo))
                # Print the enabled repos when failed to install package
                cmd = "subscription-manager repos --list-enabled"
                RemoteSSH().run_cmd(system_info, cmd, "Trying to list all enabled repos...")
                checkresult = False
        else:
            logger.info("There is no package for package installation.")
        logger.info("--------------- End to verify package installation of repo {0} of product {1} on release {2} ---------------".format(repo, pid, release_ver))
        return checkresult

    def yum_install_all_package(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, arch, release_ver, platform_version, openshift_version, master_release):
        logger.info("--------------- Begin to verify package installation for repo {0} of product {1} on release {2} ---------------".format(repo, pid, release_ver))
        checkresult = True
        check_cert_install = 0
        # Get all packages list from packages manifest
        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, arch, release_ver, "name")
        pkgs = self.get_pkgs_via_repoquery(system_info, repo, releasever_set, master_release)

        if len(manifest_pkgs) == 0:
            logger.info("Got 0 package from manifest for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))
            avail_pkgs = pkgs
        elif len(pkgs) == 0:
            logger.info("Got 0 package via repoquery for pid:repo {0}:{1} on release {2}.".format(pid, repo, release_ver))
            avail_pkgs = manifest_pkgs
        else:
            # Get a available packages list which are uninstalled got from repoquery and also in manifest.
            avail_pkgs = list(set(pkgs) & set(manifest_pkgs))

        if len(avail_pkgs):
            for pkg_name in avail_pkgs:
            # Get one package randomly to install
                check_cert_install += 1
                #yumclean_cmd = "rm -rf /var/cache/yum/*;yum clean all"
                #ret, output = RemoteSSH().run_cmd(system_info, yumclean_cmd, "Trying to clean yum cache")
                install_cmd = "yum -y install --skip-broken %s %s" % (pkg_name, releasever_set)
                ret, output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to yum install package {0}...".format(pkg_name))

                if "Nothing to do" in output and 'already installed' in output:
                    remove_cmd = "rpm -e --nodeps {0}".format(pkg_name)
                    ret, output = RemoteSSH().run_cmd(system_info, remove_cmd, "Trying to remove already installed package {0}...".format(pkg_name))
                    ret, output = RemoteSSH().run_cmd(system_info, install_cmd, "Trying to install package {0} again...".format(pkg_name))

                if "conflicts" in output:
                    pass

                if "Complete!" in output:
                    logger.info("It's successful to yum install package {0} of repo {1}.".format(pkg_name, repo))
                    # Make sure default product cert is correct after package installation for all repos
                    if check_cert_install == 1:
                        checkresult &= self.check_default_pid_cert(system_info, manifest_xml, default_pid, arch, platform_version)

                    if ("optional" not in repo) and ("supplementary" not in repo) and ("debug" not in repo):
                        # For layered os repos, correct product cert should be installed, and no extra cert, and no missing cert.only to check one time for openshift
                        if default_pid != pid and base_pid != pid and check_cert_install == 1:
                            logger.info("The product certificate {0} should be installed under /etc/pki/product.".format(pid))
                            cmd = "ls /etc/pki/product/{0}.pem".format(pid)
                            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to install package {0} again...".format(pkg_name))
                            if "No such file or directory" not in output:
                                checkresult &= self.check_openshift_info_in_product_cert(system_info, manifest_xml, pid, arch, openshift_version, "/etc/pki/product/")
                            else:
                                logger.error("Test Failed - Failed to install product certificate after package installation of repo {0}.".format(repo))
                                checkresult = False
                    rpmremove_cmd = "rpm -e --nodeps {0}".format(pkg_name)
                    ret, output = RemoteSSH().run_cmd(system_info, rpmremove_cmd,"Trying to remove already installed package {0}...".format(pkg_name))
                else:
                    logger.error("Test Failed - Failed to install package {0} of repo {1}.".format(pkg_name, repo))
                    # Print the enabled repos when failed to install package
                    cmd = "subscription-manager repos --list-enabled"
                    RemoteSSH().run_cmd(system_info, cmd, "Trying to list all enabled repos...")
                    checkresult = False
        else:
            logger.info("There is no package for package installation.")
        logger.info("--------------- End to verify package installation of repo {0} of product {1} on release {2} ---------------".format(repo, pid, release_ver))
        return checkresult

    def package_smoke_installation(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, current_arch, release_ver, platform_version, master_release):
        # Verify package's downloadable or installable
        if ("source" in repo) or ("src" in repo):
            result = self.yum_download_one_source_package(system_info, repo, releasever_set, manifest_xml, pid, current_arch, release_ver, master_release)
        else:
            result = self.yum_install_one_package(system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, current_arch, release_ver, platform_version, master_release)
        return result

    def package_full_installation(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, current_arch, release_ver, platform_version, openshift_version, master_release):
        # Verify package's downloadable or installable
        if ("source" in repo) or ("src" in repo):
            result = self.yum_download_all_source_package(system_info, repo, releasever_set, manifest_xml, pid, current_arch, release_ver, master_release)
        else:
            result = self.yum_install_all_package(system_info, repo, releasever_set, manifest_xml, pid, base_pid, default_pid, current_arch, release_ver, platform_version, openshift_version, master_release)
        return result
