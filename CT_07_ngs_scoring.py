# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
NGS Evidence scoring based on concept(s) presence in an Article Title, or Conclusion/Discussion section, or MeSH terms
Takes parent-child hierarchy into account
Uses Entry Terms (UMLS Atoms) for title/MeSH/Conclusion section presence
"""

import pickle
import json
import csv
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

csv.field_size_limit(58000000)

NGS_SCORE_TITLE = 1
NGS_SCORE_TITLE_RELATED = 0.5
NGS_SCORE_MESH = 0.5
NGS_SCORE_MESH_RELATED = 0.25
NGS_SCORE_CONCLUSION = 0.1
NGS_SCORE_CONCLUSION_RELATED = 0.1



dictionaryDir = '/tools/metathesaurus_files/2025AB_data/'


def load_whitelist():
    # TODO : add whitelist cats through an excel spreadsheet
    # wb = load_workbook(filename = '../dicts/scoring/scoring.xlsx')
    # sheet_ranges = wb['<categories_whitelisted>']
    #
    # start_row = 6
    # end_row = 304
    #
    # for row in range(start_row, end_row):
    #
    #     main_group = sheet_ranges['D'+str(row)].value

    whitelist_cats = ['PHEN|Phenomena|T034|Laboratory or Test Result', 'PHEN|Phenomena|T038|Biologic Function',
                      'PHEN|Phenomena|T067|Phenomenon or Process',
                      'PHEN|Phenomena|T068|Human-caused Phenomenon or Process',
                      'PHEN|Phenomena|T069|Environmental Effect of Humans',
                      'PHEN|Phenomena|T070|Natural Phenomenon or Process',
                      'PHYS|Physiology|T032|Organism Attribute', 'PHYS|Physiology|T039|Physiologic Function',
                      'PHYS|Physiology|T040|Organism Function', 'PHYS|Physiology|T041|Mental Process',
                      'PHYS|Physiology|T042|Organ or Tissue Function', 'PHYS|Physiology|T043|Cell Function',
                      'PHYS|Physiology|T044|Molecular Function', 'PHYS|Physiology|T045|Genetic Function',
                      'PHYS|Physiology|T201|Clinical Attribute', 'PROC|Procedures|T058|Health Care Activity',
                      'PROC|Procedures|T059|Laboratory Procedure', 'PROC|Procedures|T060|Diagnostic Procedure',
                      'PROC|Procedures|T061|Therapeutic or Preventive Procedure',
                      'PROC|Procedures|T062|Research Activity',
                      'PROC|Procedures|T063|Molecular Biology Research Technique',
                      'PROC|Procedures|T065|Educational Activity',
                      'OBJC|Objects|T167|Substance', 'OBJC|Objects|T168|Food', 'LIVB|Living Beings|T194|Archaeon',
                      'LIVB|Living Beings|T204|Eukaryote', 'LIVB|Living Beings|T097|Professional or Occupational Group',
                      'LIVB|Living Beings|T098|Population Group', 'LIVB|Living Beings|T099|Family Group',
                      'LIVB|Living Beings|T100|Age Group', 'LIVB|Living Beings|T001|Organism',
                      'LIVB|Living Beings|T002|Plant',
                      'LIVB|Living Beings|T004|Fungus', 'LIVB|Living Beings|T005|Virus',
                      'LIVB|Living Beings|T007|Bacterium',
                      'LIVB|Living Beings|T008|Animal', 'LIVB|Living Beings|T010|Vertebrate',
                      'LIVB|Living Beings|T011|Amphibian',
                      'LIVB|Living Beings|T012|Bird', 'LIVB|Living Beings|T013|Fish', 'LIVB|Living Beings|T014|Reptile',
                      'LIVB|Living Beings|T015|Mammal', 'LIVB|Living Beings|T016|Human',
                      'DEVI|Devices|T074|Medical Device',
                      'DEVI|Devices|T075|Research Device', 'DEVI|Devices|T203|Drug Delivery Device',
                      'DISO|Disorders|T019|Congenital Abnormality', 'DISO|Disorders|T020|Acquired Abnormality',
                      'DISO|Disorders|T033|Finding', 'DISO|Disorders|T037|Injury or Poisoning',
                      'DISO|Disorders|T046|Pathologic Function', 'DISO|Disorders|T047|Disease or Syndrome',
                      'DISO|Disorders|T048|Mental or Behavioral Dysfunction',
                      'DISO|Disorders|T049|Cell or Molecular Dysfunction',
                      'DISO|Disorders|T050|Experimental Model of Disease', 'DISO|Disorders|T184|Sign or Symptom',
                      'DISO|Disorders|T190|Anatomical Abnormality', 'DISO|Disorders|T191|Neoplastic Process',
                      'GENE|Genes & Molecular Sequences|T028|Gene or Genome',
                      'GENE|Genes & Molecular Sequences|T085|Molecular Sequence',
                      'GENE|Genes & Molecular Sequences|T086|Nucleotide Sequence',
                      'GENE|Genes & Molecular Sequences|T087|Amino Acid Sequence',
                      'CONC|Concepts & Ideas|T081|Quantitative Concept', 'ANAT|Anatomy|T017|Anatomical Structure',
                      'ANAT|Anatomy|T018|Embryonic Structure', 'ANAT|Anatomy|T021|Fully Formed Anatomical Structure',
                      'ANAT|Anatomy|T022|Body System', 'ANAT|Anatomy|T023|Body Part, Organ, or Organ Component',
                      'ANAT|Anatomy|T024|Tissue', 'ANAT|Anatomy|T025|Cell', 'ANAT|Anatomy|T026|Cell Component',
                      'ANAT|Anatomy|T029|Body Location or Region', 'ANAT|Anatomy|T030|Body Space or Junction',
                      'ANAT|Anatomy|T031|Body Substance', 'CHEM|Chemicals & Drugs|T103|Chemical',
                      'CHEM|Chemicals & Drugs|T104|Chemical Viewed Structurally',
                      'CHEM|Chemicals & Drugs|T109|Organic Chemical',
                      'CHEM|Chemicals & Drugs|T114|Nucleic Acid, Nucleoside, or Nucleotide',
                      'CHEM|Chemicals & Drugs|T116|Amino Acid, Peptide, or Protein',
                      'CHEM|Chemicals & Drugs|T120|Chemical Viewed Functionally',
                      'CHEM|Chemicals & Drugs|T121|Pharmacologic Substance',
                      'CHEM|Chemicals & Drugs|T122|Biomedical or Dental Material',
                      'CHEM|Chemicals & Drugs|T123|Biologically Active Substance',
                      'CHEM|Chemicals & Drugs|T125|Hormone',
                      'CHEM|Chemicals & Drugs|T127|Vitamin', 'CHEM|Chemicals & Drugs|T129|Immunologic Factor',
                      'CHEM|Chemicals & Drugs|T130|Indicator, Reagent, or Diagnostic Aid',
                      'CHEM|Chemicals & Drugs|T131|Hazardous or Poisonous Substance',
                      'CHEM|Chemicals & Drugs|T192|Receptor', 'CHEM|Chemicals & Drugs|T195|Antibiotic',
                      'CHEM|Chemicals & Drugs|T196|Element, Ion, or Isotope',
                      'CHEM|Chemicals & Drugs|T197|Inorganic Chemical',
                      'CHEM|Chemicals & Drugs|T200|Clinical Drug',
                      'ACTI|Activities & Behaviors|T055|Individual Behavior',
                      'ACTI|Activities & Behaviors|T056|Daily or Recreational Activity']

    return whitelist_cats


def resolve_concept_data(target_cui, atoms, parents, children):
    '''
    Resolve all data related to a target (cause/effect) concept

    @param target_cui: cause/effect concept passed to the function
    @param entry_terms: Atom names for a given concept from UMLS
    @param parents:
    @param children:
    @return: input_parents, input_children, input_atoms, input_parchd_atoms
    '''

    input_parents = []
    input_children = []
    input_atoms = []
    input_parchd_atoms = []

    if target_cui in parents:
        input_parents = parents[target_cui]
    if target_cui in children:
        input_children = children[target_cui]

    if target_cui in atoms:
        input_atoms = atoms[target_cui]

    for item in input_parents:
        if item in atoms:
            for atom in atoms[item]:
                input_parchd_atoms.append(atom)

    for item in input_children:
        if item in atoms:
            for atom in atoms[item]:
                input_parchd_atoms.append(atom)

    input_atoms = list(set(input_atoms))
    input_parchd_atoms = list(set(input_parchd_atoms))

    return input_parents, input_children, input_atoms, input_parchd_atoms


def evidence_from_title_case_tagging(article_title_tag, atoms, concept_cui, concept_cat_code, is_relatedatoms):
    tagged = 0
    pre_article_title_tag = article_title_tag
    debug = 0

    for item in atoms:
        query = item
        query_lower = item.lower()
        if query in article_title_tag or query_lower in article_title_tag.lower():
            article_title_tag = title_tagging(article_title_tag, concept_cui, concept_cat_code, query, is_relatedatoms)
            if pre_article_title_tag.lower() != article_title_tag.lower():
                tagged = 1
                break

    return article_title_tag, tagged


def title_tagging(title_tag, concept_cui, concept_cat_code, query, related_atoms):
    # Set up opening and closing tags, take concept data from argument list
    title_tag_open = '<concept cui=' + concept_cui.capitalize() + ' cat=' + concept_cat_code
    title_tag_close = '</concept>'

    if related_atoms == 1:
        title_tag_open = title_tag_open + ' pc=1>'
    else:
        title_tag_open = title_tag_open + ' pc=0>'

    query_lower = query.lower()

    # These are to avoid nested tags - a tag cannot be within another pair of tags
    existing_tag_open = 0
    existing_tag_close = 0
    existing_tag_open = title_tag.find('<concept>')
    existing_tag_close = title_tag.find('</concept>')

    # If query found and legit location - tag it
    # if query in title_tag or query_lower in title_tag.lower():
    query_loc = title_tag.find(query)
    if not (query_loc > existing_tag_open and query_loc < existing_tag_close):
        if query in title_tag:
            replacement = title_tag_open + query + title_tag_close
        elif query_lower.capitalize() in title_tag:
            replacement = title_tag_open + query_lower.capitalize() + title_tag_close
        elif query_lower in title_tag:
            replacement = title_tag_open + query_lower + title_tag_close
        elif query_lower in title_tag.lower():
            replacement = title_tag_open + query_lower + title_tag_close
        # title_tag = re.sub(r"\b%s\b"%query, replacement, title_tag)
        try:
            title_tag_temp = re.sub(r"\b%s\b" % query, replacement, title_tag, flags=re.IGNORECASE)
            if '</concept></' in title_tag_temp or '</concept>=T' in title_tag_temp:
                pass
            else:
                title_tag = title_tag_temp
        except Exception, e:
            print (str(e))
            print (title_tag)
            print ("Query", query)
            print ("REPLACEMENT: ", replacement)
            print ('Replacing directly...')
            title_tag = title_tag.replace(query, replacement)
            print title_tag

    # elif query_lower in title_tag.lower():
    #     query_loc = title_tag.find(query_lower)
    #     if not (query_loc > existing_tag_open and query_loc < existing_tag_close):
    #         replacement = title_tag_open + query_lower + title_tag_close
    #         # title_tag = re.sub(r"\b%s\b" % query_lower, replacement, title_tag.lower())
    #         try:
    #             title_tag = re.sub(r"\b%s\b" % query_lower, replacement, title_tag.lower())
    #         except Exception, e:
    #             print (str(e))
    #             print (title_tag.lower())
    #             print ("Query", query_lower)
    #             print ("REPLACEMENT: ", replacement)
    #             print ('Replacing directly...')
    #             title_tag = title_tag.lower().replace(query_lower, replacement)
    #             print title_tag
    #
    #         title_tag = title_tag.capitalize()

    return title_tag


def score_title_match(article_title, main_atoms, related_atoms, cause_effect_side, ngs_relevance_score,
                      title_match_flag, cui_to_cat, concept_cui, cat_whitelist, concept_categories):
    type = ''
    score = 0
    matched_flag = 0

    concept_cat_code = cui_to_cat[concept_cui][0].split('|')[2]

    for item in main_atoms:
        query = item
        query_lower = item.lower()

        if query in article_title or query_lower in article_title.lower():

            # article_title = title_tagging(article_title, concept_cui, concept_cat_code, query, 0)
            article_title, tagged = evidence_from_title_case_tagging(article_title_tag, main_atoms, concept_cui,
                                                                     concept_cat_code, 0)
            if tagged == 1:
                type = 'TITLE:' + cause_effect_side + ':' + str(NGS_SCORE_TITLE)
                score = NGS_SCORE_TITLE
                break

    if score == 0 and type == '':

        for item in related_atoms:
            query = item
            query_lower = item.lower()

            if query in article_title or query_lower in article_title.lower():
                type = 'TITLE-PARCHD:' + cause_effect_side + ':' + str(NGS_SCORE_TITLE_RELATED)
                score = NGS_SCORE_TITLE_RELATED

                # article_title = title_tagging(article_title, concept_cui, concept_cat_code, query, 1)
                article_title, tagged = evidence_from_title_case_tagging(article_title_tag, related_atoms, concept_cui,
                                                                         concept_cat_code, 1)
                break

    if not any([cat for cat in concept_categories if cat in cat_whitelist]):
        score = 0
        title_match_flag.append('TITLE-NONWHITELIST:' + cause_effect_side)

    if score != 0 and type != '':
        title_match_flag.append(type)
        ngs_relevance_score += score
        matched_flag = 1

    return ngs_relevance_score, title_match_flag, matched_flag, article_title


def score_mesh_match(article_mesh, main_atoms, related_atoms, cause_effect_side, ngs_relevance_score, mesh_match_flag):
    type = ''
    score = 0

    article_mesh = article_mesh.split('|')

    for item in article_mesh:
        query = item
        query_lower = item.lower()

        if query in main_atoms or query_lower in '|'.join(main_atoms).lower():
            type = 'MESH:' + cause_effect_side + ':' + str(NGS_SCORE_MESH)
            score = NGS_SCORE_MESH
            break

    if score == 0 and type == '':
        for item in article_mesh:
            query = item
            query_lower = item.lower()

            if query in related_atoms or query_lower in '|'.join(related_atoms).lower():
                type = 'MESH-PARCHD:' + cause_effect_side + ':' + str(NGS_SCORE_MESH_RELATED)
                score = NGS_SCORE_MESH_RELATED
                break

    if score != 0 and type != '':
        mesh_match_flag.append(type)
        ngs_relevance_score += score

    return ngs_relevance_score, mesh_match_flag


def score_conclusion_match(article_conclusion, main_atoms, related_atoms, cause_effect_side, ngs_relevance_score,
                           conclusion_match_flag):
    type = ''
    score = 0

    for item in main_atoms:
        query = item
        query_low = item.lower()

        if query in article_conclusion or query_low in article_conclusion.lower():
            type = 'CONCLUSION:' + cause_effect_side + ':' + str(NGS_SCORE_CONCLUSION)
            score = NGS_SCORE_CONCLUSION
            break

    if score != 0 and type != '':
        conclusion_match_flag.append(type)
        ngs_relevance_score += score

    return ngs_relevance_score, conclusion_match_flag


print ('Loading UMLS dictionaries...')
# Entry Terms (Atoms) dictionary - CUI -> [Atom1, Atom2...]
with open(dictionaryDir + '2025AB_atoms.pkl2', 'rb') as handle:
    mrconso_concepts = pickle.load(handle)

# Concept Preferred Name dictionary - CUI -> Preferred term
#with open(dictionaryDir + 'concepts_preferred_v5_2019AB.pickle', 'rb') as handle:
#    concepts_preferred = pickle.load(handle)

# PARENTS dictionary from UMLS MRREL.RRF
with open(dictionaryDir + '2025AB_parents.pkl2', 'rb') as handle:
    parents = pickle.load(handle)

# CHILDREN dictionary from UMLS MRREL.RRF
with open(dictionaryDir + '2025AB_children.pkl2', 'rb') as handle:
    children = pickle.load(handle)

with open(dictionaryDir + '2025AB_cui_to_cat.pkl2', 'rb') as handle:
    cui_to_cat = pickle.load(handle)

# Strip the Vocab data from Parents and Children hierarchies at the beginning
print (parents['C2239176'])  # Test output
print (children['C2239176'])  # Test output

for item in parents:
    members = parents[item]
    new_members = []
    for element in members:
        new_members.append(element.split('%')[0])
    new_members = list(set(new_members))
    parents[item] = new_members

for item in children:
    members = children[item]
    new_members = []
    for element in members:
        new_members.append(element.split('%')[0])
    new_members = list(set(new_members))
    children[item] = new_members

print (parents['C2239176'])
print (children['C2239176'])

print ('All dictionaries loaded.')

# INPUT FILE - the preloading csvs
#input_filename = '/home/a_saudabayev/ct_20200810/toload_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv'
input_filename = sys.argv[1]

# OUTPUT FILE - later should be ready for ES/NEO4j loading
# writer_0 = csv.writer(
#     open('/home/a_saudabayev/ct_20200810/ngs_scored_toload_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv', 'w'),
#     delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

writer_0 = csv.writer(open(sys.argv[2], 'w'),delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

# If a direct uuid to score needed, the below writer_source_score needs to be uncommented throughout the script
# writer_source_score = csv.writer(
#     open('/home/a_saudabayev/parse_gen_3/20200218/ngs_scored/source_uuid_to_ngs_toload_dedup_20200306_01_clinicaltrialsgov_xmlstage_condition_intervention.csv', 'w'),
#         delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
# writer_source_score_header = ['article_uuid', 'source_uuid', 'final_ngs_score']
# writer_source_score.writerow(writer_source_score_header)

# Initialize required csv column indices below
article_title_ind = 0
article_uuid_ind = 0
article_mesh_terms_ind = 0
article_pub_date_ind = 0
cause_concept_cui_ind = 0
effect_concept_cui_ind = 0
connective_type_ind = 0
cause_cat_ind = 0
effect_cat_ind = 0
article_section_ind = 0
cause_concept_ind = 0
effect_concept_ind = 0
source_hashcode_ind = 0

print ('Start input file processing')
with open(input_filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            row.append('ngs_score')
            # row.append('title_match')                 # Debug column, delete later
            # row.append('mesh_match')                  # Debug column, delete later
            # row.append('conclusion_match')            # Debug column, delete later
            row.append('article_title_evidence_tag')
            # row.append('cooccur_flag')                # Debug column, delete later
            # row.append('is_article_title')            # Debug column, delete later
            # row.append('date_multiplier')             # Debug column, delete later
            row.append('final_ngs_score')
            writer_0.writerow(row)

            # get column indices from the input csv
            article_title_ind = row.index('article_title')
            article_uuid_ind = row.index('article_uuid')
            article_mesh_terms_ind = row.index('article_mesh_terms')
            article_pub_date_ind = row.index('pub_date')
            cause_concept_cui_ind = row.index('cause_concept_cui')
            effect_concept_cui_ind = row.index('effect_concept_cui')
            connective_type_ind = row.index('connective_type')
            cause_cat_ind = row.index('cause_category')
            effect_cat_ind = row.index('effect_category')
            article_section_ind = row.index('article_section_bucket')

            cause_concept_ind = row.index('cause_concept')
            effect_concept_ind = row.index('effect_concept')

            source_hashcode_ind = row.index('source_hashcode')
            continue

        ngs_relevance_score = 0  # total evidence relevance score
        title_match_flag = []  # title match debug flag
        mesh_match_flag = []  # mesh match debug flag
        conclusion_match_flag = '0'  # conclusion match debug flag
        cause_title_flag = 0  # flag to point out if cause concept was found in the title
        effect_title_flag = 0  # flag to point out if effect concept was found in the title
        cooccure_flag = 'none'
        isarticle_title = '0'

        '''
            1. Gather Concept-related data
        '''
        # cause side resolution
        cause_concept_cui = row[cause_concept_cui_ind]
        cause_category = row[cause_cat_ind].split('%')
        cause_parents, cause_children, cause_atoms, cause_parchd_atoms = resolve_concept_data(cause_concept_cui,
                                                                                              mrconso_concepts, parents,
                                                                                              children)
        # effect side resolution
        effect_concept_cui = row[effect_concept_cui_ind]
        effect_category = row[effect_cat_ind].split('%')
        effect_parents, effect_children, effect_atoms, effect_parchd_atoms = resolve_concept_data(effect_concept_cui,
                                                                                                  mrconso_concepts,
                                                                                                  parents,
                                                                                                  children)

        '''
            2. Gather article/evidence-related data
        '''
        # gather article metadata
        article_title = row[article_title_ind]
        article_title_tag = article_title
        article_mesh = row[article_mesh_terms_ind]
        article_uuid = row[article_uuid_ind]
        article_pub_date = row[article_pub_date_ind]
        source_hashcode = row[source_hashcode_ind]

        connective_type = row[connective_type_ind]
        article_section = row[article_section_ind]
        categories_whitelist = load_whitelist()

        if cause_concept_cui == '0' or effect_concept_cui == '0':
            row.append('0')
            # row.append('0')
            # row.append('0')
            # row.append('0')
            row.append(row[article_title_ind])  # If no tags - original article title is passed
            # row.append('0')
            # row.append('0')
            # row.append('0')
            row.append('0')
            writer_0.writerow(row)

            # writer_source_score_row = [article_uuid, source_hashcode, 0]
            # writer_source_score.writerow(writer_source_score_row)
            continue

        if cause_concept_cui not in cui_to_cat:
            print ('Need input: ', cause_concept_cui)
            user_cat = input("Cat: ")
            user_cat = str(user_cat)

            cui_to_cat[cause_concept_cui] = [user_cat]

        if effect_concept_cui not in cui_to_cat:
            print ('Need input: ', effect_concept_cui)
            user_cat = input("Cat: ")
            user_cat = str(user_cat)

            cui_to_cat[effect_concept_cui] = [user_cat]

        '''
            2.1 Check if the article is COOCCUR
            EARLY EXIT POSSIBLE
            variables: ngs_relevance_score, COOCCUR match flag
        '''
        if connective_type == 'COOCCUR':

            if any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]) \
                    and any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score = 1
                cooccure_flag = 'cooccur=1'

            elif any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]) \
                    or any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score = 1
                cooccure_flag = 'cooccur=0.5'

            else:
                ngs_relevance_score = 0
                cooccure_flag = 'cooccur=0'


        elif article_section == 'Article Title':
            '''
                2.2 If evidence from the Article Title = score 2.5
                EARLY EXIT POSSIBLE
                variables: ngs_relevance_score, is_article_title
            '''
            if any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]) \
                    and any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score = 2.5
                isarticle_title = '2.5'

                # Tag CAUSE CUI by first trying primary, and later parent-child concepts
                concept_cat_code = cui_to_cat[cause_concept_cui][0].split('|')[2]
                article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, cause_atoms,
                                                                             cause_concept_cui, concept_cat_code, 0)
                if tagged == 0:
                    article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, cause_parchd_atoms,
                                                                                 cause_concept_cui, concept_cat_code, 1)

                # Tag EFFECT CUI by first trying primary, and later parent-child concepts
                concept_cat_code = cui_to_cat[effect_concept_cui][0].split('|')[2]
                article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, effect_atoms,
                                                                             effect_concept_cui, concept_cat_code, 0)
                if tagged == 0:
                    article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, effect_parchd_atoms,
                                                                                 effect_concept_cui, concept_cat_code,
                                                                                 1)


            elif any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]) \
                    or any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score = 1.25
                isarticle_title = '1.25'

                if any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]):
                    # Tag CAUSE CUI by first trying primary, and later parent-child concepts
                    concept_cat_code = cui_to_cat[cause_concept_cui][0].split('|')[2]
                    article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, cause_atoms,
                                                                                 cause_concept_cui, concept_cat_code, 0)
                    if tagged == 0:
                        article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag,
                                                                                     cause_parchd_atoms,
                                                                                     cause_concept_cui,
                                                                                     concept_cat_code, 1)

                else:

                    # Tag EFFECT CUI by first trying primary, and later parent-child concepts
                    concept_cat_code = cui_to_cat[effect_concept_cui][0].split('|')[2]
                    article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag, effect_atoms,
                                                                                 effect_concept_cui, concept_cat_code,
                                                                                 0)
                    if tagged == 0:
                        article_title_tag, tagged = evidence_from_title_case_tagging(article_title_tag,
                                                                                     effect_parchd_atoms,
                                                                                     effect_concept_cui,
                                                                                     concept_cat_code, 1)

            else:
                ngs_relevance_score = 0
                isarticle_title = '0'

        else:

            '''
                3. Match on Article Titles
                variables: ngs_relevance_score, title_match_flag
            '''
            old_article_tag = article_title_tag

            if any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]):
                ngs_relevance_score, title_match_flag, cause_title_flag, article_title_tag = \
                    score_title_match(article_title_tag, cause_atoms, cause_parchd_atoms, 'cause', ngs_relevance_score,
                                      title_match_flag, cui_to_cat, cause_concept_cui, categories_whitelist,
                                      cause_category)

            if any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score, title_match_flag, effect_title_flag, article_title_tag = \
                    score_title_match(article_title_tag, effect_atoms, effect_parchd_atoms, 'effect',
                                      ngs_relevance_score,
                                      title_match_flag, cui_to_cat, effect_concept_cui, categories_whitelist,
                                      effect_category)

            # if cause_title_flag == 1 and effect_title_flag == 1:
            #     print cause_title_flag, effect_title_flag
            #     print 'Start'
            #     print old_article_tag
            #     print '---------'
            #     print cause_atoms
            #     print cause_parchd_atoms
            #     print '---------'
            #     print effect_atoms
            #     print effect_parchd_atoms
            #     print '---------'
            #     print 'End'
            #     print article_title_tag
            #     raw_input('wait')
            '''
                4. Match on Article MeSH (if title concept did not match)
                variables: ngs_relevance_score, mesh_match_flag

                Runs only if categories are whitelisted and concepts were not found in the title
            '''
            if cause_title_flag == 0 and any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]):
                ngs_relevance_score, mesh_match_flag = \
                    score_mesh_match(article_mesh, cause_atoms, cause_parchd_atoms, 'cause', ngs_relevance_score,
                                     mesh_match_flag)

            if effect_title_flag == 0 and any([e_cat for e_cat in effect_category if e_cat in categories_whitelist]):
                ngs_relevance_score, mesh_match_flag = \
                    score_mesh_match(article_mesh, effect_atoms, effect_parchd_atoms, 'effect', ngs_relevance_score,
                                     mesh_match_flag)

            '''
                5. Match on Article Conclusion Section
                variables: ngs_relevance_score, conclusion_match_flag
            '''
            if (any([c_cat for c_cat in cause_category if c_cat in categories_whitelist]) \
                or any([e_cat for e_cat in effect_category if e_cat in categories_whitelist])) \
                    and (article_section == 'Results/Findings' or article_section == 'Conclusion/Discussion'):
                ngs_relevance_score += 0.1
                conclusion_match_flag = '1'

        final_score_multiplier = 0

        ## Check pub date is in correct format of YYYYMMDD
        ## If date is - (dash) seperated then remove dashes.
        if "-" in article_pub_date:
            article_pub_date = article_pub_date.replace("-", "")
            row[article_pub_date_ind] = article_pub_date
            print 'Date change: ' + article_uuid + ' = ' + article_pub_date

        if int(article_pub_date) <= 20090101:
            final_score_multiplier = 0
        else:
            final_score_multiplier = round(float(int(article_pub_date) - 20090901) / (20300101 - 20090101), 4) * 0.8

        if final_score_multiplier < 0:
            final_score_multiplier = 0
        final_score = ngs_relevance_score * (1 + final_score_multiplier)

        title_match_flag = '|'.join(title_match_flag)
        mesh_match_flag = '|'.join(mesh_match_flag)
        conclusion_match_flag = '|'.join(conclusion_match_flag)

        row.append(ngs_relevance_score)
        # row.append(title_match_flag)
        # row.append(mesh_match_flag)
        # row.append(conclusion_match_flag)
        row.append(article_title_tag)
        # row.append(cooccure_flag)
        # row.append(isarticle_title)
        # row.append(final_score_multiplier)
        row.append(final_score)

        writer_0.writerow(row)

        # writer_source_score_row = [article_uuid, source_hashcode, final_score]
        # writer_source_score.writerow(writer_source_score_row)

print ('Done')
