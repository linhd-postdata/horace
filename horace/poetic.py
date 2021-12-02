from rantanplan.core import format_stress
from rdflib import Graph, RDF, Namespace, Literal, XSD, URIRef, RDFS

from utils import create_uri, slugify, NAMESPACES
import time

from jollyjumper import get_enjambment

POETIC = Namespace(NAMESPACES["pdp"])
CORE = Namespace("http://postdata.linhd.uned.es/ontology/postdata-core#")
KOS = Namespace("http://postdata.linhd.uned.es/kos/")
SKOS = Namespace(NAMESPACES["skos"])


def add_metrical_elements(_json) -> Graph:
    g = Graph()
    poem_title = _json["poem_title"]
    author = _json["author"]
    dataset = _json["corpus"]

    f_time = str(time.time())
    stamp = f_time[0:10] + f_time[11:]

    # Redaction resource
    r_redaction = create_uri("R", author, poem_title, dataset)
    g.add((r_redaction, RDF.type, CORE.Redaction))

    annotation_author = "UNKNOWN"

    if "stanzas" in _json.keys():
        # Add manual annotation event
        r_event_scansion = create_uri("SP", author, poem_title, dataset, stamp)
        g.add((r_event_scansion, RDF.type, POETIC.ScansionProcess))
        # Add scansion class
        r_scansion = create_uri("SC", author, poem_title, dataset, stamp)
        g.add((r_scansion, RDF.type, POETIC.Scansion))
        # Scansion used redaction
        g.add((r_event_scansion, POETIC.usedAsInput, r_redaction))
        g.add((r_redaction, POETIC.wasInputFor, r_event_scansion))
        # Scansion event generated scansion
        g.add((r_event_scansion, POETIC.generated, r_scansion))
        g.add((r_scansion, POETIC.isGeneratedBy, r_event_scansion))
        # Type of scansion
        r_concept_manual_scansion = URIRef(KOS + "ManualAnnotation")
        g.add((r_scansion, POETIC.typeOfScansion, r_concept_manual_scansion))
        g.add((r_concept_manual_scansion, RDFS.label,
               Literal("Manual Annotation")))

        # TODO- Include the agent of the manual annotation
        r_agent_role = create_uri("AR", author, poem_title, dataset, stamp)
        g.add((r_event_scansion, CORE.hasAgentRole, r_agent_role))
        g.add((r_agent_role, CORE.isAgentRoleOf, r_event_scansion))
        r_agent = create_uri("A", annotation_author)
        g.add((r_agent, CORE.name, Literal(annotation_author)))
        r_role_function = URIRef(KOS + slugify("ManualAnnotator"))
        g.add((r_agent_role, CORE.roleFunction, r_role_function))
        g.add((r_role_function, RDFS.label, Literal("Manual Annotator")))

        # Add stanza list
        r_stanza_list = create_uri("SL", poem_title, author, dataset, stamp)
        g.add((r_stanza_list, RDF.type, POETIC.StanzaList))
        g.add((r_stanza_list, POETIC.numberOfStanzas, Literal(len(_json["stanzas"]))))

        # Include stanza list to scansion process
        g.add((r_scansion, POETIC.hasListAnnotation, r_stanza_list))
        g.add((r_stanza_list, POETIC.isListAnnotatedBy, r_scansion))

        # Add stanza list to scansion
        g.add((r_scansion, POETIC.hasStanzaList, r_stanza_list))
        g.add((r_stanza_list, POETIC.isStanzaListof, r_scansion))

        n_absolute_lines = 0
        for st_i, stanza in enumerate(_json["stanzas"]):
            stanza_number = str(stanza["stanza_number"])
            stanza_text = stanza["stanza_text"]

            # Create stanza
            r_stanza = create_uri("ST", stanza_number, author, poem_title, dataset, stamp)
            # Add Stanza Type
            g.add((r_stanza, RDF.type, POETIC.Stanza))
            # Add Stanza to stanza list
            g.add((r_stanza_list, POETIC.stanza, r_stanza))
            g.add((r_stanza, POETIC.stanzaList, r_stanza_list))
            # Add Stanza to scansion
            g.add((r_scansion, POETIC.hasStanza, r_stanza))
            g.add((r_stanza, POETIC.isStanzaOf, r_scansion))

            # First, last, next, previous
            if st_i == 0:
                g.add((r_stanza_list, POETIC.firstStanza, r_stanza))
                g.add((r_stanza, POETIC.firstStanzaOf, r_stanza_list))
            elif st_i == len(_json["stanzas"]) - 1:
                g.add((r_stanza_list, POETIC.lastStanza, r_stanza))
                g.add((r_stanza, POETIC.lastStanzaOf, r_stanza_list))
            if st_i < len(_json["stanzas"]) - 2:
                next_st = create_uri("ST", str(st_i + 1), author, poem_title, dataset, stamp)
                g.add((r_stanza, POETIC.nextStanza, next_st))
            if st_i > 0:
                prev_st = create_uri("ST", str(st_i - 1), author, poem_title, dataset, stamp)
                g.add((r_stanza, POETIC.previousStanza, prev_st))

            # Add Stanza DP
            g.add((r_stanza, POETIC.content, Literal(stanza_text)))
            g.add((r_stanza, POETIC.stanzaNumber,
                   Literal(stanza_number, datatype=XSD.nonNegativeInteger)))

            # Check for Stanza type
            # Key for stanza type
            if "stanza_type" in stanza.keys():
                if stanza["stanza_type"] is not None:
                    s_type = stanza["stanza_type"]
                    r_stype = URIRef(KOS + slugify(s_type))
                    g.add((r_stanza, POETIC.typeOfStanza, r_stype))
                    g.add((r_stype, RDFS.label, Literal(s_type)))

            if "lines" in stanza.keys():
                # Create line list
                r_line_list = create_uri("LL", poem_title, author, dataset, str(st_i), stamp)
                # Add LineList type
                g.add((r_line_list, RDF.type, POETIC.LineList))
                g.add((r_line_list, POETIC.numberOfLines, Literal(len(stanza["lines"]))))
                # Add line list to scansion
                g.add((r_scansion, POETIC.hasListAnnotation, r_line_list))
                g.add((r_line_list, POETIC.isListAnnotationOf, r_scansion))

                for l_i, line in enumerate(stanza["lines"]):
                    line_number = str(line["line_number"])
                    line_text = line["line_text"]

                    r_line = create_uri("L", line_number, stanza_number, author, poem_title,
                                          dataset, stamp)
                    # Add line type
                    g.add((r_line, RDF.type, POETIC.Line))
                    # Add line to stanza
                    g.add((r_stanza, POETIC.hasLine, r_line))
                    g.add((r_line, POETIC.isLineOf, r_stanza))
                    # Add line to line list
                    g.add((r_line_list, POETIC.line, r_line))
                    g.add((r_line, POETIC.lineList, r_line_list))

                    if l_i == 0:
                        g.add((r_line_list, POETIC.firstLine, r_line))
                        g.add((r_line, POETIC.firstLineOf, r_line_list))
                    elif l_i == len(stanza["lines"]) - 1:
                        g.add((r_line_list, POETIC.lastLine, r_line))
                        g.add((r_line, POETIC.lastLineOf, r_line_list))
                    if st_i < len(stanza["lines"]) - 2:
                        next_l = create_uri("L", str(l_i + 1), stanza_number, author, poem_title,
                                          dataset, stamp)
                        g.add((r_line, POETIC.nextLine, next_l))
                    if st_i > 0:
                        prev_l = create_uri("L", str(l_i - 1), stanza_number, author, poem_title,
                                          dataset, stamp)
                        g.add((r_line, POETIC.previousLine, prev_l))

                    # Add line DP
                    g.add((r_line, POETIC.content, Literal(line_text)))
                    g.add((r_line, POETIC.relativeLineNumber,
                           Literal(line_number, datatype=XSD.nonNegativeInteger)))
                    g.add((r_line, POETIC.absoluteLineNumber,
                           Literal(n_absolute_lines, datatype=XSD.nonNegativeInteger)))

                    n_absolute_lines += 1

                    if "words" in line.keys():
                        # Create word list
                        r_word_list = create_uri("WL", stanza_number, line_number, author, poem_title, dataset, stamp)
                        g.add((r_word_list, RDF.type, POETIC.WordList))
                        g.add((r_word_list, POETIC.numberOfWords, Literal(len(line["words"]))))
                        # Add Word list to line
                        g.add((r_line, POETIC.hasWordList, r_word_list))
                        g.add((r_word_list, POETIC.isWordListOf, r_line))
                        # Add Word List to scansion
                        g.add((r_scansion, POETIC.hasListAnnotation, r_word_list))
                        g.add((r_word_list, POETIC.isListAnnotationOf,
                               r_scansion))

                        for w_i, word in enumerate(line["words"]):
                            word_number = str(w_i)
                            word_text = word["word_text"]

                            r_word = create_uri("W", word_number, line_number, stanza_number,
                                                  author, poem_title, dataset, stamp)
                            # Add word type
                            g.add((r_word, RDF.type, POETIC.Word))
                            # Add line to word
                            g.add((r_line, POETIC.hasWord, r_word))
                            g.add((r_word, POETIC.isWordOf, r_line))
                            # Add Word DP
                            g.add((r_word, POETIC.content, Literal(word_text)))
                            g.add((r_word, POETIC.wordNumber,
                                   Literal(word_number, datatype=XSD.nonNegativeInteger)))

                            # Add Word to word list
                            g.add((r_word_list, POETIC.word, r_word))
                            g.add((r_word, POETIC.wordList, r_word_list))

                            if w_i == 0:
                                g.add((r_word_list, POETIC.firstWord, r_word))
                                g.add((r_word, POETIC.firstWordOf, r_word_list))
                            elif w_i == len(line["words"]) - 1:
                                g.add((r_word_list, POETIC.lastWord, r_word))
                                g.add((r_word, POETIC.lastWordOf, r_word_list))

                            if l_i < len(line["words"]) - 2:
                                next_word = create_uri("W", word_number, str(l_i + 1), stanza_number,
                                                  author, poem_title, dataset, stamp)
                                g.add((r_word, POETIC.nextWord, next_word))
                            if l_i > 0:
                                prev_word = create_uri("W", word_number, str(l_i - 1), stanza_number,
                                author, poem_title, dataset, stamp)
                                g.add(
                                    (r_word, POETIC.previousWord, prev_word))

                            if "syllables" in word.keys():
                                # Create syllable list
                                r_syllable_list = create_uri("GSL", stanza_number, line_number, author, poem_title, dataset, stamp)
                                g.add((r_syllable_list, RDF.type, POETIC.GrammaticalSyllableList))
                                g.add((r_syllable_list, POETIC.numberOfGrammaticalSyllables, Literal(len(word["syllables"]))))
                                # Add Syllable List to Line
                                g.add((r_line, POETIC.hasGrammaticalSyllableList, r_syllable_list))
                                g.add((r_syllable_list,
                                       POETIC.isGrammaticalSyllableListOf,
                                       r_line))
                                # Add Syllable List to Scansion
                                g.add((r_scansion, POETIC.hasListAnnotation, r_syllable_list))

                                for s_i, syllable in enumerate(word["syllables"]):
                                    syllable_number = str(s_i)
                                    r_syllable = create_uri("GSY", syllable_number,
                                                                  word_number, line_number,
                                                                  stanza_number, author,
                                                                  poem_title, dataset, stamp)
                                    # Add Syllable type
                                    g.add((r_syllable, RDF.type, POETIC.GrammaticalSyllable))
                                    # Add Syllable to word
                                    g.add((r_word, POETIC.hasGrammaticalSyllable, r_syllable))
                                    g.add((r_syllable,
                                           POETIC.isGrammaticalSyllableOf,
                                           r_syllable))
                                    # Add Syllable DP
                                    g.add((r_syllable, POETIC.grammaticalSyllableNumber,
                                           Literal(syllable_number,
                                                   datatype=XSD.nonNegativeInteger)))
                                    g.add((r_syllable, POETIC.content, Literal(syllable,
                                                                               datatype=XSD.string)))
                                    # Add Syllable to list
                                    g.add((r_syllable_list, POETIC.grmmaticalSyllable, r_syllable))
                                    g.add((r_syllable,
                                           POETIC.grmmaticalSyllableList,
                                           r_syllable_list))

                                    if s_i == 0:
                                        g.add((r_syllable_list, POETIC.firstGrammaticalSyllable, r_syllable))
                                        g.add((r_syllable, POETIC.firstGrammaticalSyllableOf, r_syllable_list))
                                    elif s_i == len(word["syllables"]) - 1:
                                        g.add((r_syllable_list, POETIC.lastGrammaticalSyllable, r_syllable))
                                        g.add((r_syllable, POETIC.lastGrammaticalSyllableOf, r_syllable_list))

                                    if s_i < len(word["syllables"]) - 2:
                                        next_syl = create_uri("GSY", str(s_i + 1),
                                                                  word_number, line_number,
                                                                  stanza_number, author,
                                                                  poem_title, dataset, stamp)
                                        g.add((r_syllable, POETIC.nextGrammaticalSyllable, next_syl))
                                    if s_i > 0:
                                        prev_syl = create_uri("GSY", str(s_i - 1),
                                                                  word_number, line_number,
                                                                  stanza_number, author,
                                                                  poem_title, dataset, stamp)
                                        g.add((r_syllable, POETIC.previousGrammaticalSyllable, prev_syl))

    return g


