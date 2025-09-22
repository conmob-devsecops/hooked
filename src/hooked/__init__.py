try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0+dev"
__pkg_name__ = "hooked"
__upgrade_interval_seconds__ = 10
