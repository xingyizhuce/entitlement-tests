import os
import sys
import json
import commands


# CDN test data
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel5.10/rhel5.10-rc-1.3.json
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel7.2/rhel-7.2-snapshot1-qa-cdn.json
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhcmsys8/15017-package-manifest.json

# RHN test data
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel5.10/rhel5.10-rc-1.3.json
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhcmsys8/15017-package-manifest.json

# EUS test data
# http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/eus/manifest/eus_filter_manifest.json


def usage():
    print "Usage: {0} cdn|CDN|eus|EUS|sat6|SAT6|sat5|SAT5|rhn|RHN|Container|container".format(sys.argv[0])
    exit(1)

def download_read_manifest(MANIFEST_PATH, MANIFEST_NAME, MANIFEST_URL):
    # Check if there is MANIFEST.json, if yes, delete it and re-download
    if os.path.exists(MANIFEST_PATH):
        if os.path.exists(MANIFEST_NAME):
            os.remove(MANIFEST_NAME)
            print "Deleting {0}".format(MANIFEST_NAME)
    else:
        os.mkdir(MANIFEST_PATH)
    cmd = 'wget --no-check-certificate %s -O %s' % (MANIFEST_URL, MANIFEST_NAME)
    print cmd
    ret, output = commands.getstatusoutput(cmd)
    if ret == 0:
        print "download manifest successfully."
    else:
        print "Failed to download manifest!"
        exit(1)

    # Open and load MANIFEST.json
    content = json.load(open(MANIFEST_NAME, 'r'))
    return content


