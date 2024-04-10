from pympi.Elan import Eaf


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

    def populate_ref_tier(self, annotation_data, tier, parent_tier):
        it = iter(annotation_data)
        begin, _, value = next(it)
        self.add_ref_annotation(tier, parent_tier, begin + 1, value)
        prev_id = self.last_annotation_id(tier) 

        for begin, _, value in it:
            self.add_ref_annotation(tier, parent_tier, begin + 1, value, prev_id)
            prev_id = self.last_annotation_id(tier)
    
    def populate_ref_tier2(self, annotation_data, tier, parent_tier):
        for _, _, value in annotation_data:
            self.add_ref_annotation(tier, parent_tier, value=value)

    def substract_tiers(self, id_tier1, id_tier2):
        tier1 = self.get_annotation_data_for_tier(id_tier1)
        tier2 = set([tup[:-1] for tup in self.get_annotation_data_for_tier(id_tier2)])

        annotation_data = []

        for ann in tier1:
            if ann[:-1] not in tier2:
                annotation_data.append(ann)

        return annotation_data
        
        
def benchmark(func):
    from time import process_time

    def wrapper():
        start = process_time()
        func()
        end = process_time()
        print('----- Conversion has completed in ', end - start , 'seconds! -----')
    return wrapper
