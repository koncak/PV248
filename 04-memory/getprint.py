import sqlite3
import json
import sys


def main():
    conn = sqlite3.connect("./scorelib.dat")
    number = sys.argv[1]

    c = conn.cursor()

    c.execute("select per.name, per.born, per.died from"
              " edition e JOIN"
              " print p ON e.id = p.edition JOIN"
              " score s ON e.score = s.id JOIN"
              " score_author sa ON sa.score = s.id JOIN"
              " person per ON sa.composer = per.id "
              "where p.id = ?", (number,))
    authors = c.fetchall()

    author_list = []
    for author in authors:
        author_dict = {}
        author_dict['name'] = author[0]
        if author[1]:
            author_dict['born'] = author[1]
        if author[2]:
            author_dict['died'] = author[2]

        author_list.append(author_dict)

    json.dump(author_list, sys.stdout, indent=4, ensure_ascii=False)
    c.close()
    conn.close()

main()

