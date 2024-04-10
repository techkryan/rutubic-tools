from sys import argv
from pathlib import Path
from pympi.Elan import Eaf
from time import time

from setup import MyEaf, benchmark
from processing.tokenize import tokenize_tier
from processing.validate import validate
from processing.tag_converter import TagConverter


@benchmark
def main():
    path = Path(argv[1])
    src = Eaf(path)
    dest = MyEaf()

    try:
        validate(
            src.get_annotation_data_for_tier('word_morph'),
            src.get_annotation_data_for_tier('transcript_resp'),
        )
    except ValueError as e:
        print(e)
        ans = input('Would you like to proceed? [y/N]: ')
        if ans.lower() != 'y':
            return

    dest.populate_tier(MyEaf.substract_tiers(src, 'text', 'transcript_resp'), 'transcript_inter')
    dest.populate_tier(src.get_annotation_data_for_tier('transcript_resp'), 'transcript_resp')
    dest.populate_tier(src.get_annotation_data_for_tier('Discourse'), 'Discourse')
    dest.populate_tier(src.get_annotation_data_for_tier('CT'), 'CT')
    
    tc = TagConverter()
    dest.populate_tier(tc.convert_tags(src.get_annotation_data_for_tier('Theme'), tc.THEME), 'Theme')
    dest.populate_tier(tc.convert_tags(src.get_annotation_data_for_tier('Genre'), tc.GENRE), 'Genre')
    
    for ann in tokenize_tier(dest.get_annotation_data_for_tier('transcript_inter')):
        dest.populate_ref_tier(ann, 'token_inter', 'transcript_inter')
    
    for token_data, lemma_data, gramm_data in tokenize_tier(src.get_annotation_data_for_tier('word_morph'), True):
        dest.populate_ref_tier(token_data, 'token_resp', 'transcript_resp')
        dest.populate_ref_tier2(lemma_data, 'lemma', 'token_resp')
        dest.populate_ref_tier2(gramm_data, 'gramm', 'token_resp')
        
    # leaving mistake tiers as they are
    dest.add_tier('mistake_old', 'span', 'transcript_resp',)
    dest.add_tier('word_correct_old', 'SA', 'mistake_old')
    dest.populate_tier(src.get_annotation_data_for_tier('mistake'), 'mistake_old')
    dest.populate_tier(src.get_annotation_data_for_tier('word_correct'), 'word_correct_old')

    dest.clean_time_slots()
    
    filename = str(int(time())) + '_' + path.name
    dest.to_file(path.parent / filename)

if __name__ == '__main__':
    main()
