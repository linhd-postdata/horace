from rantanplan.core import format_stress
from rdflib import Graph, RDF, Namespace, Literal, XSD, URIRef, RDFS

from utils import create_uri, slugify, NAMESPACES
import time

METRICAL = Namespace(NAMESPACES["pdm"])
CORE = Namespace("http://postdata.linhd.uned.es/ontology/postdata-core#")
KOS = Namespace("http://postdata.linhd.uned.es/kos/")
SKOS = Namespace(NAMESPACES["skos"])


def add_metrical_elements(_json) -> Graph:
    g = Graph()
    poem_title = _json["poem_title"]
    author = _json["author"]
    dataset = _json["corpus"]

    # Redaction resource
    r_redaction = create_uri("R", author, poem_title, dataset)
    g.add((r_redaction, RDF.type, CORE.Redaction))

    if "stanzas" in _json.keys():
        # Add stanza list
        r_stanza_list = create_uri("SL", poem_title, author, dataset)
        g.add((r_stanza_list, RDF.type, METRICAL.StanzaList))
        # Add stanza list to redaction
        g.add((r_redaction, METRICAL.hasStanzaList, r_stanza_list))
        # Add manual annotation event
        r_event_scansion = create_uri("MSC", author, poem_title, dataset)
        g.add((r_event_scansion, RDF.type, METRICAL.Scansion))
        r_concept_manual_scansion = URIRef(KOS + slugify("ManualAnnotation"))
        g.add((r_event_scansion, METRICAL.employed, r_concept_manual_scansion))
        # Add stanza list to scansion
        g.add((r_event_scansion, METRICAL.generated, r_stanza_list))

        # Add line list
        r_line_list = create_uri("LL", poem_title, author, dataset)
        g.add((r_line_list, RDF.type, METRICAL.LineList))
        g.add((r_redaction, METRICAL.hasLineList, r_line_list))
        # Add line list to scansion event
        g.add((r_event_scansion, METRICAL.generated, r_line_list))

        n_absolute_lines = 0
        for st_i, stanza in enumerate(_json["stanzas"]):
            stanza_number = str(stanza["stanza_number"])
            stanza_text = stanza["stanza_text"]

            r_stanza = create_uri("ST", stanza_number, author, poem_title, dataset)
            # Add Stanza Type
            g.add((r_stanza, RDF.type, METRICAL.Stanza))
            # Add Stanza to stanza list
            g.add((r_stanza_list, METRICAL.stanza, r_stanza))
            # Add Stanza to redaction
            g.add((r_redaction, METRICAL.hasStanza, r_stanza))

            if st_i == 0:
                g.add((r_stanza_list, METRICAL.firstStanza, r_stanza))
                g.add((r_redaction, METRICAL.hasFirstStanza, r_stanza))
            elif st_i == len(_json["stanzas"]) - 1:
                g.add((r_stanza, METRICAL.lastStanza, r_stanza))
                g.add((r_redaction, METRICAL.hasLastStanza, r_stanza))

            if st_i < len(_json["stanzas"]) - 2:
                next_st = create_uri("ST", str(st_i + 1), author, poem_title, dataset)
                g.add((r_stanza, METRICAL.nextStanza, next_st))
            if st_i > 0:
                prev_st = create_uri("ST", str(st_i - 1), author, poem_title, dataset)
                g.add((r_stanza, METRICAL.previousStanza, prev_st))

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

            if "lines" in stanza.keys():
                # Add line list to scansion event
                g.add((r_line_list, RDF.type, METRICAL.LineList))
                g.add((r_event_scansion, METRICAL.generated, r_line_list))
                g.add((r_redaction, METRICAL.hasLineList, r_line_list))

                for l_i, line in enumerate(stanza["lines"]):
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

                    if l_i == 0:
                        g.add((r_stanza, METRICAL.hasFirstLine, r_line))
                    elif l_i == len(stanza["lines"]) - 1:
                        g.add((r_stanza, METRICAL.hasLastLine, r_line))

                    if n_absolute_lines == 0:
                        g.add((r_line_list, METRICAL.firstLine, r_line))
                    elif st_i == len(_json["stanzas"]) - 1 and\
                        l_i == len(stanza["lines"]) - 1:
                        g.add((r_line_list, METRICAL.lastLine, r_line))

                    if st_i < len(stanza["lines"]) - 2:
                        next_l = create_uri("L", str(l_i + 1), stanza_number, author, poem_title,
                                          dataset)
                        g.add((r_line, METRICAL.nextLine, next_l))
                    if st_i > 0:
                        prev_l = create_uri("L", str(l_i - 1), stanza_number, author, poem_title,
                                          dataset)
                        g.add((r_line, METRICAL.previousLine, prev_l))

                    # Add line DP
                    g.add((r_line, METRICAL.content, Literal(line_text, lang="es")))
                    g.add((r_line, METRICAL.relativeLineNumber,
                           Literal(line_number, datatype=XSD.nonNegativeInteger)))
                    g.add((r_line, METRICAL.absoluteLineNumber,
                           Literal(n_absolute_lines, datatype=XSD.nonNegativeInteger)))

                    n_absolute_lines += 1

                    if "words" in line.keys():
                        # Create word list
                        r_word_list = create_uri("WL", stanza_number, line_number, author, poem_title, dataset)
                        g.add((r_word_list, RDF.type, METRICAL.WordList))
                        # Add Word list to line
                        g.add((r_line, METRICAL.hasWordList, r_word_list))
                        # Add Word List to scansion
                        g.add((r_event_scansion, METRICAL.generated, r_word_list))

                        for w_i, word in enumerate(line["words"]):
                            word_number = str(w_i)
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

                            # Add Word to word list
                            g.add((r_word_list, METRICAL.word, r_word))

                            if w_i == 0:
                                g.add((r_word_list, METRICAL.firstWord, r_word))
                                g.add((r_line, METRICAL.hasFirstWord, r_word))
                            elif w_i == len(line["words"]) - 1:
                                g.add((r_word_list, METRICAL.LastWord, r_word))
                                g.add((r_line, METRICAL.hasLastWord, r_word))

                            if l_i < len(line["words"]) - 2:
                                next_word = create_uri("W", word_number, str(l_i + 1), stanza_number,
                                                  author, poem_title, dataset)
                                g.add((r_word, METRICAL.nextWord, next_word))
                            if l_i > 0:
                                prev_word = create_uri("W", word_number, str(l_i - 1), stanza_number,
                                author, poem_title, dataset)
                                g.add(
                                    (r_word, METRICAL.previousWord, prev_word))

                            if "syllables" in word.keys():
                                # Create syllable list
                                r_syllable_list = create_uri("GSL", stanza_number, line_number, author, poem_title, dataset)
                                g.add((r_syllable_list, RDF.type, METRICAL.GrammaticalSyllableList))
                                # Add Syllable List to line
                                g.add((r_line, METRICAL.hasGrammaticalSyllableList, r_syllable_list))
                                # Add Syllable List to Scansion
                                g.add((r_event_scansion, METRICAL.generated, r_syllable_list))

                                for s_i, syllable in enumerate(word["syllables"]):
                                    syllable_number = str(s_i)
                                    r_syllable = create_uri("GSY", syllable_number,
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
                                                                                 datatype=XSD.string)))
                                    # Add Syllable to list
                                    g.add((r_syllable_list, METRICAL.grmmaticalSyllable, r_syllable))

                                    if s_i == 0:
                                        g.add((r_syllable_list, METRICAL.firstGrammaticalSyllable, r_syllable))
                                        g.add((r_word, METRICAL.hasFirstSyllable, r_syllable))
                                    elif s_i == len(word["syllables"]) - 1:
                                        g.add((r_syllable_list, METRICAL.lastGrammaticalSyllable, r_syllable))
                                        g.add((r_word, METRICAL.hasLastSyllable, r_syllable))

                                    if s_i < len(word["syllables"]) - 2:
                                        next_syl = create_uri("GSY", str(s_i + 1),
                                                                  word_number, line_number,
                                                                  stanza_number, author,
                                                                  poem_title, dataset)
                                        g.add((r_syllable, METRICAL.nextGrammaticalSyllable, next_syl))
                                    if s_i > 0:
                                        prev_syl = create_uri("GSY", str(s_i - 1),
                                                                  word_number, line_number,
                                                                  stanza_number, author,
                                                                  poem_title, dataset)
                                        g.add((r_syllable, METRICAL.previousGrammaticalSyllable, prev_syl))

    return g


