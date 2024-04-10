import json
from difflib import SequenceMatcher


class TagConverter:
    with open('processing/tags.json', 'r', encoding='utf-8') as fp:
        for key, value in json.load(fp).items():
            locals()[key.upper()] = value
        
    def __init__(self):
        self.mapping = {}
        
    def convert_gram(self, tags, mode='en'):
        if mode == 'en':
            gram = self.GRAM
        elif mode == 'ru':
            gram = {v: k for k, v in self.GRAM.items()}
        else:
            raise ValueError('"mode" parameter must be "en" or "ru"')
            
        out = []
        
        for tag in tags:
            try:
                out.append(gram[tag])
            except KeyError:
                if tag not in gram.values():
                    raise ValueError(f'Unknown tag: "{tag}"')
                out.append(tag)
        else:
            return out  
    
    @staticmethod    
    def most_similar_seq(seq, seq_list, ratio=0.6):
        """Find the most similar character sequence against the list."""
        ratios = [SequenceMatcher(None, seq, el).quick_ratio() for el in seq_list]
        maxr = max(ratios)
        if maxr < ratio:
            return None
        return seq_list[ratios.index(maxr)]
            
    def convert_tag(self, tag, tags):
        is_dict = isinstance(tags, dict)
        if tag in tags:
            return tags[tag] if is_dict else tag

        if tag in self.mapping:
            return self.mapping[tag]
        
        res = self.most_similar_seq(tag, list(tags))
        if res is None:
            ans = input(f'Unknown tag "{tag}". Type in the correct value: ')
        else:
            while True:
                ans = input(f'Unknown tag "{tag}". Did you mean "{res}"? [Y/n]: ').lower()
                if ans in ('y', ''):
                    ans = res
                    break
                elif ans == 'n':
                    ans = input('Type in the correct value: ')
                    break
        
        self.mapping[tag] = ans
        return tags[ans] if is_dict else ans
        
    def convert_tags(self, annotation_data, tags):
        # print(tags.upper() + ' tag convertion has started.')
        for i in range(len(annotation_data)):
            begin, end, value = annotation_data[i]
            value = value.strip()
            if ':' in value:
                value = ','.join(self.convert_tag(tag, tags) for tag in value.split(':'))
            else:
                value = self.convert_tag(value, tags)
            annotation_data[i] = (begin, end, value)
        return annotation_data
