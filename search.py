import tkinter as tk
from tkinter import filedialog
import subprocess
from tkhtmlview import HTMLScrolledText
import json
from pathlib import Path
import string
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

  
def search_event():
    query = inputtxt.get(1.0, "end-1c") # get the text from textbox
    query_words = query.split() # tokenize the query words

    # santize the query:
    # remove punctuations, stopwords
    # stem the query words
    query_words = [w.lower() for w in query_words]
    query_words = [w for w in query_words if w not in stop_words]
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in query_words]
    query_words = [word for word in stripped if word.isalpha()]
    query_words = [stemmer.stem(w) for w in query_words]


    # get the word ids of the words from lexicon
    query_word_ids = []
    for word in query_words:
        query_word_ids.append(lexicon.get(word, ''))

    query_word_ids = [w for w in query_word_ids if w != '']
    if len(query_word_ids) == 0:
        no_results = tk.Label(frame, text='No results')
        no_results.pack()
    else:
        empty_set = {}
        docs = search_inverted(empty_set, query_word_ids, len(query_word_ids) - 1)
        while len(docs) == 0:
            empty_set = {}
            del query_word_ids[-1] # delete the last word_id from the list
            if len(query_word_ids) == 0:
                break
            docs = search_inverted(empty_set, query_word_ids, len(query_word_ids) - 1)
        if len(docs) == 0:
            no_results = tk.Label(frame, text='No results')
            no_results.pack()
        # Calculate rank
        else:
            rank = {}
            for doc_id in docs:
                rank[doc_id] = 0
                for word_id in query_word_ids:
                    hit = inverted_index[str(word_id)][doc_id]
                    hit = int(bin(hit & 65535), 2) # to check if MSB is 1 for 16 bit num
                    if hit >= 32768: # if MSB == 1 i.e it is a fancy hit
                        rank[doc_id] += 50 # rank increment for fancy hit

                    hit = int(bin(hit & 32767), 2) # 32767 = 0111_1111_1111_1111
                    rank[doc_id] += hit # add the remaining number after setting MSB to 0
                    

            rank = sorted(rank.items(), key=lambda x: x[1], reverse=True) # return list of tuples

            html_string = ''
            total = 0
            for doc_id, rank_n in rank:
                total += 1
                if total == 200:
                    break
                title = doc_index[doc_id][0] # get the document title from document index
                url = doc_index[doc_id][1] # get the document url from the document index
                # now we first display the url and then the title
                html_string += '<i style="font-size:8px">'+ str(url) +'</i><br><a style="font-size:15px" href=\"' + str(url) + '\">' + str(title) + '</a><br><br>'
                
            html_label = HTMLScrolledText(frame, html=html_string)
            searchAgainButton = tk.Button(frame, text='Search Again', command=lambda: [html_label.pack_forget(), searchAgainButton.pack_forget()])
            searchAgainButton.pack()
            html_label.pack(fill='both', expand=True)



def search_inverted(all_doc_ids, query_word_ids, last):
    if (last == -1): # base condition
        return all_doc_ids
    word_id = query_word_ids[last]
    doc_id_list = inverted_index[str(word_id)].keys()
    docs = set(doc_id_list)
    all_doc_ids = set(all_doc_ids) | docs # take union with all doc ids
    return docs & search_inverted(all_doc_ids, query_word_ids, last-1) # recursively take intersections


def open_file_dialog():
    # select file with File Chooser
    filename = tk.filedialog.askopenfilename()
    # run a subprocess to update the forward and inverted index
    try:
        subprocess.call(['python', 'update_forward_and_inverted_index.py', filename], shell=True)
    except FileNotFoundError:
        print('File not found')

    # load them again after new insertions
    global inverted_index
    inverted_index = json.loads(Path("inverted_index.json").read_text())
    global lexicon
    lexicon = json.loads(Path("lexicon.json").read_text())
    global doc_index
    doc_index = json.loads(Path("doc_index.json").read_text())
    


# load the inverted index, lexicon and document index in memory
inverted_index = json.loads(Path("inverted_index.json").read_text())
lexicon = json.loads(Path("lexicon.json").read_text())
doc_index = json.loads(Path("doc_index.json").read_text())

# Top level window
frame = tk.Tk()
frame.title("DuckDuckGo")
frame.geometry('1200x600')
# Function for getting Input
# from textbox and printing it 
# at label widget

stemmer = SnowballStemmer('english') # construct a stemmer to stem the query
stop_words = set(stopwords.words('english')) # to remove stopwords from query
stop_words.add('the')

# Enter query label
start_label = tk.Label(frame, text='Enter Query: ')
start_label.pack()

# TextBox Creation
inputtxt = tk.Text(frame, height = 1, width = 80)
inputtxt.pack()
inputtxt.configure(font=('Arial', 16))
  
# Button Creation
searchButton = tk.Button(frame, text='Search', command=search_event)
searchButton.pack()

# import new file button
importFileButton = tk.Button(frame, text='Insert File', command=open_file_dialog)
importFileButton.place(x=20, y=80)

frame.mainloop()