import xml.dom.minidom
import json
import time
import os

"""
Reference doc: https://mojo.redhat.com/docs/DOC-1135059
"""


product_type = os.environ['Product_Type']
master_release = os.environ["master_release"]
minor_release = os.environ["minor_release"]
variant = os.environ['Variant']
arch = os.environ['Arch']
cdn = os.environ['CDN']
build_url = os.environ['BUILD_URL']
errata_id = os.environ['Errata_id']
ocp_version = os.environ['Openshift_Version']

def get_testrun_name():
    """
    Get Polarion testrun name.

    RHEL Product:     Entitlement_OCP_$errata_id_$arch
    RHEL-ALT Product: Entitlement_OCP_$errata_id_rhel_alt_$arch


    :return:
    """

    if product_type in ["RHEL7", "RHEL8"]:
        testrun_name = "Entitlement_OCP_{0}_{1}".format(errata_id, arch)
    elif product_type == "RHEL-ALT":
        testrun_name = "Entitlement_OCP_{0}_rhel_alt_{1}".format(errata_id, arch)
    else:
        testrun_name = "{0}Entitlement-RHEL{1}{2}-{3}_{4}_{5}-CDN".format(product_type, master_release, minor_release,
                                                                          variant, arch, cdn)
    return testrun_name


def get_polarion_template():
    """
    Get Polarion template name.

    :return:
    """
    return 'ENT-TEM-CDN'


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
