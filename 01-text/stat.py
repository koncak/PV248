import sys
import re
from collections import Counter
import operator


def clean_name(name):
    new_name = re.sub(re.compile(' \((.*?)\)'), "", name)  # ocisteni jmena o letopocet v zavorce
    return new_name


def composer(file):
    # odstranit zavorky a stredniky
    r = re.compile("Composer: (.*)")
    counter = Counter()

    for line in file:
        m = r.match(line)
        if m is None:
            continue
        name = m.group(1).strip()
        name = clean_name(name)

        if ";" in name:
            for n in name.split(';'):
                counter[n.strip()] += 1
        elif '&' in name:
            for n in name.split('&'):
                counter[n.strip()] += 1
        else:
            counter[name.strip()] += 1

    # for k, v in sorted(counter.items()):
    #     print("%s: %d" % (k, v))

    sorted_counter = sorted(counter.items(), key=operator.itemgetter(1))
    sorted_counter.reverse()
    for s in sorted_counter:
        if s[0] == "":
            continue
        print("%s: %d" % (s[0], s[1]))


def century_from_year(year):
    return (year) // 100 + 1


def century(file):
    r = re.compile("Composition Year: (.*)")
    c = []
    for line in file:
        m = r.match(line)
        if m is None:
            continue
        year = m.group(1).strip()
        year = [int(s) for s in year.split() if s.isdigit()]
        if len(year) > 0:
            c.append(year)

    counter = Counter()
    for x in c:
        counter[century_from_year(x[0])] += 1

    for k, v in sorted(counter.items()):
        print("%sth century: %d" % (k, v))


def main():
    args = sys.argv
    file = open(args[1])
    stat = sys.argv[2]

    if stat == 'composer':
        composer(file)
        return

    if stat == 'century':
        century(file)
        return

    else:
        raise ValueError("Unknown operation: %s" % stat)

main()