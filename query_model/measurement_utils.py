from __future__ import print_function
import time
import numpy


def describe_measurements(measurements):
    return {
        'min': min(measurements),
        'mean': numpy.mean(measurements),
        'sd': numpy.std(measurements), #[+/-sd]
        'median': numpy.median(measurements),
        'max': max(measurements)
    }


def relative_accuracy(results):
    return results['sd'] / results['median'] * 100


def repeat_measurement_and_describe(
        repetitions,
        measurement_fct,
        sleep_between_tests=.01,
        goal_accuracy=10,
        accuracy_miss_repeat_count=4,
        *args, **kwargs
        ):
    """ Repeats the measurement_fct call <repetitions> times and
    returns min, max, median, mean, sd. Repeats the call if accuracy
    not met and returns most accurate result for many iterations
    """
    def cleanup_res(res):
        res.update(**kwargs)
        if 'url_list' in res: res.pop('url_list')
        res['identifier'] = measurement_fct.__name__
        return res

    assert not args, "Args not supported. Use kwargs instead"
    run_count = 1
    best_measurement = None
    while True:
        total_time_measurements = []

        for _ in range(repetitions):
            time.sleep(sleep_between_tests) #wait.
            try:
                result = measurement_fct(
                    quiet=True,
                    *args, **kwargs
                )
            except AssertionError:
                continue
            total_time_result = result['total_time_result']
            total_time_measurements.append(total_time_result)

        # sort measurements: slowest results last
        total_time_measurements.sort()

        results = describe_measurements(total_time_measurements)

        rel_accuracy = relative_accuracy(results)

        print(u"{0:30} p={1:2}: {2}{3}".format(
            measurement_fct.__name__,
            kwargs['parallelism'] if 'parallelism' in kwargs else "",
            total_time_measurements,
            " Accuracy: {0}%".format(rel_accuracy) \
                if rel_accuracy > goal_accuracy else ""
        ))

        if (not best_measurement
            or rel_accuracy < relative_accuracy(best_measurement)
            ):
            best_measurement = results

        if rel_accuracy < goal_accuracy:
            return cleanup_res(results)

        if run_count >= accuracy_miss_repeat_count:
            print("Accuracy not met during {0} runs. "
                "Returning best result {1}%".format(
                accuracy_miss_repeat_count,
                relative_accuracy(best_measurement)
            ))
            return cleanup_res(best_measurement)

        print("Accuracy not met. Retrying measurement...")
        run_count += 1


def get_actor_list(actor_source, limit):
    """ Returns a list of actors registered at actor_source
    url of length limit """
    import urllib2
    import json

    actor_urls_json = urllib2.urlopen(actor_source).read()

    # convert to str because otherwise pycurl will fail
    actor_urls = [str(url) for url in json.loads(actor_urls_json)]
    print("Real known actors: {0}".format(len(actor_urls)))

    if len(actor_urls) < limit:
        print("Reusing actors. Maybe start more real actors")
    while len(actor_urls) < limit:
        actor_urls.extend(actor_urls)
    return actor_urls[:limit]