class AnalyzeCDN(object):
    """
    1. Get base testing platforms from manifest, such as {"68":["Client-x86_64", "Client-i386"], "69":["Server-x86_64", "Server-i386"]}
    2. Get Jenkins upstream job parameter 'Product_ID' as PIDs and 'RHEL_Variant' as VARIANTs
    3. Get testing platform intersection
        If 'Product_ID' and 'RHEL_Variant' are both empty
        If 'Product_ID' is not empty, 'RHEL_Variant' is empty
        If 'Product_ID' is not empty, 'RHEL_Variant' is not empty
        If 'Product_ID' is empty, 'RHEL_Variant' is not empty
    4. Generate properties files(such as Server-x86_64.properties, Server-i386.properties), and write Variant, Arch, PID variables
    5. Append other parameters into properties files in order to pass down these params listed in properties files to downstream jobs
    6. Content of properties file:
        Variant=Server
        Arch=i386
        PID=90,83,69
        Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
        Distro=RHEL-7.2-20150904.0
        CDN=QA
        Candlepin=Stage
        Release_Version=7.2
        Test_Type=GA
    """
    def __init__(self):
        # Get Jenkins job parameters
        self.Distro = os.environ["Distro"]
        self.CDN = os.environ["CDN"]
        self.Candlepin = os.environ["Candlepin"]
        self.Test_Type = os.environ["Test_Type"]
        self.Release_Version = os.environ["Release_Version"]
        self.Product_ID = os.environ["Product_ID"]
        self.RHEL_variant = os.environ["RHEL_Variant"]
        self.Manifest_URL = os.environ["Manifest_URL"]

        # Download and load manifest
        self.Manifest_PATH = os.path.join(os.getcwd(), "manifest")
        self.Manifest_NAME = os.path.join(self.Manifest_PATH, "CDN_MANIFEST.json")
        self.content = download_read_manifest(self.Manifest_PATH, self.Manifest_NAME, self.Manifest_URL)

    def analyze_testing_platform(self):
        if "cdn" in self.content.keys():
            # Get testing platforms from provided mainfest
            platforms = {}
            for pid in self.content["cdn"]["products"]:
                arches = []
                for repo_path in self.content["cdn"]["products"][pid]["Repo Paths"]:
                
                    basearch = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["basearch"]
                    releasever = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["releasever"]
                    master_release = releasever.split(",")[0]
                    
                    if master_release == "8":
                        variant = "Server"
                    else:
                        variant = repo_path.split('/')[4]
                        if variant in ["server", "system-z", "power", "power-le", "arm"]:
                            variant = "Server"
                        if variant == "client":
                            variant = "Client"
                        if variant == "workstation":
                            variant = "Workstation"
                        if variant == "computenode":
                            variant = "ComputeNode"

                    # $arches: ['Server-ppc64le', 'ComputeNode-x86_64', 'Server-aarch64', 'Server-ppc64', 'Client-x86_64', 'Server-s390x', 'Server-x86_64', 'Workstation-x86_64']
                    if master_release == "8" and basearch == "x86_64":
                    # For RHEL8-x86_64, there are 3 variants: Server, Workstation, ComputeNode for the same pid like for GA: 479
                        arches.append("{0}-{1}".format(variant, basearch))
                        arches.append("{0}-{1}".format("Workstation", basearch))
                        arches.append("{0}-{1}".format("ComputeNode", basearch))
                    else:
                        arches.append("{0}-{1}".format(variant, basearch))

                    platforms[pid] = list(set(arches))

            print "PID, variants and arches list in manifest:"
            # Variable $platforms format: {"68":["Client-x86_64", "Client-i386"], "69":["Server-x86_64", "Server-i386"]}
            for i in platforms:
                print "{0}: {1}".format(i, platforms[i])

            # Jenkins upstream job parameter 'Product_ID' and 'RHEL_Variant' are both empty
            if self.Product_ID == "" and self.RHEL_variant == "":
                # Write testing properties files according to platforms listed in manifest
                for pid in platforms:
                    # Generate *.properties files used to trigger downstream jobs
                    for variant_arch in platforms[pid]:
                        self.__generate_properties(variant_arch, pid)

            # Jenkins upstream job parameter 'Product_ID' is not empty
            elif self.Product_ID != "":
                for pid in self.Product_ID.split(","):
                    if pid not in platforms.keys():
                        print "Warning: PID {0} is not in manifest!".format(pid)
                        continue

                    # Jenkins upstream job parameter 'Product_ID' is not empty, 'RHEL_Variant' is empty
                    if self.RHEL_variant == "":
                        # If VARIANTs is empty, then generate *.properties files according to variant_arch under pid in manifest
                        for variant_arch in platforms[pid]:
                            self.__generate_properties(variant_arch, pid)

                    # Jenkins upstream job parameter 'Product_ID' and 'RHEL_Variant' are both not empty
                    else:
                        # Delete those invalid arches which are not in manifest
                        variants = self.__check_arches(self.RHEL_variant, platforms[pid])

                        # Generate *.properties files used to trigger downstream jobs
                        for variant_arch in variants:
                            self.__generate_properties(variant_arch, pid)

            # Jenkins upstream job parameter Product_ID is empty, RHEL_Variant is not empty
            else:
                for pid in platforms.keys():
                    # Delete those invalid arches which are not in manifest
                    print "PID {0}:{1}".format(pid, platforms[pid])
                    variants = self.__check_arches(self.RHEL_variant, platforms[pid])

                    # Generate *.properties files used to trigger downstream jobs
                    for variant_arch in variants:
                        self.__generate_properties(variant_arch, pid)

            # Generate the final properties file
            output = commands.getoutput("ls | grep properties")
            if output != "":
                for prop_file in output.splitlines():
                    # Content of current properties file
                    # Variant=Server
                    # Arch=i386
                    # PID=90
                    # PID=83
                    # PID=69

                    # Merge several PIDs into one line, such as, merge the above PID lines to PID=90,83,69
                    pid_info = commands.getoutput("cat %s | grep PID | awk -F'=' '{print $2}'" % prop_file).replace('\n', ',')

                    # Delete PID lines from properties file
                    commands.getoutput("sed -i '/PID/d' {0}".format(prop_file))

                    # Content of final *.properties file
                    # Variant=Server
                    # Arch=i386
                    # PID=90,83,69
                    # Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
                    # Distro=RHEL-7.2-20150904.0
                    # CDN=QA
                    # Candlepin=Stage
                    # Release_Version=7.2
                    # Test_Type=GA
                    with open("{0}".format(prop_file), 'a+') as f:
                        # Re-write PID line into properties file
                        f.write("PID={0}\n".format(pid_info))

                        # Write other Jenkins job parameters into properties file
                        f.write("Manifest_URL={0}\n".format(self.Manifest_URL))
                        f.write("Distro={0}\n".format(self.Distro))
                        f.write("CDN={0}\n".format(self.CDN))
                        f.write("Candlepin={0}\n".format(self.Candlepin))
                        f.write("Release_Version={0}\n".format(self.Release_Version))
                        f.write("Test_Type={0}\n".format(self.Test_Type))
            else:
                print "No eligible testing platform provided!"
        else:
            print "No CDN part provided in manifest!"

    def __generate_properties(self, variant_arch, pid):
        # Content of current *.properties file
        # Variant=Server
        # Arch=i386
        # PID=69
        # PID=83
        variant = variant_arch.split("-")[0]
        arch = variant_arch.split("-")[1]
        file_name = "{0}.properties".format(variant_arch)
        if os.path.exists(file_name):
            with open(file_name, 'a+') as f:
                f.write("PID={0}\n".format(pid))
                print "write PID {0} into {1}.properties".format(pid, variant_arch)
        else:
            with open(file_name, 'a+') as f:
                f.write("Variant={0}\n".format(variant))
                f.write("Arch={0}\n".format(arch))
                f.write("PID={0}\n".format(pid))
                print "write variant({0}), arch({1}) and pid({2}) into {3}.properties".format(variant, arch, pid, variant_arch)

    def __check_arches(self, VARIANTs, VTs_manifest):
        variants = []
        for v in VARIANTs.split(","):
            if v in VTs_manifest:
                variants.append(v)
                print "Requested variant {0} is in manifest!".format(v)
            else:
                print "Warning: requested variant {0} is not in manifest!".format(v)
        return variants


