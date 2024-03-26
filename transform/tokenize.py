import re
from .tag_converter import convert


def split_tag(tag):
    if not tag:
        return None, None
    # ISSUE: place tag validator here
    match = re.fullmatch(r'([-а-я]+)=([A-Z]+)(.*=.*)', tag)
    if not match:
        raise ValueError(f'Invalid tag format: {tag}')
    # gramm = match[3]
    gramm = convert([v for v in re.split('[=,]', match[3]) if v])
    lemma, pos = match[1], match[2]
    return (lemma, ','.join([pos] + gramm))

def tokenize(annotation, is_tagged=False):
    regexp = re.compile('([-А-яЁё]+){(.*?)}') if is_tagged else re.compile('[-А-яЁё]+')

    _, _, value = annotation
    tokens = regexp.findall(value)
    
    for token in tokens:
        if not is_tagged:
            yield token
        else:
            lemma, gramm = split_tag(token[1])
            yield token[0], lemma, gramm       