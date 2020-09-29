"""Core module."""
import os
import json
from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD, FOAF, DC
from horace import uri
import re
from rdflib.plugins.stores import sparqlstore


CORE = Namespace("http://postdata.linhd.uned.es/ontology/postdata-core#")
STRUCT = Namespace("http://postdata.linhd.uned.es/ontology/postdata-structuralElements#")

NAMESPACES = {"xsd": "http://www.w3.org/2001/XMLSchema#",
              "objectrole": "http://www.ontologydesignpatterns.org/cp/owl/objectrole.owl#",
              "obj": "http://www.openrdf.org/rdf/2009/object#",
              "skos": "http://www.w3.org/2004/02/skos/core#",
              "pdstruct": "http://postdata.linhd.uned.es/ontology/postdata-structuralElements#",
              "pdcore": "http://postdata.linhd.uned.es/ontology/postdata-core#",
              "pd": "http://postdata.linhd.uned.es/resource/",
              "dc": "http://purl.org/dc/elements/1.1/",
              "foaf": "http://xmlns.com/foaf/0.1/"}


def to_rdf(_json) -> Graph:
    g = Graph()

    g = g + add_core_elements(_json, "PLCSO")
    g = g + add_structural_elements(_json, "PLCSO")

    return g


def add_core_elements(_json, dataset):
    g = Graph()
    poem_title = _json["poem_title"]
    author = _json["author"]

    r_redaction = uri.uri_redaction(author, poem_title, dataset)
    r_creator = uri.uri_creator_role(author, poem_title)
    r_poetic_work = uri.uri_poetic_work(author, poem_title)
    r_person = uri.uri_person(author)

    # Types
    g.add((r_poetic_work, RDF.type, CORE.PoeticWork))
    g.add((r_redaction, RDF.type, CORE.Redaction))
    g.add((r_creator, RDF.type, CORE.CreatorRole))
    g.add((r_person, RDF.type, CORE.Person))

    # Labels
    g.add((r_poetic_work, DC.title, Literal(poem_title, lang="es")))
    g.add((r_person, FOAF.name, Literal(author, lang="es")))

    # Object Properties
    g.add((r_poetic_work, CORE.isRealisedThrough, r_redaction))
    g.add((r_redaction, CORE.hasCreator, r_creator))
    g.add((r_creator, CORE.isRoleOf, r_person))

    return g


def add_structural_elements(_json, dataset):
    g = Graph()
    poem_title = _json["poem_title"]
    author = _json["author"]

    r_stanza_list = uri.uri_stanza_list(poem_title, author, dataset)
    r_redaction = uri.uri_redaction(author, poem_title, dataset)

    # Add stanza_list type
    g.add((r_stanza_list, RDF.type, STRUCT.OrderedStanzaList))
    # Add redaction to stanza_list
    g.add((r_redaction, STRUCT.hasStanzaList, r_stanza_list))

    for stanza in _json["stanzas"]:
        stanza_number = stanza["stanza_number"]
        stanza_text = stanza["stanza_text"]

        r_stanza = uri.uri_stanza(stanza_number, author, poem_title, dataset)
        # Add Stanza Type
        g.add((r_stanza_list, RDF.type, STRUCT.Stanza))
        # Add StanzaList to Stanza
        g.add((r_stanza_list, STRUCT.hasStanzaItem, r_stanza))

        # Add Stanza DP
        g.add((r_stanza, STRUCT.content, Literal(stanza_text, lang="es")))
        g.add((r_stanza, STRUCT.stanzaNumber, Literal(stanza_number, datatype=XSD.nonNegativeInteger)))

        for line in stanza["lines"]:
            line_number = line["line_number"]
            line_text = line["line_text"]

            r_line = uri.uri_line(line_number, stanza_number, author, poem_title, dataset)
            # Add line type
            g.add((r_line, RDF.type, STRUCT.Line))
            # Add stanza to line
            g.add((r_stanza, STRUCT.hasLine, r_line))
            # Add line DP
            g.add((r_line, STRUCT.content, Literal(line_text, lang="es")))
            g.add((r_line, STRUCT.lineNumber, Literal(line_number, datatype=XSD.nonNegativeInteger)))

            if "words" in line.keys():
                for i, word in enumerate(line["words"]):
                    word_number = str(i)
                    word_text = word["word_text"]

                    r_word = uri.uri_word(word_number, line_number, stanza_number, author, poem_title, dataset)
                    # Add word type
                    g.add((r_word, RDF.type, STRUCT.Word))
                    # Add line to word
                    g.add((r_line, STRUCT.hasContent, r_word))
                    # Add Word DP
                    g.add((r_word, STRUCT.content, Literal(word_text, lang="es")))
                    g.add((r_word, STRUCT.lineNumber, Literal(word_number, datatype=XSD.nonNegativeInteger)))

                    if "syllables" in word.keys():
                        for i, syllable in enumerate(word["syllables"]):
                            syllable_number = str(i)
                            r_syllable = uri.uri_syllable(syllable_number, word_number, line_number, stanza_number, author, poem_title, dataset)
                            # Add Syllable type
                            g.add((r_syllable, RDF.type, STRUCT.Syllable))
                            # Add Syllable DP
                            g.add((r_syllable, STRUCT.positionInWord, Literal(syllable_number, datatype=XSD.nonNegativeInteger)))
                            g.add((r_syllable, STRUCT.content, Literal(syllable, datatype=XSD.nonNegativeInteger)))
    return g


def sparql_update(graph: Graph):
    import requests
    from requests.auth import HTTPDigestAuth

    prefixes = ""
    for prefix, uri in NAMESPACES.items():
        graph.namespace_manager.bind(prefix, uri)
        prefixes = prefixes + "prefix " + prefix + ": " + "<" + uri + ">" + "\n"

    data = graph.serialize(format='turtle').decode('utf-8')

    url = "http://localhost:8890/sparql-auth"
    query = """
    INSERT IN GRAPH <http://localhost:8890/POSTDATA/>
    {
        #DATA#
    }""".replace("#DATA#", data)

    query = re.sub(r'@prefix.*>\s\.', "", query)
    query = prefixes + query
    # print(query)

    auth = HTTPDigestAuth(username="dba", password="dba")
    result = requests.post(url, params={"query": query}, auth=auth)
    print(result.text)
    return result.status_code


total_jsons = {}
base_root = "/home/omar/Documents/POSTDATA/Averell/datasets_json/"
datasets = os.listdir(base_root)
print(datasets)

for dataset in datasets:
    jsons_root = base_root + dataset + "/averell/parser"
    authors = os.listdir(jsons_root)
    for author in authors:
        json_files = os.listdir(jsons_root + "/" + author)
        for json_file in json_files:
            if json_file[-5:] == ".json":
                total_jsons.update({json_file[:-5]: jsons_root + "/" + author + "/" + json_file})

n_doc = 0
for name, root in total_jsons.items():
    n_doc += 1
    rdf = to_rdf(json.load(open(root)))
    status = sparql_update(rdf)
    print(name, root, n_doc, status)
