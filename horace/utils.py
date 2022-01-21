from rdflib import URIRef
from slugify import slugify

NAMESPACE_URL_TEMPLATE = ("http://postdata.linhd.uned.es/ontology/"
                          "postdata-{onto}#")

NAMESPACES = {
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "objectrole": "http://www.ontologydesignpatterns.org/cp/owl/objectrole.owl#",
    "obj": "http://www.openrdf.org/rdf/2009/object#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "pdc": NAMESPACE_URL_TEMPLATE.format(onto="core"),
    "pdp": NAMESPACE_URL_TEMPLATE.format(onto="poeticAnalysis"),
    "pd": "http://postdata.linhd.uned.es/resource/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "foaf": "http://xmlns.com/foaf/0.1/",
}

CONTEXT = {
    # "@language": "es",
    "author": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#author"},
    "score": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#score"},
    "name": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#name"},
    "title": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#title"},
    "deathDate": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#deathDate",
                  "@type": "http://www.w3.org/2001/XMLSchema#dateTime"},
    "roleFunction": {
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-core#roleFunction",
        "@type": "@id"},
    "birthDate": {
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-core#birthDate",
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime"},
    "date": {
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-core#date",
        "@type": "http://www.w3.org/2001/XMLSchema#date"},
    "birthPlace": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#birthPlace"},
    "deathPlace": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#deathPlace"},
    "gender": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#gender" },
    "movement": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#movement" },
    "religiousAffiliation": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#religiousAffiliation" },
    "occupation": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#occupation" },
    "portrait": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#portrait" ,
                 "@type": "@id"},
    "works": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#works" },
    "ethnicity": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#ethnicity" },
    "stanzas": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasStanza",
                "@type": "@id"},
    "lines": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasLine",
              "@type": "@id"
              },
    "patterningMetricalScheme": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#patterningMetricalScheme"},
    "rhymeScheme": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#rhymeScheme"},
    "relativeLineNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#relativeLineNumber",
                           "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "absoluteLineNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#absoluteLineNumber",
                           "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "hasPunctuation": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasPunctuation",
                       "@type": "@id",
                       "@container": "@set"},
    "isRealisedThrough": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#isRealisedThrough"},
    "text": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#text"},
    "metricalSyllableList": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasMetricalSyllable",
                            "@type": "@id",
                            "@container": "@set"},
    "wordList": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasWord",
                "@type": "@id",
                "@container": "@set"},
    "grammaticalSyllableList": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasGrammaticalSyllable",
                                "@type": "@id",
                                "@container": "@set"},
    "grammaticalSyllableNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#grammaticalSyllableNumber",
                                  "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "metricalSyllableNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#metricalSyllableNumber",
                               "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "isStressed": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isStressed"},
    "analysesWord": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#analysesWord",
                     "@type": "@id",
                     "@container": "@set"},
    "isGrammaticalSyllableAnalysedBy": {"@id":"http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isGrammaticalSyllableAnalysedBy",
                                        "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
                                        "@container": "@set"},
    "isMetricalSyllableAnalysedBy": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isMetricalSyllableAnalysedBy",
                                     "@type": "@id",
                                     "@container": "@set"},
    "content": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#content"},
    "wordNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#wordNumber",
                   "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "scansions": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-core#scansions"},
    "typeOfScansion": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#typeOfScansion"},
    "employedTechnique": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#employedTechnique",
                          "@type": "@id"},
    "lineList": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#lineList",
                 "@container": "@set"},
    "stanzaList": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#stanzaList",
                   "@container": "@set"},
    "stanzaNumber": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#stanzaNumber",
                     "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"},
    "typeOfRhymeMatching": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#typeOfRhymeMatching"},
    "rhyme": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#rhyme"},
    "rhymeLabel": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#rhymeLabel"},
    "isWordAnalysedBy": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isWordAnalysedBy",
                         "@type": "@id",
                         "@container": "@set"},
    "enjambment": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#enjambment"},
    "affectLine": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#affectLine",
                   "@type": "@id"},
    "typeOfEnjambment": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#typeOfEnjambment"},
    "metaplasm": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#metaplasm"},
    "typeOfMetaplasm": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#typeOfMetaplasm"},
    "affectsFirstWord": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#affectsFirstWord",
                         "@type": "@id"},
    "affectsLine": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#affectsLine",
                    "@type": "@id"},
    "before": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#before",
               "@type": "@id"},
    "after": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#after",
               "@type": "@id"},
    "hasRhymeMatch": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasRhymeMatch",
                "@type": "@id",
                "@container": "@set"},
    "hasEchoLine": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasEchoLine",
                "@type": "@id"},
    "hasCallLine": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasCallLine",
                "@type": "@id"},
    "rhymeGrapheme": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#rhymeGrapheme"},
    "hasEchoWord": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasEchoWord",
                "@type": "@id"},
    "hasCallWord": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#hasCallWord",
                "@type": "@id"},
    "presentsRhyme":{"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#presentsRhyme",
                "@type": "@id"},
    "isRhymePresentAt": { "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isRhymePresentAt",
        "@type": "@id"},
    "isLineAffectedBy": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isLineAffectedBy",
        "@type": "@id"},
    "isFirstWordAffectedBy":{"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isFirstWordAffectedBy",
        "@type": "@id"},
    "id": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#id"},
    "isCallLineIn": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isCallLineIn",
                "@type": "@id"},
    "isEchoLineIn": {"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isEchoLineIn",
                "@type": "@id"},
    "isFirstGrammaticalSyllableAffectedBy": {
            "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isFirstGrammaticalSyllableAffectedBy",
            "@type": "@id"
    },
    "beforeWordNumber": {
            "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#beforeWordNumber",
            "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    },
    "afterWordNumber": {
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#afterWordNumber",
        "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    },
    "callLineNumber":{
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#callLineNumber",
        "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    },
    "echoLineNumber":{
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#echoLineNumber",
        "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    },
    "metaplasms":{
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#isFirsGrammaticalSyllableAffectedBy",
    },
    "metaplasmIndex":{
        "@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#metaplasmIndex",
        "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    },
    "metricalType":{"@id": "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#metricalType"}
}


QUERY = """
PREFIX pdc: <http://postdata.linhd.uned.es/ontology/postdata-core#>
PREFIX pdp: <http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT{
    ?scansion
        pdp:stanzaList ?stanza.

    ?stanza
        pdp:content ?stanza_content;
        pdp:lineList ?line;
        pdp:typeOfStanza ?type_of_stanza;
        pdp:stanzaNumber ?stanza_number;
        pdp:rhymeScheme ?stanza_type;
        pdp:metricalType ?metrical_type.

    ?line
        pdp:patterningMetricalScheme ?patterning_metrical_scheme;
        pdp:relativeLineNumber ?relative_line_number;
        pdp:absoluteLineNumber ?absolute_line_number;
        pdp:content ?line_content.

    # Q2
    ?line pdp:hasWord ?word;
        # pdp:hasGrammaticalSyllable ?gram_syll;
        pdp:hasMetricalSyllable ?met_syll;
        pdp:hasPunctuation ?punctuation;
        pdp:rhymeLabel ?rhyme_label.

    ?line pdp:isEchoLineIn ?rhymeMatch_echo;
        pdp:isCallLineIn ?rhymeMatch_call.

    ?rhymeMatch_call pdp:rhymeGrapheme ?rhyme_grapheme_call;
        pdp:typeOfRhymeMatching ?rhyme_matching_type_call;
        pdp:echoLineNumber ?echo_line_number.
    #    pdp:hasEchoLine ?echo_line.
    # ?echo_line pdp:relativeLineNumber ?echo_line_number.

    ?rhymeMatch_echo pdp:rhymeGrapheme ?rhyme_grapheme_echo;
        pdp:typeOfRhymeMatching ?rhyme_matching_type_echo;
        pdp:callLineNumber ?call_line_number.
    #     pdp:hasCallLine ?call_line.
    # ?call_line pdp:relativeLineNumber ?call_line_number.

    ?punctuation pdp:content ?punctuation_content;
        pdp:beforeWordNumber ?before_word_number;
        pdp:afterWordNumber ?after_word_number.

    ?word pdp:content ?word_content;
        pdp:isWordAnalysedBy ?word_unit;
        pdp:wordNumber ?word_number.

    ?gram_syll pdp:grammaticalSyllableNumber ?gram_syll_number;
        pdp:isStressed ?is_stressed_g;
        pdp:content ?gram_syll_text;
        # pdp:isGrammaticalSyllableAnalysedBy ?gram_syll_unit.
        pdp:isGrammaticalSyllableAnalysedBy ?gram_syll_unit_number.

    ?met_syll pdp:metricalSyllableNumber ?met_syll_number;
        pdp:isStressed ?is_stressed_m;
        pdp:content ?met_syll_text;
        pdp:isMetricalSyllableAnalysedBy ?met_syll_unit. # We don't have this in spanish meter.

    # Add Metaplasm
    # ?scansion pdp:enjambment ?enjambment;
    #    pdp:metaplasm ?metaplasm.

    ?line pdp:isLineAffectedBy ?enjambment.
    ?enjambment pdp:typeOfEnjambment ?type_of_enjambment.

    ?gram_syll pdp:isFirsGrammaticalSyllableAffectedBy ?metaplasm.
    ?metaplasm pdp:typeOfMetaplasm ?type_of_metaplasm;
        pdp:metaplasmIndex ?metaplasm_index.
}

WHERE{
    BIND (<$> AS ?scansion)

    ?scansion a pdp:Scansion;
        pdp:hasStanza ?stanza.

    ?stanza a pdp:Stanza;
        pdp:stanzaNumber ?stanza_number;
        pdp:content ?stanza_content;
        pdp:hasLine ?line.

    OPTIONAL{
        ?stanza pdp:typeOfStanza ?type_of_stanza.
    }
    OPTIONAL{
        ?stanza pdp:metricalType ?mt.
        ?mt rdfs:label ?metrical_type.
    }

    ?line a pdp:Line;
        pdp:relativeLineNumber ?relative_line_number;
        pdp:absoluteLineNumber ?absolute_line_number;
        pdp:content ?line_content;
        pdp:hasWord ?word.

    ?word pdp:wordNumber ?word_number;
        pdp:content ?word_content.

    OPTIONAL{
        ?word pdp:isWordAnalysedBy ?word_unit.
    }

    # OPTIONAL{
    #     ?word pdp:isFirstWordAffectedBy ?metaplasm.
    #     ?metaplasm pdp:typeOfMetaplasm ?mtp_type.
    #     ?mtp_type rdfs:label ?type_of_metaplasm.
    # }

    OPTIONAL{
        ?line pdp:hasGrammaticalSyllable ?gram_syll.
        ?gram_syll pdp:grammaticalSyllableNumber ?gram_syll_number.
    }
    OPTIONAL{
            ?gram_syll pdp:isStressed ?is_stressed_g.
    }
    OPTIONAL{
            ?gram_syll pdp:content ?gram_syll_text.
    }
    OPTIONAL{
            ?gram_syll pdp:isGrammaticalSyllableAnalysedBy ?gram_syll_unit.
            ?gram_syll_unit pdp:metricalSyllableNumber ?gram_syll_unit_number.
    }

    OPTIONAL{
            ?line pdp:isLineAffectedBy ?enjambment.
            ?enjambment pdp:typeOfEnjambment ?enj_type.
            ?enj_type rdfs:label ?type_of_enjambment.
        }

    OPTIONAL{
        ?line pdp:hasMetricalSyllable ?met_syll.
        ?met_syll pdp:isStressed ?is_stressed_m;
            pdp:metricalSyllableNumber ?met_syll_number;
            pdp:phoneticTranscription ?met_syll_text.
    }

    OPTIONAL{
        ?line pdp:hasPunctuation ?punctuation.
        ?punctuation pdp:content ?punctuation_content.
        OPTIONAL{
            ?punctuation pdp:before ?before_word.
            ?before_word pdp:wordNumber ?before_word_number.
        }
        OPTIONAL{
            ?punctuation pdp:after ?after_word.
            ?after_word pdp:wordNumber ?after_word_number.
        }
    }

    OPTIONAL{
        ?line pdp:presentsRhyme ?rhyme.
        ?rhyme pdp:rhymeLabel ?rhyme_label.
    }

    OPTIONAL{
        ?line pdp:isEchoLineIn ?rhymeMatch_echo.
        ?rhymeMatch_echo pdp:rhymeGrapheme ?rhyme_grapheme_echo;
            pdp:typeOfRhymeMatching ?rmte;
            pdp:hasCallLine ?call_line.
        ?rmte rdfs:label ?rhyme_matching_type_echo.
        ?call_line pdp:absoluteLineNumber ?call_line_number.
    }

    OPTIONAL{
        ?line pdp:isCallLineIn ?rhymeMatch_call.
        ?rhymeMatch_call pdp:rhymeGrapheme ?rhyme_grapheme_call;
            pdp:typeOfRhymeMatching ?rmtc;
            pdp:hasEchoLine ?echo_line.
        ?rmtc rdfs:label ?rhyme_matching_type_call.
        ?echo_line pdp:absoluteLineNumber ?echo_line_number.
    }

    OPTIONAL{
        ?line pdp:patterningMetricalScheme ?patterning_metrical_scheme.
    }

    OPTIONAL{
        ?stanza pdp:rhymeScheme ?stanza_type.
    }

    OPTIONAL{
        ?gram_syll pdp:isFirstGrammaticalSyllableAffectedBy ?metaplasm.
        ?metaplasm pdp:typeOfMetaplasm ?tom.
        ?tom rdfs:label ?type_of_metaplasm.
        OPTIONAL{
            ?metaplasm pdp:metaplasmIndex ?metaplasm_index.
        }
    }
}
"""


def create_uri(*uri_data) -> URIRef:
    """Generate a new POSTDATA resources URI

    :param uri_data: Necessary data for building each POSTDATA resources URI
    :return: URIRef object representing the resource
    :rtype: :class:`rdflib.URIRef`
    """
    # print(uri_data)
    pd_uri = "_".join([slugify(token) for token in uri_data])
    return URIRef(f"{NAMESPACES['pd']}{pd_uri}")
