#!/usr/bin/python

'''
This file automates submitting a taxi_pickups.py run to Stanford's
SGE system on the barley machines.
You can change the parameters to the qsub command below.
Sample usage:
    python submit_twitter_graph_barley_job.py authors_josh.tsv
'''

import os
import sys

args = ' '.join(sys.argv[1:])

# qsub command: submits jobs to the barley queue. For more information, see:
# https://web.stanford.edu/group/farmshare/cgi-bin/wiki/index.php/FarmShare_tutorial
#	qsub parameters:
#   -N  ... job name
#   -l ... what follows is resource request parameters
#   mem_free=1G ... request 1 GB per core
#   -pe shm 4 ... request 4 cores
os.system('qsub -v args="%s" -l mem_free=1G -pe shm 1 -N fetch_html ' \
    'run_fetch_html_barley.sh' % args)