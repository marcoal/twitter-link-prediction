import csv

# This script splits the data in the first column of a CSV into num_col segments, and places the segments
# side-by-side (opposite of "unrolling" a matrix).

num_cols = 9

links_1_col_file = '1000_to_2000links_1_col.csv'
links_split_col_outfile = '1000_to_2000links_' + str(num_cols) + '_col.csv'

rows = []
with open(links_1_col_file) as f:
    row = []
    for line in f.readlines():
        row.append(line[1:-2])
        if len(row) >= num_cols:
            rows.append(row)
            row = []

with open(links_split_col_outfile, 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['Quotation_HTML_' + str(col + 1) for col in xrange(num_cols)])
    for row in rows:
        csvwriter.writerow(row)