
# Firstly, install one 6Server_x86_64 system, and register/subscribe
# Install necessary packages
yum install -y wget
yum install -y java-1.8.0-openjdk
yum install -y git
yum install -y vim-enhanced
yum install -y krb*
#yum groupinstall -y Base

# Prepare conf files
wget http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/Jenkins/etc.beaker/RedHatInternalCA.pem -P /etc/beaker/
wget http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/Jenkins/etc.beaker/client.conf -P /etc/beaker/
wget http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/Jenkins/etc.beaker/jenkins.keytab-entitlement-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com -P /etc/
mv /etc/krb5.conf /etc/krb5.conf.bk
wget http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/ftan/Jenkins/etc.krb/krb5.conf -P /etc/

# Clone code
git clone http://git.app.eng.bos.redhat.com/git/ci-ops-central.git
git clone http://git.app.eng.bos.redhat.com/git/ci-ops-projex.git
git clone http://git.app.eng.bos.redhat.com/git/job-runner.git
git clone http://git.app.eng.bos.redhat.com/git/entitlement-tests.git

pip install --upgrade setuptools
pip install --upgrade urllib3
pip install --upgrade pyOpenSSL

# Install ci-ops-central tools
cd ci-ops-central
./install.sh

# Install the following packages if 'No package ... available.'
pip install python-glanceclient python-keystoneclient python-novaclient python-neutronclient
yum -y install compat-gcc-44

# Install Nova client 2.0 to resolve error - UnsupportedVersion: Invalid client version '1.1'. Major part should be '2'
wget https://pypi.python.org/packages/98/7e/c00519e57db47b5fdb036785ccac7fd6cf22243ffb0923469b26c7f05aa9/python_novaclient-2.25.0-py2.py3-none-any.whl#md5=8109c443f2e15c54c0980c6eade17f59
pip install python_novaclient-2.25.0-py2.py3-none-any.whl

# Prepare testing envrionment
# Install/Upgrade nose
pip install --upgrade nose

# install kobo kobo-rpmlib koji to parse manifest
echo ; echo "Generate /etc/yum.repos.d/manifest.repo in order to install packages kobo kobo-rpmlib koji..."
echo "[manifest]
name=git install
failovermethod=priority
baseurl=http://dl.fedoraproject.org/pub/epel/7/x86_64/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch
" > /etc/yum.repos.d/manifest.repo

yum install -y kobo kobo-rpmlib koji

# To provision one master system
# notice variable --name, if refuse to create, please change this name value
#ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=ci-ops-projex/config/project_defaults_osp7 --ssh_keyfile=ci-ops-projex/config/keys/ci-ops-central --name=ci-ops --cleanup=on_failure
#ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=entitlement-tests/CI/config/project-entitlement-qe-jenkins --ssh_keyfile=entitlement-tests/CI/keys/ent-qe --name=$Slave_Name  --topology=entitlement-tests/CI/config/ent-qe-entitlement-qe-jenkins --site=SITE --do_not_create_jobs --cleanup=on_failure

# To Provison one slave system
# Need to modify entitlement-tests/CI/config/bkr.json before run the following command
#ci-ops-central/bootstrap/provision_jslave.sh --project_defaults=entitlement-tests/CI/config/project-entitlement-qe-jenkins --ssh_keyfile=entitlement-tests/CI/keys/ent-qe-entitlement-qe-jenkins --topology=entitlement-tests/CI/config/slave-system --jenkins_master_url=$JENKINS_MASTER_URL --jslavelabel=entitlement-test --jslave_execs=10 --jslavename=$Slave_Name --jslavecreate

# To Provision one system in beaker
#ci-ops-central/bootstrap/provision_resources.sh --site=qeos --project_defaults=entitlement-tests/CI/config/project-entitlement-qe-jenkins --topology=entitlement-tests/CI/config/bkr --ssh_keyfile=entitlement-tests/CI/keys/beaker-keytab-entitlement-qe-jenkins --name=$Distro_$Variant_$Arch


# Reference Links:
# ci-ops-central’s code documentation: https://ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com/job/ci-ops-central-documentation/lastSuccessfulBuild/artifact/ci-ops-central/docs/build/html/index.html
# Beaker Configuration: https://docs.engineering.redhat.com/display/CentralCI/Beaker+Configuration+with+Keytab+and+Cert+Example
# UMB: https://docs.engineering.redhat.com/display/CentralCI/UMB+Migration
# Use CI Plugin with JJB: https://docs.engineering.redhat.com/display/CentralCI/Configuring+Jobs+to+use+the+CI+Plugin+with+Jenkins+Job+Builder
# JJB: https://docs.openstack.org/infra/jenkins-job-builder/
# Add Beaker Jenkins SSH Key for CI-Central: https://mojo.redhat.com/docs/DOC-1054659
# OpenStack Server: https://ci-rhos.centralci.eng.rdu2.redhat.com
# Central CI Home: https://docs.engineering.redhat.com/display/CentralCI/Central+CI+Home
