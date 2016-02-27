import csv, os, re

TEXT_OUTPUT_DIR = 'txts'
MANIFEST_LOCATION = 'file_manifest.csv'

FILE_NAME_RE = re.compile(r'pdfs\/(C\d+)\.pdf')

FROM_REGEX = re.compile(r'\A\s*From[:;]\s*(.*)\s*\Z', re.I)
TO_REGEX = re.compile(r'\A\s*To[:;]\s*(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
SENT_REGEX = re.compile(r'\A\s*Sent[:;]\s*(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
SUBJECT_REGEX = re.compile(r'\A\s*Subject[:;]\s*(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
CC_REGEX = re.compile(r'\A\s*Cc[:;]\s*(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"



def clean_email(email):
    email = email.replace("B6", "")
    email = email
    email = ' '.join(email.split())
    return email

def read_metadata_from_txt_pages(list_of_files):
    has_from = False
    has_to = False
    has_sent = False
    has_subj = False 
    
    froms = []
    tos = []
    subjs = []
    sents = []
    ccs = []
    
    body_contents = []
    body_offset = 0
    body_contents.append("")
    
    for page, filepath in enumerate(list_of_files):
        print "Handling %s %s" % (page, filepath)
        this_file = open(filepath)
        for i, line in enumerate(this_file):
            from_result = re.search(FROM_REGEX, line)
            if from_result:
                body_offset += 1
                body_contents.append("")
                from_field = clean_email(from_result.group(1))
                has_from=True
                froms.append({'line':i, 'value':from_field})
                print "%s: From: '%s'" % (i, clean_email(from_field))
                continue

            to_result = re.search(TO_REGEX, line)
            if to_result:
                to_field = clean_email(to_result.group(1))
                has_to=True
                tos.append({'line':i, 'value':to_field})
                print "%s: To: '%s'" % (i, to_field)
                continue

            sent_result = re.search(SENT_REGEX, line)
            if sent_result:
                sent_field = clean_email(sent_result.group(1))
                has_sent=True
                sents.append({'line':i, 'value':sent_field})
                print "%s: Sent: '%s'" % (i, sent_field)
                continue
                    
            subj_result = re.search(SUBJECT_REGEX, line)
            if subj_result:
                subj_field = clean_email(subj_result.group(1))
                has_subj=True
                subjs.append({'line':i, 'value':subj_field})
                print "%s: Subj: '%s'" % (i, subj_field)
                continue

            cc_result = re.search(CC_REGEX, line)
            if cc_result:
                cc_field = clean_email(cc_result.group(1))
                ccs.append({'line':i, 'value':cc_field})
                print "%s: cc: '%s'" % (i, cc_field)
                continue

            body_contents[body_offset] += line + "\n"
            
    #print body_contents
    if not has_from:
        print "No from field found in %s" % (list_of_files[0])
        pass
        
    if has_from:
        if not has_to:
            print "Has from but no to: %s" % (list_of_files[0])
        if not has_subj:
            print "Has from but no subj: %s" % (list_of_files[0])
        if not has_sent:
            print "Has from but no sent: %s" % (list_of_files[0])
        


if __name__ == '__main__':
    
    
    
    #file_list = ['txts/C05796382_1.txt',]
    #read_metadata_from_txt_pages(file_list)
    #assert False
    
    manifest_csv = open(MANIFEST_LOCATION, 'r')
    #manifest_csv.readline() # skip the info line at the top
    dr = csv.DictReader(manifest_csv)
    files = []
    for row in dr:
        files.append({'local_filepath':row['local_filepath'], 'remote_filepath':row['remote_filepath'], 'id':row['id'], 'Filesize':row['Filesize'], 'PDFversion':row['PDFversion'], 'Pagesize':row['Pagesize'], 'total_pages':int(row['Pages'])})

    pages_converted = 0

    for doc in files:

        pdffilename = doc['local_filepath']
        total_pages = doc['total_pages']
        
        file_list = []
        for page_number in range (1,total_pages+1):
            
            fileregexgroups = FILE_NAME_RE.findall(doc['local_filepath'])
            filename = fileregexgroups[0]

            page_filename = TEXT_OUTPUT_DIR + "/%s_%s.txt" % (filename, page_number)
            file_list.append(page_filename)
        
        read_metadata_from_txt_pages(file_list)