class AnalyzeSAT6(object):
    """
    1. Get base testing platforms from manifest, such as {"68":["Client-x86_64", "Client-i386"], "69":["Server-x86_64", "Server-i386"]}
    2. Get Jenkins upstream job parameter 'Product_ID' as PIDs and 'RHEL_Variant' as VARIANTs
    3. Get testing platform intersection
        If 'Product_ID' and 'RHEL_Variant' are both empty
        If 'Product_ID' is not empty, 'RHEL_Variant' is empty
        If 'Product_ID' is not empty, 'RHEL_Variant' is not empty
        If 'Product_ID' is empty, 'RHEL_Variant' is not empty
    4. Generate properties files(such as Server-x86_64.properties, Server-i386.properties), and write Variant, Arch, PID variables
    5. Append other parameters into properties files in order to pass down these params listed in properties files to downstream jobs
    6. Content of properties file:
        Variant=Server
        Arch=i386
        PID=90,83,69
        Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
        Distro=RHEL-7.2-20150904.0
        SAT6_Server_Hostname=sat62-server.redhat.com
        SAT6_Server_IP=10.8.243.120
        SAT6_Server_Username=admin
        SAT6_Server_Password=admin
        SAT6_Server_OrgLabel=Entitlements_QE
        Release_Version=7.2
        Test_Type=GA
    """
    def __init__(self):
        # Get Jenkins job parameters
        self.Distro = os.environ["Distro"]
        self.SAT6_Server_Hostname = os.environ["SAT6_Server_Hostname"]
        self.SAT6_Server_IP = os.environ["SAT6_Server_IP"]
        self.SAT6_Server_Username = os.environ["SAT6_Server_Username"]
        self.SAT6_Server_Password = os.environ["SAT6_Server_Password"]
        self.SAT6_Server_OrgLabel = os.environ["SAT6_Server_OrgLabel"]
        self.Test_Type = os.environ["Test_Type"]
        self.Release_Version = os.environ["Release_Version"]
        self.Product_ID = os.environ["Product_ID"]
        self.RHEL_variant = os.environ["RHEL_Variant"]
        self.Manifest_URL = os.environ["Manifest_URL"]

        # Download and load manifest
        self.Manifest_PATH = os.path.join(os.getcwd(), "manifest")
        self.Manifest_NAME = os.path.join(self.Manifest_PATH, "CDN_MANIFEST.json")
        self.content = download_read_manifest(self.Manifest_PATH, self.Manifest_NAME, self.Manifest_URL)

    def analyze_testing_platform(self):
        if "cdn" in self.content.keys():
            # Get testing platforms from provided mainfest
            platforms = {}
            for pid in self.content["cdn"]["products"]:
                arches = []
                for repo_path in self.content["cdn"]["products"][pid]["Repo Paths"]:

                    basearch = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["basearch"]
                    releasever = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["releasever"]
                    master_release = releasever.split(",")[0]
                    
                    if master_release == "8":
                        variant = "Server"
                    else:
                        variant = repo_path.split('/')[4]
                        if variant in ["server", "system-z", "power", "power-le", "arm"]:
                            variant = "Server"
                        if variant == "client":
                            variant = "Client"
                        if variant == "workstation":
                            variant = "Workstation"
                        if variant == "computenode":
                            variant = "ComputeNode"
                    # $arches: ['Server-ppc64le', 'ComputeNode-x86_64', 'Server-aarch64', 'Server-ppc64', 'Client-x86_64', 'Server-s390x', 'Server-x86_64', 'Workstation-x86_64']
                    arches.append("{0}-{1}".format(variant, basearch))
                    platforms[pid] = list(set(arches))
            print "PID, variants and arches list in manifest:"
            # Variable $platforms format: {"68":["Client-x86_64", "Client-i386"], "69":["Server-x86_64", "Server-i386"]}
            for i in platforms:
                print "{0}: {1}".format(i, platforms[i])

            # Jenkins upstream job parameter 'Product_ID' and 'RHEL_Variant' are both empty
            if self.Product_ID == "" and self.RHEL_variant == "":
                # Write testing properties files according to platforms listed in manifest
                for pid in platforms:
                    # Generate *.properties files used to trigger downstream jobs
                    for variant_arch in platforms[pid]:
                        self.__generate_properties(variant_arch, pid)

            # Jenkins upstream job parameter 'Product_ID' is not empty
            elif self.Product_ID != "":
                for pid in self.Product_ID.split(","):
                    if pid not in platforms.keys():
                        print "Warning: PID {0} is not in manifest!".format(pid)
                        continue

                    # Jenkins upstream job parameter 'Product_ID' is not empty, 'RHEL_Variant' is empty
                    if self.RHEL_variant == "":
                        # If VARIANTs is empty, then generate *.properties files according to variant_arch under pid in manifest
                        for variant_arch in platforms[pid]:
                            self.__generate_properties(variant_arch, pid)

                    # Jenkins upstream job parameter 'Product_ID' and 'RHEL_Variant' are both not empty
                    else:
                        # Delete those invalid arches which are not in manifest
                        variants = self.__check_arches(self.RHEL_variant, platforms[pid])

                        # Generate *.properties files used to trigger downstream jobs
                        for variant_arch in variants:
                            self.__generate_properties(variant_arch, pid)

            # Jenkins upstream job parameter Product_ID is empty, RHEL_Variant is not empty
            else:
                for pid in platforms.keys():
                    # Delete those invalid arches which are not in manifest
                    print "PID {0}:{1}".format(pid, platforms[pid])
                    variants = self.__check_arches(self.RHEL_variant, platforms[pid])

                    # Generate *.properties files used to trigger downstream jobs
                    for variant_arch in variants:
                        self.__generate_properties(variant_arch, pid)

            # Generate the final properties file
            output = commands.getoutput("ls | grep properties")
            if output != "":
                for prop_file in output.splitlines():
                    # Content of current properties file
                    # Variant=Server
                    # Arch=i386
                    # PID=90
                    # PID=83
                    # PID=69

                    # Merge several PIDs into one line, such as, merge the above PID lines to PID=90,83,69
                    pid_info = commands.getoutput("cat %s | grep PID | awk -F'=' '{print $2}'" % prop_file).replace('\n', ',')

                    # Delete PID lines from properties file
                    commands.getoutput("sed -i '/PID/d' {0}".format(prop_file))

                    # Content of final *.properties file
                    # Variant=Server
                    # Arch=i386
                    # PID=90,83,69
                    # Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
                    # Distro=RHEL-7.2-20150904.0
                    # SAT6_Server_Hostname=sat62-server.redhat.com
                    # SAT6_Server_IP=10.8.243.120
                    # SAT6_Server_Username=admin
                    # SAT6_Server_Password=admin
                    # SAT6_Server_OrgLabel=Entitlements_QE
                    # Release_Version=7.2
                    # Test_Type=GA
                    with open("{0}".format(prop_file), 'a+') as f:
                        # Re-write PID line into properties file
                        f.write("PID={0}\n".format(pid_info))

                        # Write other Jenkins job parameters into properties file
                        f.write("Manifest_URL={0}\n".format(self.Manifest_URL))
                        f.write("Distro={0}\n".format(self.Distro))
                        f.write("SAT6_Server_Hostname={0}\n".format(self.SAT6_Server_Hostname))
                        f.write("SAT6_Server_IP={0}\n".format(self.SAT6_Server_IP))
                        f.write("SAT6_Server_Username={0}\n".format(self.SAT6_Server_Username))
                        f.write("SAT6_Server_Password={0}\n".format(self.SAT6_Server_Password))
                        f.write("SAT6_Server_OrgLabel={0}\n".format(self.SAT6_Server_OrgLabel))
                        f.write("Release_Version={0}\n".format(self.Release_Version))
                        f.write("Test_Type={0}\n".format(self.Test_Type))
            else:
                print "No eligible testing platform provided!"
        else:
            print "No CDN part provided in manifest!"

    def __generate_properties(self, variant_arch, pid):
        # Content of current *.properties file
        # Variant=Server
        # Arch=i386
        # PID=69
        # PID=83
        variant = variant_arch.split("-")[0]
        arch = variant_arch.split("-")[1]
        file_name = "{0}.properties".format(variant_arch)
        if os.path.exists(file_name):
            with open(file_name, 'a+') as f:
                f.write("PID={0}\n".format(pid))
                print "write PID {0} into {1}.properties".format(pid, variant_arch)
        else:
            with open(file_name, 'a+') as f:
                f.write("Variant={0}\n".format(variant))
                f.write("Arch={0}\n".format(arch))
                f.write("PID={0}\n".format(pid))
                print "write variant({0}), arch({1}) and pid({2}) into {3}.properties".format(variant, arch, pid, variant_arch)

    def __check_arches(self, VARIANTs, VTs_manifest):
        variants = []
        for v in VARIANTs.split(","):
            if v in VTs_manifest:
                variants.append(v)
                print "Requested variant {0} is in manifest!".format(v)
            else:
                print "Warning: requested variant {0} is not in manifest!".format(v)
        return variants


