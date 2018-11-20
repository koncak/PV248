import pandas as pd
import sys
import json
import numpy as np
from scipy import stats
import re
import math
from datetime import datetime, timedelta


def stats(df):
    columns = list(df)
    exercises = set()
    dates = []
    for column in columns:
        ex = re.match('(.*)[/](.*)', column.strip())
        exercises.add(ex.group(2))
        dates.append(datetime.strptime(ex.group(1), '%Y-%m-%d'))

    start = datetime.strptime("2018-09-17", '%Y-%m-%d')

    df = df.reindex(sorted(df.columns), axis=1)

    columns = list(df)
    datese = set()
    for column in columns:
        ex = re.match('(.*)[/].*', column.strip())
        datese.add(ex.group(1))

    datese = sorted(list(datese))

    dic = {}
    for d in datese:
        cols = [x for x in columns if d in re.match('(.*)[/].*', x).group(1)]

        suming = 0
        for i in range(len(cols)):
            suming += df[cols[i]]
        dic[d] = suming

    fd = pd.DataFrame.from_dict(dic)

    cumsum = np.cumsum(fd, axis=1)

    cum_dates = list(cumsum)
    cum_values = cumsum.values

    cum_dates = [(datetime.strptime(x, '%Y-%m-%d')-start).days for x in cum_dates]
    cum_values = [item for sublist in cum_values for item in sublist]

    x = [0] + cum_dates
    y = [0] + cum_values

    x = np.array(x)
    y = np.array(y)

    x = x[:, np.newaxis]

    a, _, _, _ = np.linalg.lstsq(x, y, rcond=-1)

    regression = float(a)
    if a <= 0:
        date_16 = "inf"
        date_20 = "inf"
    else:
        date_16 = '{:%Y-%m-%d}'.format(start + timedelta(days=math.ceil(16 / regression)))
        date_20 = '{:%Y-%m-%d}'.format(start + timedelta(days=math.ceil(20 / regression)))

    exercises = sorted(list(exercises))
    for ex in exercises:
        cols = [x for x in columns if ex in re.match('.*[/](.*)', x).group(1)]
        suming = 0
        for i in range(len(cols)):
            suming += df[cols[i]]
        df[ex] = suming
    easy = []

    for ex in exercises:
        easy.append(df.iloc[0][ex])

    out = {"mean": np.mean(easy),
           "median": np.median(easy),
           "total": sum(easy),
           "passed": np.count_nonzero(easy),
           "regression slope": regression,
           "date 16": date_16,
           "date 20": date_20}

    json.dump(out, sys.stdout, indent=4, ensure_ascii=False)


def main():
    file = sys.argv[1]
    id = sys.argv[2]

    df = pd.read_csv(file)

    if id == 'average':
        df = df.drop(['student'], 1)
        df = df.reindex(sorted(df.columns), axis=1)
        dates = list(df)
        means = df[dates].mean()
        df = pd.DataFrame(means).transpose()
        stats(df)

    else:
        id = int(id)
        frame = df.loc[df['student'] == id]
        if frame.empty:
            print("Nezname student ID")
            return
        frame = frame.drop(['student'], 1)
        stats(frame)


main()
