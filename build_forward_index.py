import time
import json
from pathlib import Path
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

start = time.time()
paths = Path("newsdata")
all_articles_paths = [p for p in paths.glob('*.json')]

lexicon = {}
doc_index = {}
forward_index = {}
remove_duplicate_articles = {}
word_id = 0
doc_id = 0
total = 0
new_num = 0
stemmer = SnowballStemmer('english')
stop_words = set(stopwords.words('english'))
# This piece of code tokenizes and cleans data 
# and build the lexicon, document index and forward index
# --------------
# for every file in newsdata/ folder
for articles_path in all_articles_paths:
    articles = json.loads(Path(articles_path).read_text())
    # for every article in one file
    for article in articles:
        if article['url'] in remove_duplicate_articles:
            continue

        remove_duplicate_articles[article['url']] = new_num
        new_num += 1
        # If article's url not in prev_docs, then we
        # update our lexicon, doc_index and forward index
        if total % 1000 == 0:
            print(total)
        total += 1
        hit_list = {}
        doc_index[doc_id] = [article['title'], article['url']]
        text = article['content']
        # split into words
        tokens = word_tokenize(text)
        # convert to lower case
        tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
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
                    lexicon[word] = word_id
                    word_id += 1

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
            

        forward_index[doc_id] = hit_list # insert hit list in forward index
        doc_id += 1 # get the next doc_id
                
        
# write lexicon to file
lex_data = json.dumps(lexicon)
Path('lexicon.json').write_text(lex_data)
# write doc_index to file
doc_index_data = json.dumps(doc_index)
Path('doc_index.json').write_text(doc_index_data)
# write forward_index to file
forward_index_data = json.dumps(forward_index)
Path('forward_index.json').write_text(forward_index_data)
# -------------
end = time.time()
print(str(end - start) + " seconds")