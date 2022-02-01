"""Core module."""
import os
import json
from rdflib import Graph, Namespace, RDF, Literal, XSD, RDFS
from utils import create_uri, NAMESPACES, URIRef, slugify


CORE = Namespace("http://postdata.linhd.uned.es/ontology/postdata-core#")
KOS = Namespace("http://postdata.linhd.uned.es/kos/")


def to_rdf(_json) -> Graph:
    graph = add_core_elements(_json)
    return graph


def add_core_elements(cj_store, _json):
    graph = Graph(store=cj_store, identifier="tag:stardog:api:context:default")

    # Add namespaces
    for prefix, uri_ns in NAMESPACES.items():
        graph.namespace_manager.bind(prefix, uri_ns)

    # Get mandatory keys
    poem_title = _json["poem_title"]
    author = _json["author"]
    dataset = _json["corpus"]

    # Creation of mandatory resources
    r_redaction = create_uri("R", author, poem_title, dataset)
    r_agent_role = create_uri("AR", author, poem_title)
    r_poetic_work = create_uri("PW", author, poem_title)
    r_person = create_uri("P", author)
    r_work_conception = create_uri("WC", author, poem_title)

    # Assignation of types for mandatory resources
    graph.add((r_poetic_work, RDF.type, CORE.PoeticWork))
    graph.add((r_redaction, RDF.type, CORE.Redaction))
    graph.add((r_agent_role, RDF.type, CORE.AgentRole))
    graph.add((r_person, RDF.type, CORE.Person))
    graph.add((r_work_conception, RDF.type, CORE.WorkConception))

    # Data Properties for mandatory resources
    graph.add((r_poetic_work, CORE.title, Literal(poem_title)))
    graph.add((r_person, CORE.name, Literal(author)))

    # Object Properties for mandatory resources
    graph.add((r_poetic_work, CORE.isRealisedThrough, r_redaction))
    graph.add((r_redaction, CORE.realises, r_poetic_work))

    graph.add((r_work_conception, CORE.initiated, r_poetic_work))
    graph.add((r_poetic_work, CORE.wasInitiatedBy, r_work_conception))

    graph.add((r_work_conception, CORE.hasAgentRole, r_agent_role))
    graph.add((r_agent_role, CORE.isAgentRoleOf, r_work_conception))

    graph.add((r_agent_role, CORE.hasAgent, r_person))
    graph.add((r_person, CORE.isAgentOf, r_agent_role))

    graph.add((r_agent_role, CORE.roleFunction, KOS.Creator))
    graph.add((KOS.Creator, RDFS.label, Literal("Creator", lang="en")))

    # Key for year : year
    # Add year of poetic work conception
    if "year" in _json.keys():
        work_date = _json["year"]
        if work_date is not None:
            r_conception_date = create_uri("TS_C_", author, poem_title)
            graph.add(
                (r_conception_date, RDF.type, CORE.TimeSpan))
            if work_date.isdigit():
                # Distinguish DPs or distinguish classes (date, textualDate VS period, timePoint)
                graph.add((r_conception_date, CORE.date, Literal(work_date, datatype=XSD.date)))
            else:
                graph.add((r_conception_date, CORE.date, Literal(work_date, datatype=XSD.string)))

            graph.add((r_work_conception, CORE.hasTimeSpan, r_conception_date))
            graph.add((r_conception_date, CORE.isTimeSpanOf, r_work_conception))

    # Key for alt title : poem_alt_title
    # Add alternative poetic work title
    if "poem_alt_title" in _json.keys():
        alt_title = _json["poem_alt_title"]
        graph.add((r_poetic_work, CORE.alternativeTitle, Literal(alt_title, lang="es")))

    # Key for poem type : structure
    # Add poetic work genre
    if "structure" in _json.keys():
        genre = _json["structure"]
        r_genre = URIRef(KOS + slugify(genre))
        graph.add((r_poetic_work, CORE.genre, r_genre))
        graph.add((r_genre, RDFS.label, Literal(genre)))

    # Add textual content
    if "stanzas" in _json.keys():
        # print("LEN", len([stanza["stanza_text"] for stanza in _json["stanzas"]]))
        text = "\n\n".join(stanza["stanza_text"] for stanza in _json["stanzas"])
        graph.add((r_redaction, CORE.text, Literal(text)))
        # print(text)
    # return conjunctive_graph
