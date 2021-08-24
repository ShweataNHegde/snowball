import os
import glob
import xml.etree.ElementTree as ET
import pathlib
import yake
import subprocess
import logging
from bs4 import BeautifulSoup
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

def parse_xml(output_directory, results_txt, body_section='figure'):
    """globs the specified section parsed xml and dumps the text to a file

    Args:
        output_directory (str): CProject directory
        results_txt (str):name of text file to write parsed XML
        body_section (str, optional): [description]. Defaults to 'method'.
    """
    WORKING_DIRECTORY = os.getcwd()
    glob_results = glob.glob(os.path.join(WORKING_DIRECTORY,
                                          output_directory,"*", "sections",
                                          "**", f"*{body_section}*.xml"), recursive = True)
    logging.info(f'globbed_xml: {glob_results}')
    file1 = open(results_txt,"w+", encoding='utf-8')
    for result in glob_results:
        tree = ET.parse(result)
        root = tree.getroot()
        xmlstr = ET.tostring(root, encoding='utf8', method='xml')
        soup = BeautifulSoup(xmlstr, features='lxml')
        text = soup.get_text(separator="")
        text = text.replace(
            '\n', '')
        print(text, file = file1)
    logging.info(f'wrote text to {results_txt}')
   
def key_phrase_extraction(results_txt, terms_txt):
    """extract key phrases from the text file with parsed xml and saves the phrases in a text file (comma-separated)

    Args:
        results_txt (str): text file with parsed XML text
        terms_txt (str): name of text file with comma-separated extracted key phrases
    """
    text = pathlib.Path(results_txt).read_text(encoding='utf-8')
    custom_kw_extractor = yake.KeywordExtractor(lan='en', n=2, top=50, features=None)
    keywords = custom_kw_extractor.extract_keywords(text)

    keywords_list = []
    for kw in keywords:
        keywords_list.append(kw[0])
    logging.info('extracted key phrases')
    keywords_list_string = ', '.join(str(i) for i in keywords_list)
    with open(terms_txt, 'w', encoding='utf-8') as fo:
        fo.write(keywords_list_string)
    logging.info(f'wrote the phrases to {terms_txt}')

# Defining all variables
OD_QUERY = '(cyclic voltammetry) AND batteries'
OD_HITS = '50'
OD_OUTPUT='cyclic_voltammetry_20210824_1'
OD_RESULTS= 'cyclic_volammtery_1.txt'
OD_TERMS = 'terms_1.txt'
OD_OUTPUT_2 = 'cyclic_voltammetry_2'
#OD_RESULTS_2= 'cyclic_volammtery_2.txt'


querying_pygetpapers_sectioning(OD_QUERY, OD_HITS, OD_OUTPUT)
parse_xml(OD_OUTPUT,OD_RESULTS)
key_phrase_extraction(OD_RESULTS, OD_TERMS)
#querying_pygetpapers_sectioning(OD_QUERY, OD_HITS, OD_OUTPUT_2, using_terms=True, terms_txt=OD_TERMS)

