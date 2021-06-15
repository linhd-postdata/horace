from rantanplan.core import format_stress
from rdflib import Graph, RDF, Namespace, Literal, XSD, URIRef, RDFS

from horace.utils import create_uri, slugify, NAMESPACES

METRICAL = Namespace(NAMESPACES["pdm"])
KOS = Namespace("http://postdata.linhd.uned.es/kos/")
SKOS = Namespace(NAMESPACES["skos"])


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


def add_rantanplan_elements(scansion, poem_title, author, dataset) -> Graph:
    g = Graph()
    r_redaction = create_uri("R", author, poem_title, dataset)
    r_stanza_list = create_uri("SL", poem_title, author, dataset)
    r_line_list = create_uri("LL", poem_title, author, dataset)

    # Add type
    g.add((r_stanza_list, RDF.type, METRICAL.StanzaList))
    g.add((r_line_list, RDF.type, METRICAL.LineList))
    # Add lists to redaction
    g.add((r_redaction, METRICAL.hasStanzaList, r_stanza_list))
    g.add((r_redaction, METRICAL.hasLineList, r_line_list))
    line_count = 0
    word_count = 0
    syllable_count = 0
    structure = None
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

        # Add Stanza DP
        g.add((r_stanza, METRICAL.content, Literal(stanza_text, lang="es")))
        g.add((r_stanza, METRICAL.stanzaNumber,
               Literal(st_index, datatype=XSD.nonNegativeInteger)))
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
        # Add StanzaPattern DP
        g.add((r_stanza_pattern, METRICAL.rhymeScheme,
               Literal(get_rhyme_pattern(stanza))))
        for l_index, line in enumerate(stanza):
            l_index = str(l_index)
            r_line = create_uri("L", str(line_count), st_index, author,
                                poem_title,
                                dataset)
            r_word_list = create_uri("WL", l_index, st_index, author,
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
            # Add line type
            g.add((r_line, RDF.type, METRICAL.Line))
            g.add((r_word_list, RDF.type, METRICAL.WordList))
            g.add((r_grammatical_list, RDF.type,
                   METRICAL.GrammaticalSyllableList))
            g.add((r_metrical_list, RDF.type, METRICAL.MetricalSyllableList))
            g.add((r_line_pattern, RDF.type, METRICAL.LinePattern))
            # Add line to stanza
            g.add((r_stanza, METRICAL.hasLine, r_line))
            # Add line to line list
            g.add((r_line_list, METRICAL.line, r_line))
            # Add lists to line
            g.add((r_line, METRICAL.hasWordList, r_word_list))
            g.add((r_line, METRICAL.hasGrammaticalSyllableList,
                   r_grammatical_list))
            g.add((r_line, METRICAL.hasMetricalSyllableList, r_metrical_list))
            # Add pattern to line
            g.add((r_line, METRICAL.hasPattern, r_line_pattern))
            # Add line DP
            g.add((r_line, METRICAL.indexInStanza,
                   Literal(l_index, datatype=XSD.nonNegativeInteger)))
            g.add((r_line, METRICAL.absoluteLineNumber,
                   Literal(str(line_count), datatype=XSD.nonNegativeInteger)))
            # Add pattern
            g.add((r_line_pattern, METRICAL.patterningMetricalScheme,
                   Literal(line["rhythm"]["stress"], datatype=XSD.string)))
            # Check for Stanza type
            if not structure and line.get("structure") is not None:
                structure = line["structure"]
                r_stype = URIRef(KOS + slugify(structure))
                g.add((r_stanza, METRICAL.typeOfStanza, r_stype))
                g.add((r_stype, RDFS.label, Literal(structure)))
                g.add((r_stanza_pattern, METRICAL.rhymeDispositionType,
                       Literal(structure)))
            if "tokens" not in line:
                continue
            line_text = join_tokens(line["tokens"])
            g.add((r_line, METRICAL.content, Literal(line_text, lang="es")))
            g.add((r_line_pattern, METRICAL.grammaticalStressPattern,
                   Literal(get_grammatical_stress_pattern(line["tokens"]),
                           datatype=XSD.string)))
            # first last previous next Line
            if line_count == 0:
                g.add((r_line_list, METRICAL.firstLine, r_line))
            else:
                g.add((r_line, METRICAL.previousLine,
                       create_uri("L", str(line_count - 1), st_index, author,
                                  poem_title,
                                  dataset)))
            if int(st_index) + 1 == len(scansion) and int(l_index) + 1 == len(
                stanza):
                g.add((r_line_list, METRICAL.lastLine, r_line))
            else:
                g.add((r_line, METRICAL.nextLine,
                       create_uri("L", str(line_count + 1), st_index, author,
                                  poem_title,
                                  dataset)))
            # last Word of Line, add Rhyme to the Word URIRef
            rhyme_label = line["rhyme"]
            rhyme_ending = line["ending"]
            r_rhyme = create_uri("R", rhyme_label, author, poem_title, dataset)
            g.add((r_rhyme, RDF.type, METRICAL.Rhyme))
            g.add((r_rhyme, METRICAL.rhymeLabel, Literal(rhyme_label)))
            g.add((r_rhyme, METRICAL.rhymeGrapheme, Literal(rhyme_ending)))
            # Get last word index
            last_word_index = get_last_word_index(line["tokens"])

            r_rhyming_word = create_uri("W", str(last_word_index), l_index,
                                        st_index,
                                        author, poem_title, dataset)
            g.add((r_rhyme, METRICAL.hasRhymeWord, r_rhyming_word))
            r_rhyme_type = line["rhyme_type"]
            r_rtype = URIRef(KOS + slugify(r_rhyme_type))
            g.add((r_rhyme, METRICAL.presentsRhymeMatching, r_rtype))
            g.add((r_rtype, RDF.type, SKOS.concept))
            # Gramatical List
            for w_index, token in enumerate(line["tokens"]):
                w_index = str(w_index)
                if "word" not in token:
                    continue
                word_text = join_syllables(token)
                r_word = create_uri("W", w_index, l_index, st_index,
                                    author, poem_title, dataset)
                # Add word type
                g.add((r_word, RDF.type, METRICAL.Word))
                # Add word to WordList
                g.add((r_word_list, METRICAL.word, r_word))
                # Add Word DP
                g.add((r_word, METRICAL.content, Literal(word_text, lang="es")))
                g.add((r_word, METRICAL.indexInLine,
                       Literal(w_index, datatype=XSD.nonNegativeInteger)))
                g.add((r_word, METRICAL.wordNumber,
                       Literal(word_count, datatype=XSD.nonNegativeInteger)))
                # first last previous next Word
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
                    netx_w_index = int(w_index) + 1
                    g.add((r_word, METRICAL.nextWord,
                           create_uri("W", str(netx_w_index), l_index, st_index,
                                      author, poem_title, dataset)))
                for sy_index, syllable in enumerate(token['word']):
                    sy_index = str(sy_index)
                    r_syllable = create_uri("SY", sy_index,
                                            w_index, l_index,
                                            st_index, author,
                                            poem_title, dataset)
                    # Add Syllable type
                    g.add((r_syllable, RDF.type, METRICAL.GrammaticalSyllable))
                    # Add Syllable to word
                    g.add((r_word, METRICAL.hasGrammaticalSyllable, r_syllable))
                    g.add((r_grammatical_list, METRICAL.syllable, r_syllable))
                    # Add Syllable DP
                    g.add((r_syllable, METRICAL.indexInWord,
                           Literal(sy_index,
                                   datatype=XSD.nonNegativeInteger)))
                    g.add((r_syllable, METRICAL.grammaticalSyllableNumber,
                           Literal(syllable_count,
                                   datatype=XSD.nonNegativeInteger)))
                    g.add((r_syllable, METRICAL.content,
                           Literal(syllable["syllable"],
                                   datatype=XSD.nonNegativeInteger)))
                    g.add((r_syllable, METRICAL.isStressed,
                           Literal(syllable["is_stressed"],
                                   datatype=XSD.Boolean)))
                    # first last previous next Syllable
                    if int(sy_index) == 0 and word_count == 0:
                        g.add((r_grammatical_list,
                               METRICAL.firstGrammaticalSyllable, r_syllable))
                    elif int(sy_index) != 0:
                        prev_sy_index = int(sy_index) - 1
                        g.add((r_syllable, METRICAL.previousGrammaticalSyllable,
                               create_uri("SY", str(prev_sy_index),
                                          w_index, l_index,
                                          st_index, author,
                                          poem_title, dataset)))
                        print(syllable["syllable"], sy_index)
                    if int(w_index) + 1 == len(line["tokens"]) and int(
                        sy_index) + 1 == len(token["word"]):
                        g.add((r_grammatical_list,
                               METRICAL.lastGrammaticalSyllable, r_syllable))
                    else:
                        next_sy_index = int(sy_index) + 1
                        g.add((r_line, METRICAL.nextLine,
                               create_uri("SY", str(next_sy_index),
                                          w_index, l_index,
                                          st_index, author,
                                          poem_title, dataset)))
                    syllable_count += 1
                word_count += 1
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
    """Join all symbols and syllables from a list of tokens into a string."
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
