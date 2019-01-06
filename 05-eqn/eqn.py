import numpy as np
import sys
import re


def split_value(value):
    """
    Splits numbers and letters to tuple 4x to (4, 'x')
    :param value: string to be splited
    :return: tuple
    """
    value = value.strip()
    out = re.match("(-?\d*)?([a-z])", value)
    if out.group(1):
        if "-" is out.group(1):
            return int(-1), out.group(2)
        return int(out.group(1)), out.group(2)
    else:
        return 1, out.group(2)


def get_tuples(left_side):
    """
    Recursivly splits left side of the equation. Calls split_value on each and returns list of tuples
    :param left_side: left side of the equation
    :return: list of tuples
    """
    groups = []
    left_side = left_side.strip()

    def split_left(value):
        if " " not in value:
            groups.append(value)
            return
        out = re.match("(.*) (\+|-) (.*)", value)
        if out is None:
            return
        else:
            out_string = ""
            if out.group(2) == "-":
                out_string = "-" + out_string
            out_string = out_string + out.group(3)
            groups.append(out_string)
            split_left(out.group(1))

    split_left(left_side)
    return [split_value(x) for x in groups]


def get_left(left_together):
    """
    Fills empty places in the variable matrix for easier manipulation and returns sorted list for one left side
    :param left_together: one left side of the equation
    :return: list of tuples
    """
    for i in range(len(left_together)):
        variables = set([x[1] for x in left_together[i]])

        for j in range(len(left_together)):
            second = set([x[1] for x in left_together[j]])
            diff = second.difference(variables)
            variables = variables.union(diff)

            for d in diff:
                left_together[i].append((0, d))

    left_sorted = []
    for left in left_together:
        left_sorted.append(sorted(left, key=lambda x: x[1]))
    return left_sorted


def main():
    args = sys.argv
    file = open(args[1])
    rights = []
    left_together = []

    for line in file:
        equals = re.match("(.*) = (.*)", line)
        right_side = equals.group(2)
        right_side = int(right_side)
        rights.append(right_side)

        left_side = equals.group(1)

        groups = get_tuples(left_side)
        left_together.append(groups)

    lefts = []
    letters = []
    for l in get_left(left_together):
        letters.append([x[1] for x in l])
        lefts.append([x[0] for x in l])

    letters = letters[0]
    lefts = np.array(lefts)

    augumented = np.c_[lefts, rights]
    left_rank = np.linalg.matrix_rank(lefts)
    augumented_rank = np.linalg.matrix_rank(augumented)

    if not left_rank == augumented_rank:
        print("no solution")
        return

    unknowns = len(lefts[0])  # they all have the same dimension

    if unknowns == left_rank:
        solution = np.linalg.solve(lefts, rights)
        print("solution: ", end="")
        first = False
        for i in range(len(solution)):
            if not first:
                print(letters[i] + " = " + str(solution[i]), end="")
                first = True
            else:
                print(', ' + letters[i] + " = " + str(solution[i]), end="")

        print()
        return
    else:
        print("solution space dimension:", unknowns - left_rank)
        return


main()