def add_rantanplan_elements(scansion, poem_title, author, dataset, enjambments) -> Graph:
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

    # Create Scansion process
    r_event_scansion = create_uri("SP", author, poem_title, dataset, stamp)
    g.add((r_event_scansion, RDF.type, POETIC.ScansionProcess))
    # Associate agent to scansion process
    r_rantanplan_agent = URIRef(KOS + "Rantanplan")
    g.add((r_rantanplan_agent, RDFS.label, Literal("Rantanplan v.0.6.0")))
    g.add((r_rantanplan_agent, RDFS.seeAlso,
           URIRef("https://github.com/linhd-postdata/rantanplan")))
    g.add((r_event_scansion, POETIC.hasAgent, r_rantanplan_agent))
    g.add((r_rantanplan_agent, POETIC.isAgentOf, r_event_scansion))
    r_spanish_syll = URIRef(KOS + "CompleteSpanishSyllabification")
    g.add((r_event_scansion, POETIC.employedTechnique, r_spanish_syll))
    g.add((r_spanish_syll, RDFS.label, Literal("Complete Spanish Syllabification")))
    # Scansion created by scansion process
    r_scansion = create_uri("SC", author, poem_title, dataset, stamp)
    g.add((r_scansion, RDF.type, POETIC.Scansion))
    g.add((r_event_scansion, POETIC.generated, r_scansion))
    g.add((r_scansion, POETIC.isGeneratedBy, r_event_scansion))
    # Type of scansion
    r_concept_auto_scansion = URIRef(KOS + slugify("AutomaticScansion"))
    g.add((r_scansion, POETIC.typeOfScansion, r_concept_auto_scansion))
    g.add((r_concept_auto_scansion, RDFS.label, Literal("Automatic Scansion")))

    # Resources
    r_redaction = create_uri("R", author, poem_title, dataset)
    r_stanza_list = create_uri("SL", poem_title, author, dataset, stamp)

    # Scansion used redaction
    g.add((r_event_scansion, POETIC.usedAsInput, r_redaction))
    g.add((r_redaction, POETIC.wasInputFor, r_event_scansion))
    # Scansion generated stanza list
    g.add((r_scansion, POETIC.hasListAnnotation, r_stanza_list))
    g.add((r_stanza_list, POETIC.isListAnnotationOf, r_scansion))

    # Add types
    g.add((r_redaction, RDF.type, CORE.Redaction))
    g.add((r_stanza_list, RDF.type, POETIC.StanzaList))
    # Add stanza list to scansion
    g.add((r_scansion, POETIC.hasStanzaList, r_stanza_list))
    g.add((r_stanza_list, POETIC.isStanzaListOf, r_scansion))

    # Add number of stanzas
    g.add((r_stanza_list, POETIC.numberOfStanzas, Literal(len(scansion))))

    line_count = 0
    syllable_count = 0
    structure = None

    # Iterate over stanzas
    for st_index, stanza in enumerate(scansion):
        st_index = str(st_index)
        stanza_text = join_lines(stanza)
        r_stanza = create_uri("ST", st_index, author, poem_title, dataset, stamp)
        r_stanza_pattern = create_uri("SP", st_index, author, poem_title,
                                      dataset, stamp)
        # Add Stanza Type
        g.add((r_stanza, RDF.type, POETIC.Stanza))
        g.add((r_stanza_pattern, RDF.type, POETIC.StanzaPattern))
        # Add Stanza to StanzaList
        g.add((r_stanza_list, POETIC.stanza, r_stanza))
        g.add((r_stanza, POETIC.stanzaList, r_stanza_list))
        # Add Stanza to scansion
        g.add((r_scansion, POETIC.hasStanza, r_stanza))
        g.add((r_stanza, POETIC.isStanzaOf, r_scansion))

        # Add StanzaPattern to Stanza
        g.add((r_stanza, POETIC.hasStanzaPattern, r_stanza_pattern))
        g.add((r_stanza_pattern, POETIC.isStanzaPatternOf, r_stanza))
        # Add StanzaPattern to Scansion
        g.add((r_scansion, POETIC.hasPatternAnnotation, r_stanza_pattern))
        g.add((r_stanza_pattern, POETIC.isPatternAnnotationOf, r_scansion))

        # Add Stanza DP
        g.add((r_stanza, POETIC.content, Literal(stanza_text)))
        g.add((r_stanza, POETIC.stanzaNumber,
               Literal(st_index, datatype=XSD.nonNegativeInteger)))
        # Add Stanza pattern DP
        g.add((r_stanza_pattern, POETIC.rhymeScheme,
               Literal(get_rhyme_pattern(stanza))))

        # Add first and last stanzas to list - Previous and Next Stanzas
        if int(st_index) == 0:
            g.add((r_stanza_list, POETIC.firstStanza, r_stanza))
            g.add((r_stanza, POETIC.firstStanzaoF, r_stanza_list))
        else:
            prev_st_index = int(st_index) - 1
            g.add((r_stanza, POETIC.previousStanza,
                   create_uri("ST", str(prev_st_index), author, poem_title,
                              dataset, stamp)))
        if int(st_index) + 1 == len(scansion):
            g.add((r_stanza_list, POETIC.lastStanza, r_stanza))
            g.add((r_stanza, POETIC.lastStanzaOf, r_stanza_list))
        else:
            next_st_index = int(st_index) + 1
            g.add((r_stanza, POETIC.nextStanza,
                   create_uri("ST", str(next_st_index), author, poem_title,
                              dataset, stamp)))

        # Create line list and add type
        r_line_list = create_uri("LL", poem_title, author, dataset, str(st_index), stamp)
        g.add((r_line_list, RDF.type, POETIC.LineList))
        g.add((r_line_list, POETIC.numberOfLines, Literal(len(stanza))))
        # Add line list to scansion
        g.add((r_scansion, POETIC.hasListAnnotation, r_line_list))
        g.add((r_line_list, POETIC.isListAnnotationOf, r_scansion))
        # Add line list to stanza
        g.add((r_stanza, POETIC.hasLineList, r_line_list))
        g.add((r_line_list, POETIC.isLineListOf, r_stanza))

        # Print rhymes in the poem
        # rhymes = [(line["rhythm"], line["rhyme"]) for line in stanza]
        # rhymes = [line for line in stanza]
        # print(rhymes)
        # for l_index, line in enumerate(stanza):
            # print("RHYMES FOR LINE # ", l_index, "   ----   ", line["rhythm"], line["rhyme"])

        ### ADD ENJAMBMENTS ###



        #### ENJAMBMENTS ###


        ### ADD RHYMES ###
        rhymes_list = [(get_last_word_index(line["tokens"]), line["rhyme"], line["rhyme_type"], line["ending"], line_index) for line_index, line in enumerate(stanza)]
        # Add rhyme info - last Word of Line, add Rhyme to the Word URIRef
        for (w_ind, rhyme_label, rhyme_type, rhyme_ending, line_index) in rhymes_list:
            # print(w_ind, rhyme_label, rhyme_type, rhyme_ending, line_index)
            if rhyme_label != "-":
                # Rhyme is denoted by a label
                r_rhyme = create_uri("R", poem_title, author, dataset, rhyme_label, stamp)
                g.add((r_rhyme, RDF.type, POETIC.Rhyme))
                g.add((r_rhyme, POETIC.rhymeLabel, Literal(rhyme_label)))

                r_line = create_uri("L", str(line_count), st_index, author,
                                    poem_title,
                                    dataset, stamp)

                g.add((r_rhyme, RDF.type, POETIC.Rhyme))
                g.add((r_rhyme, POETIC.rhymeLabel, Literal(rhyme_label)))

                # Associate current line to the rhyme (label set x stanza)
                g.add((r_line, POETIC.hasRhyme, r_rhyme))
                g.add((r_rhyme, POETIC.isRhymeOf, r_line))

                # Associate last word of line with the rhyme
                r_rhyming_word = create_uri("W", str(w_ind), str(line_index),
                                            st_index, author, poem_title,
                                            dataset,
                                            stamp)
                g.add((r_rhyme, POETIC.hasRhymingWord, r_rhyming_word))
                g.add((r_rhyming_word, POETIC.isRhymingWordIn, r_rhyme))

                r_word = create_uri("W", str(w_ind), str(line_index),
                                    str(st_index),
                                    author, poem_title, dataset, stamp)
                g.add((r_word, POETIC.ending, Literal(rhyme_ending)))

                # Look for rhyme matchings
                prev_indexes = [i for i in range(0, line_index-1)]
                prev_indexes.reverse()
                prev_objects = [rhymes_list[j] for j in prev_indexes]
                # print("Indexes", line_index, prev_objects)
                # For line in the previous lines of the stanza, look for same label
                for j in prev_objects:
                    if j[1] == rhyme_label:
                        # Create Rhyme match if labels match for a previous line in same stanza
                        prev_word_line_index = j[4]
                        prev_word_index = j[0]

                        r_prev_line = create_uri("L", str(prev_word_line_index), st_index, author,
                                    poem_title,
                                    dataset, stamp)
                        r_prev_word = create_uri("W", str(prev_word_index), str(r_prev_line), str(st_index),
                                        author, poem_title, dataset, stamp)

                        r_next_word = create_uri("W", str(w_ind),
                                                 str(line_index), str(st_index),
                                                 author, poem_title, dataset,
                                                 stamp)

                        r_rhyme_match = create_uri("RM", poem_title, author, dataset, rhyme_label, str(prev_word_line_index), str(line_index), stamp)
                        g.add((r_rhyme_match, RDF.type, POETIC.RhymeMatch))
                        g.add((r_rhyme, POETIC.hasRhymeMatch, r_rhyme_match))
                        g.add((r_rhyme_match, POETIC.isRhymeMatchOf, r_rhyme))

                        g.add((r_rhyme_match, POETIC.rhymeLabel, Literal(rhyme_label)))
                        g.add((r_rhyme_match, POETIC.rhymeEnding, Literal(rhyme_ending)))

                        g.add((r_rhyme_match, POETIC.hasCallWord, r_prev_word))
                        g.add((r_prev_word, POETIC.isCallIn, r_rhyme_match))

                        g.add((r_rhyme_match, POETIC.hasEchoWord, r_next_word))
                        g.add((r_next_word, POETIC.isEchoIn, r_rhyme_match))

                        r_rtype = URIRef(KOS + slugify(rhyme_type))

                        # Add rhyme matching type
                        g.add((r_rhyme_match, POETIC.typeOfRhymeMatching, r_rtype))
                        g.add((r_rtype, RDF.type, SKOS.concept))
                        g.add((r_rtype, RDFS.label, Literal(rhyme_type)))
                        break
        ##### RHYMES END #####

        # Iterate over lines
        for l_index, line in enumerate(stanza):
            l_index = str(l_index)

            # print("LINEA RHYME", line)

            # Create line
            r_line = create_uri("L", str(line_count), st_index, author,
                                poem_title,
                                dataset, stamp)
            # Create lists
            r_word_list = create_uri("WL", l_index, st_index, author,
                                     poem_title,
                                     dataset, stamp)
            r_punctuation_list = create_uri("PL", l_index, st_index, author,
                                            poem_title,
                                            dataset, stamp)
            r_grammatical_list = create_uri("GSL", l_index, st_index, author,
                                            poem_title,
                                            dataset, stamp)
            r_metrical_list = create_uri("MSL", l_index, st_index, author,
                                         poem_title,
                                         dataset, stamp)
            r_line_pattern = create_uri("LP", l_index, st_index, author,
                                        poem_title,
                                        dataset, stamp)

            # Add types
            g.add((r_line, RDF.type, POETIC.Line))
            g.add((r_word_list, RDF.type, POETIC.WordList))
            g.add((r_grammatical_list, RDF.type,
                   POETIC.GrammaticalSyllableList))
            g.add((r_metrical_list, RDF.type, POETIC.MetricalSyllableList))
            g.add((r_line_pattern, RDF.type, POETIC.LinePattern))
            g.add((r_punctuation_list, RDF.type, POETIC.PunctuationList))
            # Add patterns to scansion
            g.add((r_scansion, POETIC.hasPatternAnnotation, r_line_pattern))
            g.add((r_line_pattern, POETIC.isPatternAnnotationOf, r_scansion))
            # Add lists to scansion
            g.add((r_scansion, POETIC.hasListAnnotation, r_word_list))
            g.add((r_word_list, POETIC.isListAnnotationOf, r_scansion))
            g.add((r_scansion, POETIC.hasListAnnotation, r_punctuation_list))
            g.add((r_punctuation_list, POETIC.isListAnnotationOf, r_scansion))
            g.add((r_scansion, POETIC.hasListAnnotation, r_metrical_list))
            g.add((r_metrical_list, POETIC.isListAnnotationOf, r_scansion))
            g.add((r_scansion, POETIC.hasListAnnotation, r_grammatical_list))
            g.add((r_grammatical_list, POETIC.isListAnnotationOf, r_scansion))

            # Add line to stanza - Add first and last lines to stanza
            g.add((r_stanza, POETIC.hasLine, r_line))
            g.add((r_line, POETIC.isLineOf, r_stanza))

            # Add line to line list
            g.add((r_line_list, POETIC.line, r_line))
            g.add((r_line, POETIC.lineList, r_line_list))
            # Add lists to line
            g.add((r_line, POETIC.hasWordList, r_word_list))
            g.add((r_word_list, POETIC.isWordListOf, r_line))
            g.add((r_line, POETIC.hasGrammaticalSyllableList,
                   r_grammatical_list))
            g.add((r_grammatical_list, POETIC.isGramamticalSyllableListOf,
                   r_line))
            g.add((r_line, POETIC.hasMetricalSyllableList, r_metrical_list))
            g.add((r_metrical_list, POETIC.isMetricalSyllableListOf, r_line))

            # Add pattern to line
            g.add((r_line, POETIC.hasLinePattern, r_line_pattern))
            g.add((r_line_pattern, POETIC.isLinePatternOf, r_line))

            # Add Enjambments to the line
            if enjambments.get(line_count):
                # print(enjambments.get(line_count))
                r_enjambment = create_uri("ENJ", str(line_count), st_index, author,
                                poem_title,
                                dataset, stamp)
                g.add((r_enjambment, RDF.type, POETIC.Enjambment))
                g.add((r_enjambment, POETIC.affectsLine, r_line))
                g.add((r_line, POETIC.isLineAffectedBy, r_enjambment))
                enjmb_type = enjambments.get(line_count).get("type")
                r_enjambment_type = URIRef(KOS + slugify(enjmb_type))
                g.add((r_enjambment, POETIC.typeOfEnjambment, r_enjambment_type))
                g.add((r_enjambment_type, RDFS.label, Literal(enjmb_type)))

                # Add enjambment to scansion
                g.add((r_scansion, POETIC.hasDeviceAnnotation, r_enjambment))
                g.add((r_enjambment, POETIC.isDeviceAnnotationOf, r_scansion))

            # Add line DP indexes
            g.add((r_line, POETIC.relativeLineNumber,
                   Literal(l_index, datatype=XSD.nonNegativeInteger)))
            g.add((r_line, POETIC.absoluteLineNumber,
                   Literal(str(line_count), datatype=XSD.nonNegativeInteger)))
            # Add metrical pattern to line pattern
            g.add((r_line_pattern, POETIC.patterningMetricalScheme,
                   Literal(line["rhythm"]["stress"], datatype=XSD.string)))
            # Check for Stanza type
            if not structure and line.get("structure") is not None:
                structure = line["structure"]
                r_stype = URIRef(KOS + slugify(structure))
                g.add((r_stanza_pattern, POETIC.metricalType, r_stype))
                g.add((r_stype, RDFS.label, Literal(structure)))

            if "tokens" not in line:
                continue

            # Add line text
            line_text = join_tokens(line["tokens"])
            g.add((r_line, POETIC.content, Literal(line_text)))
            # Add grammatical pattern to line pattern
            g.add((r_line_pattern, POETIC.grammaticalStressPattern,
                   Literal(get_grammatical_stress_pattern(line["tokens"]),
                           datatype=XSD.string)))

            # Add first last lines to line list - Add previous next Line links
            if line_count == 0:
                g.add((r_line_list, POETIC.firstLine, r_line))
                g.add((r_line, POETIC.firstLineOf, r_line_list))
            else:
                g.add((r_line, POETIC.previousLine,
                       create_uri("L", str(line_count - 1), st_index, author,
                                  poem_title,
                                  dataset, stamp)))
            if int(st_index) + 1 == len(scansion) and int(l_index) + 1 == len(stanza):
                g.add((r_line_list, POETIC.lastLine, r_line))
                g.add((r_line, POETIC.lastLineOf, r_line_list))
            else:
                g.add((r_line, POETIC.nextLine,
                       create_uri("L", str(line_count + 1), st_index, author,
                                  poem_title, dataset, stamp)))

            word_count = 0  # Relative to Line
            punct_count = 0

            # Iterate over words
            for w_index, token in enumerate(line["tokens"]):
                w_index = str(w_index)
                if "symbol" in token:
                    r_punct = create_uri("P", str(punct_count), st_index,
                                         author, poem_title, dataset, stamp)
                    # Add punctuation to line
                    g.add((r_line, POETIC.hasPunctuation, r_punct))
                    g.add((r_punct, POETIC.isPunctuationOf, r_line))
                    # Add punctuation to punctuation list
                    g.add((r_punctuation_list, POETIC.punctuation, r_punct))
                    g.add((r_punct, POETIC.punctuationList, r_punctuation_list))
                    if word_count > 0:
                        r_prev_word = create_uri("W", str(word_count-1), str(l_index),
                                                 str(st_index), author, poem_title,
                                                 dataset, stamp)
                        g.add((r_punct, POETIC.after, r_prev_word))
                    if int(w_index) != len(line["tokens"]):
                        r_next_word = create_uri("W", str(word_count), str(l_index),
                                                 str(st_index), author, poem_title,
                                                 dataset, stamp)
                        g.add((r_punct, POETIC.before, r_next_word))
                    punct_count += 1
                    g.add((r_punct, POETIC.content, Literal(token["symbol"])))
                    continue

                word_text = join_syllables(token)
                # Create word resource
                r_word = create_uri("W", str(word_count), str(l_index), str(st_index),
                                    author, poem_title, dataset, stamp)
                # Add word type
                g.add((r_word, RDF.type, POETIC.Word))
                # Add word to WordList
                g.add((r_word_list, POETIC.word, r_word))
                g.add((r_word, POETIC.wordList, r_word_list))
                # Add word to Line
                g.add((r_line, POETIC.hasWord, r_word))
                g.add((r_word, POETIC.isWordOf, r_line))

                # Add Word DP
                # print("WORD TEXT", word_text, token)
                g.add((r_word, POETIC.content, Literal(word_text)))
                g.add((r_word, POETIC.wordNumber,
                       Literal(word_count, datatype=XSD.nonNegativeInteger)))

                if int(w_index) == 0:
                    g.add((r_word_list, POETIC.firstWord, r_word))
                    g.add((r_word, POETIC.firstWordOf, r_word_list))
                else:
                    prev_w_index = int(w_index) - 1
                    g.add((r_word, POETIC.previousWord,
                           create_uri("W", str(prev_w_index), l_index, st_index,
                                      author, poem_title, dataset, stamp)))
                if int(w_index) + 1 == len(line["tokens"]):
                    g.add((r_word_list, POETIC.lastWord, r_word))
                    g.add((r_word, POETIC.lastWordOf, r_word_list))
                else:
                    next_w_index = int(w_index) + 1
                    g.add((r_word, POETIC.nextWord,
                           create_uri("W", str(next_w_index), l_index, st_index,
                                      author, poem_title, dataset, stamp)))

                # Add Synalepha metaplasm
                # print("TOK", token)
                for syll in token["word"]:
                    # print("SYLL", syll)
                    if "has_synalepha" in syll.keys():
                        if syll["has_synalepha"] == True:
                            r_metaplasm = create_uri("MET-SYN", str(word_count), str(l_index), str(st_index),
                                    author, poem_title, dataset, stamp)
                            # Associate metaplasm to word
                            g.add((r_metaplasm, RDF.type, POETIC.Metaplasm))
                            g.add((r_metaplasm, POETIC.affectsFirstWord, r_word))
                            g.add((r_word, POETIC.isFirstWordAffectedBy, r_metaplasm))
                            # Type of metaplasm
                            r_metaplasm_type = URIRef(KOS + slugify("Synalepha"))
                            g.add((r_metaplasm, POETIC.typeOfMetaplasm, r_metaplasm_type))
                            g.add((r_metaplasm_type, RDFS.label, Literal("Synalepha")))
                            # Add metaplasm to scansion
                            g.add((r_scansion, POETIC.hasDeviceAnnotation, r_metaplasm))
                            g.add((r_metaplasm, POETIC.isDeviceAnnotationOf, r_scansion))

                # Iterate over Grammatical syllables
                for sy_index, syllable in enumerate(token['word']):
                    sy_index = str(sy_index)
                    r_syllable = create_uri("GSY", sy_index, w_index, l_index,
                                            st_index, author, poem_title,
                                            dataset, stamp)
                    # Add Gram Syllable type
                    g.add((r_syllable, RDF.type, POETIC.GrammaticalSyllable))
                    # Add Gram Syllable to line
                    g.add((r_line, POETIC.hasGrammaticalSyllable, r_syllable))
                    g.add((r_syllable, POETIC.isGrammaticalSyllableOf, r_line))
                    # Add Gram Syllable analyses word
                    g.add((r_word, POETIC.isWordAnalysedBy, r_syllable))
                    g.add((r_syllable, POETIC.analysesWord, r_word))
                    # Add Gram Syllable to Gram Syllable List
                    g.add((r_grammatical_list, POETIC.grammaticalSyllable, r_syllable))
                    g.add((r_syllable, POETIC.grammaticalSyllableList,
                           r_grammatical_list))

                    # Add Syllable DP
                    g.add((r_syllable, POETIC.grammaticalSyllableNumber,
                           Literal(syllable_count,
                                   datatype=XSD.nonNegativeInteger)))
                    g.add((r_syllable, POETIC.content,
                           Literal(syllable["syllable"],
                                   datatype=XSD.string)))
                    g.add((r_syllable, POETIC.isStressed,
                           Literal(syllable["is_stressed"],
                                   datatype=XSD.boolean)))
                    # first last previous next Gram Syllable
                    if int(sy_index) == 0 and word_count == 0:
                        g.add((r_grammatical_list,
                               POETIC.firstGrammaticalSyllable, r_syllable))
                        g.add((r_syllable,
                               POETIC.firstGrammaticalSyllableOf, r_grammatical_list))
                    elif int(sy_index) != 0:
                        prev_sy_index = int(sy_index) - 1
                        g.add((r_syllable, POETIC.previousGrammaticalSyllable,
                               create_uri("GSY", str(prev_sy_index), w_index,
                                          l_index, st_index, author, poem_title,
                                          dataset, stamp)))
                    if int(w_index) + 1 == len(line["tokens"]) and int(
                        sy_index) + 1 == len(token["word"]):
                        g.add((r_grammatical_list,
                               POETIC.lastGrammaticalSyllable, r_syllable))
                        g.add((r_syllable,
                               POETIC.lastGrammaticalSyllableOf, r_grammatical_list))
                    else:
                        next_sy_index = int(sy_index) + 1
                        g.add((r_line, POETIC.nextLine,
                               create_uri("GSY", str(next_sy_index), w_index,
                                          l_index, st_index, author, poem_title,
                                          dataset, stamp)))
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

            for msyl_index, msyl in enumerate(line["phonological_groups"]):
                # TODO - Add metricalSyllable content/phoneticTranscription

                metsyll_list_length = len(line["phonological_groups"])

                # Create Met Syllable Resource and add type
                r_metsyll = create_uri("MSY", str(msyl_index), l_index,
                                            st_index, author, poem_title,
                                            dataset, stamp)
                g.add((r_metsyll, RDF.type, POETIC.MetricalSyllable))

                # Add Met Syllable to Met Syllable List
                g.add((r_metrical_list, POETIC.metricalSyllable, r_metsyll))
                g.add((r_metsyll, POETIC.metricalSyllableList, r_metrical_list))

                # Add Met Syllable to Line
                g.add((r_line, POETIC.hasMetricalSyllable, r_metsyll))
                g.add((r_metsyll, POETIC.isMetricalSyllableOf, r_line))
                # Add Met Syllable list to line
                g.add((r_line, POETIC.hasMetricalSyllableList, r_metrical_list))
                g.add((r_metrical_list, POETIC.isMetricalSyllableListOf, r_line))

                # Add DP - Stress and number
                g.add((r_metsyll, POETIC.isStressed,
                       Literal(msyl["is_stressed"],
                               datatype=XSD.boolean)))
                g.add((r_metsyll, POETIC.metricalSyllableNumber,
                       Literal(msyl_index,
                               datatype=XSD.nonNegativeInteger)
                       ))

                # Add first/last to list - Add next and prev links MetSyllables
                if msyl_index == 0:
                    g.add((r_metrical_list, POETIC.firstMetricalSyllable, r_metsyll))
                    g.add((r_metsyll, POETIC.firstMetricalSyllableOf,
                           r_metrical_list))
                elif msyl_index > 0:
                    r_prev_metsyll = create_uri("MSY", str(msyl_index - 1),
                                                 l_index,
                                                 st_index, author, poem_title,
                                                 dataset, stamp)
                    g.add((r_metsyll, POETIC.previousMetricalSyllable, r_prev_metsyll))
                    if msyl_index == metsyll_list_length - 1:
                        g.add((r_metrical_list, POETIC.lastMetricalSyllable,
                               r_metsyll))
                        g.add((r_metsyll, POETIC.lastMetricalSyllableOf,
                               r_metrical_list))
                if msyl_index < metsyll_list_length - 2:
                    r_next_met_syll = create_uri("MSY", str(msyl_index + 1),
                                                 l_index,
                                                 st_index, author,
                                                 poem_title,
                                                 dataset, stamp)
                    g.add((r_metsyll, POETIC.nextMetricalSyllable, r_next_met_syll))

                # if all_gram_syllables_index < metsyll_list_length - 1:
                    if not all_gram_syllables[all_gram_syllables_index]["synalepha"]:
                        r_gram_syll = create_uri("GSY", str(all_gram_syllables_index),
                                                 str(all_gram_syllables[all_gram_syllables_index]["w_number"]),
                                                 l_index, st_index, author, poem_title,
                                                 dataset, stamp)
                        g.add((r_metsyll, POETIC.analysesGrammaticalSyllable, r_gram_syll))
                        g.add((r_gram_syll, POETIC.isGrammaticalSyllableAnalysedBy,
                               r_metsyll))
                    else:
                        r_gram_syll_1 = create_uri("GSY",
                                                 str(all_gram_syllables_index),
                                                 str(all_gram_syllables[
                                                         all_gram_syllables_index][
                                                         "w_number"]), l_index, st_index, author,
                                                 poem_title, dataset, stamp)
                        r_gram_syll_2 = create_uri("GSY",
                                                 str(all_gram_syllables_index + 1),
                                                 str(all_gram_syllables[
                                                         all_gram_syllables_index][
                                                         "w_number"]), l_index, st_index, author,
                                                 poem_title, dataset, stamp)

                        g.add((r_metsyll, POETIC.analysesGrammaticalSyllable, r_gram_syll_1))
                        g.add((r_gram_syll_1, POETIC.isGrammaticalSyllableAnalysedBy,
                               r_metsyll))
                        g.add((r_metsyll, POETIC.analysesGrammaticalSyllable, r_gram_syll_2))
                        g.add((r_gram_syll_2, POETIC.isGrammaticalSyllableAnalysedBy,
                               r_metsyll))
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
