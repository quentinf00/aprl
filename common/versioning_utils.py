from git.repo import Repo as GitRepo
from hydra.experimental.callback import Callback
import os
from git import IndexFile
from pathlib import Path



def commit_cwd(
        branch,
        message,
        repo=None,
        cwds=None,
        ignore_cwds=None,
        working_tree_dir=None,
        additional_parent_commits=None,
        start_index='HEAD',
    ):
    # TODO : full test suite with fixtures
    # TODO : test with Keyboard interrupt
    repo = repo or GitRepo('.')
    if working_tree_dir is not None:
        repo._working_tree_dir = working_tree_dir
    start_index = IndexFile.from_tree(repo, start_index)
    index = IndexFile(repo)
    log_branch = getattr(repo.heads, branch, False) or repo.create_head(branch)

    to_add = (
                 set(repo.untracked_files)
                 | set([d.a_path or d.b_path for d in index.diff(None) if d.change_type != 'D'])
                 | set([d.a_path or d.b_path for d in index.diff(repo.head.commit) if d.change_type != 'A'])
         ) - set([d.a_path or d.b_path for d in index.diff(None) if d.change_type == 'D'])

    if cwds is not None:
        filt_to_add = set()
        for cwd in cwds:
            filt_to_add |= set(p for p in to_add if Path(cwd) in (Path(repo.working_dir) / p).parents)
    else: filt_to_add = to_add

    if ignore_cwds is not None:
        for cwd in ignore_cwds:
            filt_to_add -= set(p for p in to_add if Path(cwd) in (Path(repo.working_dir) / p).parents)

    start_index.add(
        [str((Path(repo.working_dir)/Path(p)).relative_to(repo.working_tree_dir))
            for p in filt_to_add],
        force=False,
        write=False,
        write_extension_data=True,
    )

    parent_commits = [log_branch.commit]
    if additional_parent_commits is not None:
        parent_commits += additional_parent_commits

    log_commit = start_index.commit(message, parent_commits=parent_commits, head=False)
    log_branch.commit = log_commit
    return str(log_commit)

def no_ignore(fn):
    gitignore = Path('.gitignore')
    if gitignore.exists():
        content = gitignore.read_text()
        gitignore.unlink()
        try:
            out = fn()
            gitignore.write_text(content)
            return out
        finally:
            gitignore.write_text(content)
    else:
        return fn()

def with_symlinks(srcs, dst_dir, fn):
    symlinks = []
    try:
        for src in srcs:
            sl = Path(f'{dst_dir}/{src}')
            tgt = Path(src)

            sl.symlink_to(tgt, target_is_directory=tgt.is_dir())
            print(Path(f'{dst_dir}/src').exists())
            symlinks.append(sl)
        fn()
    finally:
        for sl in symlinks:
            os.unlink(sl)

class VersioningCallback(Callback):
    def __init__( self, commit_fn, msg_fn):
        self.src_ci = None
        self.commit_fn=commit_fn
        self.msg_fn=msg_fn
    
    def on_job_start(self, config):
        if self.src_ci is None:
            self.src_ci = self.commit_fn(message=self.msg_fn(config))
        else:
            print(self.src_ci)
            self.commit_fn(message=self.msg_fn(config), cwds=[], start_index=self.src_ci)

def git_log_grep(repo, branch, grep):
    return str(next(repo.iter_commits(
        rev=branch,
        grep=grep
    )))
