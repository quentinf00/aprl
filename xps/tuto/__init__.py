from pathlib import Path
import hydra.core.config_store

cs = hydra.core.config_store.ConfigStore().instance()
#toto
cs.store(
    'tuto',
    dict(
        params={'my_param': 2},
        entrypoints=[
            dict(
            _target_='builtins.print',
            _args_=['output dir ${hydra:runtime.output_dir}'],
            ),
            dict(
            _target_='xps.tuto.repeat',
            path_in='data/my_dep.csv',
            path_out='${hydra:runtime.output_dir}/outs/out.csv',
            times='${params.my_param}',
        )]
    ),
    group='xp',
    package='_global_'
)



def repeat(path_in, path_out, times):
    txt = Path(path_in).read_text()
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(path_out).write_text(txt * times)


