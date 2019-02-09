
# Test Fixtures

This directory contains necessary data to run automated unit tests.

During execution, `wavectl` reaches out to your specified Wavefront server
using the [Wavefront API](https://docs.wavefront.com/wavefront_api.html).
However, during automated test execution, we do not want to reach out to a live
Wavefront server. Instead, the json state of some selected alerts and
dashboards are saved in json files in this directory. The json representation
in files are in the same format as a Wavefront server returns them via http
calls.

During unit test execution, the test functions read the json files in this
directory and "mock" the behavior of a Wavefront server. That way the `wavectl`
unit tests can execute independently from a live running Wavefront server.

As it turns out, Wavefront can change the json representation of alerts or
dashboards any time, without giving much notice to users. For that reason,
whenever a new Wavefront server version is deployed, we would like to update
the json files in this directory to contain the latest representations. With a
new version of Wavefont server, the json state may get new keys, or some keys
may be removed or renamed.

To update the json files in this directory, the user needs to execute the
included `create_test_fixtures.py` script. That script reaches out to the
specified Wavefront server. Then the existing alerts and dashboards in this
directory are written into the Wavefront server. After that, they are read back
and again saved in the same json files in this directory. If anything in the
Wavefront representation has changed, the json files in this directory will
have the same change.


For example to update the json files in-place execute the following from this
directory:

```
./create_test_fixtures.py <wavefront-server-url> <wavefront-server-api-token> alert TestAlerts.json TestAlerts.json
./create_test_fixtures.py <wavefront-server-url> <wavefront-server-api-token> dashboard TestDashboards.json TestDashboards.json
```

An example for `<wavefront-server-url>` is `https://try.wavefront.com`
