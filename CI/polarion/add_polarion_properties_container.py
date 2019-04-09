import xml.dom.minidom
import os

"""
Reference doc: https://mojo.redhat.com/docs/DOC-1135059
"""

container = os.environ["Container"]
product_type = os.environ['Product_Type']
test_type = os.environ['Test_Type']
compose_version = os.environ['Compose_Version']
arch = os.environ['Arch']
cdn = os.environ['CDN']
master_release = os.environ['master_release']
minor_release = os.environ['minor_release']
build_url = os.environ['BUILD_URL']


def get_para_host_version():
    """
    Get parameter para_host_version of Palorion container case

    :return:
    """
    return "{0} {1}".format(product_type, arch)


def get_para_subscription():
    """
    Get parameter para_subscription of Palorion container case

    :return:
    """
    para_subscription = ""
    if product_type == "RHEL7":
        if arch == "x86_64":
            para_subscription = "RH00003"
        elif arch == "s390x":
            para_subscription = "MCT0343"
        elif arch == "ppc64le":
            para_subscription = "RH00284"
    elif product_type == "RHEL8":
        if arch == "x86_64":
            para_subscription = "RH00003"
        elif arch == "s390x":
            para_subscription = "MCT0343"
        elif arch == "ppc64le":
            para_subscription = "RH00284"
        elif arch == "aarch64":
            para_subscription = "RH00784"
    elif product_type == "RHEL-ALT":
        if arch == "s390x":
            para_subscription = "MCT0343"
        elif arch == "ppc64le":
            para_subscription = "RH00284"
        elif arch == "aarch64":
            para_subscription = "RH00784"
    return para_subscription


def get_para_docker_image(image_version):
    """
    Get parameter para_docker_image of Palorion container case

    :return:
    """
    return "{0} {1}".format(image_version, arch)


def get_para_registry(image_version):
    """
    Get parameter para_registry of Palorion container case

    :return:
    """
    if image_version == "RHEL6":
        para_registry = "registry.access.redhat.com"
    elif image_version == "RHEL7":
        para_registry = "registry.access.redhat.com"
    else:
        para_registry = "brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888"
    return para_registry


def get_para_default_enabled_repo(image_version):
    if image_version == "RHEL6":
        if arch == "x86_64":
            default_repo = "rhel-6-server-rpms"
    elif image_version == "RHEL7":
        if arch == "x86_64":
            default_repo = "rhel-7-server-rpms"
        elif arch == "s390x":
            default_repo = "rhel-7-for-system-z-rpms"
        elif arch == "ppc64le":
            default_repo = "rhel-7-for-power-rpms"
        elif arch == "aarch64":
        # RHEL7-ALT aarch64
            default_repo = "rhel-7-for-arm-64-rpms"
    elif image_version == "RHEL8":
        if arch == "x86_64":
            default_repo = "rhel-8-for-x86_64-baseos-rpms,rhel-8-for-x86_64-appstream-rpms"
        elif arch == "s390x":
            default_repo = "rhel-8-for-system-z-baseos-rpms,rhel-8-for-system-z-appstream-rpms"
        elif arch == "ppc64le":
            default_repo = "rhel-8-for-ppc64le-baseos-rpms,rhel-8-for-ppc64le-appstream-rpms"
        elif arch == "aarch64":
            default_repo = "rhel-8-for-aarch64-baseos-rpms,rhel-8-for-aarch64-appstream-rpms"
    return default_repo


def get_testrun_name():
    """
    Get Polarion testrun name.

    :return:
    """

    global test_type
    if test_type == "GA":
        test_type = "RC"

    global compose_version
    compose_version = compose_version.replace(".", "")

    # RHELEntitlement-Container-RHEL8-Beta10-Prod
    testrun_name = "RHELEntitlement-Container-RHEL{0}{1}-{2}{3}-{4}-CDN".format(master_release, minor_release, test_type, compose_version, cdn)

    return testrun_name


def get_polarion_template():
    """
    Get Polarion template name.
   
    :return:
    """

    return 'ENT-TEM-CONTAINER'


def get_polarion_custom_arch():
    """
    Get Polarion custom arch name used for plugin 'CI Polarion xUnit Importer'.

    :return:
    """
    if arch == 'x86_64':
        return 'x8664'
    return arch


def get_container_polarion_case_name():
    """
    Get Container Polarion test case name.

    :return:
    """
    return "RHEL-133147"


def get_polarion_project():
    """
    Get Container Polarion project name.

    :return:
    """
    return "RedHatEnterpriseLinux7"


