"""Core module."""
from rdflib import Graph, RDF, Literal, DC, URIRef, XSD, Namespace

from horace.utils import create_uri, NAMESPACES

CORE = Namespace(NAMESPACES['pdcore'])
DATES = Namespace(NAMESPACES['pddates'])


def get_core_graph(poem: dict) -> Graph:
    """Transform an Averell poem data dictionary into a :class:`rdflib.Graph`.

    :param poem: Dictionary with an Averell-like poem info
    :type poem: dict
    :return: the generated graph
    :rtype: :class:`rdflib.Graph`
    """
    g = Graph()
    for prefix, uri in NAMESPACES.items():
        g.namespace_manager.bind(prefix, uri)
    # Get poem core data
    title = poem["poem_title"]
    author = poem["author"]
    source = poem["corpus"]
    poem_text = "\n\n".join(
        [stanza["stanza_text"] for stanza in poem["stanzas"]])
    incipit = poem["stanzas"][0]["lines"][0]["line_text"]
    explicit = poem["stanzas"][-1]["lines"][-1]["line_text"]

    # Generate resources uris
    r_redaction = create_uri(onto_class="R", author=author, poem_title=title,
                             source=source)
    r_creator = create_uri(onto_class="CR", author=author, poem_title=title)
    r_poetic_work = create_uri(onto_class="PW", author=author, poem_title=title)
    r_person = create_uri(onto_class="P", author=author)

    # Add Types
    g.add((r_poetic_work, RDF.type, CORE.PoeticWork))
    g.add((r_redaction, RDF.type, CORE.Redaction))
    g.add((r_creator, RDF.type, CORE.CreatorRole))
    g.add((r_person, RDF.type, CORE.Person))

    # Labels
    g.add((r_poetic_work, DC.title, Literal(title, lang="es")))
    g.add((r_poetic_work, CORE.isSong, Literal(False, datatype=XSD.boolean)))
    g.add((r_redaction, DC.title, Literal(title, lang="es")))
    g.add((r_redaction, CORE.text, Literal(poem_text, lang="es")))
    g.add((r_redaction, CORE.incipit, Literal(incipit, lang="es")))
    g.add((r_redaction, CORE.explicit, Literal(explicit, lang="es")))
    g.add((r_person, CORE.name, Literal(author, lang="es")))
    g.add((r_creator, CORE.isAnonymous,
           Literal((True if author == "unknown" else False),
                   datatype=XSD.boolean)))

    # Object Properties
    g.add((r_poetic_work, CORE.isRealisedThrough, r_redaction))
    g.add((r_poetic_work, CORE.hasCreator, r_creator))
    g.add((r_redaction, CORE.hasCreator, r_creator))
    g.add((r_creator, CORE.isRoleOf, r_person))

    if "year" in poem:
        year = poem["year"]
        r_date_entity = create_uri(onto_class="DE", author=author,
                                   poem_title=title)
        r_date = create_uri(onto_class="Y", author=author,
                            poem_title=title, year=year)
        g.add((r_date_entity, RDF.type, DATES.DateEntity))
        g.add((r_date, RDF.type, DATES.ExactDateExpression))
        g.add((r_date, DATES.dateExpressionAsDate,
               Literal(year, datatype=XSD.date)))
        g.add((r_date_entity, DATES.isExpressedAs, r_date))
        g.add((r_date_entity, DATES.certainty,
               URIRef("http://postdata.linhd.uned.es/kos/definitely")))
    return g
