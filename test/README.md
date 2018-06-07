
# Tests

`wavectl` project primarily uses
[unittest](https://docs.python.org/2/library/unittest.html) framework from the
python standard library.

[unittest.mock](https://docs.python.org/3/library/unittest.mock.html) is also
heavily utilized. While testing the `wavectl` command line tool, we do not want
to reach out to a running Wavefront remote server. Instead, the tests read the
json blobs of wavefront resources from the `fixtures` directory and "mock" the
behavior of a wavefront server.

For executing test executables [Makefile.test](https://github.com/box/Makefile.test)
is used.

