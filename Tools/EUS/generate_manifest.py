import os
import shutil
import sys
import logging
import requests
import time


def download_manifest(errata_id, retry_count=0):
    """
    Download manifest.

    Download manifest via the RCM Manifest API at http://rcm-team.app.eng.bos.redhat.com/errata-manifest/<ERRATA_ID>
    :param retry_count: integer. How many times we will retry this method to download manifest.
    """

    url = 'http://rcm-prod.host.prod.eng.bos.redhat.com/errata-manifest/{0}'.format(errata_id)

    try:
        logging.info('Trying to download manifest for Errata {0}'.format(errata_id))
        response = requests.get(url)
        response.raise_for_status()
        with open('{0}.json'.format(errata_id), 'w') as json_file:
            json_file.write(response.content)
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 500:
            message = 'RCM API encountered an error'
            logging.error("Error downloading manifest: {0} - {1}".format(error.response.status_code, message))
            if retry_count > 0:
                retry_count -= 1
                time.sleep(5)
                logging.info('Retrying to download manifest')
                download_manifest(errata_id, retry_count=retry_count)
            elif retry_count == 0:
                logging.info("Unable to download manifest. Exiting...")
        else:
            logging.error("Error downloading manifest: {0}".format(error.response.status_code))
        #raise


def generate_manifest(errata_id_list):
    """
    Generate manifests.

    Attempts to generate manifests for $errata_id_list under directory
    generate a manifest file <Errata_ID>.json for per errata id
    :param errata_id_list: shipped errata id list.
    """
    
    eus_manifest_dir = 'eus_manifest'
    if os.path.exists(eus_manifest_dir):
        shutil.rmtree(eus_manifest_dir)
    os.mkdir(eus_manifest_dir)
    os.chdir(eus_manifest_dir)
    
    for eid in errata_id_list:
        download_manifest(eid)


def usage():
    logging.info("""
        python <script_name.py> <errata_id_list>
        <errata_id_list>: "26817, 26952, 27548"
    """)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='generate_manifest.log',
                filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
   
    errata_id_list = [i.strip() for i in sys.argv[1].split(",")]
    generate_manifest(errata_id_list)
