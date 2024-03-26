from sys import argv
from pathlib import Path
from itertools import islice
from pympi.Elan import Eaf
from transform.tokenize import tokenize
from transform.validate import validate


def benchmark(func):
    from time import process_time

    def wrapper():
        start = process_time()
        func()
        end = process_time()
        print('-----', end - start , 'seconds -----')
    return wrapper

class MyEaf(Eaf):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.linguistic_types = {}
        self.tiers = {}

        self.add_linguistic_type('parent_transcript')
        self.add_linguistic_type('SS', 'Symbolic_Subdivision')
        self.add_linguistic_type('SA', 'Symbolic_Association')
        self.add_linguistic_type('SA_mistakes', 'Symbolic_Association')
        self.add_linguistic_type('span', 'Included_In')
        self.add_linguistic_type('ct')
        self.add_linguistic_type('discourse')
        self.add_linguistic_type('genre')
        self.add_linguistic_type('theme')

        self.add_tier('transcript_inter', 'parent_transcript',),
        self.add_tier('token_inter', 'SS', 'transcript_inter'),
        self.add_tier('transcript_resp', 'parent_transcript'),
        self.add_tier('token_resp', 'SS', 'transcript_resp'),
        self.add_tier('lemma', 'SA', 'token_resp'),
        self.add_tier('gramm', 'SA', 'token_resp'),
        self.add_tier('mistake', 'SA_mistakes', 'token_resp'),
        self.add_tier('word_correct', 'SA', 'token_resp'),
        self.add_tier('span', 'span', 'transcript_resp'),
        self.add_tier('Discourse', 'discourse'),
        self.add_tier('CT', 'ct'),
        self.add_tier('Theme', 'theme'),
        self.add_tier('Genre', 'genre')

    def last_annotation_id(self, tier_name):
        return next(reversed(self.tiers[tier_name][1]))

    def populate_tier(self, annotation_data, tier_name):
        for begin, end, value in annotation_data:
            self.add_annotation(tier_name, begin, end, value)

    def populate_SS(self, annotation_data, tier, parent_tier, time):
        value = next(annotation_data)
        self.add_ref_annotation(tier, parent_tier, time, value)
        prev_id = self.last_annotation_id(tier) 

        for value in annotation_data:
            self.add_ref_annotation(tier, parent_tier, time, value, prev_id)
            prev_id = self.last_annotation_id(tier)
    
    # def populate_SA(self, annotation_data, tier, parent_tier):
    #     for begin, end, value in annotation_data:
    #         print(begin, end, value)
    #         time = int(begin + ((end - begin)/2))
    #         self.add_ref_annotation(tier, parent_tier, time, value)

    def populate_morph(self, annotation_data, time):
        word, lemma, gramm = next(annotation_data)
        self.add_ref_annotation('token_resp', 'transcript_resp', time, word)
        self.add_ref_annotation('lemma', 'token_resp', value=lemma)
        self.add_ref_annotation('gramm', 'token_resp', value=gramm)
        prev_id = self.last_annotation_id('token_resp') 

        for word, lemma, gramm in annotation_data:
            self.add_ref_annotation('token_resp', 'transcript_resp', time, word, prev_id)
            self.add_ref_annotation('lemma', 'token_resp', value=lemma)
            self.add_ref_annotation('gramm', 'token_resp', value=gramm)
            prev_id = self.last_annotation_id('token_resp')

    def substract_tiers(self, id_tier1, id_tier2):
        tier1 = self.get_annotation_data_for_tier(id_tier1)
        tier2 = set([tup[:-1] for tup in self.get_annotation_data_for_tier(id_tier2)])

        annotation_data = []

        for ann in tier1:
            if ann[:-1] not in tier2:
                annotation_data.append(ann)

        return annotation_data

@benchmark
def main():
    p = Path(argv[1])
    src = Eaf(p)
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
    dest.populate_tier(src.get_annotation_data_for_tier('Theme'), 'Theme')
    dest.populate_tier(src.get_annotation_data_for_tier('Genre'), 'Genre')

    for ann in dest.get_annotation_data_for_tier('transcript_inter'):
        dest.populate_SS(tokenize(ann), 'token_inter', 'transcript_inter', ann[0] + 1)
    for i, ann in enumerate(src.get_annotation_data_for_tier('word_morph')):
        try:
            dest.populate_morph(tokenize(ann, True), ann[0] + 1)
        except KeyError as e:
            print(f'Annotation {i+1}', ann, e)
    # leaving mistake tiers as they are
    dest.add_tier('mistake_old', 'span', 'transcript_resp',)
    dest.add_tier('word_correct_old', 'SA', 'mistake_old')
    dest.populate_tier(src.get_annotation_data_for_tier('mistake'), 'mistake_old')
    dest.populate_tier(src.get_annotation_data_for_tier('word_correct'), 'word_correct_old')

    dest.clean_time_slots()
    dest.to_file(p.parent / (p.stem + '_TEST.eaf'))

if __name__ == '__main__':
    main()