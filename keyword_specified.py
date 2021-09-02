import os
import glob
import xml.etree.ElementTree as ET
import subprocess
import logging
import re
import pandas as pd
#from pprint import pprint
keywords_dictionary = {}

logging.basicConfig(level=logging.INFO)

# All the functions
def querying_pygetpapers_sectioning(query, hits, output_directory, using_terms = False, terms_txt=None):
    """queries pygetpapers for specified query. Downloads XML, and sections papers using ami section

    Args:
        query (str): query to pygetpapers
        hits (int): no. of papers to download
        output_directory (str): CProject Directory (where papers get downloaded)
        using_terms (bool, optional): pygetpapers --terms flag. Defaults to False.
        terms_txt (str, optional): path to text file with terms. Defaults to None.
    """
    logging.info('querying pygetpapers')
    if using_terms:
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x --terms {terms_txt} --logfile pygetpapers_log.txt',
                                shell=True)
    else:  
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x  --logfile pygetpapers_log.txt', 
                                shell=True)
    logging.info('running ami section')
    subprocess.run(f'ami -p {output_directory} section', shell=True)

def get_keyword_path(output_directory, section='kwd'):
    """globs for keywords section, parses keywords and writes to a text file

    Args:
        output_directory (str): path to CProject
        results_txt (str): name of text file where keywords are stored
        section (str, optional): [description]. Defaults to 'kwd'.
    """
    WORKING_DIRECTORY = os.getcwd()
    glob_results = glob.glob(os.path.join(WORKING_DIRECTORY,
                                          output_directory,"*", "sections",
                                          "0_front","1_article-meta",  f"*{section}*.xml"), recursive = True)
    logging.info(f'no.of globbed_xml: {(len(glob_results))}')
    keywords_dictionary["glob"] = glob_results

def parse_xml_get_keywords(keywords_dictionary=keywords_dictionary):
    keywords_list = []
    for result in keywords_dictionary["glob"]:
        tree = ET.parse(result)
        root = tree.getroot()
        ind_keywords = []
        for keyword in root.iter('kwd'):
            ind_keywords.append(keyword.text)
        keywords_list.append(ind_keywords)
    keywords_dictionary["keywords"] = keywords_list
    logging.info("getting keywords")

def get_PMCIDS(keywords_dictionary=keywords_dictionary):
    PMCIDS = []
    for result in keywords_dictionary["glob"]:
        split_path = result.split('\\')
        r = re.compile(".*PMC")
        PMCID = (list(filter(r.match, split_path)))
        PMCIDS.extend(PMCID)
    keywords_dictionary["PMCIDS"] = PMCIDS
    logging.info('getting PMCIDs')

def get_abstract_path(output_directory, section='abstract', keywords_dictionary=keywords_dictionary):
    """globs for keywords section, parses keywords and writes to a text file

    Args:
        output_directory (str): path to CProject
        results_txt (str): name of text file where keywords are stored
        section (str, optional): [description]. Defaults to 'kwd'.
    """
    WORKING_DIRECTORY = os.getcwd()
    for PMCID in keywords_dictionary["PMCIDS"]:
        glob_results_ab = glob.glob(os.path.join(WORKING_DIRECTORY,
                                            output_directory,f"{PMCID}", "sections",
                                            "0_front","1_article-meta",  f"*{section}*.xml"), recursive = True)

    keywords_dictionary["abstract"] = glob_results_ab
def convert_to_csv(path='keywords.csv', keywords_dictionary=keywords_dictionary):
    df = pd.DataFrame(keywords_dictionary)
    df.to_csv(path, encoding='utf-8', line_terminator='\r\n')
    logging.info('writing the keywords to csv')

CPROJECT = os.path.join(os.getcwd(), 'corpus', 'invasion_biology_100')
#querying_pygetpapers_sectioning('(invasive species)', '100', CPROJECT)
get_keyword_path(CPROJECT)
parse_xml_get_keywords()
get_PMCIDS()
get_abstract_path(CPROJECT)
convert_to_csv()


'''
    PMCID = []
    for result in glob_results:
       
        split_path = result.split('\\')
        PMCID.append(split_path[6])

    PMCID_set = set(PMCID)
    unique_PMC = list(PMCID_set)
    print(len(unique_PMC))
    result = 'C:\\Users\\shweata\\snowball\\corpus\\cyclic_voltammetry_20210824_1\\PMC8004831\\sections\\0_front\\1_article-meta\\19_kwd-group.xml'
    split_path = result.split('\\')
    r = re.compile(".*PMC")
    print(list(filter(r.match, split_path)))
'''