def add_rantanplan_elements(scansion, poem_title, author, dataset) -> Graph:
    """Function to generate RDF triples from rantanplan scansion output for a
    poem.

    :param scansion: dict with rantanplan output
    :type scansion: dict
    :param poem_title: Title of the poem to be analyzed
    :type poem_title: str
    :param author: Author of the poem to be analyzed
    :type author: str
    :param dataset: Dataset of the poem to be analyzed
    :type dataset: str
    :return: Graph with the RDF triples compliant with
        POSTDATA Metrical Analysis ontology
    :rtype: Graph
    """
    g = Graph()
    # Scansion event
    f_time = str(time.time())
    stamp = f_time[0:10] + f_time[11:]

    r_event_scansion = create_uri("ASC", author, poem_title, dataset, stamp)
    g.add((r_event_scansion, RDF.type, METRICAL.Scansion))
    r_concept_auto_scansion = URIRef(KOS + slugify("AutomaticScansion"))
    g.add((r_event_scansion, METRICAL.employed, r_concept_auto_scansion))

    r_rantanplan_agent = URIRef(KOS + slugify("Rantanplan"))
    g.add((r_rantanplan_agent, RDFS.label, Literal("Rantanplan v.0.6.0")))
    g.add((r_rantanplan_agent, RDFS.seeAlso,
           URIRef("https://github.com/linhd-postdata/rantanplan")))
    g.add((r_event_scansion, CORE.hasAgent, r_rantanplan_agent))
    g.add((r_rantanplan_agent, CORE.isAgentOf, r_event_scansion))

    # Resources
    r_redaction = create_uri("R", author, poem_title, dataset)
    r_stanza_list = create_uri("SL", poem_title, author, dataset)
    r_line_list = create_uri("LL", poem_title, author, dataset)

    # Scansion generated
    g.add((r_event_scansion, CORE.generated, r_stanza_list))
    g.add((r_stanza_list, CORE.wasGeneratedBy, r_event_scansion))
    g.add((r_event_scansion, CORE.generated, r_line_list))
    g.add((r_line_list, CORE.wasGeneratedBy, r_event_scansion))

    # Add types
    g.add((r_redaction, RDF.type, CORE.Redaction))
    g.add((r_stanza_list, RDF.type, METRICAL.StanzaList))
    g.add((r_line_list, RDF.type, METRICAL.LineList))
    # Add lists to redaction
    g.add((r_redaction, METRICAL.hasStanzaList, r_stanza_list))
    g.add((r_redaction, METRICAL.hasLineList, r_line_list))

    line_count = 0
    syllable_count = 0
    structure = None

    # Iterate over stanzas
    for st_index, stanza in enumerate(scansion):
        st_index = str(st_index)
        stanza_text = join_lines(stanza)
        r_stanza = create_uri("ST", st_index, author, poem_title, dataset)
        r_stanza_pattern = create_uri("SP", st_index, author, poem_title,
                                      dataset)
        # Add Stanza Type
        g.add((r_stanza, RDF.type, METRICAL.Stanza))
        g.add((r_stanza_pattern, RDF.type, METRICAL.StanzaPattern))
        # Add Stanza to StanzaList
        g.add((r_stanza_list, METRICAL.stanza, r_stanza))
        # Add Stanza to redaction
        g.add((r_redaction, METRICAL.hasStanza, r_stanza))
        # Add first and last stanzas to redaction
        if int(st_index) == 0:
            g.add((r_redaction, METRICAL.hasFirstStanza, r_stanza))
        if int(st_index) == len(scansion) - 1:
            g.add((r_redaction, METRICAL.hasLastStanza, r_stanza))

        # Add StanzaPattern to Stanza
        g.add((r_stanza, METRICAL.hasStanzaPattern, r_stanza_pattern))

        # Add Stanza DP
        g.add((r_stanza, METRICAL.content, Literal(stanza_text, lang="es")))
        g.add((r_stanza, METRICAL.stanzaNumber,
               Literal(st_index, datatype=XSD.nonNegativeInteger)))
        # Add Stanza DP pattern
        g.add((r_stanza_pattern, METRICAL.rhymeScheme,
               Literal(get_rhyme_pattern(stanza))))

        # Add first and last stanzas to list - Previous and Next Stanzas
        if int(st_index) == 0:
            g.add((r_stanza_list, METRICAL.firstStanza, r_stanza))
        else:
            prev_st_index = int(st_index) - 1
            g.add((r_stanza, METRICAL.previousStanza,
                   create_uri("ST", str(prev_st_index), author, poem_title,
                              dataset)))
        if int(st_index) + 1 == len(scansion):
            g.add((r_stanza_list, METRICAL.lastStanza, r_stanza))
        else:
            next_st_index = int(st_index) + 1
            g.add((r_stanza, METRICAL.nextStanza,
                   create_uri("ST", str(next_st_index), author, poem_title,
                              dataset)))

        # Iterate over lines
        for l_index, line in enumerate(stanza):
            l_index = str(l_index)

            # Create line
            r_line = create_uri("L", str(line_count), st_index, author,
                                poem_title,
                                dataset)
            # Create lists
            r_word_list = create_uri("WL", l_index, st_index, author,
                                     poem_title,
                                     dataset)
            r_punctuation_list = create_uri("PL", l_index, st_index, author,
                                            poem_title,
                                            dataset)
            r_grammatical_list = create_uri("GSL", l_index, st_index, author,
                                            poem_title,
                                            dataset)
            r_metrical_list = create_uri("MSL", l_index, st_index, author,
                                         poem_title,
                                         dataset)
            r_line_pattern = create_uri("LP", l_index, st_index, author,
                                        poem_title,
                                        dataset)

            # Add types
            g.add((r_line, RDF.type, METRICAL.Line))
            g.add((r_word_list, RDF.type, METRICAL.WordList))
            g.add((r_grammatical_list, RDF.type,
                   METRICAL.GrammaticalSyllableList))
            g.add((r_metrical_list, RDF.type, METRICAL.MetricalSyllableList))
            g.add((r_line_pattern, RDF.type, METRICAL.LinePattern))

            # Add line pattern to scansion
            g.add((r_event_scansion, METRICAL.generated, r_line_pattern))
            g.add((r_line_pattern, METRICAL.wasGeneratedBy, r_event_scansion))

            # Add line to stanza - Add first and last lines to stanza
            g.add((r_stanza, METRICAL.hasLine, r_line))
            if int(l_index) == 0:
                g.add((r_stanza, METRICAL.hasFirstLine, r_line))
            if int(l_index) == len(stanza) - 1:
                g.add((r_stanza, METRICAL.hasLastLine, r_line))

            # Add line to line list
            g.add((r_line_list, METRICAL.line, r_line))
            # Add lists to line
            g.add((r_line, METRICAL.hasWordList, r_word_list))
            g.add((r_line, METRICAL.hasGrammaticalSyllableList,
                   r_grammatical_list))
            g.add((r_line, METRICAL.hasMetricalSyllableList, r_metrical_list))
            # Add pattern to line
            g.add((r_line, METRICAL.hasLinePattern, r_line_pattern))

            # Add line DP indexes
            g.add((r_line, METRICAL.relativeLineNumber,
                   Literal(l_index, datatype=XSD.nonNegativeInteger)))
            g.add((r_line, METRICAL.absoluteLineNumber,
                   Literal(str(line_count), datatype=XSD.nonNegativeInteger)))
            # Add metrical pattern to line pattern
            g.add((r_line_pattern, METRICAL.patterningMetricalScheme,
                   Literal(line["rhythm"]["stress"], datatype=XSD.string)))
            # Check for Stanza type
            if not structure and line.get("structure") is not None:
                structure = line["structure"]
                r_stype = URIRef(KOS + slugify(structure))
                g.add((r_stanza_pattern, METRICAL.metricalType, r_stype))
                g.add((r_stype, RDFS.label, Literal(structure)))

                # Add stanza pattern to scansion
                g.add((r_event_scansion, METRICAL.generated, r_stanza_pattern))
                g.add((r_stanza_pattern, METRICAL.wasGeneratedBy, r_event_scansion))

            if "tokens" not in line:
                continue

            # Add line text
            line_text = join_tokens(line["tokens"])
            g.add((r_line, METRICAL.content, Literal(line_text, lang="es")))
            # Add grammatical pattern to line pattern
            g.add((r_line_pattern, METRICAL.grammaticalStressPattern,
                   Literal(get_grammatical_stress_pattern(line["tokens"]),
                           datatype=XSD.string)))

            # Add first last lines to line list - Add previous next Line links
            if line_count == 0:
                g.add((r_line_list, METRICAL.firstLine, r_line))
            else:
                g.add((r_line, METRICAL.previousLine,
                       create_uri("L", str(line_count - 1), st_index, author,
                                  poem_title,
                                  dataset)))
            if int(st_index) + 1 == len(scansion) and int(l_index) + 1 == len(stanza):
                g.add((r_line_list, METRICAL.lastLine, r_line))
            else:
                g.add((r_line, METRICAL.nextLine,
                       create_uri("L", str(line_count + 1), st_index, author,
                                  poem_title, dataset)))

            # Add rhyme info - last Word of Line, add Rhyme to the Word URIRef
            rhyme_label = line["rhyme"]
            rhyme_ending = line["ending"]
            r_rhyme = create_uri("R", rhyme_label, author, poem_title, dataset)
            g.add((r_rhyme, RDF.type, METRICAL.Rhyme))
            g.add((r_rhyme, METRICAL.rhymeLabel, Literal(rhyme_label)))
            g.add((r_rhyme, METRICAL.rhymeGrapheme, Literal(rhyme_ending)))

            # Get last word index
            last_word_index = get_last_word_index(line["tokens"])
            # Add rhyming words
            r_rhyming_word = create_uri("W", str(last_word_index), l_index,
                                        st_index, author, poem_title, dataset)
            g.add((r_rhyme, METRICAL.hasRhymeWord, r_rhyming_word))
            r_rhyme_type = line["rhyme_type"]
            r_rtype = URIRef(KOS + slugify(r_rhyme_type))
            # Add rhyme matching type
            g.add((r_rhyme, METRICAL.presentsRhymeMatching, r_rtype))
            g.add((r_rtype, RDF.type, SKOS.concept))
            word_count = 0  # Relative to Line
            punct_count = 0

            # Add Scansion generated word list
            g.add((r_event_scansion, CORE.generated, r_word_list))
            g.add((r_word_list, CORE.wasGeneratedBy, r_event_scansion))

            # Iterate over words
            for w_index, token in enumerate(line["tokens"]):
                w_index = str(w_index)
                if "symbol" in token:
                    r_punct = create_uri("P", str(punct_count), st_index,
                                         author, poem_title, dataset)
                    g.add((r_punctuation_list, METRICAL.punctuation, r_punct))
                    if word_count > 0:
                        r_prev_word = create_uri("W", str(word_count-1), str(l_index),
                                                 str(st_index), author, poem_title,
                                                 dataset)
                        g.add((r_punct, METRICAL.after, r_prev_word))
                    if int(w_index) != len(line["tokens"]):
                        r_next_word = create_uri("W", str(word_count), str(l_index),
                                                 str(st_index), author, poem_title,
                                                 dataset)
                        g.add((r_punct, METRICAL.before, r_next_word))
                    punct_count += 1
                    continue
                word_text = join_syllables(token)
                # Create word resource
                r_word = create_uri("W", str(word_count), str(l_index), str(st_index),
                                    author, poem_title, dataset)
                # Add word type
                g.add((r_word, RDF.type, METRICAL.Word))
                # Add word to WordList
                g.add((r_word_list, METRICAL.word, r_word))
                # Add word to Line
                g.add((r_line, METRICAL.hasWord, r_word))
                if int(w_index) == 0:
                    g.add((r_line, METRICAL.hasFirstWord, r_word))
                if int(w_index) == len(line["tokens"]) - 1:
                    g.add((r_line, METRICAL.hasLastWord, r_word))
                # Add Word DP
                g.add((r_word, METRICAL.content, Literal(word_text, lang="es")))
                g.add((r_word, METRICAL.wordNumber,
                       Literal(word_count, datatype=XSD.nonNegativeInteger)))
                if int(w_index) == 0:
                    g.add((r_word_list, METRICAL.firstWord, r_word))
                else:
                    prev_w_index = int(w_index) - 1
                    g.add((r_word, METRICAL.previousWord,
                           create_uri("W", str(prev_w_index), l_index, st_index,
                                      author, poem_title, dataset)))
                if int(w_index) + 1 == len(line["tokens"]):
                    g.add((r_word_list, METRICAL.lastWord, r_word))
                else:
                    next_w_index = int(w_index) + 1
                    g.add((r_word, METRICAL.nextWord,
                           create_uri("W", str(next_w_index), l_index, st_index,
                                      author, poem_title, dataset)))

                # Add Gramm syllables list to scansion
                g.add((r_event_scansion, CORE.generated, r_grammatical_list))
                g.add((r_grammatical_list, CORE.wasGeneratedBy, r_event_scansion))

                # Iterate over Grammatical syllables
                for sy_index, syllable in enumerate(token['word']):
                    sy_index = str(sy_index)
                    r_syllable = create_uri("GSY", sy_index, w_index, l_index,
                                            st_index, author, poem_title,
                                            dataset)
                    # Add Gram Syllable type
                    g.add((r_syllable, RDF.type, METRICAL.GrammaticalSyllable))
                    # Add Gram Syllable to word
                    g.add((r_word, METRICAL.hasGrammaticalSyllable, r_syllable))
                    if int(sy_index) == 0:
                        g.add((r_word, METRICAL.hasFirstGrammaticalSyllable, r_syllable))
                    if int(sy_index) == len(token['word']) - 1:
                        g.add((r_word, METRICAL.hasLastGrammaticalSyllable, r_syllable))
                    # Add Gram Syllable to Gram Syllable List
                    g.add((r_grammatical_list, METRICAL.grammaticalSyllable, r_syllable))

                    # Add Syllable DP
                    g.add((r_syllable, METRICAL.grammaticalSyllableNumber,
                           Literal(syllable_count,
                                   datatype=XSD.nonNegativeInteger)))
                    g.add((r_syllable, METRICAL.content,
                           Literal(syllable["syllable"],
                                   datatype=XSD.string)))
                    g.add((r_syllable, METRICAL.isStressed,
                           Literal(syllable["is_stressed"],
                                   datatype=XSD.boolean)))
                    # first last previous next Gram Syllable
                    if int(sy_index) == 0 and word_count == 0:
                        g.add((r_grammatical_list,
                               METRICAL.firstGrammaticalSyllable, r_syllable))
                    elif int(sy_index) != 0:
                        prev_sy_index = int(sy_index) - 1
                        g.add((r_syllable, METRICAL.previousGrammaticalSyllable,
                               create_uri("GSY", str(prev_sy_index), w_index,
                                          l_index, st_index, author, poem_title,
                                          dataset)))
                    if int(w_index) + 1 == len(line["tokens"]) and int(
                        sy_index) + 1 == len(token["word"]):
                        g.add((r_grammatical_list,
                               METRICAL.lastGrammaticalSyllable, r_syllable))
                    else:
                        next_sy_index = int(sy_index) + 1
                        g.add((r_line, METRICAL.nextLine,
                               create_uri("GSY", str(next_sy_index), w_index,
                                          l_index, st_index, author, poem_title,
                                          dataset)))
                    syllable_count += 1
                word_count += 1

            # Variables to include analyses link
            all_gram_syllables = []
            for w_ind, token in enumerate(line["tokens"]):
                # print(token)
                if "symbol" in token.keys():
                    continue
                for s_ind, syll in enumerate(token["word"]):
                    if "has_synalepha" in syll.keys() and syll["has_synalepha"] == True:
                        all_gram_syllables.append({"w_number": w_ind,
                                                   "s_number": s_ind,
                                                   "synalepha": True,
                                                   "is_stressed": syll["is_stressed"]})
                    else:
                        all_gram_syllables.append({"w_number": w_ind,
                                                   "s_number": s_ind,
                                                   "synalepha": False,
                                                   "is_stressed": syll["is_stressed"]})
            all_gram_syllables_index = 0

            # Add Metrical syllables list to scansion
            g.add((r_event_scansion, CORE.generated, r_metrical_list))
            g.add((r_metrical_list, CORE.wasGeneratedBy, r_event_scansion))

            for msyl_index, msyl in enumerate(line["phonological_groups"]):
                metsyll_list_length = len(line["phonological_groups"])

                # Create Met Syllable Resource and add type
                r_metsyll = create_uri("MSY", str(msyl_index), l_index,
                                            st_index, author, poem_title,
                                            dataset)
                g.add((r_metsyll, RDF.type, METRICAL.MetricalSyllable))

                # Add Met Syllable to Met Syllable List
                g.add((r_metrical_list, METRICAL.metricalSyllable, r_metsyll))

                # Add DP - Stress and number
                g.add((r_metsyll, METRICAL.isStressed,
                       Literal(msyl["is_stressed"],
                               datatype=XSD.boolean)))
                g.add((r_metsyll, METRICAL.metricalSyllableNumber,
                       Literal(msyl_index,
                               datatype=XSD.nonNegativeInteger)
                       ))

                # Add first/last to list - Add next and prev links MetSyllables
                if msyl_index == 0:
                    g.add((r_metrical_list, METRICAL.firstMetricalSyllable, r_metsyll))
                elif msyl_index > 0:
                    r_prev_metsyll = create_uri("MSY", str(msyl_index - 1),
                                                 l_index,
                                                 st_index, author, poem_title,
                                                 dataset)
                    g.add((r_metsyll, METRICAL.previousMetricalSyllable, r_prev_metsyll))
                    if msyl_index == metsyll_list_length - 1:
                        g.add((r_metrical_list, METRICAL.lastMetricalSyllable,
                               r_metsyll))
                if msyl_index < metsyll_list_length - 2:
                    r_next_met_syll = create_uri("MSY", str(msyl_index + 1),
                                                 l_index,
                                                 st_index, author,
                                                 poem_title,
                                                 dataset)
                    g.add((r_metsyll, METRICAL.nextMetricalSyllable, r_next_met_syll))

                # if all_gram_syllables_index < metsyll_list_length - 1:
                    if not all_gram_syllables[all_gram_syllables_index]["synalepha"]:
                        r_gram_syll = create_uri("GSY", str(all_gram_syllables_index),
                                                 str(all_gram_syllables[all_gram_syllables_index]["w_number"]),
                                                 l_index, st_index, author, poem_title,
                                                 dataset)
                        g.add((r_metsyll, METRICAL.analyses, r_gram_syll))
                    else:
                        r_gram_syll_1 = create_uri("GSY",
                                                 str(all_gram_syllables_index),
                                                 str(all_gram_syllables[
                                                         all_gram_syllables_index][
                                                         "w_number"]), l_index, st_index, author,
                                                 poem_title, dataset)
                        r_gram_syll_2 = create_uri("GSY",
                                                 str(all_gram_syllables_index + 1),
                                                 str(all_gram_syllables[
                                                         all_gram_syllables_index][
                                                         "w_number"]), l_index, st_index, author,
                                                 poem_title, dataset)

                        g.add((r_metsyll, METRICAL.analyses, r_gram_syll_1))
                        g.add((r_metsyll, METRICAL.analyses, r_gram_syll_2))
                        all_gram_syllables_index += 1

                all_gram_syllables_index += 1

            line_count += 1
    return g


