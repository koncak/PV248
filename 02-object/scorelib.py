import re

class Print:

    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        pass

    def composition(self):
        pass


class Edition:

    def __init__(self, composition, name):
        self.composition = composition
        self.authors = []
        self.name = name

    def add_author(self, author):
        self.authors.append(author)


class Composition:

    def __init__(self, name, incipit, key, genre, year, voices):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = []

    def add_author(self, author):
        self.authors.append(author)


class Voice:

    def __init__(self, name, range):
        self.name = name
        self.range = range


class Person:

    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died


def create_person(person_string):
    if ';' in person_string:
        for n in person_string.split(';'):
            dates = re.search(r'\((.*?)\)', n.strip())
            if dates is not None:
                print(dates.group(1))


def load(filename):
    file = open(filename)
    out = []

    composer = re.compile("Composer: (.*)")
    for line in file:
        m = composer.match(line)
        if m is None:
            continue
        name = m.group(1).strip()
        create_person(name)


    return out


load('./scorelib.txt')