import re
import sys
import scorelib as sc


def print_create(list_of_lines):
    print_object = sc.Print(None, None, False)
    edition_object = sc.Edition(None, None)
    composition = sc.Composition(None, None, None, None, None)

    for line in list_of_lines:
        print_number = re.match("Print Number: (.*)", line)
        if print_number:
            print_object.print_id = int(print_number.group(1))

        composers = re.match("Composer: (.*)", line)
        if composers:
            pass

        title = re.match("Title: (.*)", line)
        if title and title.group(1).strip() != "":
            composition.name = title.group(1).strip()

        genre = re.match("Genre: (.*)", line)
        if genre and genre.group(1).strip() != "":
            composition.genre = genre.group(1).strip()

        key = re.match("Key: (.*)", line)
        if key and key.group(1).strip() != "":
            composition.key = key.group(1).strip()

        edition = re.match("Edition: (.*)", line)
        if edition and edition.group(1).strip() != "":
            edition_object.name = edition.group(1).strip()

        incipit = re.match("Incipit: (.*)", line)
        if incipit and incipit.group(1).strip() != "":
            composition.incipit = incipit.group(1).strip()

        partiture = re.match("Partiture: (.*)", line)
        if partiture and partiture.group(1).strip() != "":
            part = re.match(".*yes.*", partiture.group(1).strip())
            if part:
                print_object.partiture = True

        composition_year = re.match("Composition Year: (.*)", line)
        if composition_year:
            year = re.match(".*(\d{4}).*", composition_year.group(1).strip())
            if year:
                composition.year = int(year.group(1))

        composers = re.match("Composer: (.*)", line)
        if composers:
            composers = composers.group(1).split(";")
            for c in composers:
                composition.add_author(create_person(c))

        editors = re.match("Editor: (.*)", line)
        if editors:
            editors = editors.group(1).strip()
            single_person = re.match("(\w+ \w+|\w+$|\w+-\w+ \w+)", editors)

            if single_person:
                editor = create_person(single_person.group(1).strip())
                edition_object.add_author(editor)

            else:
                single_person = re.match("(\w+, \w+$|\w+, \w+\.$|(\w+\. ){1,2}(\w+[\s]?){1,2}$)", editors)

                if single_person:
                    editor = create_person(single_person.group(1).strip())
                    edition_object.add_author(editor)

                else:
                    persons = editors.split(",")

                    if len(persons) == 2:
                        for person in persons:
                            editor = create_person(person)
                            edition_object.add_author(editor)

                    else:
                        persons = [x+y for x, y in zip(persons[0::2], persons[1::2])]
                        for person in persons:
                            editor = create_person(person)
                            edition_object.add_author(editor)

        voices = re.match("Voice (\d*): (.*)", line)
        if voices:
            voice = create_voice(voices.group(2))
            voice.check_range()
            voice.number = int(voices.group(1))
            composition.add_voice(voice)

    edition_object.composition = composition
    print_object.edition = edition_object

    return print_object


def create_voice(voice_string):
    voice = sc.Voice(None, None)

    ranger = re.match("(\(?\w*?\)?\w*-{1,2}\w*),?;?[\s]?(.*)?", voice_string)
    if ranger:
        voice.range = ranger.group(1).strip()
        if ranger.group(2).strip() != "":
            voice.name = ranger.group(2).strip()

    else:
        voice.name = voice_string

    return voice


def create_person(person_string):
    p = sc.Person(None, None, None)
    o = re.match("(.*)\((.*?)\)", person_string)
    if o:
        born = None
        died = None
        alive = re.match("(\d{4}--$|\*\d{4})", o.group(2))
        if alive:
            born = int(re.findall(r"(\d+)", alive.group(1))[0])

        else:
            born_died = re.match("(\d{4})-{1,2}(\d{4})", o.group(2))

            died_plus = re.match('\+(\d{4})', o.group(2))

            if born_died:
                born = int(born_died.group(1))
                died = int(born_died.group(2))

            if died_plus:
                died = int(died_plus.group(1))

        p.name = o.group(1).strip()
        p.born = born
        p.died = died

    else:
        p.name = person_string.strip()

    return p


def load(filename):

    data = open(filename)
    lines = data.readlines()

    lines.insert(0, '\n')
    out = []

    for i in range(len(lines)):
        if lines[i] == "\n":
            i += 1
            list_of_lines = []

            while lines[i] != "\n":
                list_of_lines.append(lines[i].strip())
                i += 1
                if i == len(lines):
                    break

            if list_of_lines:
                out.append(print_create(list_of_lines))

    return out


def main(filename):
    prints = load(filename)

    prints.sort(key=lambda x: x.print_id)  # not needed

    return prints
