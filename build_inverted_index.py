# sorts the forward index to make inverted index
import json
from pathlib import Path

# loads the forward index
forward_index = json.loads(Path('forward_index.json').read_text())

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