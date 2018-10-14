import sqlite3
import test
import os


def store_print(cursor, print, edition_id):
    partiture = "N"
    if print.partiture:
        partiture = "Y"
    cursor.execute("INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)",
                   (print.print_id, partiture, edition_id))


def store_edition_author(cursor, editor_id, edition_id):
    cursor.execute("INSERT INTO edition_author (editor, edition) VALUES (?, ?)",
                   (editor_id, edition_id))


def store_score_author(cursor, author_id, score_id):
    cursor.execute("INSERT INTO score_author (composer, score) VALUES (?, ?)",
                   (author_id, score_id))


def store_edition(cursor, edition, score_id):
    cursor.execute("INSERT INTO edition (score, name, year) VALUES (?, ?, ?)",
                   (score_id, edition.name, None))


def store_voice(cursor, voice, score_id):
    cursor.execute("INSERT INTO voice (name, range, number, score) VALUES (?, ?, ?, ?)",
                   (voice.name, voice.range, voice.number, score_id))


def store_score(cursor, score):
    cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                   (score.name, score.genre, score.key, score.incipit, score.year))


def store_author(cursor, person):
    cursor.execute("SELECT * FROM person WHERE name=?", (person.name,))
    stored = cursor.fetchone()
    if stored is None:
        cursor.execute("INSERT INTO person (born, died, name) VALUES (?, ?, ?)",
                       (person.born, person.died, person.name))
    else:
        if stored[1] is None and person.born is not None:
            cursor.execute("UPDATE person SET born = ? WHERE name = ?",
                           (person.born, person.name))
        if stored[2] is None and person.died is not None:
            cursor.execute("UPDATE person SET died = ? WHERE name = ?",
                           (person.died, person.name))


def main():
    qry = open('scorelib.sql', 'r').read()
    conn = sqlite3.connect('scorelib.dat')
    c = conn.cursor()
    c.executescript(qry)

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())

    prints = test.main()  # bez posilani file

    for prin in prints:
        editors = []

        for author in prin.edition.authors:
            c = conn.cursor()
            store_author(c, author)
            editors.append(c.lastrowid)
            conn.commit()

        authors = []
        for author in prin.edition.composition.authors:
            c = conn.cursor()
            store_author(c, author)
            authors.append(c.lastrowid)
            conn.commit()

        c = conn.cursor()
        store_score(c, prin.edition.composition)
        score = c.lastrowid
        conn.commit()

        for voice in prin.edition.composition.voices:
            c = conn.cursor()
            store_voice(c, voice, score)
        conn.commit()

        c = conn.cursor()
        store_edition(c, prin.edition, score)
        edition_id = c.lastrowid

        c = conn.cursor()
        for author in authors:
            store_score_author(c, author, score)
        conn.commit()

        c = conn.cursor()
        for editor in editors:
            store_edition_author(c, editor, edition_id)
        conn.commit()

        c = conn.cursor()
        store_print(c, prin, edition_id)
        conn.commit()

    c = conn.cursor()
    c.execute("SELECT * FROM person;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM score;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM voice;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM edition;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM score_author;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM edition_author;")
    print(len(c.fetchall()))

    c = conn.cursor()
    c.execute("SELECT * FROM print;")
    print(len(c.fetchall()))

    c.close()
    conn.close()
    os.remove("scorelib.dat")

main()