import csv, os, re

TEXT_OUTPUT_DIR = 'txts'
MANIFEST_LOCATION = 'file_manifest.csv'

SPLIT_EMAIL_DIR = 'split_emails/'
METADATA_CSV = 'email_split.csv'

FILE_NAME_RE = re.compile(r'pdfs\/(C\d+)\.pdf')

FROM_REGEX = re.compile(r'\A\s*From[:;]\s+(.*)\s*\Z', re.I)
TO_REGEX = re.compile(r'\A\s*To[:;]\s+(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
RELAXED_TO_REGEX = re.compile(r'\A\s*To\s+(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"

SENT_REGEX = re.compile(r'\A\s*Sent[:;]\s+(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
# Can't use this till we filter out the boilerplate that says date....
# DATE_REGEX = re.compile(r'\A\s*Date[:;]*\s+(.*)\s*\Z', re.I)
SUBJECT_REGEX = re.compile(r'\A\s*Subject[:;]*\s+(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"
CC_REGEX = re.compile(r'\A\s*Cc[:;]*\s+(.*)\s*\Z', re.I) # Sometimes the "To: field is empty C05739546_1.txt"

WRITE_SPLIT_EMAIL = True

def clean_email(email):
    email = email.replace("B6", "")
    email = email
    email = ' '.join(email.split())
    return email

def get_offset_fromdict(metadata_array, index):
    for i in metadata_array:
        try:
            if i['offset'] == index:
                return i['value']
        except KeyError:
            return ''
    return ''
    
def aggregate_email_data(metadata, email_sections, parent_document, dictwriter):
    # first element of email sections is  before first sent. 
    print "email_sections = %s" % len(email_sections)
    print parent_document, metadata
    
    for i,email in enumerate(email_sections):
        # ['parent_doc', 'offset', 'from', 'to', 'subj', 'sent', 'cc']
        this_email_data = {'from':get_offset_fromdict(metadata['from'], i), 'cc':get_offset_fromdict(metadata['cc'], i), 'to':get_offset_fromdict(metadata['to'], i), 'subj':get_offset_fromdict(metadata['subj'], i), 'sent':get_offset_fromdict(metadata['sent'], i), 'parent_doc':parent_document, 'offset':i}
        dictwriter.writerow(this_email_data)
        
        if WRITE_SPLIT_EMAIL:
            output_path = SPLIT_EMAIL_DIR + "/" + parent_document + "_part" + str(i) + ".txt"
            output_fh = open(output_path, 'w')
            output_fh.write(email)
            output_fh.close()

    
    

def read_metadata_from_txt_pages(list_of_files, dictwriter):
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
        in_to_field = False
        in_cc_field = False
        lastlinesent = False
        for i, line in enumerate(this_file):
            from_result = re.match(FROM_REGEX, line)
            if from_result:
                in_to_field = False
                in_cc_field = False
                body_offset += 1
                body_contents.append("")
                from_field = clean_email(from_result.group(1))
                has_from=True
                froms.append({'line':i, 'value':from_field, 'offset':body_offset})
                print "%s: From: '%s'" % (i, clean_email(from_field))
                continue


            to_result = re.match(TO_REGEX, line)
            if to_result:
                in_to_field = True
                to_field = clean_email(to_result.group(1))
                has_to=True
                tos.append({'line':i, 'value':to_field, 'offset':body_offset})
                print "%s: To: '%s'" % (i, to_field)
                continue
            else:
                relaxed_to_result = re.match(RELAXED_TO_REGEX, line)
                
                try:
                    if relaxed_to_result and i < froms[len(froms)-1]['line'] + 3:
                        in_to_field = True
                        to_field = clean_email(relaxed_to_result.group(1))
                        has_to=True
                        tos.append({'line':i, 'value':to_field, 'offset':body_offset})
                        print "%s: To: '%s'" % (i, to_field)
                        continue
                except IndexError:
                    pass
                
                
            
            sent_result = re.match(SENT_REGEX, line)
            if sent_result:
                lastlinesent = True
                sent_field = clean_email(sent_result.group(1))
                has_sent=True
                sents.append({'line':i, 'value':sent_field, 'offset':body_offset})
                # print "%s: Sent: '%s'" % (i, sent_field)
                continue
            else:
                lastlinesent = False
            
            """ Need to filter out lines that occur like this naturally.
            date_result = re.match(DATE_REGEX, line)
            if date_result:
                lastlinesent = True
                sent_field = clean_email(date_result.group(1))
                has_sent=True
                sents.append({'line':i, 'value':sent_field, 'offset':body_offset})
                print "%s: Sent: '%s'" % (i, sent_field)
                continue
            else:
                lastlinesent = False
            """
                                
            subj_result = re.match(SUBJECT_REGEX, line)
            if subj_result:
                lastlinesubject = True
                
                in_to_field = False
                in_cc_field = False
                subj_field = clean_email(subj_result.group(1))
                has_subj=True
                subjs.append({'line':i, 'value':subj_field, 'offset':body_offset})
                # print "%s: Subj: '%s'" % (i, subj_field)
                continue
            else: 
                lastlinesubject = True
                

            cc_result = re.search(CC_REGEX, line)
            if cc_result:
                in_to_field = False
                in_cc_field = True
                cc_field = clean_email(cc_result.group(1))
                ccs.append({'line':i, 'value':cc_field, 'offset':body_offset})
                # print "%s: cc: '%s'" % (i, cc_field)
                continue
            
            # deal with multiline to fields.
            if len(line)==1:
                in_to_field = False
                in_cc_field = False
            
            elif in_to_field:
                print "Multiline to field %s" % (list_of_files[0])
                tos[len(tos)-1]['value'] = tos[len(tos)-1]['value'] + " " + clean_email(line)

            elif in_cc_field:
                print "Multiline cc field %s" % (list_of_files[0])
                ccs[len(ccs)-1]['value'] = ccs[len(ccs)-1]['value'] + " " + clean_email(line)
            
            else:
                body_contents[body_offset] += line + "\n"
            
    #print body_contents
    if not has_from:
        print "No from field found in %s" % (list_of_files[0])
        pass
        
    """
    if has_from:
        if not has_to:
            print "Has from but no to: %s" % (list_of_files[0])
        if not has_subj:
            print "Has from but no subj: %s" % (list_of_files[0])
        if not has_sent:
            print "Has from but no sent: %s" % (list_of_files[0])
    """
    
    metadata = {'from':froms,'to':tos,'subj':subjs, 'sent':sents, 'cc':ccs }
    #txts/C05770109_1.txt
    txt_file = list_of_files[0].replace("txts/","").replace("_1.txt","")
    
    aggregate_email_data(metadata, body_contents, txt_file, dictwriter)

if __name__ == '__main__':
    
    # Create directories that do not exist.
    for directory in [SPLIT_EMAIL_DIR]:
        if not os.path.isdir(directory):
            os.system('mkdir -p %s' % directory)
    
    #file_list = ['txts/C05796382_1.txt',]
    #read_metadata_from_txt_pages(file_list)
    #assert False
    
    metadata_csv_fh = open(METADATA_CSV, 'w')
    fieldnames = ['parent_doc', 'offset', 'from', 'to', 'subj', 'sent', 'cc']
    metadata_csv_fh.write(",".join(fieldnames) + "\n")
    dictwriter = csv.DictWriter(metadata_csv_fh, fieldnames=fieldnames, restval='', extrasaction='ignore')
    
    
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
        
        read_metadata_from_txt_pages(file_list, dictwriter)

