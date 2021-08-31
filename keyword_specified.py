import os
import glob
import xml.etree.ElementTree as ET
import subprocess
import logging
from pprint import pprint

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
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x --terms {terms_txt}',
                                shell=True)
    else:  
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x', 
                                shell=True)
    logging.info('running ami section')
    subprocess.run(f'ami -p {output_directory} section', shell=True)

def parse_xml(output_directory, section='kwd'):
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
    logging.info(f'no.of globbed_xml: {print(len(glob_results))}')
    pprint(glob_results)
    keywords_list = []
    for result in glob_results:
        tree = ET.parse(result)
        root = tree.getroot()
        for keyword in root.iter('kwd'):
            keywords_list.append(keyword.text)
    logging.info(f'list of keywords{keywords_list}')
    PMCID = []
    for result in glob_results:
        split_path = result.split('\\')
        PMCID.append(split_path[6])

    PMCID_set = set(PMCID)
    unique_PMC = list(PMCID_set)
    print(len(unique_PMC))

def get_unique_ids(glob_results):

    PMCID = []
    for result in glob_results:
        split_path = result.split('\\')
        PMCID.append(split_path[7])

    PMCID_set = set(PMCID)
    unique_PMC = list(PMCID_set)
    print(len(unique_PMC))

CPROJECT = os.path.join(os.getcwd(), 'corpus', 'climate_change')

#querying_pygetpapers_sectioning('climate change', '50', CPROJECT)
parse_xml(CPROJECT)
