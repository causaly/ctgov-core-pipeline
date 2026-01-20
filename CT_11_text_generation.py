import csv
import json
import os
import re
import sys

from lxml import etree as ET
from utils.xml_parser import XMLParser

csv.field_size_limit(58000000)


OUT_DIR = os.getcwd()+os.sep+str(sys.argv[3])
CT_DIR = sys.argv[2]

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

filename = sys.argv[1]

seen = {}


def parse_article_uuid(uuid):
    cols = uuid.split('_')
    _nct_id = cols[0]
    _prefix = cols[0][:7]

    return _nct_id, _prefix


def make_ct_file(_nct_id, _prefix):
    _filename = f'{CT_DIR}/{_prefix}xxxx/{_nct_id}.xml'

    return _filename


def filepath(path, set_id, suffix):
    return os.path.abspath(os.path.join(path, "{}.{}".format(set_id, suffix)))


def sanitise(input_str):
    input_str = input_str.replace('\r', '')
    input_str = input_str.replace('\n', ' ').replace('\t', ' ')
    input_str = re.sub(' +', ' ', input_str).strip()

    return input_str


def is_valid_value(in_str):
    if in_str != '0' and in_str != 0 and in_str != 'None' and in_str is not None and len(in_str.strip()) > 0:
        return True
    return False


def read_ct_file(_filename, _xml_parser_obj):
    print(f'reading {_filename}')
    xml = ET.parse(_filename, parser=parser)
    parsed_output = xml_parser_obj.start_parsing(xml)
    eligibility = '0'

    brief_title = '<ABSTRACT BRIEF TITLE>+++' + parsed_output["brief_title"] if is_valid_value(
        parsed_output["brief_title"]) else '0'
    official_title = '<ABSTRACT OFFICIAL TITLE>+++' + parsed_output["official_title"] if is_valid_value(
        parsed_output["official_title"]) else '0'
    intervention_list = []
    for inter in parsed_output["interventions"]:
        inter_str = inter["intervention_type"] + ": " + inter["intervention_name"]
        if is_valid_value(inter["intervention_description"]):
            inter_str += " / " + inter["intervention_description"]
        intervention_list.append(inter_str)
    if len(intervention_list) > 0:
        intervention = '<ABSTRACT INTERVENTION>+++' + sanitise(' '.join(intervention_list))
    else:
        intervention = '0'
    brief_summary = '<ABSTRACT BRIEF SUMMARY>+++' + sanitise(parsed_output["brief_summary"]) if is_valid_value(
        parsed_output["brief_summary"]) else '0'
    detailed_description = '<ABSTRACT DETAILED DESCRIPTION>+++' + sanitise(parsed_output["detailed_description"]) if (
        is_valid_value(parsed_output["detailed_description"])) else '0'

    arm_groups = []
    for _arm in parsed_output["study_arm_groups"]:
        arm_str = _arm["study_arm_group_type"] + ": " + _arm["study_arm_group_label"]
        if is_valid_value(_arm["study_arm_group_description"]):
            arm_str += " / " + _arm["study_arm_group_description"]
        arm_groups.append(arm_str)

    keywords = []
    if (parsed_output["trial_keywords"] != '0' and parsed_output["trial_keywords"] != 0 and
            parsed_output["trial_keywords"] is not None):

        if isinstance(parsed_output["trial_keywords"], str) and len(
                parsed_output["trial_keywords"].strip()) > 0:
            keywords.append(sanitise(parsed_output["trial_keywords"]))
        elif isinstance(parsed_output["trial_keywords"], list):
            keywords.extend([sanitise(x) for x in parsed_output["trial_keywords"]])

    if "eligibility_criteria" in parsed_output and len(parsed_output["eligibility_criteria"]) == 1:
        eligibility = sanitise(re.sub(r'\n+', '\n- ',
                                      parsed_output["eligibility_criteria"][0]["eligibility_text_description"]))
        eligibility = re.split('(Key )?Exclusion Criteria:?', eligibility, flags=re.IGNORECASE)[0]
        eligibility = eligibility.strip().strip("-")
        eligibility = '<ABSTRACT ELIGIBILITY>+++' + eligibility

    arm_group = '<ABSTRACT ARM GROUP>+++' + sanitise(' '.join(arm_groups))
    keyword = '<ABSTRACT KEYWORD>+++' + ' '.join(keywords)

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


