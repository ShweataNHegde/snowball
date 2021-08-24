import os
import glob
import xml.etree.ElementTree as ET
import pathlib
import yake
import subprocess
# All the functions
def querying_pygetpapers_sectioning(query, hits, output_directory, using_terms = False, terms_txt=None):

    if using_terms:
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x --terms {terms_txt}',
                                shell=True)
    else:  
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x', 
                                shell=True)
    subprocess.run(f'ami -p {output_directory} section', shell=True)

def globbing(output_directory, results_txt):
    WORKING_DIRECTORY = os.getcwd()
    glob_results = glob.glob(os.path.join(WORKING_DIRECTORY,
                                          output_directory,"*", "sections",
                                          "**", "*method*","**" ,"*_p.xml"), recursive = True)
    file1 = open(results_txt,"w+", encoding='utf-8')
    for result in glob_results:
        tree = ET.parse(result)
        root = tree.getroot()
        for para in root.iter('p'):
            print (para.text, file = file1) 

def key_phrase_extraction(results_txt, terms_txt):
    text = pathlib.Path(results_txt).read_text(encoding='utf-8')
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(text)
    keywords_list = []
    for kw in keywords:
        keywords_list.append(kw[0])
    keywords_list_string = ', '.join(str(i) for i in keywords_list)
    with open(terms_txt, 'w') as fo:
        fo.write(keywords_list_string)

# Defining all variables
OD_QUERY = 'cyclic voltammetry'
OD_HITS = '5'
OD_OUTPUT='cyclic_voltammetry_20210823'
OD_RESULTS= 'cyclic_volammtery.txt'
OD_TERMS = 'terms.txt'
OD_OUTPUT_2 = 'cyclic_voltammetry_2'
OD_RESULTS_2= 'cyclic_volammtery_2.txt'
OD_TERMS_2 = 'terms_2.txt'

querying_pygetpapers_sectioning(OD_QUERY, OD_HITS, OD_OUTPUT)
globbing(OD_OUTPUT,OD_RESULTS)
key_phrase_extraction(OD_RESULTS, OD_TERMS)
querying_pygetpapers_sectioning(OD_QUERY, OD_HITS, OD_OUTPUT_2, using_terms=True, terms_txt=OD_TERMS)

