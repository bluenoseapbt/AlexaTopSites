import argparse
import os
import logging

from typing import Any, Union
from site_details import AlexaSites
from datetime import datetime

LOG = logging.getLogger(__name__)

# Read in S3 credentials (~/.aws/credentials)
os.environ['AWS_PROFILE'] = "MyProfile"
os.environ['AWS_DEFAULT_REGION'] = "us-east-1"


def main(num_sites, num_headers, debug_level):
    """
    Main entry point
    """
    time_start = datetime.now()

    print('\nProcessing the top {} Alexa sites. Start time is: {}'.format(num_sites, time_start))

    logging.root.setLevel(level=debug_level)

    site_list = AlexaSites.top_sites(num_sites)

    print('\n\n------------------------ Per Site Statistics ---------------------------')

    rank = 1
    total_word_count = 0
    for site in site_list:
        print('{}) {}'.format(rank, site))
        total_word_count += site.word_count
        rank += 1

    print('\n\n------------------------ All Site Statistics ---------------------------')

    rank = 1
    number_of_sites = len(site_list)

    # Header info
    headers = AlexaSites.headers(site_list, num_headers)

    for header in headers:
        header_name = header.name
        header_percent = (header.count / number_of_sites) * 100
        print('{}) {} in {}% of sites'.format(rank, header_name, header_percent))
        rank += 1

    average_word_count = total_word_count / number_of_sites
    print('\n\nAverage word count: {}'.format(average_word_count))
    print('Duration of entire scan: {}'.format(datetime.now() - time_start))


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description="Script for the Alexa Top Sites.", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    PARSER.add_argument("-S", "--sites", type=int, default=1000, help="Total number of sites")
    PARSER.add_argument("-H", "--headers", type=int, default=20, help="Total number of headers")
    PARSER.add_argument(
        "-L", "--loglevel", type=str, default="INFO", help="Logging level. ex) DEBUG, INFO, WARN, ERROR, FATAL"
    )
    OPTIONS = PARSER.parse_args()

    main(OPTIONS.sites, OPTIONS.headers, OPTIONS.loglevel)



