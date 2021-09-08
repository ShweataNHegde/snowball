import glob
import json
import logging
import os
import re
import subprocess
import xml.etree.ElementTree as ET

import pandas as pd
import scispacy
import spacy
import yake
from bs4 import BeautifulSoup


class ScilitAnalyis:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def scoping_analyis(self, QUERY, HITS, CPROJECT, SECTION, PATH):
        #self.querying_pygetpapers_sectioning(QUERY,HITS,CPROJECT)
        metadata_dictionary = self.get_metadata_json(CPROJECT)
        self.get_PMCIDS(metadata_dictionary=metadata_dictionary)
        self.parse_xml(CPROJECT, SECTION,
                       metadata_dictionary=metadata_dictionary)
        self.get_abstract(metadata_dictionary=metadata_dictionary)
        self.get_keywords(metadata_dictionary=metadata_dictionary)
        self.key_phrase_extraction(
            SECTION, metadata_dictionary=metadata_dictionary)
        self.get_organism(SECTION, metadata_dictionary=metadata_dictionary)
        self.look_for_a_word(SECTION, metadata_dictionary=metadata_dictionary)
        self.look_for_a_word(
            SECTION, metadata_dictionary=metadata_dictionary,  search_for="C.")
        self.look_for_a_word(
            SECTION, metadata_dictionary=metadata_dictionary, search_for='Citrus')
        self.add_if_file_contains_terms(
            SECTION, metadata_dictionary=metadata_dictionary)
        self.convert_to_csv(metadata_dictionary=metadata_dictionary,
                            path=PATH)

    def querying_pygetpapers_sectioning(self, query, hits, output_directory, using_terms=False, terms_txt=None):
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

    def get_metadata_json(self, output_directory):
        metadata_dictionary = {}
        WORKING_DIRECTORY = os.getcwd()
        glob_results = glob.glob(os.path.join(WORKING_DIRECTORY,
                                              output_directory, "*", 'eupmc_result.json'))
        metadata_dictionary["metadata_json"] = glob_results
        logging.info(
            f'metadata found for {len(metadata_dictionary["metadata_json"])} papers')
        return metadata_dictionary

    def get_PMCIDS(self, metadata_dictionary):
        metadata_dictionary["PMCIDS"] = []
        for metadata in metadata_dictionary["metadata_json"]:
            with open(metadata) as f:
                metadata_in_json = json.load(f)
                try:
                    metadata_dictionary["PMCIDS"].append(
                        metadata_in_json["full"]["pmcid"])
                except KeyError:
                    metadata_dictionary["PMCIDS"].append('NaN')
        logging.info('getting PMCIDs')

    def parse_xml(self, output_directory, section, metadata_dictionary):
        metadata_dictionary[f"{section}"] = []
        for pmc in metadata_dictionary["PMCIDS"]:
            paragraphs = []
            test_glob = glob.glob(os.path.join(os.getcwd(), output_directory,
                                               pmc, 'sections', '**', f'*{section}*', '**', '*.xml'),
                                  recursive=True)
            for result in test_glob:
                tree = ET.parse(result)
                root = tree.getroot()
                xmlstr = ET.tostring(root, encoding='utf8', method='xml')
                soup = BeautifulSoup(xmlstr, features='lxml')
                text = soup.get_text(separator="")
                text = text.replace('\n', '')
                paragraphs.append(text)
            concated_paragraph = ' '.join(paragraphs)
            metadata_dictionary[f"{section}"].append(concated_paragraph)
        logging.info(f"parsing {section} section")

    def get_abstract(self, metadata_dictionary):
        TAG_RE = re.compile(r"<[^>]+>")
        metadata_dictionary["abstract"] = []
        for metadata in metadata_dictionary["metadata_json"]:
            with open(metadata) as f:
                metadata_in_json = json.load(f)
                try:
                    raw_abstract = metadata_in_json["full"]["abstractText"]
                    abstract = TAG_RE.sub(' ', raw_abstract)
                    metadata_dictionary["abstract"].append(abstract)
                except KeyError:
                    metadata_dictionary["abstract"].append('NaN')
        logging.info("getting the abstracts")

    def get_keywords(self, metadata_dictionary):
        metadata_dictionary["keywords"] = []
        for metadata in metadata_dictionary["metadata_json"]:
            with open(metadata) as f:
                metadata_in_json = json.load(f)
                try:
                    metadata_dictionary["keywords"].append(
                        metadata_in_json["full"]["keywordList"]["keyword"])
                except KeyError:
                    metadata_dictionary["keywords"].append('NaN')
        logging.info("getting the keywords from metadata")

    def key_phrase_extraction(self, section, metadata_dictionary):
        metadata_dictionary["yake_keywords"] = []
        for text in metadata_dictionary[f"{section}"]:
            custom_kw_extractor = yake.KeywordExtractor(
                lan='en', n=2, top=10, features=None)
            keywords = custom_kw_extractor.extract_keywords(text)
            keywords_list = []
            for kw in keywords:
                keywords_list.append(kw[0])
            metadata_dictionary["yake_keywords"].append(keywords_list)
        logging.info(f'extracted key phrases from {section}')

    def get_organism(self, section, metadata_dictionary, label_interested='GENE_OR_GENE_PRODUCT'):
        nlp = spacy.load("en_ner_bionlp13cg_md")
        metadata_dictionary["entities"] = []
        for text in metadata_dictionary[f"{section}"]:
            entity = []
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == label_interested:
                    entity.append(ent)
            metadata_dictionary["entities"].append(entity)
        logging.info(F"NER using SciSpacy - looking for {label_interested}")

    def convert_to_csv(self, metadata_dictionary, path='keywords_results_yake_organism_pmcid_tps_cam_ter_c.csv'):
        df = pd.DataFrame(metadata_dictionary)
        df.to_csv(path, encoding='utf-8', line_terminator='\r\n')
        logging.info(f'writing the keywords to {path}')

    def look_for_a_word(self, section, metadata_dictionary, search_for="TPS"):
        metadata_dictionary[f"{search_for}_match"] = []
        for text in metadata_dictionary[f"{section}"]:
            words = text.split(" ")
            match_list = ([s for s in words if f"{search_for}" in s])
            metadata_dictionary[f"{search_for}_match"] .append(match_list)
        logging.info(f"looking for {search_for} in {section}")

    def add_if_file_contains_terms(self, section, metadata_dictionary, terms=['terpene synthase']):
        metadata_dictionary["terms"] = []
        for term in terms:
            for text in metadata_dictionary[f"{section}"]:
                if term.lower() in text.lower():
                    metadata_dictionary["terms"].append(term)
                else:
                    metadata_dictionary["terms"].append('NaN')
        logging.info(f'looking for term matches in {section}')



QUERY = "('terpene synthase') AND ('volatile') AND ('Citrus') AND (((SRC:MED OR SRC:PMC OR SRC:AGR OR SRC:CBA) NOT (PUB_TYPE:'Review')))"
HITS = 200
CPROJECT = os.path.join(os.getcwd(), 'corpus', 'tps_citrus')
SECTION = 'result'
PATH = f'citrus_full_search_{SECTION}_2.csv'

tps_analysis = ScilitAnalyis()
analysis = tps_analysis.scoping_analyis(QUERY, HITS, CPROJECT, SECTION, PATH)