def write_txt_file(_article_uuid,
                   _issn, _journal_title, _publisher, _pmid, _pmc, _pii, _publisher_id, _doi, _pub_date, _article_title,
                   _article_authors, _article_keywords, _data_source, _article_type_tag, _article_category,
                   _article_pubtype_id, _meshes, _texts):

    outfile = open(filepath(OUT_DIR, _article_uuid, 'txt'), 'w', encoding='utf-8')

    outfile.write('ISSN ' + _issn + '\n')
    outfile.write('JOURNAL_TITLE ' + _journal_title + '\n')
    outfile.write('PUBLISHER ' + _publisher + '\n')
    outfile.write('PMID ' + _pmid + '\n')
    outfile.write('PMC ' + _pmc + '\n')
    outfile.write('PII ' + _pii + '\n')
    outfile.write('PUBLISHER_ID ' + _publisher_id + '\n')
    outfile.write('DOI ' + _doi + '\n')
    outfile.write('PUBLICATON_DATE ' + _pub_date + '\n')
    outfile.write('TITLE ' + _article_title + '\n')
    outfile.write('AUTHORS : ' + _article_authors + '\n')
    outfile.write('KEYWORDS ' + _article_keywords + '\n')
    outfile.write('DATA_SOURCE : ' + _data_source + '\n')
    outfile.write('ARTICLE_PUBTYPE_TAG : ' + _article_type_tag + '\n')
    outfile.write('ARTICLE_CATEGORIES_HEADLINE : ' + _article_category + '\n')
    outfile.write('ARTICLE_PUBTYPE_ID : ' + _article_pubtype_id + '\n')
    outfile.write(_meshes + '\n')
    # outfile.write(mesh_headings + '\n')
    # outfile.write(mesh_heading_ids + '\n')
    # outfile.write(mesh_major_topic + '\n')
    # outfile.write(mesh_qualifiers + '\n')
    outfile.write('DATABANK : ' + '0' + '\n')
    outfile.write('LISTOFCHEM : ' + '0' + '\n')
    outfile.write('SUPPL_MESH : ' + '0' + '\n')
    outfile.write('NLM_JID ' + '0' + '\n')
    outfile.write('CITATION_STATUS ' + '0' + '\n')
    outfile.write('CITATION_VERSION ' + '0' + '\n')
    outfile.write('CITATION_OWNER ' + '0' + '\n')
    outfile.write('================================================\n')
    # writeText(setId, outfile)
    outfile.write(_texts + '\n')
    outfile.close()


def make_mesh_string(_article_mesh_terms):
    terms = _article_mesh_terms.split('|')
    mesh_headings = []
    mesh_headings_ids = []
    for term in terms:
        if term == '0':
            break
        mesh_id, mesh = term.split('#####')
        mesh_headings.append(mesh)
        mesh_headings_ids.append(mesh_id)
    mesh_major_topicyn = ['Y'] * len(mesh_headings_ids)

    mesh_headings_string = f'MESH_HEADINGS : {"|".join(mesh_headings)}'
    mesh_headings_ids_string = f'MESH_HEADINGS_IDS : {"|".join(mesh_headings_ids)}'
    mesh_major_topicyn_string = f'MESH_MAJOR_TOPICYN : {"|".join(mesh_major_topicyn)}'
    mesh_qualifiers_string = f'MESH_QUALIFIERS : '

    mesh_string = '\n'.join([mesh_headings_string, mesh_headings_ids_string,
                             mesh_major_topicyn_string, mesh_qualifiers_string])

    # MESH_QUALIFIERS  = []
    return mesh_string


if __name__ == "__main__":

    RULES_FILE_PATH = "config" + os.sep + "rules.json"
    with open(RULES_FILE_PATH, "r") as f:
        rules = json.load(f)
    parser = ET.XMLParser(remove_comments=True, huge_tree=True)
    xml_parser_obj = XMLParser(rules)

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

            if article_uuid not in seen:  # and not seen[article_uuid]:
                # print(article_uuid)
                nct_id, prefix = parse_article_uuid(article_uuid)
                ct_filename = make_ct_file(nct_id, prefix)
                # print(nct_id)
                # print(prefix)
                print(ct_filename)
                # print(article_mesh_terms)
                meshes = make_mesh_string(article_mesh_terms)
                #  print(meshes)
                texts = read_ct_file(ct_filename, xml_parser_obj)
                write_txt_file(article_uuid, issn, journal_title, publisher, pmid, pmc, pii, publisher_id, doi,
                               pub_date, article_title, article_authors, article_keywords, data_source,
                               article_type_tag, article_category, article_pubtype_id, meshes, texts)
                seen[article_uuid] = True
