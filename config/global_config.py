from attrdict import AttrDict

__all__ = ['config']

config = None


def init():
    global config
    if config is None:
        config = AttrDict()
        config.loaded = True
