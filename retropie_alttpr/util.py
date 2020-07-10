import asyncio
import functools
import os
import tempfile


DEFAULT_MEMORY_TMPDIR = os.environ.get('XDG_RUNTIME_DIR', '/dev/shm')


def async_to_sync(fun):
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        return asyncio.run(fun(*args, **kwargs))

    return wrapped


def invert_dict(source):
    """ Invert a dict

    Behavior if multiple values are the same is undefined
    """
    out = {}
    for k, v in source.items():
        out[v] = k

    return out


def dict_no_none(*args, **kwargs):
    orig = dict(*args, **kwargs)
    return dict((k, v) for k, v in orig.items() if v is not None)


def in_memory_tempfile(**kwargs):
    """ Create a named temporary file in the in memory filesystem

    Crappy MicroSD cards and limiting disk IO is a thing in the RaspPi
    community and pyz3r explicitly wants to write to files, not file streams or
    anything like that.

    So we'll use the systemd user tmp folder or /dev/shm.

    If neither of these exist, I think this will error out.
    """
    kwargs.setdefault('dir', DEFAULT_MEMORY_TMPDIR)
    return tempfile.NamedTemporaryFile(**kwargs)