class AnalyzeSAT5(object):
    """
    1. Get base testing platforms from manifest, such as ['Client_x86_64', 'Server_s390x', 'Server_x86_64', 'Workstation_x86_64']
    2. Get Jenkins upstream job parameter 'RHEL_Variant' as VARIANTs
    3. Get testing platform intersection
       If 'RHEL_Variant' is empty
       If 'RHEL_Variant' is not empty
    4. Generate properties files, such as Server-x86_64.properties, Server-i386.properties, and write VARIANT and ARCH variables
    5. Append other parameters into properties files in order to pass down these params listed in properties files to downstream jobs
    6. Content of properties file:
        Variant=Server
        Arch=i386
        Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
        Distro=RHEL-7.2-20150904.0
        SAT5_Server=cloud-qe-16-vm-10.idmqe.lab.eng.bos.redhat.com
    """
    def __init__(self):
    
        try:
            self.RHEL_Variant = os.environ["RHEL_Variant"]
        except KeyError as e:
            self.RHEL_Variant = ""

        try:
            self.SAT5_Activation_Key = os.environ["SAT5_Activation_Key"]
        except KeyError as e:
            self.SAT5_Activation_Key = ""

        self.Product_Type = os.environ["Product_Type"]
        self.Manifest_URL = os.environ["Manifest_URL"]


        # Download and load manifest
        self.MANIFEST_PATH = os.path.join(os.getcwd(), "manifest")
        self.MANIFEST_NAME = os.path.join(self.MANIFEST_PATH, "SAT5_MANIFEST.json")
        self.content = download_read_manifest(self.MANIFEST_PATH, self.MANIFEST_NAME, self.Manifest_URL)

    def analyze_testing_platform(self):
        if "rhn" in self.content.keys():
            
            ### [1] Figure out the testing platforms (variant and arch) which are needed to do testing
            
            # 1. Get testing platforms from mainfest:
            platforms_in_manifest = []
            rhn = self.content["rhn"]
            for channel in rhn["channels"].keys():
                print channel

                if self.Product_Type == "RHEL8":
                    arch = channel.split("-")[1]
                    variant = "Server"
                else:
                    arch = channel.split("-")[1]
                    variant = channel.split("-")[2]
                    if variant == "server":
                        variant = "Server"
                    elif variant == "client":
                        variant = "Client"
                    elif variant == "workstation":
                        variant = "Workstation"
                    elif variant == "hpc":
                        variant = "ComputeNode"

                platforms_in_manifest.append("{0}-{1}".format(variant, arch))
                
            platforms_in_manifest = list(set(platforms_in_manifest))
            # ['Server-ppc64le', 'ComputeNode-x86_64', 'Server-aarch64', 'Server-ppc64', 
            # 'Client-x86_64', 'Server-s390x', 'Server-x86_64', 'Workstation-x86_64']
            print "Variants and arches list in manifest:", platforms_in_manifest

            # 2. Get the testing platforms which are needed to do testing
            testing_platforms = []
            
            # If 'RHEL_Variant' is empty, the testing platform is that got from manifest
            # If the 'RHEL_Variant' is not empty, the testing platform is the intersection of manifest and RHEL_Variant
            if self.RHEL_Variant == "":
                testing_platforms = platforms_in_manifest
            else:
                # Get the intersection of $platforms in manifest and $RHEL_Variant provided as parameter
                # RHEL_Variant: ['Server-i386', 'Server-x86_64']
                testing_platforms = list(set(self.RHEL_Variant.split(",")).intersection(set(platforms_in_manifest)))
            print "Need to do testing on the testing platforms:", testing_platforms

            ### [2] Fill the testing platforms into properties file
            
            # Generate properties file to trigger downstream jobs and pass down testing parameters
            # Properties files, such as Server-x86_64.properties, Server-i386.properties
            # Content of *.properties file like:
            # Variant=Server
            # Arch=i386
            for variant_arch in testing_platforms:
                variant = variant_arch.split("-")[0]
                arch = variant_arch.split("-")[1]
                with open("{0}.properties".format(variant_arch), 'w') as f:
                    # Write $variant to new properties file
                    f.write("Variant={0}\n".format(variant))

                    # Write $arch to new properties file
                    f.write("Arch={0}\n".format(arch))

            ### [3] Fill the activation key into relevant properties file
            if self.SAT5_Activation_Key != "":
                activation_key_dict = json.loads("{" + self.SAT5_Activation_Key + "}")

                for variant_arch in activation_key_dict.keys():
                    variant = variant_arch.split("-")[0]
                    arch = variant_arch.split("-")[1]
                    if variant == "server":
                        variant = "Server"
                    elif variant == "client":
                        variant = "Client"
                    elif variant == "workstation":
                        variant = "Workstation"
                    elif variant == "hpc":
                        variant = "ComputeNode"

                    activation_key = activation_key_dict[variant_arch]
                    with open("{0}-{1}.properties".format(variant, arch), 'a') as f:
                        # Write $activation_key to new properties file
                        print "Write the activation key '{0}' into the properties file '{1}-{2}.properties': ".format(
                                activation_key, variant, arch)
                        
                        f.write("SAT5_Activation_Key={0}\n".format(activation_key))
                    
        else:
            print "No RHN part provided in manifest!"

