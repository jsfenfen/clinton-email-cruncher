import csv
import re
from copy import deepcopy

NAME_HASH_FILE = 'allnames.csv'
WSJ_NAME_FILE = 'HRCEMAIL_names.csv'
OUTPUT_FILE = 'matched_names.csv'

### regexes to clean

BRACKETS = re.compile('\[.+?\]')
ANGLE_BRACES = re.compile('\<.+?\>')
PARENTHETICAL = re.compile('\(.+?\)')
EMAIL_DOMAIN = re.compile('@[\w\d]+\.\w\w\w')


def clean_email_name(name):
    raw_name = deepcopy(name)
    raw_name = re.sub(BRACKETS,'', raw_name)
    raw_name = re.sub(ANGLE_BRACES,'', raw_name)
    raw_name = re.sub(PARENTHETICAL,'', raw_name)
    #raw_name = re.sub(EMAIL_DOMAIN,'', raw_name)
    raw_name = raw_name.replace("'",'')
    raw_name = raw_name.strip()
    return raw_name
    
# originalName,commonName

wsj_name_hash = {}
print "Hashing wsj names"
wsjfh = open(WSJ_NAME_FILE, 'r')
dr = csv.DictReader(wsjfh)
for row in dr:
    wsj_name_hash[row['originalName'].strip()]=row['commonName']


print "reading names"
field_names = ['id', 'count', 'name', 'cleaned_name', 'wsj_common_name']
output_fh = open(OUTPUT_FILE, 'w')
output_fh.write(",".join(field_names) + "\n")
dictwriter = csv.DictWriter(output_fh, fieldnames=field_names, restval='', extrasaction='ignore')

total_hits = 0
name_hash_fh =  open(NAME_HASH_FILE, 'r')
dr = csv.DictReader(name_hash_fh)
for row in dr:
    cleaned_name = clean_email_name(row['name'])
    #print cleaned_name
    wsj_common_name = ''
    try:
        wsj_common_name = wsj_name_hash[cleaned_name]
        print "Found hit %s" % (cleaned_name)
        total_hits += 1
    except KeyError:
        pass
        
    dictwriter.writerow({'id':row['id'], 'name':row['name'], 'cleaned_name':cleaned_name, 'wsj_common_name':wsj_common_name, 'count':row['count']})

print "total hits: %s" % (total_hits)
