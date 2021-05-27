from rdflib import URIRef
from slugify import slugify

NAMESPACE_URL_TEMPLATE = ("http://postdata.linhd.uned.es/ontology/"
                          "postdata-{onto}#")

NAMESPACES = {"xsd": "http://www.w3.org/2001/XMLSchema#",
              "objectrole": "http://www.ontologydesignpatterns.org/cp/owl/objectrole.owl#",
              "obj": "http://www.openrdf.org/rdf/2009/object#",
              "skos": "http://www.w3.org/2004/02/skos/core#",
              "pdc": NAMESPACE_URL_TEMPLATE.format(onto="core"),
              "pdm": NAMESPACE_URL_TEMPLATE.format(
                  onto="metricalAnalysis"),
              "pdd": "http://postdata.linhd.uned.es/ontology/postdata-dates#",
              "pd": "http://postdata.linhd.uned.es/resource/",
              "dc": "http://purl.org/dc/elements/1.1/",
              "foaf": "http://xmlns.com/foaf/0.1/",
              }


def create_uri(*uri_data) -> URIRef:
    """Generate a new POSTDATA resources URI

    :param uri_data: Necessary data for building each POSTDATA resources URI
    :return: URIRef object representing the resource
    :rtype: :class:`rdflib.URIRef`
    """
    print(uri_data)
    pd_uri = "_".join([slugify(token) for token in uri_data])
    return URIRef(f"{NAMESPACES['pd']}{pd_uri}")
