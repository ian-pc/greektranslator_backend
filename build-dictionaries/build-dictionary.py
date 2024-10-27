import json

# Load the lsj.json file
with open('lsj.json') as f:
    lsj = json.load(f)

dictionary = {}
exact = {}
greek = {}
latin = {}

# Process the lsj data
for key, val in lsj.items():
    dictionary[key] = val['d']
    
    for word in val['m']:
        if word not in exact:
            exact[word] = []
        exact[word].append(key)
    
    for word in val['g']:
        if word not in greek:
            greek[word] = []
        greek[word].append(key)
    
    for word in val['l']:
        if word not in latin:
            latin[word] = []
        latin[word].append(key)

# Write the processed data to JSON files
with open('dictionaries/dictionary.json', 'w') as f:
    json.dump(dictionary, f)

with open('dictionaries/exact-match.json', 'w') as f:
    json.dump(exact, f)

with open('dictionaries/greek-match.json', 'w') as f:
    json.dump(greek, f)

with open('dictionaries/latin-match.json', 'w') as f:
    json.dump(latin, f)
