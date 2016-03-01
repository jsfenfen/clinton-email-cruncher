
from asciidammit import asciiDammit

import re, csv
from urllib import urlopen
from nltk import word_tokenize
from nltk.stem.snowball import PorterStemmer, SnowballStemmer
from nltk.corpus import stopwords


stop = stopwords.words('english')
stemmer = SnowballStemmer("english")

#stemmer = PorterStemmer()

#email_file = open('/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/emails_from_hillary.csv', 'r')
email_file = open('/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/emails_to_hillary.csv', 'r')

hrc_reader  = csv.DictReader(email_file)

# parent_doc,offset,from,to,subj,sent,cc,questions,chars,hanle_valmor,text


field_names = ['doc_number', 'positive', 'negative', 'ratio_pos_over_neg', 'positive_ratio', 'negative_ratio','net_ratio', 'length', 'parent_doc','offset','from','to','subj','sent','cc','questions','chars']
output_fh = open("/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/sentiment/to_hrc_email_sentiment.csv", 'w')
#output_fh = open("/Users/jfenton/github-whitelabel/hrcemail/clinton-email-cruncher/sentiment/from_hrc_email_sentiment.csv", 'w')

output_fh.write(",".join(field_names) + "\n")
dictwriter = csv.DictWriter(output_fh, fieldnames=field_names, restval='', extrasaction='ignore')


##we already downloaded the files, just open them with: 

pos_words = open('/Users/jfenton/jsk/polisci_150B/021116/positive.txt','r').readlines()
neg_words = open('/Users/jfenton/jsk/polisci_150B/021116/negative.txt','r').readlines()


    
def dictify(word_array, stopwords=None):
    this_array = {}
    for i in word_array:
        i = i.lower().replace("\n","")
        i = stemmer.stem(i)
        if stopwords:
            try:
                stopwords[i]
            except KeyError:
                this_array[i]=1
        else:
            this_array[i]=1
    return this_array

stop_dict = dictify(stop)

neg_words_dict = dictify(neg_words)
pos_words_dict = dictify(pos_words)

def count_pos_neg_words(word_array):
    neg_word_count = 0
    pos_word_count = 0
    for this_word in word_array:
        # print "trying %s" % this_word
        try:
            pos_word_count += pos_words_dict[this_word]
        except KeyError:
            pass
        
        try:
            neg_word_count += neg_words_dict[this_word]
        except KeyError:
            pass
    
    return {'negative':neg_word_count, 'positive':pos_word_count}
    
    # field_names = ['doc_number', 'positive', 'negative', 'ratio_pos_over_neg', 'parent_doc','offset','from','to','subj','sent','cc','questions','chars']
    
for i, row in enumerate(hrc_reader):
    tokenized_words = word_tokenize(asciiDammit(row['text']))
    lowercase_stemmed_tokenized_words = [stemmer.stem(x.lower()) for x in tokenized_words]
    result = count_pos_neg_words(lowercase_stemmed_tokenized_words)
    length = len(lowercase_stemmed_tokenized_words)
    if length==0:
        length=1
    # print lowercase_tokenized_words
    print i, result
    ratio = 0
    if result['negative']:
        ratio =  (0.0+result['positive'])/(result['negative'] + 0.0)
    pos_ratio = result['positive']/(length+0.0)
    neg_ratio = result['negative']/(length+0.0)
    net_ratio = pos_ratio - neg_ratio
        
    #     parent_doc,offset,from,to,subj,sent,cc,questions,chars,hanle_valmor,text
    
    dictwriter.writerow({'doc_number':row['parent_doc'],'offset':row['offset'], 'positive':result['positive'], 'negative':result['negative'], 'ratio_pos_over_neg':ratio, 'positive_ratio':pos_ratio, 'negative_ratio':neg_ratio, 'net_ratio':net_ratio, 'length':length, 'from':row['from'], 'to':row['to'], 'subj':row['subj'], 'sent':row['sent'], 'cc':row['cc'], 'chars':row['chars']})
    # print "\n\n\n\n"