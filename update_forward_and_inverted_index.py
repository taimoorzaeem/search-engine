import json
import sys
from pathlib import Path
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

filepath = sys.argv[1]

# load lexicon, document index and forward index into memory
lexicon = json.loads(Path('lexicon.json').read_text())
doc_index = json.loads(Path('doc_index.json').read_text())
forward_index = json.loads(Path('forward_index.json').read_text())

# get the next doc_id and word_id from doc_index and lexicon
next_doc_id = int(max(doc_index.keys()))
next_doc_id += 1
next_word_id = max(lexicon.values())
next_word_id += 1

new_num = 0

# construct a stemmer and get stopwords
stemmer = SnowballStemmer('english')
stop_words = set(stopwords.words('english'))
remove_duplicate_articles = {}
# get previous document urls
prev_docs = doc_index.values()
prev_docs = [title_url[1] for title_url in prev_docs]

print("Updating forward index...")
# for every file in newsdata/ folder

articles = json.loads(Path(filepath).read_text())
    # for every article in one file
for article in articles:
    if article['url'] in remove_duplicate_articles:
        continue


    remove_duplicate_articles[article['url']] = new_num
    new_num += 1
                
    hit_list = {}
    doc_index[next_doc_id] = [article['title'], article['url']]
    text = article['content']
    # split into words
    tokens = word_tokenize(text)
    # convert to lower case
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
                # filter out stop words
    words = [w for w in words if not w in stop_words]
                # stem the words
    words = [stemmer.stem(w) for w in words]
    for word in words:
        # insert word in lexicon that is not already in lexicon
        if word not in lexicon:
            lexicon[word] = next_word_id
            next_word_id += 1

                # make hit list
    for word in words:
        temp_hit = 0
        if lexicon[word] not in hit_list:
            if (word in article['title']) or (word in article['url']): # if fancy hit
                # we set the MSB to one in hit to indicate that the hit is fancy
                temp_hit = int(bin(temp_hit | 32768), 2) # 32768 == 0b1000_0000_0000_0000
                        
            temp_hit += 1
            hit_list[lexicon[word]] = temp_hit

        else:
            hit_list[lexicon[word]] += 1 # increment the occurances already in hit list
                

    forward_index[next_doc_id] = hit_list # insert hit list in forward index
    next_doc_id += 1

# write lexicon to file
lex_data = json.dumps(lexicon)
Path('lexicon.json').write_text(lex_data)
# write doc_index to file
doc_index_data = json.dumps(doc_index)
Path('doc_index.json').write_text(doc_index_data)
# write forward_index to file
forward_index_data = json.dumps(forward_index)
Path('forward_index.json').write_text(forward_index_data)

print("Building forward index...")
inverted_index = {}

# outer loop to iterate over the doc_ids in forward index
for doc_id in forward_index.keys():
    # inner loop to iterate over the word ids of a document
    for word_id in forward_index[doc_id]:
        if word_id in inverted_index: # if word id is already a key in inverted index
            # then assign the doc id and hit as value to the word id in inverted index
            inverted_index[word_id][doc_id] = forward_index[doc_id][word_id]
            
        else:
            # the word id is not in inverted index
            temp_dict = {}
            # assign the current doc id and hit asa value to word id in inverted index
            temp_dict[doc_id] = forward_index[doc_id][word_id]
            inverted_index[word_id] = temp_dict
    
    # just to see progress in terminal
    # TODO: remove the following two lines
    if (int(doc_id) % 1000 == 0):
        print(doc_id)

print("Writing the inverted index to file...")
# write the json object to file
inv_data = json.dumps(inverted_index)
Path('inverted_index.json').write_text(inv_data)
print("Updation Completed.")