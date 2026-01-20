import os
import re
import sys
import csv
from lxml import etree

# OUT_DIR = '/home/jee/Projects/causaly_statex/ClinicalTrials_pipeline/files20210301'
OUT_DIR = '/home/jee/Projects/causaly_statex/ClinicalTrials_pipeline/files20210208'
# CT_DIR = '/home/jee/Corpora/CT20210301'
CT_DIR = '/home/jee/Corpora/CT20210208'

filename = sys.argv[1]

seen = {}


def parse_article_uuid(uuid):
    cols = uuid.split('_')
    nct_id = cols[0]
    prefix = cols[0][:7]

    return nct_id, prefix


def make_ct_file(nct_id, prefix):
    filename = f'{CT_DIR}/{prefix}xxxx/{nct_id}.xml'

    return filename


def filepath(path, setId, suffix):
    return os.path.abspath(os.path.join(path, "{}.{}".format(setId, suffix)))

def sanitise(input_str):
    # input_str = input_str.replace('?.','?')
    input_str = input_str.replace('\r','')
    input_str = input_str.replace('\n', ' ').replace('\t', ' ')
    # input_str = re.sub(r'\?\.)+', '?', input_str)
    input_str = re.sub(r'( \.)+', '', input_str)
    input_str = re.sub(' +', ' ', input_str).strip()

    return input_str

def add_dot(s):
    if s.endswith('?'):
        return s
    elif s.endswith('!'):
        return s
    elif not s.endswith('.'):
        return f'{s}.'
    return s

def add_dots(l):
    l = [add_dot(e) for e in l]
    # l = [add_dot(e2.strip()) for e in l for e2 in e.split('\r\n')]
    # l = [e for e in l if e != '.']
    return l

def add_dots2(l):
    # l = [add_dot(e) for e in l]
    l = [add_dot(e2.strip()) for e in l for e2 in e.split('    -  ')]
    l = [e for e in l if e != '.']
    return l
    # l = [add_dot(e2.strip()) for e in l for e2 in e.split('\r\n')]

def readCTFile(filename):
    print(f'reading {filename}')
    infile = open(filename).read()
    doc_tree = etree.fromstring(infile)
    brief_title = '0'
    official_title = '0'
    interventions = []
    # intervention = '0'
    brief_summary = '0'
    detailed_description = '0'
    arm_groups = []
    keywords = []
    eligibility = '0'

    for main_tag in doc_tree.getchildren():
        if main_tag.tag == 'brief_title' and main_tag.text != None:
            brief_title = '<ABSTRACT BRIEF TITLE>+++' + add_dot(main_tag.text)
        if main_tag.tag == 'official_title' and main_tag.text != None:
            official_title = '<ABSTRACT OFFICIAL TITLE>+++' + add_dot(main_tag.text)
        if main_tag.tag == 'intervention' and main_tag.text != None:
            intervention = sanitise(' '.join(add_dots(main_tag.itertext())))
            interventions.append(intervention)
            # intervention = '<ABSTRACT INTERVENTION>+++' + sanitise(' '.join(add_dots(main_tag.itertext())))
        if main_tag.tag == 'brief_summary' and main_tag.text != None:
            brief_summary = '<ABSTRACT BRIEF SUMMARY>+++' + sanitise(' '.join(add_dots(main_tag.itertext())))
        if main_tag.tag == 'detailed_description' and main_tag.text != None:
            detailed_description = '<ABSTRACT DETAILED DESCRIPTION>+++' + sanitise(' '.join(add_dots(main_tag.itertext())))
        if main_tag.tag == 'arm_group' and main_tag.text != None:
            arm_group = sanitise(' '.join(add_dots(main_tag.itertext())))
            arm_groups.append(arm_group)
        if main_tag.tag == 'keyword' and main_tag.text != None:
            keyword = sanitise(' '.join(add_dots(main_tag.itertext())))
            keywords.append(keyword)
        if main_tag.tag == 'eligibility' and main_tag.text != None:
            for tag in main_tag.getchildren():
                if tag.tag == 'criteria' and tag.text != None:
                    eligibility = sanitise(' '.join(add_dots2(main_tag.itertext())))
                    eligibility = re.split('(Key )?Exclusion Criteria:?', eligibility, flags=re.IGNORECASE)[0]
                    eligibility = '<ABSTRACT ELIGIBILITY>+++' + add_dot(eligibility.strip())

    intervention = '<ABSTRACT INTERVENTION>+++' + ' '.join(interventions)
    arm_group = '<ABSTRACT ARM GROUP>+++' + ' '.join(arm_groups)
    keyword = '<ABSTRACT KEYWORD>+++' + ' '.join(keywords)

    if intervention == '<ABSTRACT INTERVENTION>+++':
        intervention = '0'
    if arm_group == '<ABSTRACT ARM GROUP>+++':
        arm_group = '0'
    if keyword == '<ABSTRACT KEYWORD>+++':
        keyword = '0'

    out_list = [
        brief_title,
        official_title,
        intervention,
        brief_summary,
        detailed_description,
        arm_group,
        keyword,
        eligibility
    ]

    out_list = [e for e in out_list if e != '0']
    return '\n'.join(out_list)


