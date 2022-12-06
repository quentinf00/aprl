from pathlib import Path
import glob
import toolz
import subprocess
import re
import git
from dvc.api import DVCFileSystem
from omegaconf import OmegaConf

def safy(filt_fn):
    def safe_fn(*args, **kwargs):
        try:
            return filt_fn(*args, **kwargs)
        except:
            return False
    return safe_fn


filter_xp = lambda d: OmegaConf.select(OmegaConf.load('.' + d + '/.hydra/hydra.yaml'), key='hydra.runtime.choices.xp')=='tuto'

fs = DVCFileSystem('.')
folders = fs.find('/outputs', maxdepth=2, withdirs=True)

len(folders)
len(list(toolz.pipe(
    folders, 
    toolz.curried.filter(safy(filter_xp))
)))

outs = list(Path('outputs').glob('*'))
toto.match(str(outs[0]))