def join_lines(stanza):
    stanza_content = []
    for line in stanza:
        line_text = join_tokens(line["tokens"])
        stanza_content.append(line_text)
    return "\n".join(stanza_content)


def join_tokens(tokens):
    """Join all words from a list of tokens into a string.

    :param tokens: List of dictionaries representing tokens
    :return: String of words
    """
    output = []
    for token in tokens:
        item = join_syllables(token)
        output.append(item)
    return " ".join(output)


def join_syllables(token):
    """Join all symbols and syllables from a list of tokens into a string.

    :param token: List of dictionaries representing tokens
    :return: String of syllables
    """
    if "symbol" in token:
        return token["symbol"]
    else:
        return "".join([syll["syllable"] for syll in token["word"]])


def get_grammatical_stress_pattern(tokens):
    stresses = []
    for token in tokens:
        word = token.get("word")
        if word:
            for syllable in word:
                stresses.append(syllable["is_stressed"])
    return format_stress(stresses, "pattern")


def get_rhyme_pattern(stanza):
    return "".join(line["rhyme"] for line in stanza)


def get_rhymes_lines(stanza):
    rhymes_dict = {}
    for idx, line in enumerate(stanza):
        if line["rhyme"] != "-":
            if rhymes_dict.get(line["rhyme"]):
                rhymes_dict[line["rhyme"]].append(idx)
            else:
                rhymes_dict[line["rhyme"]] = [idx]
    return rhymes_dict


def get_last_word_index(tokens):
    last_word_index = -1
    for token in tokens[::-1]:
        if "word" in token:
            break
        last_word_index -= 1
    return tokens.index(tokens[last_word_index])
