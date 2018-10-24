import numpy as np
import sys
import re


def split_value(value):
    out = re.match("(-?\d+)?([a-z])", value)  # -b ? MAYBEE
    if out.group(1):
        return int(out.group(1)), out.group(2)
    else:
        return 1, out.group(2)


def get_tuples(left_side):
    groups = []

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
    print(lefts)
    letters = letters[0]
    print(letters)
    lefts = np.array(lefts)

    augumented = np.c_[lefts, rights]
    print(augumented)
    left_rank = np.linalg.matrix_rank(lefts)
    augumented_rank = np.linalg.matrix_rank(augumented)

    if not left_rank == augumented_rank:
        print("NO SOLUTION")
        return

    unknowns = len(lefts[0])  # they all have same dimension

    if unknowns == left_rank:
        solution = np.linalg.solve(lefts, rights)
        print("Unique solution: ", end="")
        for i in range(len(solution)):
            print(letters[i] + "=" + str(solution[i]), end=" ")

        print()
        return
    else:
        print("Infinite number of solution with dimension", unknowns - left_rank)
        return


main()
