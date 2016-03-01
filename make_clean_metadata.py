import csv
import re


NAME_HASH_FINAL = 'allnames_cleaned.csv'
METADATA_FLATTENED = 'cleaned_split_metadata.csv'


final_hash_fh =  open(NAME_HASH_FINAL, 'r')
dr = csv.DictReader(final_hash_fh)
name_lookup = {}
for row in dr:
    try:
        name_lookup[row['name']]
    except KeyError:
        name_lookup[row['name']] = row['final_name']


def get_lookup(name):
    fixed_name = name
    try:
        fixed_name = name_lookup[name]
    except KeyError:
        pass
    return fixed_name
    

field_names = ['DocNumber', 'Subject', 'Recipient', 'Sender', 'DateSent', 'CC', 'offset']
output_fh = open(METADATA_FLATTENED, 'w')
output_fh.write(",".join(field_names) + "\n")
dictwriter = csv.DictWriter(output_fh, fieldnames=field_names, restval='', extrasaction='ignore')


email_metadata = open('email_split.csv','r')
er = csv.DictReader(email_metadata)

metadata_dict = {}
for row in er:
    tos = row["to"].split(';')
    from_fixed = get_lookup(row["from"])
    ccs = row["cc"].split(';')
    
    for i, name in enumerate(tos):
        tos[i] = get_lookup(name)
    to_fixed = ";".join(tos)
    
    for i, name in enumerate(ccs):
        ccs[i] = get_lookup(name)
    cc_fixed = ";".join(ccs)
    
    dictwriter.writerow({'DocNumber':row['parent_doc'], 'Subject':row['subj'], 'Recipient':to_fixed, 'Sender':from_fixed, 'DateSent':row['sent'], 'CC':cc_fixed, 'offset':row['offset']})
    
    
    
    
        