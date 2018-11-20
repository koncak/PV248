import sys
import numpy as np
import pandas as pd
import json
import re
import collections


def exercise(df):
    df = df.drop(['student'], 1)

    columns = list(df)
    exercises = set()
    for column in columns:
        ex = re.match('.*[/](.*)', column.strip())
        exercises.add(ex.group(1))

    deadlines = {}
    for ex in exercises:
        cols = [x for x in columns if ex in re.match('.*[/](.*)', x).group(1)]

        suming = 0
        for i in range(len(cols)):
            suming += df[cols[i]]

        df[ex] = suming
        deadline = {"mean": df[ex].mean(),
                    "median": df[ex].median(),
                    "first": df[ex].quantile(.25),
                    "last": df[ex].quantile(.75),
                    "passed": int(df[ex].astype(bool).sum(axis=0))}
        deadlines[ex] = deadline

    od = collections.OrderedDict(sorted(deadlines.items()))
    json.dump(od, sys.stdout, indent=4, ensure_ascii=False)


def deadlines(df):
    df = df.drop(['student'], 1)
    deadlines = {}
    for column in df.columns:
        deadline = {"mean": df[column].mean(),
                    "median": df[column].median(),
                    "first": df[column].quantile(.25),
                    "last": df[column].quantile(.75),
                    "passed": int(df[column].astype(bool).sum(axis=0))}

        deadlines[column] = deadline

    od = collections.OrderedDict(sorted(deadlines.items()))
    json.dump(od, sys.stdout, indent=4, ensure_ascii=False)


def dates(df):
    df = df.drop(['student'], 1)
    columns = list(df)
    unique_dates = set()
    for column in columns:
        ex = re.match('(.*)[/].*', column.strip())
        unique_dates.add(ex.group(1))

    deadlines = {}
    for date in unique_dates:
        cols = [x for x in columns if date in re.match('(.*)[/].*', x).group(1)]

        suming = 0
        for i in range(len(cols)):
            suming += df[cols[i]]
        df[date] = suming

        deadline = {"mean": df[date].mean(),
                    "median": df[date].median(),
                    "first": df[date].quantile(.25),
                    "last": df[date].quantile(.75),
                    "passed": int(df[date].astype(bool).sum(axis=0))}
        deadlines[date] = deadline

    od = collections.OrderedDict(sorted(deadlines.items()))
    json.dump(od, sys.stdout, indent=4, ensure_ascii=False)


def main():
    file = sys.argv[1]
    mode = sys.argv[2]

    df = pd.read_csv(file)

    if mode == "deadlines":
        deadlines(df)
        return
    if mode == "exercises":
        exercise(df)
        return
    if mode == "dates":
        dates(df)
        return


main()