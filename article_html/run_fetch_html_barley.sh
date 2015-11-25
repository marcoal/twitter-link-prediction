#!/bin/bash

# This bash script can be invoked in the qsub command
# to submit a job to barley. This script is called
# from the python script submit_job_barley.py.

# Tell grid engine to merge stdout and stderr streams.
#$ -j y

# # Mail to this address.
# #$ -M <your-email-address>@stanford.edu
# # Send mail on beginning, ending, or suspension of job.
# #$ -m bes

# Tell grid engine what directory to use.
# cwd means current directory.
#$ -cwd

echo ${args}

time python fetchHTML.py ${args}