def add_polarion_properties():
    """
    Add properties into nosetests.xml in order to use plugin 'CI Polarion xUnit Importer' upload test results into Ploarion.

    1. Add testsuite property: polarion-project-id
    2. Add testsuite property: polarion-testrun-id
    3. Add testsuite property: polarion-template-id
    4. Add testcase property: polarion-testcase-id
    5. Add testcase property: polarion-parameter-para_host_version
    6. Add testcase property: polarion-parameter-para_subscription
    7. Add testcase property: polarion-parameter-para_docker_image
    8. Add testcase property: polarion-parameter-para_registry
    9. Add testcase property: polarion-parameter-para_default_enabled_repo
    """

    container_case_name = get_container_polarion_case_name()
    container_polarion_project = get_polarion_project()

    dom = xml.dom.minidom.parse('nosetests_original.xml')

    for suit in dom.getElementsByTagName("testsuite"):
        # prepare to write polarion project info into xml
        properties_testsuite = dom.createElement('properties')

        property_project_id = dom.createElement('property')
        property_project_id.setAttribute('name', 'polarion-project-id')
        property_project_id.setAttribute('value', container_polarion_project)

        property_testrun_id = dom.createElement('property')
        property_testrun_id.setAttribute('name', 'polarion-testrun-id')
        property_testrun_id.setAttribute('value', get_testrun_name())

        property_template_id = dom.createElement('property')
        property_template_id.setAttribute('name', 'polarion-testrun-template-id')
        property_template_id.setAttribute('value', get_polarion_template())

        property_custom_jenkinsjobs = dom.createElement('property')
        property_custom_jenkinsjobs.setAttribute('name', 'polarion-custom-jenkinsjobs')
        property_custom_jenkinsjobs.setAttribute('value', build_url)

        properties_testsuite.appendChild(property_project_id)
        properties_testsuite.appendChild(property_testrun_id)
        properties_testsuite.appendChild(property_template_id)
        properties_testsuite.appendChild(property_custom_jenkinsjobs)

        testcase = suit.getElementsByTagName('testcase')[0]
        suit.insertBefore(properties_testsuite, testcase)

        for testcase in suit.getElementsByTagName('testcase'):
            # Get test case name and the image version
            testcase_name = testcase.getAttribute('name')
            image_version = testcase_name.split('_')[2]

            # Reset test case name, eg: test_Container_Host-RHEL7-s390x_Container-RHEL8
            testcase_new_name = "test_Container_Host-{0}-{1}_Container-{2}".format(product_type, arch, image_version)
            testcase.setAttribute('name', testcase_new_name)

            # Delete the useless test case log, modify the test case failures number and tests number
            ignore_info = "CONTAINER TESTING IS NOT NEEDED"
            system_out = testcase.getElementsByTagName("system-out")[0]
            if ignore_info in system_out.childNodes[0].nodeValue:
                suit.removeChild(testcase)
                #failures_number = suit.getAttribute('failures').encode("utf-8")
                tests_number = suit.getAttribute('tests').encode("utf-8")
                #suit.setAttribute('failures', str(int(failures_number)-1))
                suit.setAttribute('tests', str(int(tests_number) - 1))
                continue

            para_host_version = get_para_host_version()
            para_subscription = get_para_subscription()
            para_docker_image = get_para_docker_image(image_version)
            para_registry = get_para_registry(image_version)
            para_default_enabled_repo = get_para_default_enabled_repo(image_version)


            properties_testcase = dom.createElement('properties')
            property_testcase_id = dom.createElement('property')
            property_testcase_id.setAttribute('name', 'polarion-testcase-id')
            property_testcase_id.setAttribute('value', container_case_name)

            property_para_host_version = dom.createElement('property')
            property_para_host_version.setAttribute('name', 'polarion-parameter-para_host_version')
            property_para_host_version.setAttribute('value', para_host_version)

            property_para_subscription = dom.createElement('property')
            property_para_subscription.setAttribute('name', 'polarion-parameter-para_subscription')
            property_para_subscription.setAttribute('value', para_subscription)

            property_para_docker_image = dom.createElement('property')
            property_para_docker_image.setAttribute('name', 'polarion-parameter-para_docker_image')
            property_para_docker_image.setAttribute('value', para_docker_image)

            property_para_registry = dom.createElement('property')
            property_para_registry.setAttribute('name', 'polarion-parameter-para_registry')
            property_para_registry.setAttribute('value', para_registry)

            property_para_default_enabled_repo = dom.createElement('property')
            property_para_default_enabled_repo.setAttribute('name', 'polarion-parameter-para_default_enabled_repo')
            property_para_default_enabled_repo.setAttribute('value', para_default_enabled_repo)

            properties_testcase.appendChild(property_testcase_id)
            properties_testcase.appendChild(property_para_host_version)
            properties_testcase.appendChild(property_para_subscription)
            properties_testcase.appendChild(property_para_docker_image)
            properties_testcase.appendChild(property_para_registry)
            properties_testcase.appendChild(property_para_default_enabled_repo)

            systemout = testcase.getElementsByTagName('system-out')[0]
            testcase.insertBefore(properties_testcase, systemout)

    with open("nosetests.xml", 'w') as f:
        f.write(dom.toprettyxml(indent='\t', encoding='utf-8'))


if __name__ == '__main__':
    add_polarion_properties()
