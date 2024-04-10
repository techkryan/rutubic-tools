import re
import sys
from difflib import ndiff

def validate(annotation_data1, annotation_data2):    
    mismatches = 0
    for i, ann1, ann2 in zip(
            range(1, len(annotation_data1) + 1),
            annotation_data1,
            annotation_data2):
        
        toprint = [f'Annotation {i}:']
        tagged = re.findall(r'([-А-яЁё]+){(.*?)}', ann1[2])
        wf1 = [tag[0] for tag in tagged]
        wf2 = re.findall(r'[-А-яЁё]+', ann2[2])

        if wf1 != wf2:
            mismatches += 1

            diff = ndiff([' '.join(wf2)], [' '.join(wf1)])
            toprint.append('\n'.join(list(diff)))
        
        for wf, tag in tagged:
            match = re.fullmatch(r'([-а-я]+)=([A-Z]+[-,0-9а-я]*=[-,0-9а-я]*)', tag)
            if not match:
                mismatches += 1
                toprint.append(f'{wf} -> {{{tag}}}')

        if len(toprint) > 1:
            for li in toprint:
                print(li)
            print()

    if mismatches:
        raise ValueError(
            f'{mismatches} issues found in total. (See above)')