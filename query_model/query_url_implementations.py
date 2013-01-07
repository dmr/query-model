# -*- coding: utf-8 -*-
from functools import wraps
import time
import multiprocessing
import urllib2

from cStringIO import StringIO
import pycurl2 as pycurl
import human_curl
from human_curl.async import default_success_callback


def url_get(uri):
    return urllib2.urlopen(uri, timeout=3).read()


def curl_get(url, return_none=True):
    curl_obj = pycurl.Curl()
    curl_obj.setopt(pycurl.URL, url)
    curl_obj.setopt(pycurl.HTTPGET, True)
    body = StringIO()
    curl_obj.setopt(pycurl.WRITEFUNCTION, body.write)
    curl_obj.perform()
    if return_none:
        status_code = curl_obj.getinfo(pycurl.HTTP_CODE)
        assert status_code == 200, status_code
        curl_obj.close()
        return
    return body


def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        #print func.__name__ + " was called"
        quiet = False
        if 'quiet' in kwargs and kwargs.pop('quiet'):
            quiet = True
        ret = func(*args, **kwargs)
        if not quiet:
            print u"{0:30} p={1:2} url_count={2}: {3}".format(
                func.__name__,
                kwargs['parallelism'] if 'parallelism' in kwargs else "",
                len(kwargs['url_list']) if 'url_list' in kwargs else "",
                ret['total_time_result']
            )
        return ret
    return with_logging


@logged
def run_urllib2_multiprocessing(parallelism, url_list):
    worker_count = parallelism
    pool = multiprocessing.Pool(processes=worker_count)

    time_before = time.time()
    result = pool.map_async(url_get, url_list)
    result.wait()
    total_time_result = time.time() - time_before

    pool.close()
    pool.join()
    assert not multiprocessing.active_children()

    return {'total_time_result':total_time_result}


@logged
def run_curl_multiprocessing(parallelism, url_list):
    worker_count = parallelism

    pool = multiprocessing.Pool(processes=worker_count)
    time.sleep(.2)

    time_before = time.time()
    pool.map(curl_get, url_list)
    total_time_result = time.time() - time_before
    # don't set chunk size 1 for pool.map!

    pool.close()
    pool.join()
    assert not multiprocessing.active_children()

    return {'total_time_result':total_time_result}


@logged
def run_curl_single_process(url_list, parallelism):
    time_before = time.time()
    _result = [curl_get(u) for u in url_list]
    total_time_result = time.time() - time_before

    return {'total_time_result':total_time_result}


@logged
def run_pycurl_async(url_list, parallelism):
    reqs = []

    # Build multi-request object
    m = pycurl.CurlMulti()
    for url in url_list:
        response_body = StringIO()
        handle = pycurl.Curl()
        handle.setopt(pycurl.URL, url)
        handle.setopt(pycurl.WRITEFUNCTION, response_body.write)
        m.add_handle(handle)
        reqs.append((handle, response_body, url))

    # Perform multi-request
    # Code copied pycurl docs with modification to explicitly
    # set num_handles before outer while loop
    SELECT_TIMEOUT = .01
    num_handles = len(reqs)

    time_before = time.time()
    while num_handles:
        ret = m.select(SELECT_TIMEOUT)
        if ret == -1:
            continue
        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
    total_time_result = time.time() - time_before

    return {'total_time_result':total_time_result}


@logged
def run_human_curl_async(parallelism, url_list):
    def fail_cb(*a, **kw):
        print "fail_cb", a, kw
        assert 0, "Error executing AsyncClient"

    async_client = human_curl.AsyncClient(
        size=parallelism,
        success_callback=default_success_callback,
        fail_callback=fail_cb,
        sleep_timeout=.01
    )
    for u in url_list:
        async_client.get(u)

    time_before = time.time()
    async_client.start()
    total_time_result = time.time() - time_before

    # set by default_success_callback
    for r in async_client.responses:
        assert r._response_info['HTTP_CODE'] == 200, \
            u"{0} returned {1}".format(r.url,
                r._response_info['HTTP_CODE'])

    return {'total_time_result':total_time_result}
