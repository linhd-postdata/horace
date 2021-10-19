import os
from core import add_core_elements
from poetic import add_metrical_elements, add_rantanplan_elements
from rantanplan import get_scansion
import json
import sys
import getopt


def generate(corpora_root, rdf_root):
    total_jsons = {}
    # base_root = "/home/uned/POSTDATA/corpora/"
    base_root = corpora_root
    datasets = os.listdir(base_root)
    print(datasets)

    spanish_datasets = ["disco2_1", "disco3", "adso", "adso100", "plc", "gongo"]
    all_datasets = spanish_datasets + ["fbfv", "ecpa"]

    for dataset in datasets:
        if dataset in all_datasets:
            print(dataset)
            jsons_root = base_root + dataset + "/averell/parser"
            authors = os.listdir(jsons_root)
            print(authors)
            for author in [a for a in authors if os.path.isdir(jsons_root + "/" + a)]:
                json_files = os.listdir(jsons_root + "/" + author)
                for json_file in json_files:
                    if json_file[-5:] == ".json":
                        total_jsons.update({json_file[:-5]: jsons_root + "/" + author + "/" + json_file})

    n_doc = 0
    for name, root in total_jsons.items():
        n_doc += 1

        _json = json.load(open(root))

        rdf = add_core_elements(_json)
        rdf = rdf + add_metrical_elements(_json)

        poem_text = "\n\n".join([stanza["stanza_text"] for stanza in _json["stanzas"]])
        poem_title = _json["poem_title"]
        author = _json["author"]
        dataset = _json["corpus"]

        if dataset in spanish_datasets:
            scansion = None
            try:
                scansion = get_scansion(poem_text, rhyme_analysis=True, rhythm_format="pattern",
                     rhythmical_lengths=None, split_stanzas_on=r"\n\n",
                     pos_output=False, always_return_rhyme=True)
                # print(scansion)
            except:
                print("Rantanplan Error", " -- ", poem_title, "--", author, "--", dataset)
                pass
            if scansion is not None:
                try:
                    rdf = rdf + add_rantanplan_elements(scansion, poem_title, author, dataset)
                except:
                    print("Horace error parsing ", poem_title, "--", author, "--", dataset)
                    pass
                # print("PARSED", " -- ", poem_title, "--", author,

        rdf.serialize(rdf_root + "poem_" + str(n_doc) + ".ttl",
                      format="ttl", encoding="utf-8")
        if n_doc % 300 == 0:
            print("PARSED TO RDF #", n_doc, "--- Last poem -> ", name, root)


def query():
    """Not used"""
    import requests
    from requests.auth import HTTPBasicAuth

    sparql_endpoint = "http://localhost:3030/core_dataset/sparql"
    sparqlquery = "SELECT DISTINCT ?a WHERE { ?a ?b ?c. }"

    params = {
        "query": sparqlquery
    }
    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:59.0) Gecko/20100101 Firefox/59.0'
    }
    get = requests.get(sparql_endpoint, params=params, headers=headers)
    results = get.content
    print(results)


def main(argv):
    inputfolder = ''
    # The input folder that has as subfolders for each dataset downloaded by averell
    # "/home/uned/POSTDATA/corpora/"
    outputfolder = ''
    # "/home/uned/POSTDATA/KG/"
    try:
        opts, args = getopt.getopt(argv, "i:o:", ["ifold=", "ofold="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifold"):
            inputfolder = arg
        elif opt in ("-o", "--ofold"):
            outputfolder = arg

    print("L", inputfolder, outputfolder)
    generate(inputfolder, outputfolder)


if __name__ == "__main__":
    main(sys.argv[1:])
    # generate("/home/uned/POSTDATA/corpora/", "/home/uned/POSTDATA/KG/")