class AnalyzeRHN(object):
    """
    1. Get base testing platforms from manifest, such as ['Client_x86_64', 'Server_s390x', 'Server_x86_64', 'Workstation_x86_64']
    2. Get Jenkins upstream job parameter 'Channels' as CHANNELs and 'RHEL_Variant' as VARIANTs
    3. Get testing platform intersection
       If 'Channels' and 'RHEL_Variant' are both empty
       If 'Channels' is not empty, 'RHEL_Variant' is empty
       If 'Channels' is not empty, 'RHEL_Variant' is not empty
       If 'Channels' is empty, 'RHEL_Variant' is not empty
    4. Generate properties files, such as Server-x86_64.properties, Server-i386.properties, and write VARIANT and ARCH variables
    5. Append other parameters into properties files in order to pass down these params listed in properties files to downstream jobs
    6. Content of properties file:
        Variant=Server
        Arch=i386
        Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
        Distro=RHEL-7.2-20150904.0
        RHN=QA
    """
    def __init__(self):
        self.Distro = os.environ["Distro"]
        self.RHN = os.environ["RHN"]
        self.Channels = "" #os.environ["Channels"]
        self.RHEL_Variant = os.environ["RHEL_Variant"]
        self.Manifest_URL = os.environ["Manifest_URL"]

        # Download and load manifest
        self.MANIFEST_PATH = os.path.join(os.getcwd(), "manifest")
        self.MANIFEST_NAME = os.path.join(self.MANIFEST_PATH, "RHN_MANIFEST.json")
        self.content = download_read_manifest(self.MANIFEST_PATH, self.MANIFEST_NAME, self.Manifest_URL)

    def analyze_testing_platform(self):
        if "rhn" in self.content.keys():
            # Get testing platforms from mainfest
            platforms = []
            rhn = self.content["rhn"]
            for channel in rhn["channels"].keys():
                print channel
                arch = channel.split("-")[1]
                variant = channel.split("-")[2]
                if variant == "server":
                    variant = "Server"
                elif variant == "client":
                    variant = "Client"
                elif variant == "workstation":
                    variant = "Workstation"
                elif variant == "hpc":
                    variant = "ComputeNode"
                platforms.append("{0}-{1}".format(variant, arch))
            platforms = list(set(platforms))
            # ['Server-ppc64le', 'ComputeNode-x86_64', 'Server-aarch64', 'Server-ppc64', 
            # 'Client-x86_64', 'Server-s390x', 'Server_x86_64', 'Workstation-x86_64']
            print "Variants and arches list in manifest:", platforms

            testing_platforms = []
            if self.Channels == "" and self.RHEL_Variant == "":
                testing_platforms = platforms
            elif self.Channels != "":
                pass
            else:
                # Get the intersection of $platforms in manifest and $VARIANTs provided as parameter
                # VARIANTs: ['Server-i386', 'Server-x86_64']
                testing_platforms = list(set(self.RHEL_Variant.split(",")).intersection(set(platforms)))
            print "Need to do testing on:", testing_platforms

            # Generate properties file to trigger downstream jobs and pass down testing parameters
            # Content of *.properties file
            # Variant=Server
            # Arch=i386
            # Manifest_URL=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/manifests/rhel6.7/rhel-6.7-beta-blacklist-prod.json
            # Distro=RHEL-7.2-20150904.0
            # RHN=QA
            for file_content in testing_platforms:
                variant = file_content.split("-")[0]
                arch = file_content.split("-")[1]
                with open("{0}.properties".format(file_content), 'w') as f:
                    # Write $variant to new properties file
                    f.write("Variant={0}\n".format(variant))

                    # Write $arch to new properties file
                    f.write("Arch={0}\n".format(arch))

                    # Write other Jenkins job parameters to properties file
                    f.write("Manifest_URL={0}\n".format(self.Manifest_URL))
                    f.write("Distro={0}\n".format(self.Distro))
                    f.write("RHN={0}\n".format(self.RHN))
        else:
            print "No RHN part provided in manifest!"


