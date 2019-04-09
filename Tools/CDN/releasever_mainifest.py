#!/bin/python

import simplejson as json
import sys


def releasever_manifest(manifest):
    # Load the manifest to be corrected for the "basearch" value.
    with open(manifest) as access_json:
        read_content = json.load(access_json)

    # Define the supported arches for manifest
    supported_arches = ["x86_64", "ppc64le"]
    question_access = read_content['cdn']['products']

    for pid_data in question_access:
        repo_paths = question_access[pid_data]["Repo Paths"]
        for repo_path in repo_paths:
            arch_detected = False
            release = '7Server'
            for arch in supported_arches:
                if arch in repo_path:
                    arch_detected = True
                    question_access[pid_data]["Repo Paths"][repo_path]["releasever"] = release
                    break

            if not arch_detected:
                raise Exception()

    # Finally upload the updated manifest with correct basearch in source folder.
    with open('./Updated_manifest_with_releasever.json', "w") as json_file:
        json.dump(read_content, json_file, indent=4)
        print("Please check 'CDN' folder for the Updated manifest")


if __name__ == '__main__':
    releasever_manifest(sys.argv[1])
