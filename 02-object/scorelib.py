
class Print:

    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        print("Print Number:", self.print_id)

        self.print_persons("composer")

        print("Title:", end='')
        if self.edition.composition.name:
            print("", self.edition.composition.name)
        else:
            print()

        print("Genre:", end='')
        if self.edition.composition.genre:
            print("", self.edition.composition.genre)
        else:
            print()

        print("Key:", end='')
        if self.edition.composition.key:
            print("", self.edition.composition.key)
        else:
            print()

        print("Composition Year:", end='')
        if self.edition.composition.year:
            print("", self.edition.composition.year)
        else:
            print()

        print("Edition:", end='')
        if self.edition.name:
            print("", self.edition.name)
        else:
            print()

        self.print_persons("editor")

        voices = self.edition.composition.voices
        if voices:
            for i in range(len(voices)):
                print("Voice " + str(i+1) + ": ", end='')
                if voices[i].range:
                    print(voices[i].range, end='')
                    if voices[i].name:
                        print(",", voices[i].name)
                    else:
                        print()
                if not voices[i].range and voices[i].name:
                    print(voices[i].name)

        else:
            print("Voice 1:")

        print("Partiture:", "yes" if self.partiture else "no")

        print("Incipit:", end='')
        if self.edition.composition.incipit:
            print("", self.edition.composition.incipit)
        else:
            print()

        print()

    def composition(self):
        return self.edition.composition

    def print_persons(self, type):
        if type == "composer":
            out_string = "Composer:"
            authors = self.edition.composition.authors

        if type == "editor":
            out_string = "Editor:"
            authors = self.edition.authors

        if len(authors) > 0:
            for i in range(len(authors)):
                author = authors[i]
                if i == 0:
                    print(out_string+" ", end='')
                    print(author.name, end='')
                    if author.born is not None:
                        print(' ({}--'.format(author.born), end='')
                        if author.died is None:
                            print(')', end='')

                    if author.died is not None:
                        if author.born is None:
                            print('(--', end='')
                        print('{})'.format(author.died), end='')
                else:
                    print("; ", author.name, end='')
                    if author.born is not None:
                        print('({}--'.format(author.born), end='')
                    if author.died is not None:
                        print('{})'.format(author.died), end='')
            print()
        else:
            print(out_string)


class Edition:

    def __init__(self, composition, name):
        self.composition = composition
        self.authors = []
        self.name = name

    def add_author(self, author):
        self.authors.append(author)


class Composition:

    def __init__(self, name, incipit, key, genre, year):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = []
        self.authors = []

    def add_author(self, author):
        self.authors.append(author)

    def add_voice(self, voice):
        self.voices.append(voice)


class Voice:

    def __init__(self, name, range):
        self.name = name
        self.range = range
        self.number = None

    def check_range(self):
        if self.range and self.range.count("-") == 1:
            position = self.range.find("-")
            self.range = self.range[:position] + "-" + self.range[position:]


class Person:

    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

