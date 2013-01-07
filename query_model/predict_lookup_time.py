# -*- coding: utf-8 -*-
from __future__ import print_function
import math

default_connect_time = .033
default_processing_time = .036
default_calculation_time = .003

def predict_lookup_time(
        uri_count,
        parallelism,
        connect_time=default_connect_time,
        processing_time=default_processing_time,
        calculation_time=default_calculation_time,
        quiet=False
        ):

    avg_lookup_time = connect_time + processing_time

    cycles = math.ceil(uri_count / float(parallelism))
    predicted_tme = cycles * avg_lookup_time + \
                    calculation_time * uri_count

    if not quiet:
        print("Simulation: Lookup of {0} Urls over a "
            "connection with parallelism {1} takes '{2}s' "
            "({3} cycles)".format(uri_count, parallelism,
            predicted_tme, cycles)
        )

    return predicted_tme


def main():
    import argparse
    parser = argparse.ArgumentParser(
        "Measure different implementations for get many urls"
    )
    parser.add_argument("-c", "--uri_count",
        type=int,
        default=16,
        help="Urls to query (simulate)"
    )
    parser.add_argument("-p", "--parallelism",
        type=int, default=4,
        help="Parallelism of connection and hardware"
    )
    parser.add_argument("--connect_time",
        default=.033, type=float,
        help="Time until connected. Default: .033s"
    )
    parser.add_argument("--processing_time",
        default=.036, type=float,
        help=("Time of waiting for server response + "
            "time to transfer. Default: .036s")
    )
    parser.add_argument("--calculation_time",
        default=.003, type=float,
        help=("Calculation overhead. Default: .003s")
    )
    predict_lookup_time(**parser.parse_args().__dict__)
