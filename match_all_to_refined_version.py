import csv
import re

NAME_HASH_FILE = 'matched_names.csv'
NAME_HASH_FINAL = 'allnames_cleaned.csv'
REFINED_NAME_FILE = 'top_matched_names_cleaned.csv'



    
# name,column_fixed,count,wsj_common_name

refined_name_to_wsj_hash = {}
raw_name_to_wsj_hash = {}

print "Hashing cleaned names to wsj name"
refinefh = open(REFINED_NAME_FILE, 'r')
dr = csv.DictReader(refinefh)
for row in dr:
    try:
        val = refined_name_to_wsj_hash[row['name_refined']]
    except KeyError:
        if row['wsj_common_name']:
            refined_name_to_wsj_hash[row['name_refined']] = row['wsj_common_name']
        else:
            refined_name_to_wsj_hash[row['name_refined']] = row['name_refined']
            
    try:
        val = raw_name_to_wsj_hash[row['name']]
    except KeyError:
        if row['wsj_common_name']:
            raw_name_to_wsj_hash[row['name']] = row['wsj_common_name']
        else:
            raw_name_to_wsj_hash[row['name']] = row['name']



            
# print refined_name_to_wsj_hash

refinefh.seek(0)
dr = csv.DictReader(refinefh)
all_name_dict = {}
for row in dr:
    fixed_val = ''
    try:
        fixed_val = refined_name_to_wsj_hash[row['name_refined']]
    except KeyError:
        
        try:
            fixed_val = raw_name_to_wsj_hash[row['name']]
        
        except KeyError:
            fixed_val = row['name_refined']
        
        
        if not fixed_val:
            fixed_val = row['name_refined']
    
    try:
        all_name_dict[row['name']]
    except KeyError:
        all_name_dict[row['name']] = fixed_val
print all_name_dict

outfilefh = open(NAME_HASH_FINAL, 'w')
fieldnames = ['id', 'count', 'name', 'cleaned_name', 'final_name']
outfilefh.write(",".join(fieldnames) + "\n")
dictwriter = csv.DictWriter(outfilefh, fieldnames=fieldnames, restval='', extrasaction='ignore')


name_hash_fh =  open(NAME_HASH_FILE, 'r')
dr = csv.DictReader(name_hash_fh)
errors = 0
for row in dr:
    fixed_val = ''
    name = row['name']
    try:
        fixed_val = all_name_dict[name]
    except KeyError:
        errors += 1
        fixed_val = name
    row['final_name'] = fixed_val
    dictwriter.writerow(row)
    
print "errors: %s" % (errors)
    
    
