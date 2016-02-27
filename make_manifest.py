""" Read a directory of pdfs and run pdf info on each, storing results to a csv file. """

import csv, os, subprocess
from wrap_pdfinfo import pdfinfo
from datetime import datetime

MANIFEST_LOCATION = 'file_manifest.csv'
PDF_DIR = 'pdfs'
files_found = 0
start_time = datetime.now()


fh = open(MANIFEST_LOCATION, 'w')
# remote filepath is empty here. 
fieldnames = ['id', 'local_filepath', 'remote_filepath', 'Tagged', 'Producer', 'Creator', 'Encrypted', 'Author', 'Filesize', 'Optimized', 'PDFversion', 'Title', 'Pagesize', 'CreationDate', 'Pages']
fh.write(",".join(fieldnames) + "\n")
dictwriter = csv.DictWriter(fh, fieldnames=fieldnames, restval='', extrasaction='ignore')


for d, _, files in os.walk(PDF_DIR):

    for i, this_file in enumerate(files):
        files_found += 1
        file_path = PDF_DIR + "/" + this_file
        
        # avoid id number of zero
        row = {'local_filepath':file_path, 'id':i+1}
        
        # get pdfinfo data
        pdf_data = None
        try:
            pdf_data = pdfinfo(file_path)
        except subprocess.CalledProcessError:
            # Sometimes this happens on weird pdfs. Just note it and keep going.
            print "WARNING: couldn't run pdfinfo on %s" % (pdf_data)
            
        if pdf_data:
            result_dict = dict(row.items() + pdf_data.items())
        else:
            result_dict = row
        
        dictwriter.writerow(result_dict)
        