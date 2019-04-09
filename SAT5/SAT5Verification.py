import logging
import random
import datetime
import time
import json

from Utils.RemoteSSH import RemoteSSH
from Utils.EntitlementBase import EntitlementBase

from SAT5.SAT5ReadXML import SAT5ReadXML
from SAT5 import variant
from SAT5 import arch


# Create logger
logger = logging.getLogger("entLogger")

try:
    from kobo.rpmlib import parse_nvra
except ImportError:
    logger.info('Need to install packages kobo kobo-rpmlib koji firstly')

class SAT5Verification(EntitlementBase):
    def install_packages(self, system_info):
        # Install packages for RHEL8
        RemoteSSH().run_cmd(system_info, "yum install -y wget")
        RemoteSSH().run_cmd(system_info, "yum install -y python3")
        RemoteSSH().run_cmd(system_info, "yum install -y rhn-setup")

    def download_cert(self, system_info, sat5_server):
        cmd_wget_check = "wget"
        retwgetcheck, outputwgetcheck = RemoteSSH().run_cmd(system_info, cmd_wget_check, "Trying to chech wget exit or not")
        if retwgetcheck != 0:
            cmd = "yum install -y wget"
            retwget, outputwget = RemoteSSH().run_cmd(system_info, cmd, "Trying to install wget")
        cert_download_path = "/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT"
        RemoteSSH().run_cmd(system_info, "rm -rf {0}".format(cert_download_path), "Trying to remove old cert {0} before download it...".format(cert_download_path))
        cmd = "wget http://%s/pub/RHN-ORG-TRUSTED-SSL-CERT -O %s" % (sat5_server, cert_download_path)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to download cert {0}...".format(cert_download_path))
        if ret == 0:
            logger.info("It's successful to download ssl CA cert {0}.".format(cert_download_path))
            return True
        else:
            logger.error("Test Failed - Failed to download ssl CA cert {0}.".format(cert_download_path))
            return False

    def update_up2date(self, system_info, server_url):
        # sslCACert default value:
        # RHEL6: sslCACert=/usr/share/rhn/RHNS-CA-CERT
        # RHEL7: sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
        up2date_path = "/etc/sysconfig/rhn/up2date"
        cert = "/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT"
        #cert = "/usr/share/rhn/RHNS-CA-CERT"
        cmd = "sed -i -e '/sslCACert=/d' -e '/^sslCACert/a\sslCACert={0}' {1}".format(cert, up2date_path)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set sslCACert in {0}...".format(up2date_path))
        if ret == 0:
            logger.info("It's successful to set sslCACert to {0} in {1}.".format(cert, up2date_path))
        else:
            logger.error("Test Failed - Failed to set sslCACert to {0} in {1}.".format(cert, up2date_path))
            return False

        cmd = "sed -i -e '/serverURL=/d' -e '/^serverURL/a\serverURL={0}' {1}".format(server_url, up2date_path)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to set serverUrl in {0}...".format(up2date_path))
        if ret == 0:
            logger.info("It's successful to set serverURL to {0} in {1}.".format(server_url, up2date_path))
        else:
            logger.error("Test Failed - Failed to set serverURL to {0} in {1}.".format(server_url, up2date_path))
            return False

        return True

    def register(self, system_info, username, password, server_url):
        cmd = "rhnreg_ks --username=%s --password=%s --serverUrl=%s" % (username, password, server_url)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to register to Satellite 5 server...")
        if ret == 0:
            logger.info("It's successful to register to Satellite 5 server.")
            return True
        else:
            # Error Message:
            # Invalid username/password combination
            logger.error("Test Failed - Failed to register with Satellite 5 server.")
            return False

    def register_by_activationkey(self, system_info, activation_key):
        # Register with server
        cmd = "rhnreg_ks --activationkey={0}".format(activation_key)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to register with server...")
        if ret == 0:
            logger.info("It's successful to register.")
            return True
        else:
            logger.error("Test Failed - Failed to register.")
            return False

    def isregistered(self, system_info):
        cmd = "ls /etc/sysconfig/rhn/systemid"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check if registered to Satellite 5 server...")
        if ret == 0:
            logger.info("The system is registered to Satellite 5 server now.")
            return True
        else:
            logger.info("The system is not registered to Satellite 5 server now.")
            return False

    def unregister(self, system_info, product_type):
        cmd = "rm -rf /etc/sysconfig/rhn/systemid"
        (ret1, output1) = RemoteSSH().run_cmd(system_info, cmd, "Trying to unregister from Satellite 5 - delete systemid...")

        if product_type == "RHEL8":
            if ret1 == 0:
                logger.info("It's successful to unregister from Satellite 5 server.")
                return True
            else:
                logger.error("Test Failed - Failed to unregister from Satellite 5 server.")
                return False
        else:
            cmd = "sed -i 's/enabled = 1/enabled = 0/' /etc/yum/pluginconf.d/rhnplugin.conf"
            (ret2, output2) = RemoteSSH().run_cmd(system_info, cmd, "Trying to unregister from Satellite 5 - modify rhnplugin.conf...")

            if ret1 == 0 and ret2 == 0:
                logger.info("It's successful to unregister from Satellite 5 server.")
                return True
            else:
                logger.error("Test Failed - Failed to unregister from Satellite 5 server.")
                return False

    def clean_yum_cache(self, system_info):
        # Clean yum cache
        cmd = "rm -rf /var/cache/yum/*"
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to clean the yum cache.")
        if ret == 0:
            logger.info("It's successful to clean the yum cache.")
            return True
        else:
            logger.error("Test Failed - Failed to clean yum cache.")
            return False

    def get_base_channel(self, test_type, variant, arch, master_release):
    
        base_channel = ""
        if test_type.lower() == "beta":
                if master_release == "8":
                    base_channel = "rhel-{0}-{1}-{2}-{3}".format(arch, "baseos", master_release,"beta")
                    base_channel += ","
                    base_channel += "rhel-{0}-{1}-{2}-{3}".format(arch, "appstream", master_release,"beta")
                else:
                    if variant == "ComputeNode":
                        base_channel = "rhel-{0}-{1}-{2}-{3}".format(arch, "hpc-node", master_release,"beta")
                    else:
                        base_channel = "rhel-{0}-{1}-{2}-{3}".format(arch, self.variant.lower(), master_release,"beta")
                
        elif test_type.lower() == "htb":
                if master_release == "8":
                    base_channel = "rhel-{0}-{1}-{2}-{3}".format(arch, "baseos", master_release,"htb")
                    base_channel += ","
                    base_channel += "rhel-{0}-{1}-{2}-{3}".format(arch, "appstream", master_release,"htb")
                else:
                    base_channel = "rhel-{0}-{1}-{2}-{3}".format(arch, self.variant.lower(), master_release,"htb")

        else:
                if master_release == "8":
                    base_channel = "rhel-{0}-{1}-{2}".format(arch, "baseos", master_release)
                    base_channel += ","
                    base_channel += "rhel-{0}-{1}-{2}".format(arch, "appstream", master_release)
                else:
                    if self.variant == "ComputeNode":
                        base_channel = "rhel-{0}-{1}-{2}".format(arch, "hpc-node", master_release)
                    else:
                        base_channel = "rhel-{0}-{1}-{2}".format(arch, self.variant.lower(), master_release)
                       
        return base_channel

    def add_channels(self, system_info, username, password, channels):
        channel_default = []
        cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list the channel which was added by default after register...")
        if ret == 0:
            channel_default = output.splitlines()
            logger.info("It's successful to get default channel from Satellite 5 server: %s" % channel_default)

        if not isinstance(channels, list):
            channels = [channels]

        result = True
        for channel in channels:
            if channel not in channel_default:
                # Add channel
                cmd = "rhn-channel --add --channel=%s --user=%s --password=%s" % (channel, username, password)
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "add channel %s" % channel)

            cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check if channel {0} was added successfully...".format(channel))
            channel_added = output.splitlines()

            if ret == 0 and channel in channel_added:
                logger.info("It's successful to add channel %s." % channel)
                result &= True
            else:
                logger.error("Test Failed - Failed to add channel %s." % channel)
                result &= False
        return result

    def remove_channels(self, system_info, username, password, channels=None):
        if channels == None:
            cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to list all added channel already...")
            channels = output.splitlines()

        if not isinstance(channels, list):
            channels = [channels]

        result = True
        for channel in channels:
            cmd = "rhn-channel --remove --channel=%s --user=%s --password=%s" % (channel, username, password)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to remove channel {0}".format(channel))
            if ret == 0:
                logger.info("It's successful to remove channel %s." % channel)
                result &= True
            else:
                logger.info("Test Failed - Failed to remove channel %s." % channel)
                result &= False
        return result

    def get_channels_from_manifest(self, manifest_xml, current_arch, variant, product_type):
        # Get all channels from manifest which need testing
        if product_type == "RHEL8":
            repo_filter = "-%s-" % (current_arch)
        else:
            if variant == "ComputeNode":
                variant = "hpc"
            repo_filter = "%s-%s" % (current_arch, variant.lower())
        logger.info("Testing repo filter: {0}".format(repo_filter))

        all_channel_list = SAT5ReadXML().get_channel_list(manifest_xml)
        channel_list = [channel for channel in all_channel_list if repo_filter in channel]

        if len(channel_list) == 0:
            logger.error("Got 0 channel from packages manifest")
            logger.error("Test Failed - Got 0 channel from packages manifest.")
            return []
        else:
            logger.info('Got {0} channels from packages manifest:'.format(len(all_channel_list)))
            self.print_list(all_channel_list)
            return channel_list

    def verify_channels(self, system_info, manifest_xml, username, password, current_arch, variant, product_type):
        # Check if all channels listed in manifest are available in SAT5. Note:
        # For now, this function can be only tested on RHEL6 or newer RHEL version, 
        # as there is no param --available-channels on RHEL5
        
        logger.info("--------------- Begin to verify channel ---------------")
        
        # [1] Get all available channels which are not added
        available_channels = []
        cmd = "rhn-channel --available-channels --user=%s --password=%s" % (username, password)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get available channels with command rhn-channel...")
        if ret == 0:
            available_channels = output.splitlines()
        else:
            logger.error("Failed to get available channels.")

        # [2] Get all channels which are already added
        added_channels = []
        cmd = "rhn-channel --list --user=%s --password=%s" % (username, password)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to get added channels with command rhn-channel...")
        if ret == 0:
            added_channels = output.splitlines()
        else:
            logger.error("Failed to get added channels.")

        channels = available_channels + added_channels

        # [3] Get all channels from manifest which are needed to test
        channels_manifest = self.get_channels_from_manifest(manifest_xml, current_arch, variant, product_type)
        
        # Check if above channels [3] are in [1]+[2] to see if all channels listed in manifest are available is SAT5
        list1 = self.cmp_arrays(channels_manifest, channels)
        if len(list1) > 0:
            logger.error("Failed to verify below channels which are in provided manifest but not available in SAT5:")
            self.print_list(list1)
            
            logger.error("--------------- End to verify channel: FAIL ---------------")
            logger.error("Test Failed - Failed to verify channel.")
            return False, list1
        else:
            logger.info("It's successful to verify channel and all channels listed in manifest are available in SAT5!")
            logger.info("--------------- End to verify channel: PASS ---------------")
            return True, list1

    def smoke_installation(self, system_info, manifest_xml, channel, manifestfaileddict):
        # Verify package is installable or downloadable from a channel
        logger.info("--------------- Begin to verify package installation for channel {0} ---------------".format(channel))

        # Get all packages already installed in testing system before installation testing
        system_pkglist = self.get_sys_pkglist(system_info)

        # Store the failed packages when 'yum remove'.
        remove_failed_pkglist = []

        # Get packages from manifest
        rpm_src_package_list = SAT5ReadXML().get_package_list(manifest_xml, channel)
        package_install_failed_list = []
        source_download_failed_list = []

        # Install rpm packages
        package_list = rpm_src_package_list[0]
        result = True
        if len(package_list) == 0:
            logger.warning("There is no package need to install for channel '{0}'.".format(channel))
            return result

        logger.info("There are {0} packages need to install for channel '{1}'.".format(len(package_list), channel))
        self.print_list(package_list)

        # Get one package randomly to download
        pkg_name = random.sample(package_list, 1)[0]
        src_list = rpm_src_package_list[1]
        cmd = "yum install -y %s" % pkg_name
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum install package '{0}' of channel '{1}'".format(pkg_name, channel))

        if ret == 0:
            if ("Complete!" in output) or ("Nothing to do" in output) or ("conflicts" in output):
                logger.info("It's successful to install package '{0}' of channel '{1}'.".format(pkg_name, channel))
            else:
                logger.error("Test Failed - Failed to install package '{0}' of channel '{1}'.".format(pkg_name, channel))
                result = False
        else:
            #if "conflicts" in output:
                #logger.info("It's successful to install package  '{0}' of channel '{1}'.".format(pkg_name, channel))
            #else:
                logger.error("Test Failed - Failed to install package '{0}' of channel '{1}'.".format(pkg_name, channel))
                package_install_failed_list.append("{0}.{1}".format(pkg_name, "rpm"))
                result = False
        #remove_pkg = pkg_name.split(".")[0][:-2]
        # rpkg =  pkg_name.split(".")[0]
        # remove_pkg = rpkg[:rpkg.rindex("-")]
        rpkg = parse_nvra(pkg_name)
        remove_pkg = rpkg["name"]
        if result:
            logger.info("Remove package is:{0}".format(remove_pkg))
            if remove_pkg not in system_pkglist:
                # Remove package if it is not in the system package list.
                # It is used to solve the dependency issue which describe in https://bugzilla.redhat.com/show_bug.cgi?id=1272902.
                if not self.remove_pkg(system_info, pkg_name, channel):
                    remove_failed_pkglist.append(pkg_name)
                    logger.warning("Failed to remove '{0}' of channel '{1}'.".format(pkg_name, channel))
            else:
                logger.info("Package {0} is a systerm package can not be removed".format(pkg_name))

        if len(remove_failed_pkglist) != 0:
            logger.warning("Failed to remove following '{0}' packages for channel '{1}':".format(len(remove_failed_pkglist), channel))
            self.print_list(remove_failed_pkglist)
        if len(package_install_failed_list) != 0:
            manifestfaileddict["rhn"]["channels"].setdefault(channel, [ ]).extend(package_install_failed_list)
        # Download source packages
        #src_list = rpm_src_package_list[1]
        if len(src_list) == 0:
            logger.info("There is no package needed to download for channel '{0}'.".format(channel))
        else:
            logger.info("There are {0} packages needed to download for channel '{1}'.".format(len(src_list), channel))
            self.print_list(src_list)
            # Get one package randomly to download
            source_pkg_name = random.sample(src_list, 1)[0]
            cmd = "yumdownloader --destdir /tmp --source %s" % source_pkg_name
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum download package '{0}' of channel '{1}'".format(source_pkg_name, channel))

            if ret == 0:
                logger.info("It's successful to download package '{0}' of channel '{1}'.".format(source_pkg_name, channel))
            else:
                logger.error("Test Failed - Failed to download rpm source package '{0}' of channel '{1}'.".format(source_pkg_name, channel))
                source_download_failed_list.append("{0}.{1}.{2}".format(source_pkg_name, "src", "rpm"))
                result = False

        if len(source_download_failed_list) != 0:
            manifestfaileddict["rhn"]["channels"].setdefault(channel, [ ]).extend(source_download_failed_list)
        if result:
            logger.info("--------------- End to verify packages installation for channel '{0}': PASS ---------------".format(channel))
        else:
            logger.error("--------------- End to verify packages installation for channel '{0}': FAIL ---------------".format(channel))
        return result


    def installation(self, system_info, manifest_xml, channel, manifestfaileddict ,starttime):
        # Install binary packages with yum
        # There are source rpms in channels, but they can only be downloaded through the customer portal web site.  They aren't exposed to yum/yumdownloader/repoquery.
        # RHN APIs that can be used to query the source packages available, but the APIs are only available to RHN admins. So, let's not worry about SRPMs for now.
        # Download source rpms from the customer portal web site - ignored for now
        logger.info("--------------- Begin to verify packages full installation for channel {0} ---------------".format(channel))
        extendtime_flag = False
        # Get all packages already installed in testing system before installation testing
        system_pkglist = self.get_sys_pkglist(system_info)

        # Store the failed packages when 'yum remove'.
        remove_failed_pkglist = []
        check_system_pkgdict = {}
        # Get packages from manifest
        rpm_src_package_list = SAT5ReadXML().get_package_list(manifest_xml, channel)
        package_install_failed_list = []
        source_download_failed_list = []

        # Get rpm packages
        package_list = rpm_src_package_list[0]
        if len(package_list) == 0:
            logger.warning("There is no package need to install for channel '{0}'.".format(channel))
        else:
            logger.info("There are {0} packages need to install for channel '{1}'.".format(len(package_list), channel))
            self.print_list(package_list)
        result = True
        number = 0
        total_number = len(package_list)
        for pkg in package_list:

            # extendtesttime when runtime is over 80 hours
            currenttime = datetime.datetime.now()
            costtime = (currenttime - starttime).seconds
            if costtime > 70000:
                logger.info("-------Starttime-------")
                logger.info(starttime)
                logger.info("-------currenttime-------")
                logger.info(currenttime)
                logger.info("-------costtime-------")
                logger.info(costtime)
                cmd = "extendtesttime.sh 99"
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to extend system reservation time...")
                if ret == 0:
                    extendtime_flag = True
                    starttime = datetime.datetime.now()
                    logger.info("Succeed to extend reservation time for beaker system for advanced testing.")
                else:
                    logger.warning("Failed to extend reservation time, please ignore this error if it's not beaker system.")

            number += 1
            cmd = "yum install -y %s" % pkg
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum install package '{0}' of channel '{1}'".format(pkg, channel))

            if ret == 0:
                if ("Complete!" in output) or ("Nothing to do" in output) or ("conflicts" in output):
                    logger.info("It's successful to install package [{0}/{1}] '{2}' of channel '{3}'.".format(number, total_number, pkg, channel))
                else:
                    logger.error("Test Failed - Failed to install package [{0}/{1}] '{2}' of channel '{3}'.".format(number, total_number, pkg, channel))
                    result = False
            else:
                #if "conflicts" in output:
                    #logger.info("It's successful to install package [{0}/{1}] '{2}' of channel '{3}'.".format(number, total_number, pkg, channel))
                #else:
                    logger.error("Test Failed - Failed to install package [{0}/{1}] '{2}' of channel '{3}'.".format(number, total_number, pkg, channel))
                    package_install_failed_list.append("{0}.{1}".format(pkg, "rpm"))
                    result = False
            #remove_pkg = pkg.split(".")[0][:-2]
            #rpkg =  pkg.split(".")[0]
            #remove_pkg = rpkg[:rpkg.rindex("-")]
            rpkg = parse_nvra(pkg)
            remove_pkg = rpkg["name"]
            if ret == 0:
                logger.info("Remove package is {0}".format(remove_pkg))
                if remove_pkg not in system_pkglist:
                    # Remove package if it is not in the system package list.
                    # It is used to solve the dependency issue which describe in https://bugzilla.redhat.com/show_bug.cgi?id=1272902.
                    if not self.remove_pkg(system_info, pkg, channel):
                        remove_failed_pkglist.append(pkg)
                        logger.warning("Failed to remove '{0}' of channel '{1}'.".format(pkg, channel))
                else:
                    check_system_pkgdict[remove_pkg] = pkg
                    logger.info("Package {0} is a systerm package can not be removed".format(pkg))

            if number % 100 ==0:
                time.sleep(60)
        if len(remove_failed_pkglist) != 0:
            logger.warning("Failed to remove following '{0}' packages for channel '{1}':".format(len(remove_failed_pkglist), channel))
            #self.print_list(remove_failed_pkglist)
        if len(package_install_failed_list) != 0:
            manifestfaileddict["rhn"]["channels"].setdefault(channel, [ ]).extend(package_install_failed_list)
        logger.warning("Failed to install '{0}' packages for channel '{1}':".format(len(package_install_failed_list), channel))
        # if len(check_system_pkgdict) != 0:
        #     logger.warning("system packages '{0}'  for channel '{1}':".format(len(check_system_pkgdict), channel))
        #     logger.warning(check_system_pkgdict)
        # Download source packages
        src_list = rpm_src_package_list[1]
        if len(src_list) == 0:
            logger.warning("There is no package needed to download for channel '{0}'.".format(channel))
        else:
            logger.info("There are {0} packages needed to download for channel '{1}'.".format(len(src_list), channel))
            self.print_list(src_list)
            number_src = 0
            total_number_src = len(src_list)
            for srcpkg in src_list:
                number_src += 1
                cmd = "yumdownloader --destdir /tmp --source %s" % srcpkg
                ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum download package '{0}' of channel '{1}'".format(srcpkg, channel))

                if ret == 0:
                    logger.info("It's successful to download package [{0}/{1}] '{2}' of channel '{3}'.".format(number_src, total_number_src, srcpkg, channel))
                else:
                    logger.error("Test Failed - Failed to download rpm source package [{0}/{1}] '{2}' of channel '{3}'.".format(number_src, total_number_src, srcpkg, channel))
                    source_download_failed_list.append("{0}.{1}.{2}".format(srcpkg, "src", "rpm"))
                    result = False

        if len(source_download_failed_list) != 0:
            manifestfaileddict["rhn"]["channels"].setdefault(channel, [ ]).extend(source_download_failed_list)
        if result:
            logger.info("--------------- End to verify packages full installation for channel '{0}': PASS ---------------".format(channel))
        else:
            logger.error("--------------- End to verify packages full installation for channel '{0}': FAIL ---------------".format(channel))

        logger.info("--------------- Yum clean all------------" )
        #yumclean_cmd = "yum clean all"
        #ret, output = RemoteSSH().run_cmd(system_info, yumclean_cmd, "Yum clean all")
        #if ret == 0:
        #    logger.info("--------------- Yum clean all successfully------------")
        #else:
        #    logger.warning("--------------- Yum clean all failed------------")
        return result,extendtime_flag

    def yum_install_one_package(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, current_arch, release_ver):
        # Install one package with yum
        formatstr = "%{name}"
        cmd = '''repoquery --pkgnarrow=available --all --repoid=%s --qf "%s" %s''' % (repo, formatstr, releasever_set)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to repoquery available packages...", timeout=3600)

        if ret == 0:
            logger.info("It's successful to repoquery available packages for the repo {0}.".format(repo))
            pkgs = output.strip().splitlines()
            if len(pkgs) == 0:
                logger.info("No available package for the repo {0}.".format(repo))
                return True
        else:
            logger.error("Test Failed - Failed to repoquery available packages for the repo {0}.".format(repo))
            return False

        # Get all packages list from packages manifest
        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, current_arch, release_ver, "name")
        if len(manifest_pkgs) == 0:
            logger.info("There is no package in manifest for pid:repo {0}:{1} on release {2}".format(pid, repo, release_ver))
            return True

        # Get a available packages list which are uninstalled got from repoquery and also in manifest.
        avail_pkgs = list(set(pkgs) & set(manifest_pkgs))
        if len(avail_pkgs) == 0:
            logger.error("There is no available packages for repo {0}, as all packages listed in manifest have been installed before, please uninstall first, then re-test!".format(repo))
            return False

        # Get one package randomly to install
        pkg_name = random.sample(avail_pkgs, 1)[0]
        cmd = "yum -y install --skip-broken %s %s" % (pkg_name, releasever_set)

        checkresult = True
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yum install package {0}...".format(pkg_name))
        if ret == 0 and ("Complete!" in output or "Nothing to do" in output):
            logger.info("It's successful to yum install package {0} of repo {1}.".format(pkg_name, repo))

            if ("optional" not in repo) and ("supplementary" not in repo) and ("debug" not in repo):
                if base_pid == pid:
                    logger.info("For RHEL testing, skip product cert testing, the default rhel product cert is located in the folder '/etc/pki/product-default/', and will not be downloaded into '/etc/pki/product/' anew.")
                else:
                    checkresult = self.verify_productid_in_product_cert(system_info, pid, base_pid)
        else:
            logger.error("Test Failed - Failed to yum install package {0} of repo {1}.".format(pkg_name, repo))
            checkresult = False
        return checkresult



    def yum_download_one_source_package(self, system_info, repo, releasever_set, manifest_xml, pid, base_pid, current_arch, release_ver):
        # Download one package for source repo with yumdownloader
        formatstr = "%{name}-%{version}-%{release}.src"
        cmd = '''repoquery --pkgnarrow=available --all --repoid=%s --archlist=src --qf "%s" %s''' % (repo, formatstr, releasever_set)
        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to repoquery available source packages for repo {0}...".format(repo), timeout=3600)

        # Delete string "You have mail in /var/spool/mail/root" from repoquery output
        output = output.split("You have mail in")[0]

        if ret == 0:
            logger.info("It's successful to repoquery available source packages for the repo '%s'." % repo)
            pkg_list = output.strip().splitlines()
            if len(pkg_list) == 0:
                logger.info("No available source package for repo {0}.".format(repo))
                return True
        else:
            logger.error("Test Failed - Failed to repoquery available source packages for the repo {0}.".format(repo))
            return False

        manifest_pkgs = self.get_package_list_from_manifest(manifest_xml, pid, repo, current_arch, release_ver, "full-name")
        if len(manifest_pkgs) == 0:
            logger.info("There is no package in manifest for pid:repo {0}:{1} on release {2}".format(pid, repo, release_ver))
            return False

        # Get a available package list which are uninstalled got from repoquery and also in manifest.
        avail_pkgs = list(set(pkg_list) & set(manifest_pkgs))
        if len(avail_pkgs) == 0:
            logger.error("There is no available package for repo {0}!".format(repo))
            return True

        # Get one package randomly to download
        pkg_name = random.sample(avail_pkgs, 1)[0]
        cmd = "yumdownloader --destdir /tmp --source %s %s" % (pkg_name, releasever_set)

        ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to yumdownloader source package {0}...".format(pkg_name))

        if ret == 0 and ("Trying other mirror" not in output):
            cmd = "ls /tmp/{0}*".format(pkg_name)
            ret, output = RemoteSSH().run_cmd(system_info, cmd, "Trying to check downloaded source package {0} just now...".format(pkg_name))

            if ret == 0 and pkg_name in output:
                logger.info("It's successful to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                download_result = True
            else:
                logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
                download_result = False
        else:
            logger.error("Test Failed - Failed to yumdownloader source package {0} of repo {1}.".format(pkg_name, repo))
            download_result = False

        cmd = "rm -rf /tmp/*.rpm"
        RemoteSSH().run_cmd(system_info, cmd, "Trying to delete source package {0}...".format(pkg_name))
        return download_result


"""Method to write rpm mapping channel to manifest file"""
def writeFailedToManifest(channel,rpm,manifestfaileddict,rpm_map_channelflagdict):

    manifestfaileddict["rhn"]["channels"].setdefault(channel, [ ]).append(rpm)
