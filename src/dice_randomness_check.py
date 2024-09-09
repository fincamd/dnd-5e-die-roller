from sys import argv
from argparse import ArgumentParser
from tabulate import tabulate
from statsmodels.sandbox.stats.runs import runstest_1samp


def main(args):
    """This is an implementation of the statistic test used to check whether a sequence of values is random. It is called "The run test", or "The Wald-Wolfowitz test".
    """
    # 0. We have the Null Hypothesis we want to test: H0 - The sequence is random
    # 1. Perform the test against this new 1s and 0s sample
    z_statistic_value, p_value = runstest_1samp(args.values)
    # 2. Accept or reject the null hypothesis
    is_the_sample_random = p_value > args.significance_level

    logs = []
    logs.append(["Values", args.values])
    logs.append(["Z-statistic value", z_statistic_value])
    logs.append(["P-value", p_value])
    logs.append(["Significance level", args.significance_level])
    logs.append(["Can we assume that the sample is random?", is_the_sample_random])

    print(tabulate(logs, tablefmt="outline", colalign=("right",)))


if __name__ == "__main__":
    args = ArgumentParser(argv)
    args.add_argument("values", nargs="+", default=[], type=int, help="An ordered sequence of values that we want to test to know whether it is random or not.")
    args.add_argument("--significance-level", default=0.05, type=float, help="The significance level to use when performing the hypothesis check. Fea")

    main(args.parse_args())
