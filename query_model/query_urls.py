# -*- coding: utf-8 -*-
import human_curl
import json

from query_model.query_url_implementations import (
    run_human_curl_async,
    run_curl_multiprocessing,
    run_urllib2_multiprocessing
)

from query_model.predict_lookup_time import predict_lookup_time


def query_urls(
        uri_count,
        parallelism,
        actor_source,
        method,
        compare_all
        ):
    def get_actor_list(actor_source, limit):
        actor_urls = [str(u) for u in json.loads(
            human_curl.get(actor_source).content)
        ]
        if len(actor_urls) < limit:
            print "Reusing actors. Maybe start more real actors"
        while len(actor_urls) < limit:
            actor_urls.extend(actor_urls)
        return actor_urls[:limit]

    actor_urls = get_actor_list(actor_source=actor_source, limit=uri_count)

    if compare_all:
        best_result = None
        for m in (
                run_human_curl_async,
                run_curl_multiprocessing,
                run_urllib2_multiprocessing
                ):
            result = m(url_list=actor_urls, parallelism=parallelism)
            if not best_result or result < best_result:
                best_result = result
        _prediction = predict_lookup_time(
            uri_count=uri_count,
            parallelism=parallelism
        )
    else:
        return method(url_list=actor_urls, parallelism=parallelism)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        "Measure different implementations for get many urls"
    )
    parser.add_argument("-n", "--uri_count",
        default=20, type=int,
        help="Urls to crawl during a test. Default: 20"
    )
    parser.add_argument("-p", "--parallelism",
        default=5, type=int,
        help=("Run query with <p> parallelism. Default: 5")
    )
    parser.add_argument(
        "-s", "--actor-source", required=True,
        type=str,
        help=("Source that responds with a JSON list "
              "of actor URIs.")
    )
    parser.add_argument(
        "-m", "--method", default=run_human_curl_async.__name__,
        choices=(run_human_curl_async.__name__,
                 run_curl_multiprocessing.__name__,
                 run_urllib2_multiprocessing.__name__),
        help=("Which method to use for query")
    )

    parser.add_argument(
        "--compare-all", action="store_true", default=True,
        help=("Compare all implementations and include simulation")
    )

    parsed_args = parser.parse_args().__dict__

    if not parsed_args['method'] in globals():
        raise argparse.ArgumentError("Invalid choice! "
            "Please pass run_human_curl_async, run_curl_multiprocessing "
            "or run_urllib2_multiprocessing"
        )
    parsed_args['method'] = globals()[parsed_args['method']]

    query_urls(**parsed_args)
