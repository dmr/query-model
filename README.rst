query-model
===========

An model and different implementations for a parallel request.


Installation
------------

Can be installed via pip from this repository::

    pip install git+http://github.com/dmr/query-model.git#egg=query_model

Usage
-----

The package provides two CLI utils: predict_lookup_time and query_urls.

predict_lookup_time predicts the time a lookup of urls should take and accept parameters to adjust the simulation parameters accordingly.

query_urls allows to try different parallel query implementations and compare the results to the prediction.

Both commands accept -h to provide detailed usage information
