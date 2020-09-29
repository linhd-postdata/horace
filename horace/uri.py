from rdflib import Graph, URIRef


BASE_URI = "http://postdata.linhd.uned.es/resource/"


def uri_poetic_work(author, poem_title):
    return URIRef(BASE_URI + "PW_{0}_{1}".format(author, poem_title).replace(" ", "_"))

def uri_redaction(author, poem_title, dataset):
    return URIRef(BASE_URI + "R_{0}_{1}_{2}".format(author, poem_title, dataset).replace(" ", "_"))

def uri_creator_role(author, poem_title):
    return URIRef(BASE_URI + "CR_{0}_{1}".format(author, poem_title).replace(" ", "_"))

def uri_person(author):
    return URIRef(BASE_URI + "P_{0}".format(author).replace(" ", "_"))

def uri_stanza_list(poem_title, author, dataset):
    return URIRef(BASE_URI + "SL_{0}_{1}_{2}".format(author, poem_title, dataset).replace(" ", "_"))

def uri_line(line_number, stanza_number, author, poem_title, dataset):
    return URIRef(BASE_URI + "L_{0}_{1}_{2}_{3}_{4}".format(line_number, stanza_number, author, poem_title, dataset).replace(" ", "_"))

def uri_stanza(stanza_number, author, poem_title, dataset):
    return URIRef(BASE_URI + "S_{0}_{1}_{2}_{3}".format(stanza_number, author, poem_title, dataset).replace(" ", "_"))

def uri_word(word_number, line_number, stanza_number, author, poem_title, dataset):
    return URIRef(BASE_URI + "W_{0}_{1}_{2}_{3}_{4}_{5}".format(word_number, line_number, stanza_number, author, poem_title, dataset).replace(" ", "_"))

def uri_syllable(syllable_number, word_number, line_number, stanza_number, author, poem_title, dataset):
    return URIRef(BASE_URI + "SY_{0}_{1}_{2}_{3}_{4}_{5}_{6}".format(syllable_number, word_number, line_number, stanza_number, author, poem_title, dataset).replace(" ", "_"))
