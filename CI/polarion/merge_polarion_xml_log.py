import xml.dom.minidom
import sys
import os

test_product = os.environ['Test_Product']

try:
    build_url_env = os.environ['BUILD_URL']
except KeyError as e:
    build_url_env = ""


def get_property_value(parent_element, property_name):
    properties = parent_element.getElementsByTagName("properties")[0]
    prop = properties.getElementsByTagName("property")
    
    for p in prop:
        p_name = p.getAttribute("name")
        if p_name == property_name:
            p_value = p.getAttribute("value")
            
            return p_value


def set_property_value(parent_element, property_name, property_value):
    properties = parent_element.getElementsByTagName("properties")[0]
    prop = properties.getElementsByTagName("property")
    
    for p in prop:
        p_name = p.getAttribute("name")
        if p_name == property_name:
            p_value = p.getAttribute("value")
            p.setAttribute("value",property_value)
            break


def merge_xml():
    """
    Merge xml files into one file in order to use plugin 'CI Polarion xUnit Importer' to upload test results into Polarion.
    """
    try:
        first_testsuite_dom = xml.dom.minidom.parse(sys.argv[1])
        testsuite = first_testsuite_dom.getElementsByTagName("testsuite")[0]
        
        ## Set correct test product in the polarion-testrun-id if needed
        if test_product != "":
            testrun_id = get_property_value(testsuite, "polarion-testrun-id")
            
            testrun_id_list = testrun_id.split("-")
            testrun_id_list[2] = test_product.upper()
            testrun_id_str = '-'.join(testrun_id_list)

            set_property_value(testsuite, "polarion-testrun-id", testrun_id_str)

        ## Add the url of jenkins job of importing result into polarion in build_url
        build_url = "The jenkins job of importing test result into Polarion:\n" + build_url_env + "\n\n"
        build_url += "The jenkins jobs of testing result:\n"

        ## Add the first jenkins test job url in build_url       
        # Get the first jenkins test job's first test case host_version
        testcase_first_job = testsuite.getElementsByTagName('testcase')[0]
        host_version_first_job = get_property_value(testcase_first_job, "polarion-parameter-para_host_version")

        # Get the first jenkins test job url
        build_url_first_job = get_property_value(testsuite, "polarion-custom-jenkinsjobs")
        
        # Add the first jenkins test job url in build_url
        build_url += "Host " + host_version_first_job + ":\n"
        build_url += build_url_first_job + "\n\n"

        ## errors="0" failures="1" skip="0" tests="2"
        errors_number = int(testsuite.getAttribute("errors").encode("utf-8"))
        failures_number = int(testsuite.getAttribute('failures').encode("utf-8"))
        skip_number = int(testsuite.getAttribute('skip').encode("utf-8"))
        tests_number = int(testsuite.getAttribute('tests').encode("utf-8"))
        
        files = sys.argv[2:len(sys.argv)]
        for file in files:
            file_dom = xml.dom.minidom.parse(file)
            file_testsuite = file_dom.getElementsByTagName("testsuite")[0]

            errors_number = errors_number + int(file_testsuite.getAttribute("errors").encode("utf-8"))
            failures_number = failures_number + int(file_testsuite.getAttribute('failures').encode("utf-8"))
            skip_number = skip_number + int(file_testsuite.getAttribute('skip').encode("utf-8"))
            tests_number = tests_number + int(file_testsuite.getAttribute('tests').encode("utf-8"))

            ## Add the next jenkins test job url in build_url       
            # Get the next jenkins test job's first test case host_version
            testcase_next_job = file_testsuite.getElementsByTagName('testcase')[0]
            host_version_next_job = get_property_value(testcase_next_job, "polarion-parameter-para_host_version")

            # Get the next jenkins test job url
            build_url_next_job = get_property_value(file_testsuite, "polarion-custom-jenkinsjobs")
            
            # Add the next jenkins test job url in build_url
            build_url += "Host " + host_version_next_job + ":\n"
            build_url += build_url_next_job + "\n\n"

            ## Add all the test cases into the first job testsuite
            for testcase in file_testsuite.getElementsByTagName('testcase'):
                testsuite.appendChild(testcase)

        ## Set the value of the property "polarion-custom-jenkinsjobs" with build_url 
        ## in the first job nosetests xml file which will be the final nosetests xml file
        set_property_value(testsuite, "polarion-custom-jenkinsjobs", build_url)
        
        testsuite.setAttribute('errors', str(errors_number))
        testsuite.setAttribute('failures', str(failures_number))
        testsuite.setAttribute('skip', str(skip_number))
        testsuite.setAttribute('tests', str(tests_number))

    except Exception, e:
        raise AssertionError(str(e))

    with open("nosetests-final.xml", 'w') as f:
        f.write(first_testsuite_dom.toxml(encoding='utf-8'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please specify the xml files needed to merge."
        exit(1)
    merge_xml()
