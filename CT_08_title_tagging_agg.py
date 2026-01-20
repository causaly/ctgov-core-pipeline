#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import csv
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

csv.field_size_limit(58000000)

# baseDir = '/data-processing'
# batchGen = '20200727'
# filePath = baseDir + '/' + batchGen + '/pipeline/tsv/pre_loading'

# input_filename = 'ngs_scored_toload_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv'
# output_filename = 'title_agg_ngs_scored_ngs_scored_toload_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv'

input_filename = sys.argv[1]
output_filename = sys.argv[2]


# Adding batchType to be used for final update statement
# options are parsegen or batch
batchType = 'batch'

title_tags = {}
original_titles = {}

article_uuid_ind = 0
article_title_tag_ind = 0
article_title_ind = 0

# 1. Gather all titles
with open(input_filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            article_uuid_ind = row.index('article_uuid')
            article_title_tag_ind = row.index('article_title_evidence_tag')
            article_title_ind = row.index('article_title')
            continue

        if not idx % 250000:
            print idx

        # testing for the edge nested cases in tagging, e.g.
        # <concept cui=C0004391 <concept cui=C0024660 cat=T015 pc=1>cat</concept>=T043 pc=0>Autophagy</concept>, Metabolism, and Cancer.
        # skip these
        if '</concept>=T' in row[article_title_tag_ind]:
            row[article_title_tag_ind] = row[article_title_ind]

        if row[article_uuid_ind] not in title_tags:
            title_tags[row[article_uuid_ind]] = [row[article_title_tag_ind]]
        else:
            title_tags[row[article_uuid_ind]].append(row[article_title_tag_ind])

        if row[article_uuid_ind] not in original_titles:
            original_titles[row[article_uuid_ind]] = row[article_title_ind]

print 'Aggregated all title tags, num of docs is: ', len(title_tags)

# 2. Aggregate all tags in the document - title tags dictionary
aggregated_titles = {}

pattern = r"<concept (.*?)>(.*?)</concept>"

for item in title_tags:
    article_uuid = item
    article_tag_titles = title_tags[article_uuid]
    untouched_original_title = original_titles[article_uuid]
    original_article_title = original_titles[article_uuid]

    if not any([title for title in article_tag_titles if '<concept' in title]):
        # no tags found for this article title - just use the original
        aggregated_titles[article_uuid] = article_tag_titles[0]
        #print '++++++ No tags were found: ', article_tag_titles
        continue

    all_concept_tags_temp = []
    all_concept_tags = []
    seen_matched_concepts = []
    for tags in article_tag_titles:
        all_concept_tags_temp.extend(re.findall(pattern, tags, flags=0))
    all_concept_tags_temp = list(set(all_concept_tags_temp))

    # remove duplicate and nested tags
    for index, item in enumerate(all_concept_tags_temp):

        if '<concept' in all_concept_tags_temp[index][1]:
            concept_details = all_concept_tags_temp[index][0]
            fixed_matched_concept = re.sub('<[^<]+?>', '', all_concept_tags_temp[index][1])
            all_concept_tags_temp[index] = (concept_details, fixed_matched_concept)
            original_article_title = original_article_title.replace("</concept></concept>", "</concept>")

    # Consider substring tagging problem
    match_strings_list = []
    for index, item in enumerate(all_concept_tags_temp):
        match_strings_list.append(item[1])

    del_indices = []
    for index, match_str_src in enumerate(match_strings_list):
        for item in match_strings_list:
            if match_str_src == item:
                continue
            if match_str_src.lower() in item.lower():
                del_indices.append(index)
    del_indices = list(set(del_indices))

    # It might happen that two elements to tag can be substrings of each other
    # In such case a shorter string needs to be deleted
    if len(del_indices) != 0:
        # print '---- Substr encountered, need to delete one of the elements: '
        # print all_concept_tags_temp
        # print del_indices
        del_indices = sorted(del_indices, reverse=True)
        for todelete_ind in del_indices:
            del(all_concept_tags_temp[todelete_ind])
        # print all_concept_tags_temp
        # print '----------------'


    # edge cases for similar entry terms, different concepts
    for index, item in enumerate(all_concept_tags_temp):
        if item[1] in seen_matched_concepts:
            continue
        else:
            seen_matched_concepts.append(item[1])
            all_concept_tags.append(item)

    # final deduplication of matching records
    all_concept_tags = list(set(all_concept_tags))

    for item in all_concept_tags:
        opening_tag = '<concept '+item[0]+'>'
        closing_tag = '</concept>'
        match_string = item[1]
        match_string_lower = item[1].lower()

        if match_string in original_article_title:
            replace_string = opening_tag + match_string + closing_tag
        elif match_string_lower.capitalize() in original_article_title:
            replace_string = opening_tag + match_string_lower.capitalize() + closing_tag
        elif match_string_lower in original_article_title:
            replace_string = opening_tag + match_string_lower + closing_tag
        elif match_string_lower in original_article_title.lower():
            replace_string = opening_tag + match_string_lower + closing_tag
        else:
            print
            print '!!!!!!!! MATCH NOT FOUND!'
            print untouched_original_title
            print original_article_title
            print match_string
            print replace_string
            print all_concept_tags
            print '!!!!!!!!!!!!!!!!!!!!!!!!!'
            print
            #raw_input('wait')
            continue

        try:
            # ToDo for now use the approach of reverting the tag, but find a better regex solution
            original_article_title_temp = re.sub(r"\b%s\b" % match_string, replace_string, original_article_title, flags=re.IGNORECASE)
            if '</concept></' in original_article_title_temp or '</concept>=T' in original_article_title_temp:
                pass
            else:
                original_article_title = original_article_title_temp
        except Exception, e:
            print (str(e))
            print (original_article_title)
            print ("Query", match_string)
            print ("REPLACEMENT: ", replace_string)
            print 'Passing on'
            #print ('Replacing directly...')
            #original_article_title = original_article_title.replace(match_string, replace_string)

    if article_uuid not in aggregated_titles:

        # REMOVE ALL TAGS coming in from the original title
        if '<i>' in original_article_title:
            original_article_title = original_article_title.replace('<i>', '').replace('</i>', '')
        if '<em>' in original_article_title:
            original_article_title = original_article_title.replace('<em>', '').replace('</em>', '')
        if '<I>' in original_article_title:
            original_article_title = original_article_title.replace('<I>', '').replace('</I>', '')
        if '<p>' in original_article_title:
            original_article_title = original_article_title.replace('<p>', '')
        if '</p>' in original_article_title:
            original_article_title = original_article_title.replace('</p>', '')
        if '<b>' in original_article_title:
            original_article_title = original_article_title.replace('<b>', '')
        if '</b>' in original_article_title:
            original_article_title = original_article_title.replace('</b>', '')

        # Check there are no surprises
        if '</concept></' in original_article_title or original_article_title == '0' or original_article_title == '' or original_article_title == ' ':
            print 'Wrong tag: ', row[article_uuid_ind]
            print original_article_title
            raw_input('wait')

        aggregated_titles[article_uuid] = original_article_title

print 'Done matching, writing to the csv . Total count of aggregated titles: ', len(aggregated_titles)


# Write out to the csv (input csv with appended column)

# Output csv
writer_0 = csv.writer(open(output_filename, 'w'), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')

with open(input_filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            article_uuid_ind = row.index('article_uuid')

            row.append('final_aggregated_title_tagged')
            writer_0.writerow(row)
            continue

        article_uuid = row[article_uuid_ind]
        title_tagged = aggregated_titles[article_uuid].replace('"', '\'')

        row.append(title_tagged)
        try:
            writer_0.writerow(row)
        except Exception, e:
            print str(e)
            print row
            raw_input('wait')

print 'Completed all jobs'
