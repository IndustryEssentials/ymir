#    Modified from GitPython CMD wrapper:
#    https://github.com/gitpython-developers/GitPython/blob/master/git/cmd.py


from typing import Any


class BaseScm():
    """
    Base class providing an interface to retrieve attribute values upon
    first access.
    """

    def __getattr__(self, attr: Any) -> Any:
        self._set_cache_(attr)
        # will raise in case the cache was not created
        return object.__getattribute__(self, attr)

    def _set_cache_(self, attr: Any) -> Any:
        """
        This method should be overridden in the derived class.
        """
        pass
