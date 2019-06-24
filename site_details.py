import io
import boto3
import zipfile
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from datetime import datetime

LOG = logging.getLogger(__name__)

ALEXA_TOP_SITES_BUCKET = 'alexa-static'
ALEXA_TOP_SITES_KEY = 'top-1m.csv.zip'
ALEXA_TOP_SITES_FILE = 'top-1m.csv'


def _get_word_list(text: str) -> List:
    """
    For now just return the page as comma separated text.
    """
    soup = BeautifulSoup(text, 'html.parser')

    return soup.get_text().split()


class SiteDetails(object):
    """
    Retrieve the header & word count from each site
    """
    def __init__(self, name):
        time_start = datetime.now()
        self.name = name

        self.word_list, self.headers, self.scanned, self.status_code = self._get_site_first_page_data()

        if self.word_list is not None:
            self.word_count = len(self.word_list)
        else:
            self.word_count = 0

        self.scan_time = datetime.now() - time_start

    def __gt__(self, site):
        return self.word_count > site.word_count

    def __lt__(self, site):
        return self.word_count < site.word_count

    def __str__(self):
        return "{} has {} words --> scanned in {}".format(self.name,
                                                       self.word_count,
                                                       self.scan_time)

    def _get_site_first_page_data(self) -> Tuple[List, dict, bool, int]:
        url = '{}{}'.format('http://', self.name)

        try:
            resp = requests.get(url, timeout=2)
            word_list = _get_word_list(resp.text)
            headers = resp.headers
            status_code = resp.status_code
            did_scan = True

        except requests.exceptions.RequestException as e:
            LOG.error('Scan for {} failed: {}'.format(self.name, e))
            word_list = []
            headers = {}
            did_scan = False
            status_code = 500

        return word_list, headers, did_scan, status_code


class HeaderDetail(object):
    """
    Keep track of the name and of number times the header appears in the web page
    """
    def __init__(self, name=None, count=None):
        self.name = name
        self.count = count

    def __eq__(self, other):
        if isinstance(other, HeaderDetail):
            return self.name == other.name


class AlexaSites:
    @staticmethod
    def top_sites(number) -> List:
        """
        Get list of the top sites from the S3 bucket
        """

        s3_client = boto3.client('s3')
        top_sites_obj = s3_client.get_object(Bucket=ALEXA_TOP_SITES_BUCKET, Key=ALEXA_TOP_SITES_KEY)
        top_sites_bytes = io.BytesIO(top_sites_obj.get('Body').read())
        top_sites_zip = zipfile.ZipFile(top_sites_bytes)

        top_sites_list = []
        for line in io.BytesIO(top_sites_zip.read(ALEXA_TOP_SITES_FILE)):
            rank, site = line.decode('utf-8').strip().split(',')
            LOG.debug('{}) Site: {}'.format(rank, site))
            top_sites_list.append(SiteDetails(site))

            if len(top_sites_list) == number:
                break

        filtered_list: list[SiteDetails] = []
        for site in top_sites_list:
            if site.scanned:
                filtered_list.append(site)

        sorted_list = sorted(filtered_list);
        sorted_list.reverse()

        return sorted_list


    @staticmethod
    def headers(site_list: List, num_header: int) -> List:
        """
        Return the headers and number of times they appear
        """
        headers: List[HeaderDetail] = []
        for site in site_list:
            for key in site.headers.keys():
                hd = list(filter(lambda x: x.name == key, headers))
                if len(hd) != 0:
                    hd[0].count += 1
                else:
                    headers.append(HeaderDetail(key, 1))

        return AlexaSites.top_headers(headers, num_header)

    @staticmethod
    def top_headers(headers: List[HeaderDetail], num_header: int) -> List:
        """
        Sort the header list to show the top headers
        """
        headers.sort(key=lambda x: x.count)
        headers.reverse()

        return headers[:num_header]