class AnalyzeContainer(object):
    """
    1. The properties files for all testing variants are store under entitlement-test/CI/jobs/Container/upstream_trigger_files/
    2. There are 4 default parameters in properties files:
        Product_Type=RHEL8
        Container=RHEL6,RHEL7,RHEL8
        Variant=Server
        Arch=x86_64
    3. Write other testing parameters into properties files:
        Test_Type=Beta
        CDN=Prod
        Candlepin=Stage
        Distro=RHEL-8.0
        Docker_image_id=8.0-608
    4. Delete untesting properties files if parameter Hosts is set
    """
    def __init__(self):
        # Get Jenkins job parameters
        self.Distro_RHEL7 = os.environ["Distro_RHEL7"]
        self.Distro_RHEL8 = os.environ["Distro_RHEL8"]
        self.Distro_RHEL_ALT = os.environ["Distro_RHEL_ALT"]
        self.Docker_image_id = os.environ["Docker_image_id"]
        self.Test_Type = os.environ["Test_Type"]
        self.CDN = os.environ["CDN"]
        self.Candlepin = os.environ["Candlepin"]
        self.Hosts = os.environ["Hosts"]

        # the properties for all variants need testing
        self.properties_file = [
            "RHEL7-x86_64.properties",
            "RHEL8-x86_64.properties",
            "RHEL7-ppc64le.properties",
            "RHEL8-ppc64le.properties",
            "RHEL-ALT-ppc64le.properties",
            "RHEL8-aarch64.properties",
            "RHEL-ALT-aarch64.properties",
            "RHEL7-s390x.properties",
            "RHEL8-s390x.properties",
            "RHEL-ALT-s390x.properties"
        ]

    def analyze_testing_platform(self):
        for prop_file in self.properties_file:
            with open("{0}".format(prop_file), 'a+') as f:
                if "RHEL7" in prop_file:
                    f.write("Distro={0}\n".format(self.Distro_RHEL7))
                elif "RHEL8" in prop_file:
                    f.write("Distro={0}\n".format(self.Distro_RHEL8))
                else:
                    f.write("Distro={0}\n".format(self.Distro_RHEL_ALT))
                f.write("CDN={0}\n".format(self.CDN))
                f.write("Candlepin={0}\n".format(self.Candlepin))
                f.write("Test_Type={0}\n".format(self.Test_Type))
                f.write("Docker_image_id={0}\n".format(self.Docker_image_id))

        if self.Hosts:
            hosts_set = ["{0}.properties".format(i) for i in self.Hosts.split(",")]
            # Delete other files not needed testing
            files_delete = list(set(self.properties_file) - set(hosts_set))
            for i in files_delete:
                os.remove(i)
                print "Deleted file {0}.".format(i)


