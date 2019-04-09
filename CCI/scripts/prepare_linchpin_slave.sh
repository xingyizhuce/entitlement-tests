# Register and subscribe to Stage Candlepin
subscription-manager config --server.hostname=subscription.rhsm.stage.redhat.com
subscription-manager register --auto-attach --username=entitlement_testing --password=redhat
subscription-manager repos --enable=rhel-7-server-optional-rpms

# Install some requirements before Linchpin installation
yum install -y wget
yum install -y java-1.8.0-openjdk
yum install -y git
yum install -y vim-enhanced
easy_install pip

# Download Linchpin code
mkdir /home/jenkins
cd /home/jenkins/
git clone http://git.app.eng.bos.redhat.com/git/entitlement-tests.git


# Install requirements and Linchpin with Beaker in a virtualenv
yum install -y python-virtualenv  gcc krb5-devel libselinux-python libxml2-devel libxslt-devel libxslt-python libxslt-python
virtualenv .venv
cp /usr/lib64/python2.7/site-packages/*libxml2* .venv/lib64/python2.7/site-packages/
cp /usr/lib64/python2.7/site-packages/*libxslt* .venv/lib64/python2.7/site-packages/
cp -r /usr/lib64/python2.7/site-packages/*selinux .venv/lib64/python2.7/site-packages/
. .venv/bin/activate && pip install --timeout 120 yq linchpin[beaker]==1.6.2
#pip install cinch
pip install git+https://github.com/RedHatQE/cinch.git@master
deactivate


# Install Red Hat SSL certificates for Internal systems
curl -k -o /etc/yum.repos.d/it-iam.repo https://gitlab.corp.redhat.com/it-iam/idm-user-configs/raw/master/rhit-legacy-client/rhit-legacy-configs-1.0.0/yum.repos.d/it-iam.repo
curl -k -o /tmp/RPM-GPG-KEY-redhat-git https://gitlab.corp.redhat.com/it-iam/idm-user-configs/raw/master/rhit-legacy-client/rhit-legacy-configs-1.0.0/rpm-gpg/RPM-GPG-KEY-redhat-git
yum clean all
rpm --import /tmp/RPM-GPG-KEY-redhat-git
yum install -y rhit-legacy-configs


# Load Beaker client configurations
cd entitlement-tests/CCI/Linchpin/beaker
cp jenkins.keytab-entitlement-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com /etc/
mkdir /etc/beaker
cp beaker.conf /etc/beaker/client.conf


# Prepare testing envrionment
# Install/Upgrade nose
pip install --upgrade nose

# Install paramiko
pip install paramiko

# Install kobo kobo-rpmlib koji to parse manifest
echo ; echo "Generate /etc/yum.repos.d/manifest.repo in order to install packages kobo kobo-rpmlib koji..."
echo "[manifest]
name=git install
failovermethod=priority
baseurl=http://dl.fedoraproject.org/pub/epel/7/x86_64/
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch
" > /etc/yum.repos.d/manifest.repo

yum install -y --skip-broken kobo kobo-rpmlib koji
