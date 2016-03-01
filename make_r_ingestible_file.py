import csv, os, re

from clean_boilerplate import remove_boilerplate

FILE_NAME_RE = re.compile(r'pdfs\/(C\d+)\.pdf')
MANIFEST_LOCATION = 'file_manifest.csv'
TEXT_OUTPUT_DIR = 'txts'

R_OUTPUT_TXT = 'emails_output.csv'

def clean_for_R(this_line):
    line = this_line
    line = line.replace("\n"," ")
    line = line.replace("'","")
    line = line.replace('"','')
    line = line.replace("\r"," ")
    line = line.replace("\t"," ")
    line = line.replace(","," ")
    return ' '.join(line.split())

def get_cleaned_text_from_pages(list_of_files):
    
    
    full_text = ''
    for page, filepath in enumerate(list_of_files):
        this_file = open(filepath)
        
        for line in this_file:
            
            this_line = remove_boilerplate(line)
            full_text += " " + clean_for_R(this_line)
    
    return full_text
    
if __name__ == '__main__':
    
    # sketchy r output goes here. it's a csv, but don't use csv lib for this. 
    outfile = open(R_OUTPUT_TXT, 'w')
    outfile.write("doc,text\n")
    
    manifest_csv = open(MANIFEST_LOCATION, 'r')
    #manifest_csv.readline() # skip the info line at the top
    dr = csv.DictReader(manifest_csv)
    files = []
    for row in dr:
        files.append({'local_filepath':row['local_filepath'], 'remote_filepath':row['remote_filepath'], 'id':row['id'], 'Filesize':row['Filesize'], 'PDFversion':row['PDFversion'], 'Pagesize':row['Pagesize'], 'total_pages':int(row['Pages'])})

    pages_converted = 0

    for doc in files:
    
        pdffilename = doc['local_filepath']
        pdffilename = pdffilename.replace('pdfs/','')
        pdffilename = pdffilename.replace('.pdf','')

        total_pages = doc['total_pages']
        file_list = []
        for page_number in range (1,total_pages+1):
        
            fileregexgroups = FILE_NAME_RE.findall(doc['local_filepath'])
            filename = fileregexgroups[0]
            page_filename = TEXT_OUTPUT_DIR + "/%s_%s.txt" % (filename, page_number)
            file_list.append(page_filename)
    
        ft = get_cleaned_text_from_pages(file_list)
        outfile.write("%s,%s\n" % (pdffilename, ft))
        
    outfile.close()
    