class GetPID(object):
    def __init__(self):
        self.PID = []
        self.Variant = os.environ["Variant"]
        self.Arch = os.environ["Arch"]
        self.Manifest_URL = os.environ["Manifest_URL"]

        # Download and load manifest
        self.MANIFEST_PATH = os.path.join(os.getcwd(), "manifest")
        self.MANIFEST_NAME = os.path.join(self.MANIFEST_PATH, "MANIFEST.json")
        self.content = download_read_manifest(self.MANIFEST_PATH, self.MANIFEST_NAME, self.Manifest_URL)

    def get_pid(self):
        if "cdn" in self.content.keys():
            # Get PIDs need testing on current $Variant and $Arch
            for pid in self.content["cdn"]["products"]:
                for repo_path in self.content["cdn"]["products"][pid]["Repo Paths"]:
                
                    basearch = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["basearch"]
                    releasever = self.content["cdn"]["products"][pid]["Repo Paths"][repo_path]["releasever"]
                    master_release = releasever.split(".")[0]
                
                    if master_release == "8":
                        if self.Arch == basearch:
                            self.PID.append(pid)
                            break
                    else:
                        variant = repo_path.split('/')[4]
                        if variant in ["server", "system-z", "power", "power-le", "arm"]:
                            variant = "Server"
                        if variant == "client":
                            variant = "Client"
                        if variant == "workstation":
                            variant = "Workstation"
                        if variant == "computenode":
                            variant = "ComputeNode"
                        if self.Variant == variant and self.Arch == basearch:
                            self.PID.append(pid)
                            break

            # Write $PID into file PID.txt
            with open("PID.txt", 'w') as f:
                f.write(",".join(self.PID))
        else:
            print "No CDN part provided in manifest!"


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        if sys.argv[1] == "cdn":
            cdn = AnalyzeCDN()
            cdn.analyze_testing_platform()
        elif sys.argv[1] == "eus":
            eus = AnalyzeCDN()
            eus.analyze_testing_platform()
        elif sys.argv[1] == "sat6":
            sat6 = AnalyzeSAT6()
            sat6.analyze_testing_platform()
        elif sys.argv[1] == "sat5":
            rhn = AnalyzeSAT5()
            rhn.analyze_testing_platform()
        elif sys.argv[1] == "rhn":
            rhn = AnalyzeRHN()
            rhn.analyze_testing_platform()
        elif sys.argv[1] == "pid":
            GetPID().get_pid()
        elif sys.argv[1] in ["container", "Container"]:
            container = AnalyzeContainer()
            container.analyze_testing_platform()
        else:
            pass

