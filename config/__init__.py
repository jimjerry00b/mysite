# Use PyMySQL as the MySQLdb driver. It's pure-Python, so it installs without a
# compiler on both the server (Python 3.12) and local dev (Python 3.14).
# Django 6 requires the driver to report version_info >= (2, 2, 1); PyMySQL
# implements the needed MySQLdb API, so we spoof the version to pass that gate.
try:
    import pymysql

    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    # PyMySQL isn't installed (e.g. when using the SQLite fallback) -- fine.
    pass
