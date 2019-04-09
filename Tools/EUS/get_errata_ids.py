import sys
import logging
import requests
from requests_kerberos import HTTPKerberosAuth

"""
Usage:
1. Configure kerberos firstly
2. kinit
3. python get_errata_ids.py <release_version>
"""


def get_shipped_eus_errata_ids(release_version):
    """
    Retrieve the Errata IDs for 0-day advisories for a RHEL release.

    1. Take the full RHEL version, i.e. 6.9, 7.3, etc and generate the names of the release streams.
    rhel-<RHEL_version>.0 (ex. rhel-6.9.0)
    rhel-<RHEL_version>.z (ex. rhel-6.9.z)
    supplementary-<RHEL_version>.0 (ex. supplementary-6.9)
    supplementary-<RHEL_version>.z (ex. supplementary-6.9.z)
    2. Query the Errata Tool API with each of the names above at the following URL(take 6.9.z as an example), retrieve the "id" value under the "data" key.
    https://errata.devel.redhat.com/api/v1/releases?filter[name]=<release_stream> (ex. https://errata.devel.redhat.com/api/v1/releases?filter[name]=rhel-6.9.z )
    3. Use above id value in the following query, get a list of of advisories, retrieve the "id" from each of the entries, then have all the Errata IDs for this particular release stream.
    https://errata.devel.redhat.com/release/<id>/advisories.json (ex. https://errata.devel.redhat.com/release/683/advisories.json)

    :param release_version: RHEL version, i.e. 6.9, 7.3
    """

    # release_names = ["rhel-{0}.z".format(release_version), "supplementary-{0}.z".format(release_version)]
    # Change it to search with batch "RHEL-7.3.z 0day" since two much non-0day errata id generated using release name.
    batch_name = "RHEL-{0}.z 0day".format(release_version)
    errata_id_list = []

    try:
        # Get all 0 day EUS Errata IDs.
        r = requests.get("https://errata.devel.redhat.com/api/v1/batches?filter[name]={0}".format(batch_name),
                        auth=HTTPKerberosAuth(),
                        verify=False)
        r.raise_for_status()
        release_id = r.json()['data'][0]['relationships']['release']['id']
        errata_ids = [i['id'] for i in r.json()['data'][0]['relationships']['errata']]
        print "="*30
        print "All EUS Errata IDs: {0}".format(errata_ids)

        # Get a list of of advisories via above id value
        # Filter the shipped EUS Errata IDs.
        r = requests.get("https://errata.devel.redhat.com/release/{0}/advisories.json".format(release_id),
                        auth=HTTPKerberosAuth(),
                        verify=False)
        r.raise_for_status()
        for errata_id in errata_ids:
            for entry in r.json():
                if errata_id == entry['id'] and entry['status'] == 'SHIPPED_LIVE':
                    errata_id_list.append(entry['id'])

        logging.info("Shipped EUS Errata IDs: {0}".format(errata_id_list))
        return errata_id_list
    except requests.HTTPError as e:
        logging.error(e.args)


def usage():
    logging.info("""
        1. Configure kerberos firstly
        2. kinit
        3. python get_errata_ids.py <release_version>
    """)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='get_errata_id.log',
                filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    # Get Errata ID list for specific RHEL release(such as 6.9.z)
    release_version = sys.argv[1]
    errata_id_list = get_shipped_eus_errata_ids(release_version)
    logging.info(errata_id_list)

