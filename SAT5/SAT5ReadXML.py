import logging
import traceback

try:
        from xml.etree import ElementTree
except:
        from elementtree import ElementTree

# Create logger
logger = logging.getLogger("entLogger")


class SAT5ReadXML(object):
    def get_channel_list(self, manifest_xml):
        doc = ElementTree.parse(manifest_xml)
        root = doc.getroot()
        channel_list = [i.get("value") for i in root.findall('repoid')]
        return channel_list

    def get_package_list(self, manifest_xml, channel):
        doc = ElementTree.parse(manifest_xml)
        root = doc.getroot()
        package_list = []
        source_list = []
        for i in root.findall('repoid'):
            if i.get("value") == channel:
                for p in i.findall('packagename'):
                    for s in p.text.strip().splitlines():
                        if s.strip() != "" and s.strip().split()[3] != "src":
                           #package_list.append(s.strip().split()[0])
                           package_list.append("{0}-{1}-{2}.{3}".format(s.split()[0], s.split()[1], s.split()[2], s.split()[3]))
                        elif s.strip() != "" and s.strip().split()[3] == "src":
                           s1 = s.strip()
                           source_list.append("{0}-{1}-{2}".format(s1.split()[0], s1.split()[1], s1.split()[2]))
                break
        return package_list,source_list

if __name__ == "__main__":
    pass
