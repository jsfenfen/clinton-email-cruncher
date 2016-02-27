import csv, os, re
from datetime import datetime
from time import sleep

TEXT_OUTPUT_DIR = 'txts'
MANIFEST_LOCATION = 'file_manifest.csv'
RESULT_LOCATION = 'files_processed.csv'


# Create directories that do not exist.
for directory in [TEXT_OUTPUT_DIR]:
    if not os.path.isdir(directory):
        os.system('mkdir -p %s' % directory)


FILE_NAME_RE = re.compile(r'pdfs\/(C\d+)\.pdf')

if __name__ == '__main__':
    manifest_csv = open(MANIFEST_LOCATION, 'r')
    #manifest_csv.readline() # skip the info line at the top
    dr = csv.DictReader(manifest_csv)
    files = []
    for row in dr:
        files.append({'local_filepath':row['local_filepath'], 'remote_filepath':row['remote_filepath'], 'id':row['id'], 'Filesize':row['Filesize'], 'PDFversion':row['PDFversion'], 'Pagesize':row['Pagesize'], 'total_pages':int(row['Pages'])})

    start = datetime.now()
    pages_converted = 0

    for doc in files:

        pdffilename = doc['local_filepath']
        total_pages = doc['total_pages']
        print "pdffilename is %s total_pages is %s" % (pdffilename, total_pages)

        for page_number in range (1,total_pages+1):
            pages_converted += 1
            end = datetime.now()
            print "time %s" % (end-start)

            doc['pagenumber'] = page_number
            fileregexgroups = FILE_NAME_RE.findall(doc['local_filepath'])
            filename = fileregexgroups[0]
            
            output_filename = TEXT_OUTPUT_DIR + "/%s_%s.txt" % (filename, page_number)
            layout_cmd = "pdftotext -f %s -l %s -layout %s %s" % (page_number, page_number, doc['local_filepath'], output_filename)
            print layout_cmd
            result = os.popen(layout_cmd).read()
            print result
        