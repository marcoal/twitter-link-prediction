import xlrd
import csv

# This script reads in 'alllinks300_batch_results.xlsx, which has the text of the outlink surrounded by asterisks,
# and replaces the outlink text with an anchor tag hyperlink.

quotes_with_asterisks_file = 'alllinks300_batch_results.xlsx'
quotes_html_outfile = 'alllinks300_batch_html_values.csv'

quote_with_asterisks_index = 5
url_index = 3

quote_htmls = []

sheet = xlrd.open_workbook(quotes_with_asterisks_file).sheet_by_index(0)

for row_index in xrange(1, sheet.nrows - 1):
    row = sheet.row_values(row_index)
    quote_with_asterisks = []
    try:
        quote_with_asterisks = [quote_segment for quote_segment in row[quote_with_asterisks_index].split('*')]
        quote_html = quote_with_asterisks[0] + '<a href=\"' + row[url_index] + '\" target=\"_blank\">' + \
                     quote_with_asterisks[1] + '</a> ' + quote_with_asterisks[2]
        quote_htmls.append(quote_html)
    except:
        print 'ERROR: ' + str(row[quote_with_asterisks_index])

with open(quotes_html_outfile, 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for quote_html in quote_htmls:
        csvwriter.writerow([quote_html.encode('utf8')])