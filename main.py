import hydra
from omegaconf import OmegaConf, open_dict

def store(key, obj_cfg, _s={}):
    return _s.setdefault(key, obj_cfg())

OmegaConf.register_new_resolver(
    "_singleton", 
    lambda k: dict( _target_='main.store', key=k, obj_cfg='${'+k+'}',),
    replace=True
)

OmegaConf.register_new_resolver(
    "singleton", lambda k: '${oc.create:${_singleton:'+k+'}}', replace=True
)

def make_partial(obj_cfg):
    with open_dict(obj_cfg):
        obj_cfg._partial_=True
    return obj_cfg

OmegaConf.register_new_resolver( "partial", make_partial, replace=True)


@hydra.main(config_path='config', config_name='main', version_base='1.2')
def main(cfg):
    OmegaConf.resolve(cfg)
    OmegaConf.resolve(cfg)
    hydra.utils.call(cfg.entrypoints)

if __name__ == '__main__':
    main()

