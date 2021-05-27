from rdflib import Graph, RDF, Namespace, Literal, XSD, URIRef, RDFS
from horace.utils import NAMESPACES, create_uri, slugify


METRICAL = Namespace("http://postdata.linhd.uned.es/ontology/postdata-metricalAnalysis#")
KOS = Namespace("http://postdata.linhd.uned.es/kos/")


def add_metrical_elements(_json) -> Graph:
    g = Graph()
    poem_title = _json["poem_title"]
    author = _json["author"]
    dataset = _json["corpus"]

    r_stanza_list = create_uri("SL", poem_title, author, dataset)
    r_line_list = create_uri("LL", poem_title, author, dataset)
    r_redaction = create_uri("R", author, poem_title, dataset)

    # Add type
    g.add((r_stanza_list, RDF.type, METRICAL.StanzaList))
    g.add((r_line_list, RDF.type, METRICAL.LineList))
    # Add redaction to lists
    g.add((r_redaction, METRICAL.hasStanzaList, r_stanza_list))
    g.add((r_redaction, METRICAL.hasLineList, r_line_list))

    for stanza in _json["stanzas"]:
        stanza_number = str(stanza["stanza_number"])
        stanza_text = stanza["stanza_text"]

        r_stanza = create_uri("ST", stanza_number, author, poem_title, dataset)
        # Add Stanza Type
        g.add((r_stanza, RDF.type, METRICAL.Stanza))
        # Add StanzaList to Stanza
        g.add((r_stanza_list, METRICAL.stanza, r_stanza))

        # Add Stanza DP
        g.add((r_stanza, METRICAL.content, Literal(stanza_text, lang="es")))
        g.add((r_stanza, METRICAL.stanzaNumber,
               Literal(stanza_number, datatype=XSD.nonNegativeInteger)))

        # Check for Stanza type
        # Key for stanza type
        if "stanza_type" in stanza.keys():
            if stanza["stanza_type"] is not None:
                s_type = stanza["stanza_type"]
                r_stype = URIRef(KOS + slugify(s_type))
                g.add((r_stanza, METRICAL.typeOfStanza, r_stype))
                g.add((r_stype, RDFS.label, Literal(s_type)))

        for line in stanza["lines"]:
            line_number = str(line["line_number"])
            line_text = line["line_text"]

            r_line = create_uri("L", line_number, stanza_number, author, poem_title,
                                  dataset)
            # Add line type
            g.add((r_line, RDF.type, METRICAL.Line))
            # Add line to stanza
            g.add((r_stanza, METRICAL.hasLine, r_line))
            # Add line to line list
            g.add((r_line_list, METRICAL.line, r_line))
            # Add line DP
            g.add((r_line, METRICAL.content, Literal(line_text, lang="es")))
            g.add((r_line, METRICAL.lineNumber,
                   Literal(line_number, datatype=XSD.nonNegativeInteger)))

            if "words" in line.keys():
                for i, word in enumerate(line["words"]):
                    word_number = str(i)
                    word_text = word["word_text"]

                    r_word = create_uri("W", word_number, line_number, stanza_number,
                                          author, poem_title, dataset)
                    # Add word type
                    g.add((r_word, RDF.type, METRICAL.Word))
                    # Add line to word
                    g.add((r_line, METRICAL.hasWord, r_word))
                    # Add Word DP
                    g.add((r_word, METRICAL.content, Literal(word_text, lang="es")))
                    g.add((r_word, METRICAL.wordNumber,
                           Literal(word_number, datatype=XSD.nonNegativeInteger)))

                    if "syllables" in word.keys():
                        for i, syllable in enumerate(word["syllables"]):
                            syllable_number = str(i)
                            r_syllable = create_uri("SY", syllable_number,
                                                          word_number, line_number,
                                                          stanza_number, author,
                                                          poem_title, dataset)
                            # Add Syllable type
                            g.add((r_syllable, RDF.type, METRICAL.GrammaticalSyllable))
                            # Add Syllable to word
                            g.add((r_word, METRICAL.hasGrammaticalSyllable, r_syllable))
                            # Add Syllable DP
                            g.add((r_syllable, METRICAL.syllableNumber,
                                   Literal(syllable_number,
                                           datatype=XSD.nonNegativeInteger)))
                            g.add((r_syllable, METRICAL.content, Literal(syllable,
                                                                         datatype=XSD.nonNegativeInteger)))
    return g
