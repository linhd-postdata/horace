import os
from horace.core import add_core_elements
from horace.metrical import add_metrical_elements
import json


def generate(corpora_root, rdf_root):
    total_jsons = {}
    # base_root = "/home/uned/POSTDATA/corpora/"
    base_root = corpora_root
    datasets = os.listdir(base_root)
    print(datasets)

    for dataset in datasets:
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
        print(name, root, n_doc)
        rdf = add_core_elements(json.load(open(root)))
        rdf = rdf + add_metrical_elements(json.load(open(root)))
        # rdf.serialize("/home/uned/POSTDATA/KG/poem_" + str(n_doc) + ".ttl", format="ttl")
        rdf.serialize(rdf_root + "poem_" + str(n_doc) + ".ttl",
                      format="ttl")


def query():
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

generate("./corpora/", "./kg/")
