# -*- coding: utf-8 -*-
__author__ = 'marcoantonio'
import urllib2
import gzip
import os
import traceback
import logging
import re
import sys
import threading
from optparse import OptionParser

_PERCENT_PROGRESS = 0.00001  #  what percent progress will be logged
logger = logging.getLogger('fetchHTML')


def fetch_file(url):
    try:
        req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logger.warn("::HTTP error for {0}: code {1}".format(url, e.code))
        return ''
    except urllib2.URLError, e:
        logger.warn("::Url error for {0}: with args {1}".format(url, e.args))
        return ''
    except Exception, e:
        logger.warn("::Exception for url %s. Got %s, %s, Showing traceback:\n%s" % (url, type(e), e, traceback.format_exc()))
        return ''
    return response.read()

def fetch_files(urls, output_filename, progress_interval_percent, skip_percent=0.0, thread_id=-1):
    if thread_id >= 0:
        logger.info('Starting thread %d', thread_id)

    num_urls_per_interval = max(1, int(progress_interval_percent / 100 * len(urls)))

    with gzip.open(os.path.join(path, output_filename), mode='wb') as f:
        for i, url in enumerate(urls):
            # Skip over the first skip_percent of the urls.
            if skip_percent > 0 and float(i) / len(urls) * 100 < skip_percent:
                continue

            # Print the progress every time progress_interval_percent of the URLs are fetched.
            if i % num_urls_per_interval == 0:
                logger.info('\tTHREAD %d: PROGRESS=%f%%\n' % (max(0, thread_id), float(i) / len(urls) * 100))

            html = fetch_file(url)

            # Continue if an error is encountered while fetching this URL.
            if not html:
                continue

            f.writelines('-------------------------------------------------------\nU %s\n' % url)
            f.writelines(html)

    if thread_id >= 0:
        logger.info('Terminating thread %d', thread_id)

if __name__ == '__main__':
    # Parse the arguments.
    parser = OptionParser()
    parser.add_option('-f', '--url_filename', default='urls_josh.txt',
                      help='URL file, were each line has the form:\nU\twww.example.com')
    parser.add_option('-o', '--output_filename_prefix', default='raw_html',
                      help='output filename excluding the file extension')
    parser.add_option('-n', '--num_threads', type='int', default=1,
                      help='number of threads to spawn')
    parser.add_option('-s', '--skip_percent', type='float', default=0.00,
                      help='skip the first p% of URLs in url_filename')
    parser.add_option('-p', '--progress_interval', type='float', default=0.001,
                      help='print the percent of URLs completed every time p% progress is made')
    options, args = parser.parse_args()
    if not options.url_filename:
        print 'Usage: fetchHTML.py -u <url_filename> [options]'
        exit(1)

    # Initialize the logger.
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    logger.info('Running %s '.join(sys.argv))

    # Read urls into RAM.
    # Note: to get urls.txt run:
    # > cat roks_data_file | grep "^U" > urls.txt
    logger.info('Reading urls...')
    path = os.path.dirname(os.path.abspath(__file__))
    urls = []
    with open(os.path.join(path, options.url_filename)) as f:
        for line in f:
            found = re.search("U\s(.*)", line)
            if found:
                url = found.group(1)
                urls.append(url)

    #  Fetch URLs and write results to a compressed file. If num_threads > 1, spawn multiple threads to split the work.
    logger.info('Starting html fetch')
    if options.num_threads == 1:
        fetch_files(urls, options.output_filename_prefix + '.txt.gz', options.progress_interval, options.skip_percent)
    else:
        url_chunk_length = int(len(urls) / options.num_threads)
        threads = []
        for thread_id in xrange(options.num_threads):
            url_chunk = urls[thread_id * url_chunk_length:min(len(urls), (thread_id + 1) * url_chunk_length)]
            chunk_output_filename = options.output_filename_prefix + '_' + str(thread_id) + '.txt.gz'
            threads.append(threading.Thread(target=fetch_files, args=(url_chunk,
                                                                      chunk_output_filename,
                                                                      options.progress_interval,
                                                                      options.skip_percent,
                                                                      thread_id)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()