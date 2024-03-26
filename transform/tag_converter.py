import json
from difflib import SequenceMatcher
from bidict import bidict


with open('transform/tags.json', 'r', encoding='utf-8') as fp:
    gram, mistake, theme, genre = json.load(fp).values()
    gram = bidict(gram)

def convert_gram(tags, mode='en'):
    out = []

    if mode == 'en':
        for tag in tags:
            out.append(gram[tag])
    elif mode == 'ru':
        for tag in tags:
            out.append(gram.inverse[tag])

    return out

def most_similar_seq(seq, seq_list, ratio=0.6):
    """Find the most similar str sequence against the list."""
    if seq in seq_list:
        return seq
    ratios = [SequenceMatcher(None, seq, it).quick_ratio() for it in seq_list]
    maxr = max(ratios)
    if maxr < ratio:
        return None
    return seq_list[ratios.index(maxr)]
    

def validate_mistake(tag):
    res = most_similar_seq(tag, mistake)
    if res is not None:
        print(f'Unknown tag "{tag}". Did you mean "{res}"?')

def convert_theme():
    pass

def convert_genre():
    pass

validate_mistake('MorfCase')