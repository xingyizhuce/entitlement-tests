###########################
#  How to use this script #
###########################
# 1. Prepare one RHEL6 Server x86_64 system, as this script can be only run this system.
# 2. . $script_name


#############################################
# 1. Prepare a RHEL 6 Server x86_64 system: #
#############################################
# Check if package easy_install is installed, install easy_install if not
easy_install --version > /dev/null
if [ $? -eq 1 ]; then
    echo  "Install easy_install..."
    echo "# wget https://pypi.python.org/pypi/ez_setup"; wget https://pypi.python.org/pypi/ez_setup
    echo "# python ez_setup"; python ez_setup;
fi

# Install pip
echo ; echo "Install pip..."; echo "# easy_install pip"; easy_install pip

# Install nose to use nosetests
echo ; echo "Install nose to use nosetests..."; echo "# pip install nose"; pip install nose

# Install python-devel in order to resolve error when install paramiko- src/MD2.c:31:20: error: Python.h: No such file or directory
rpm -q python-devel
if [ $? -ne 0 ]; then
    echo ; echo "Install python-devel..."; echo "# yum install python-devel"; yum -y install python-devel;
    if [ $? -ne 0 ]; then echo "Failed to install packages python-devel, please install it first!"; exit 1; fi
fi

# Install paramiko
echo ; echo "Install paramiko..."; echo "# pip install paramiko"; pip install paramiko


#############################################
#      2. install kobo kobo-rpmlib koji     #
#############################################
# install kobo kobo-rpmlib koji to parse manifest
echo ; echo "Generate /etc/yum.repos.d/manifest.repo in order to install packages kobo kobo-rpmlib koji..."
echo "[manifest]
name=git install
failovermethod=priority
baseurl=http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/epel/6/x86_64/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch
" > /etc/yum.repos.d/manifest.repo

echo "Install packages kobo kobo-rpmlib koji..."
yum install -y kobo kobo-rpmlib koji


#############################################
#     3. Prepare environment variables      #
#############################################
# Please set the value of the testing environment variables according your testing
echo "Please set the value of the testing environment variables as per the following prompt:"
echo "--------------------------------------------------------------------------------------------"
read -p "Set param 'Variant' [Server/Client/Workstation/ComputeNode]: " Variant
read -p "Set param 'Arch' [x86_64/i386/ppc64/s390x/aarch64/ppc64le]: " Arch
read -p "Set param 'Manifest_URL': " Manifest_URL
read -p "Set param 'CDN'[QA/Prod]: " CDN
read -p "Set param 'Candlepin'[Stage/Prod]: " Candlepin
read -p "Set param 'Product_Type'[RHEL/RHEL-ALT/HTB/Oracle_Java_Restricted_Maintenance]: " Test_Type
read -p "Set param 'Test_Type'[Beta/GA/Snapshot]: " Test_Type
read -p "Set param 'Release_Version'[6.8/7.2/...]: " Release_Version
read -p "Set param 'master_release'[6/7/...]: " master_release
read -p "Set param 'minor_release'[4/5/...]: " minor_release
read -p "Set param 'Blacklisted'[6.10/7.5/...]: " Blacklisted
read -p "Set param 'System_IP'[Hostname/IP]: " System_IP
read -p "Set param 'Password'[QwAo2U6GRxyNPKiZaOCx]: " Password
read -p "Set param 'WORKSPACE'[/root]: " WORKSPACE

echo ; echo "Generate cdn.sh file to store testing environment variables..."
echo "
Variant=$Variant
Arch=$Arch
Manifest_URL=$Manifest_URL
CDN=$CDN
Candlepin=$Candlepin
Product_Type=$Product_Type
Test_Type=$Test_Type
Release_Version=$Release_Version
System_IP=$System_IP
Password=$Password
WORKSPACE=$WORKSPACE
master_release=$master_release
minor_release=$minor_release
Blacklisted=$Blacklisted

export Variant
export Arch
export Manifest_URL
export CDN
export Candlepin
export Product_Type
export Test_Type
export Release_Version
export System_IP
export Password
export WORKSPACE
export master_release
export minor_release
export Blacklisted
" > cdn.sh

# Load environment variables
echo ; echo "Load environment variables..."
echo "source cdn.sh"
source cdn.sh


#############################################
#          2. Downlaode Testing code        #
#############################################
# Install git if needed
rpm -q git > /dev/null
if [ $? -eq 1 ]; then
    echo ;
    echo "Install git..."
    echo "# wget hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/backup/git_install.sh"
    wget hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/backup/git_install.sh
    echo "# python git_install.sh"; python git_install.sh
fi

# Git clone your testing code under path $WORKSPACE if needed
echo ; echo "# git clone http://git.app.eng.bos.redhat.com/git/entitlement-tests.git $WORKSPACE/entitlement-tests"
git clone http://git.app.eng.bos.redhat.com/git/entitlement-tests.git $WORKSPACE/entitlement-tests


#############################################
#           2. Generate test cases          #
#############################################
# Change work dir
echo ; echo "cd $WORKSPACE/entitlement-tests/"
cd $WORKSPACE/entitlement-tests/
# Comment get_ip line in prepare.sh
echo "Comment get_ip line in prepare.sh"
sed -i "s/get_ip$/#get_ip/g" prepare.sh

# Generate test cases
echo ; echo "Generate test cases..."
echo "# bash prepare.sh cdn"
bash prepare.sh cdn
echo "List new test cases"
ll CDN/Tests/*

# Run testing
echo "Run testing..."
echo "# nosetests CDN/Tests/*.py --with-xunit --nocapture --xunit-file=nosetests.xml"
nosetests CDN/Tests/*.py --with-xunit --nocapture --xunit-file=nosetests.xml
