import re
from .tag_converter import TagConverter


def split_tag(tag):
    if not tag:
        return None, None
    # FEAT: place tag validator here
    match = re.fullmatch(r'([-а-я]+)=([A-Z]+)(.*=.*)', tag)
    if not match:
        raise ValueError(f'Invalid tag format: {tag}')
    tc = TagConverter()
    gramm = tc.convert_gram([v for v in re.split('[=,]', match[3]) if v])
    lemma, pos = match[1], match[2]
    return (lemma, ','.join([pos] + gramm))

def tokenize_tier(annotation_data, is_tagged=False):
    regex = re.compile('([-А-яЁё]+){(.*?)}') if is_tagged else re.compile('[-А-яЁё]+')
    
    for ann in annotation_data:
        begin, end, value = ann
        tokens = regex.findall(value)
        
        if is_tagged:
            words = []
            lemmas = []
            gramms = []
            for word, tag in tokens:
                lemma, gramm = split_tag(tag)
                words.append((begin, end, word))
                lemmas.append((begin, end, lemma))
                gramms.append((begin, end, gramm))
            yield words, lemmas, gramms
        else:
            words = []
            for token in tokens:
                words.append((begin, end, token))
            yield words
