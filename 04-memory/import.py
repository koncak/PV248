import sqlite3
import test
import sys


def store_print(cursor, prin, edition_id):
    partiture = "N"
    if prin.partiture:
        partiture = "Y"
    cursor.execute("INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)",
                   (prin.print_id, partiture, edition_id))


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


def store_score(cursor, score): #73, 76, 77
    cursor.execute("SELECT * FROM score WHERE name=?"
                   " AND (genre=? or genre is null) "
                   "AND (key = ? or key is null) AND "
                   "(incipit = ? or incipit is null) AND "
                   "(year = ? or year is null)",
                   (score.name, score.genre, score.key, score.incipit, score.year))
    stored = cursor.fetchone()
    if stored is None:
        cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                    (score.name, score.genre, score.key, score.incipit, score.year))
        return cursor.lastrowid
    return stored[0]


def store_author(cursor, person):
    cursor.execute("SELECT * FROM person WHERE name=?", (person.name,))
    stored = cursor.fetchone()
    if stored is None:
        cursor.execute("INSERT INTO person (born, died, name) VALUES (?, ?, ?)",
                       (person.born, person.died, person.name))
        return cursor.lastrowid
    else:
        if stored[1] is None and person.born is not None:
            cursor.execute("UPDATE person SET born = ? WHERE name = ?",
                           (person.born, person.name))

        if stored[2] is None and person.died is not None:
            cursor.execute("UPDATE person SET died = ? WHERE name = ?",
                           (person.died, person.name))
        return stored[0]


def main():
    filename = sys.argv[1]
    database = sys.argv[2]

    conn = sqlite3.connect(database)
    qry = open('./scorelib.sql', 'w').read()

    c = conn.cursor()
    c.executescript(qry)

    prints = test.main(filename)

    for prin in prints:

        editors = []
        for author in prin.edition.authors:
            c = conn.cursor()
            editors.append(store_author(c, author))
            conn.commit()

        authors = []
        for author in prin.edition.composition.authors:
            c = conn.cursor()
            authors.append(store_author(c, author))
            conn.commit()

        c = conn.cursor()
        score = store_score(c, prin.edition.composition)
        conn.commit()

        for voice in prin.edition.composition.voices:
            c = conn.cursor()
            store_voice(c, voice, score)
        conn.commit()

        c = conn.cursor()
        store_edition(c, prin.edition, score)
        edition_id = c.lastrowid
        conn.commit()

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

    c.close()
    conn.close()

main()