def writeTxtFile(article_uuid,
                 issn, journal_title, publisher, pmid, pmc, pii, publisher_id, doi, pub_date, article_title, article_authors,
                 article_keywords, data_source,
                 article_type_tag, article_category, article_pubtype_id,
                 meshes,
                 texts):

    outfile = open(filepath(OUT_DIR, article_uuid, 'txt'), 'w', encoding='utf-8')

    outfile.write('ISSN ' + issn + '\n')
    outfile.write('JOURNAL_TITLE ' + journal_title + '\n')
    outfile.write('PUBLISHER ' + publisher + '\n')
    outfile.write('PMID ' + pmid + '\n')
    outfile.write('PMC ' + pmc + '\n')
    outfile.write('PII ' + pii + '\n')
    outfile.write('PUBLISHER_ID ' + publisher_id + '\n')
    outfile.write('DOI ' + doi + '\n')
    outfile.write('PUBLICATON_DATE ' + pub_date + '\n')
    outfile.write('TITLE ' + article_title + '\n')
    outfile.write('AUTHORS : ' + article_authors + '\n')
    outfile.write('KEYWORDS ' + article_keywords + '\n')
    outfile.write('DATA_SOURCE : ' + data_source + '\n')
    outfile.write('ARTICLE_PUBTYPE_TAG : ' + article_type_tag + '\n')
    outfile.write('ARTICLE_CATEGORIES_HEADLINE : ' + article_category + '\n')
    outfile.write('ARTICLE_PUBTYPE_ID : ' + article_pubtype_id + '\n')
    outfile.write(meshes + '\n')
    #outfile.write(mesh_headings + '\n')
    #outfile.write(mesh_heading_ids + '\n')
    #outfile.write(mesh_major_topic + '\n')
    #outfile.write(mesh_qualifiers + '\n')
    outfile.write('DATABANK : ' + '0' + '\n')
    outfile.write('LISTOFCHEM : ' + '0' + '\n')
    outfile.write('SUPPL_MESH : ' + '0' + '\n')
    outfile.write('NLM_JID ' + '0' + '\n')
    outfile.write('CITATION_STATUS ' + '0' + '\n')
    outfile.write('CITATION_VERSION ' + '0' + '\n')
    outfile.write('CITATION_OWNER ' + '0' + '\n')
    outfile.write('================================================\n')
    # writeText(setId, outfile)
    outfile.write(texts + '\n')
    outfile.close()

def make_mesh_string(article_mesh_terms):
    terms = article_mesh_terms.split('|')
    MESH_HEADINGS = []
    MESH_HEADINGS_IDS  = []
    # MESH_MAJOR_TOPICYN = []
    for term in terms:
        if term == '0':
            break
        mesh_id, mesh = term.split('#####')
        MESH_HEADINGS.append(mesh)
        MESH_HEADINGS_IDS.append(mesh_id)
    MESH_MAJOR_TOPICYN = ['Y'] * len(MESH_HEADINGS_IDS)

    MESH_HEADINGS_string = f'MESH_HEADINGS : {"|".join(MESH_HEADINGS)}'
    MESH_HEADINGS_IDS_string = f'MESH_HEADINGS_IDS : {"|".join(MESH_HEADINGS_IDS)}'
    MESH_MAJOR_TOPICYN_string = f'MESH_MAJOR_TOPICYN : {"|".join(MESH_MAJOR_TOPICYN)}'
    MESH_QUALIFIERS_string = f'MESH_QUALIFIERS : '

    mesh_string = '\n'.join([MESH_HEADINGS_string, MESH_HEADINGS_IDS_string, MESH_MAJOR_TOPICYN_string, MESH_QUALIFIERS_string])

    # MESH_QUALIFIERS  = []
    return mesh_string


with open(filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t')

    for idx, row in enumerate(reader):

        if idx == 0:
            article_uuid_ind = row.index('article_uuid')
            issn_ind = row.index('issn')
            journal_title_ind = row.index('journal_title')
            publisher_ind = row.index('publisher')
            pmid_ind = row.index('pmid')
            pmc_ind = row.index('pmc')
            pii_ind = row.index('pii')
            publisher_id_ind = row.index('publisher_id')
            doi_ind = row.index('doi')
            pub_date_ind = row.index('pub_date')
            article_title_ind = row.index('article_title')
            article_authors_ind = row.index('article_authors')
            article_keywords_ind = row.index('article_keywords')
            data_source_ind = row.index('data_source')
            article_type_tag_ind = row.index('article_type_tag')

            article_mesh_terms_ind = row.index('article_mesh_terms')
            continue

        if not idx % 100000:
            print(idx)

        article_uuid = row[article_uuid_ind]
        issn = row[issn_ind]
        journal_title = row[journal_title_ind]
        publisher = row[publisher_ind]
        pmid = row[pmid_ind]
        pmc = row[pmc_ind]
        pii = row[pii_ind]
        publisher_id = row[publisher_id_ind]
        doi = row[doi_ind]
        pub_date = row[pub_date_ind]
        article_title = row[article_title_ind]
        article_authors = row[article_authors_ind]
        article_keywords = row[article_keywords_ind]
        data_source = row[data_source_ind]
        article_type_tag = row[article_type_tag_ind]
        article_category = '0'
        article_pubtype_id = '0'

        article_mesh_terms = row[article_mesh_terms_ind]

        if article_uuid not in seen: #  and not seen[article_uuid]:
            # print(article_uuid)
            nct_id, prefix = parse_article_uuid(article_uuid)
            ct_filename = make_ct_file(nct_id, prefix)
            # print(nct_id)
            # print(prefix)
            print(ct_filename)
            # print(article_mesh_terms)
            meshes = make_mesh_string(article_mesh_terms)
            #  print(meshes)
            texts = readCTFile(ct_filename)
            writeTxtFile(article_uuid, issn, journal_title, publisher, pmid, pmc, pii, publisher_id, doi, pub_date, article_title, article_authors,
                         article_keywords, data_source, article_type_tag, article_category, article_pubtype_id,
                         meshes,
                         texts)
            seen[article_uuid] = True

