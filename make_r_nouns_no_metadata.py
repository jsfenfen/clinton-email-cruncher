import csv, os, re
from get_noun_phrases import process_text
from datetime import datetime
from asciidammit import asciiDammit
from clean_boilerplate import remove_boilerplate

FILE_NAME_RE = re.compile(r'pdfs\/(C\d+)\.pdf')
METADATA_CSV = 'email_split.csv'
TEXT_OUTPUT_DIR = 'txts'

R_OUTPUT_TXT = 'emails_output_nouns.csv'

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
            
        this_file.close()
    
    return full_text
    
if __name__ == '__main__':
    
    # sketchy r output goes here. it's a csv, but don't use csv lib for this. 
    outfile = open(R_OUTPUT_TXT, 'w')
    outfile.write("doc,text\n")
    
    metadata_csv = open(METADATA_CSV, 'r')
    #manifest_csv.readline() # skip the info line at the top
    dr = csv.DictReader(metadata_csv)
    file_lookup = {}
    for row in dr:
        try:
            file_lookup[row['parent_doc']].append(row['offset'])
        except KeyError:
            file_lookup[row['parent_doc']] = [row['offset']]

    pages_converted = 0

    for i, doc in enumerate(file_lookup.keys()):
        this_array = file_lookup[doc]
        print "%s %s" % (doc, this_array)
        file_list = []
        for doc_num in this_array:
            file_name = 'split_emails/' + doc + "_part" + str(doc_num) + ".txt"
            file_list.append(file_name)
            
        ft = asciiDammit(get_cleaned_text_from_pages(file_list))
        #print "input text: %s" % (ft)
        start = datetime.now()
        terms = process_text(ft)
        text = ''
        for x in terms:
            text += " " + "-".join(x)
        end = datetime.now()
        print "%s: time to run once: %s" % (i, end-start)
        
        #print "output text: %s" % (text)
        outfile.write("%s,%s\n" % (doc, text))
        
    outfile.close()
    
