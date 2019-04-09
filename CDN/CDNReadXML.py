import logging
import traceback

try:
        from xml.etree import ElementTree
except:
        from elementtree import ElementTree


# Create logger
logger = logging.getLogger("entLogger")


class CDNReadXML(object):
    def get_element(self, ele, tags):
        for tag in tags:
            ele = self.get_next_element(ele, tag)
            if ele != None:
                continue
            else:
                assert False, "There is no element {0} in manifest.".format(tag)
        return ele

    def get_next_element(self, ele, tag):
        # get next element instance
        for i in list(ele):
            if i.get('value') == tag:
                return i

    def get_repoid_element(self, manifest_xml, args):
        doc = ElementTree.parse(manifest_xml)
        root_ele = doc.getroot()
        if root_ele != None:
            repoid_ele = self.get_element(root_ele, args)
            return repoid_ele
        else:
            assert False, "There is no rhel root element in manifest."

    def get_repo_list(self, manifest_xml, release_ver, *args):
        # args: (pid, current_arch)
        try:
            repoid_ele = self.get_repoid_element(manifest_xml, args)
            repo_list = [i.get("value") for i in repoid_ele.findall("repoid") if i.get("releasever") == release_ver]
            return repo_list
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when get repo list from cdn xml manifest!")
            logger.error(traceback.format_exc())
            assert False, str(e)

    def get_package_list(self, manifest_xml, repo, release_ver, *args):
        # args: (pid, current_arch)
        try:
            repoid_ele = self.get_repoid_element(manifest_xml, args)

            package_list = []
            for i in repoid_ele.findall("repoid"):
                if i.get("releasever") == release_ver and i.get('value') == repo:
                    package_list = [j.text.strip().splitlines() for j in list(i) if j.tag == "packagename"]
            if len(package_list) != 0:
                return [i.strip() for i in package_list[0]]
            else:
                return package_list
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when get package list from cdn xml manifest!")
            logger.error(traceback.format_exc())
            assert False, str(e)

    def get_arch_list(self, manifest_xml, *args):
        # args: (pid)
        try:
            doc = ElementTree.parse(manifest_xml)
            root_ele = doc.getroot()
            arch_ele = self.get_element(root_ele, args)
            arches = [i.get('value') for i in list(arch_ele)]
            return list(set(arches))
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when get arch list from cdn xml manifest!")
            logger.error(traceback.format_exc())
            assert False, str(e)

    def get_repo_url(self, manifest_xml, repo, release_ver, *args):
        try:
            repoid_ele = self.get_repoid_element(manifest_xml, args)

            for i in repoid_ele.findall("repoid"):
                if i.get("releasever") == release_ver and i.get('value') == repo:
                    return [j.text.strip() for j in list(i) if j.tag == "relativeurl"][0]
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when get repo url from cdn xml manifest!")
            logger.error(traceback.format_exc())
            assert False, str(e)

    def get_name(self, manifest_xml, pid):
        try:
            doc = ElementTree.parse(manifest_xml)
            root_ele = doc.getroot()
            for i in list(root_ele):
                if i.get('value') == pid:
                    return i.get('name')
        except Exception, e:
            logger.error(str(e))
            logger.error("Test Failed - Raised error when get repo url from cdn xml manifest!")
            logger.error(traceback.format_exc())
            assert False, str(e)

if __name__ == "__main__":
    # 69 x86_64 rhel-6-server-debug-rpms 6Server
    #repolist = CDNReadXML().get_repo_list("manifest/cdn_test_manifest.xml", "6Server", "69", "x86_64")
    #pkg_list = CDNReadXML().get_package_list("manifest/cdn_test_manifest.xml", "rhel-6-server-debug-rpms", "6Server", "69", "x86_64")
    #archlist = CDNReadXML().get_arch_list("example2.xml", "69")
    #repo_url = CDNReadXML().get_repo_url("manifest/cdn_test_manifest.xml", "rhel-7-for-power-9-beta-rpms", "7.4", "362", "ppc64le")
    name = CDNReadXML().get_name("manifest/cdn_test_manifest.xml", "146")
    print name