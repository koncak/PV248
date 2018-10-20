import sqlite3
import sys
import json


def main():
    conn = sqlite3.connect("./scorelib.dat")
    #name = sys.argv[1]

    name = "Haydn, Joseph"

    c = conn.cursor()
    c.execute('SELECT * FROM person p WHERE p.name LIKE ? ORDER BY p.name ASC', ("%"+name+"%",))
    for author in c.fetchall():
        author_dict = {}
        author_dict[author[-1]] = []
        author_id = author[0]
        c = conn.cursor()

        c.execute("DROP VIEW IF EXISTS tracks")
        c.execute("create view tracks AS "
                  "select *, per.id AS composer_id, per.name AS composer_name, e.id AS edition_id,"
                  " p.id AS print_id"
                  " ,s.id AS score_id "  # musi byt posledni
                  " from"
                  " edition e JOIN"
                  " print p ON e.id = p.edition JOIN"
                  " score s ON e.score = s.id JOIN"
                  " score_author sa ON sa.score = s.id JOIN"
                  " person per ON sa.composer = per.id ")

        c.execute("select * from tracks where composer_id = ?", (author_id,))
        result = c.fetchall()
        for r in result:
            print(r)
            out = {}
            out["Print Number"] = r[-2]
            out["Title"] = r[8]
            out["Genre"] = r[9]
            out["Key"] = r[10]
            out["Composition year"] = r[12]
            out["Edition"] = r[2]

            score_id = r[-1]  # carefull
            c = conn.cursor()
            c.execute("select * from tracks JOIN "
                      "edition_author ea ON ea.edition = edition_id JOIN"
                      " person ON person.id = ea.editor"
                      " where score_id = ?",
                      (score_id,))

            editors = c.fetchall()
            out_editors = []
            for editor in editors:
                out_editors.append((editor[-1], editor[-2], editor[-3]))

            editors = []
            for out_author in set(out_editors):
                editor = {}
                editor['Name'] = out_author[0]
                if out_author[1]:
                    editor['Born'] = out_author[1]
                if out_author[2]:
                    editor['Died'] = out_author[2]
                editors.append(editor)

            out["Editor"] = editors if editors else None

            c.execute("select * from tracks JOIN"
                         " voice on tracks.score_id = voice.score "
                         "where score_id = ?",
                         (score_id,))

            voices = c.fetchall()

            out_voices = []
            for voice in voices:
                voice_string = ""

                if voice[-2]:
                    voice_string += voice[-2]
                    voice_string += ", "

                voice_string += voice[-1]
                out_voices.append((voice[-4], voice_string))

            sorted_voices = sorted(list(set(out_voices)), key=lambda tup: tup[0])
            for out_voice in sorted_voices:
                out["Voice " + str(out_voice[0])] = out_voice[1]

            out["Partiture"] = "Yes" if r[5] == "Y" else "No"
            out["Incipit"] = r[11]
            author_dict[author[-1]].append(out)

            print()
        print()

        json.dump(author_dict, sys.stdout, indent=1, ensure_ascii=False)

        c.execute("DROP VIEW tracks")
main()