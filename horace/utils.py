from rdflib import URIRef
from slugify import slugify

NAMESPACE_URL_TEMPLATE = ("http://postdata.linhd.uned.es/ontology/"
                          "postdata-{onto}#")

NAMESPACES = {"xsd": "http://www.w3.org/2001/XMLSchema#",
              "objectrole": "http://www.ontologydesignpatterns.org/cp/owl/objectrole.owl#",
              "obj": "http://www.openrdf.org/rdf/2009/object#",
              "skos": "http://www.w3.org/2004/02/skos/core#",
              "pdcore": NAMESPACE_URL_TEMPLATE.format(onto="core"),
              "pdstruct": NAMESPACE_URL_TEMPLATE.format(
                  onto="structuralElements"),
              "pddates": "http://postdata.linhd.uned.es/ontology/postdata-dates#",
              "postdata": "http://postdata.linhd.uned.es/resource/",
              "dc": "http://purl.org/dc/elements/1.1/",
              "foaf": "http://xmlns.com/foaf/0.1/",
              }


def create_uri(**uri_data) -> URIRef:
    """Generate a new POSTDATA resources URI

    :param uri_data: Necessary data for building each POSTDATA resources URI
    :return: URIRef object representing the resource
    :rtype: :class:`rdflib.URIRef`
    """
    pd_uri = f"{uri_data['onto_class']}_"
    pd_uri += "_".join([slugify(uri_data[token]) for token in uri_data if
                        token != "onto_class"])
    return URIRef(f"{NAMESPACES['postdata']}{pd_uri}")
