import  xml.dom.minidom
import json
import time
import os

product_type = os.environ['Product_Type']
test_type = os.environ['Test_Type']
compose_version = os.environ['Compose_Version']
cdn = os.environ['CDN']
variant = os.environ['Variant']
arch = os.environ['Arch']
distro = os.environ['Distro']
build_url = os.environ['BUILD_URL']

def get_testrun_name():
    """
    Get Polarion testrun name.

    HTB: RHELEntitlement-RHEL68-HTB-Server-x86_64
    Beta: RHELEntitlement-RHEL68-Beta-Server-x86_64
    GA: RHELEntitlement-RHEL68-GA-Server-x86_64

    :return:
    """
    release = distro.split('-')[1].split('.')
    release_version = release[0] + release[1]

    global compose_version
    compose_version = compose_version.replace(" ", "").replace(".", "")

    if product_type in ["RHEL7"]:
        testrun_name = "RHELEntitlement-SAT5-RHEL{0}-{1}-{2}-{3}-{4}_{5}-CDN".format(release_version, test_type, compose_version, variant, arch, cdn)
    elif product_type in ["RHEL8"]:
        testrun_name = "RHELEntitlement-SAT5-RHEL{0}-{1}-{2}-{3}_{4}-CDN".format(release_version, test_type, compose_version, arch, cdn)

    return testrun_name

def get_polarion_template():
    """
    Get Polarion template name.
   
    :return:
    """

    return 'ENT-TEM-SAT5'

def get_polarion_custom_arch():
    """
    Get Polarion custom arch name used for plugin 'CI Polarion xUnit Importer'.

    :return:
    """
    if arch == 'x86_64':
        return 'x8664'
    return arch

def add_polarion_properties():
    """
    Add properties into nosetests.xml in order to use plugin 'CI Polarion xUnit Importer' upload test results into Ploarion.

    1. Add testsuite property: polarion-project-id
    2. Add testsuite property: polarion-testrun-id
    3. Add testsuite property: polarion-template-id
    4. Add testsuite property: polarion-custom-arch
    5. Add testsuite property: polarion-custom-variant
    6. Add testcase property: polarion-testcase-id
    7. Add testcase property: polarion-custom-jenkinsjobs
    """
    release_release = distro.split('-')[1]
    master_release = release_release.split('.')[0]
    json_file = 'entitlement-tests/CI/polarion/POLARION_PROPS_RHEL{0}.json'.format(master_release)
    with open(json_file, 'r') as f:
        polarion_props = json.load(f)

    dom = xml.dom.minidom.parse('nosetests_original.xml')

    for suit in dom.getElementsByTagName("testsuite"):
        # prepare to write polarion project info into xml
        properties_testsuite = dom.createElement('properties')

        property_project_id = dom.createElement('property')
        property_project_id.setAttribute('name', 'polarion-project-id')
        property_project_id.setAttribute('value', polarion_props['polarion.project'])

        property_testrun_id = dom.createElement('property')
        property_testrun_id.setAttribute('name', 'polarion-testrun-id')
        property_testrun_id.setAttribute('value', get_testrun_name())

        property_testrun_title = dom.createElement('property')
        property_testrun_title.setAttribute('name', 'polarion-testrun-title')
        property_testrun_title.setAttribute('value', get_testrun_name())

        property_template_id = dom.createElement('property')
        property_template_id.setAttribute('name', 'polarion-testrun-template-id')
        property_template_id.setAttribute('value', get_polarion_template())

        property_custom_arch = dom.createElement('property')
        property_custom_arch.setAttribute('name', 'polarion-custom-arch')
        property_custom_arch.setAttribute('value', get_polarion_custom_arch())

        property_custom_variant = dom.createElement('property')
        property_custom_variant.setAttribute('name', 'polarion-custom-variant')
        property_custom_variant.setAttribute('value', str.lower(variant))

        property_custom_jenkinsjobs = dom.createElement('property')
        property_custom_jenkinsjobs.setAttribute('name', 'polarion-custom-jenkinsjobs')
        property_custom_jenkinsjobs.setAttribute('value', build_url)

        properties_testsuite.appendChild(property_project_id)
        properties_testsuite.appendChild(property_testrun_id)
        properties_testsuite.appendChild(property_testrun_title)
        properties_testsuite.appendChild(property_template_id)
        properties_testsuite.appendChild(property_custom_arch)
        properties_testsuite.appendChild(property_custom_variant)
        properties_testsuite.appendChild(property_custom_jenkinsjobs)

        testcase = suit.getElementsByTagName('testcase')[0]
        suit.insertBefore(properties_testsuite, testcase)

        for testcase in suit.getElementsByTagName('testcase'):
            # prepare to write polarion test case id into xml

            properties_testcase = dom.createElement('properties')
            property_testcase_id = dom.createElement('property')
            property_testcase_id.setAttribute('name', 'polarion-testcase-id')
            property_testcase_id.setAttribute('value', polarion_props[testcase.getAttribute('name')])

            properties_testcase.appendChild(property_testcase_id)

            systemout = testcase.getElementsByTagName('system-out')[0]
            testcase.insertBefore(properties_testcase, systemout)

    with open("nosetests.xml", 'w') as f:
        f.write(dom.toprettyxml(indent='\t', encoding='utf-8'))

if __name__ == '__main__':
    add_polarion_properties()
