import csv

CLEANED_FILE = '/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/cleaned_split_metadata.csv'
R_OUTPUT_TXT = '/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/emails_from_hillary.csv'
#OUTPUT_TXT = '/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/data_hillary.csv'

email_metadata = open(CLEANED_FILE,'r')
cf = csv.DictReader(email_metadata)

metadata_csv_fh = open(R_OUTPUT_TXT, 'w')
fieldnames = ['parent_doc', 'offset', 'from', 'to', 'subj', 'sent', 'cc', 'questions', 'chars', 'hanle_valmor', 'text']
metadata_csv_fh.write(",".join(fieldnames) + "\n")
dictwriter = csv.DictWriter(metadata_csv_fh, fieldnames=fieldnames, restval='', extrasaction='ignore')


def clean_for_R(this_line):
    line = this_line
    line = line.replace("\n"," ")
    line = line.replace("'","")
    line = line.replace('"','')
    line = line.replace("\r"," ")
    line = line.replace("\t"," ")
    line = line.replace(","," ")
    return ' '.join(line.split())


#outfile = open(OUTPUT_TXT, 'w')


count = 0

for row in cf:
    is_from_hillary = False
    
    if row['Sender'].find('Hillary Clinton') >= 0:
        is_from_hillary = True
    elif row['Sender'].find('HDR') >= 0:
        is_from_hillary = True
    
    
    if is_from_hillary:
        count += 1
        print "%s %s %s" % (row['DocNumber'], row['Sender'], row['offset'])
        file_name = 'split_emails/' + row['DocNumber'] + "_part" + str(row['offset']) + ".txt"
        
        ft = clean_for_R(open(file_name, 'r').read())
        
        chars = list(ft)
        question_marks = chars.count('?')
        email_length = len(chars)
        
        hanle_valmor = 0
        if row['Recipient'].lower().find('valmor') >= 0 or row['Recipient'].lower().find('hanle') >= 0:
            hanle_valmor=1
        
        dictwriter.writerow({'parent_doc':row['DocNumber'], 'offset':row['offset'], 'from':row['Sender'], 'to':row['Recipient'], 'subj':row['Subject'], 'sent':row['DateSent'], 'cc':row['CC'], 'text':ft, 'questions':question_marks, 'chars': email_length, 'hanle_valmor':hanle_valmor})
        
        
        

print "Total emails %s" % count