__all__ = ['__version__', 'get_version']

version_info = (0, 0, 1, 'a', 0)
# format: ('major', 'minor', 'micro', 'releaselevel', 'serial')
# __version__ format compatible with distutils2.version.NormalizedVersion


def get_version():
    "Returns the version as a human-format string."
    version = '%d.%d.%d' % (version_info[:3])
    # add revision info if not final version
    if version_info[3] != 'f':
        import os

        version = '%d.%d.%d%s%d' % version_info
        dir = os.path.abspath(os.path.dirname(__file__))
        hg_dir = os.path.normpath(os.path.join(dir, '../'))
        if os.path.isdir(os.path.join(hg_dir, '.hg')):
            hg_rev = 'dev0'  # unknown version
            try:
                from mercurial import ui, hg, error
            except ImportError:
                pass
            else:
                try:
                    repo = hg.repository(ui.ui(), hg_dir)
                    c = repo['tip']
                    hg_rev = 'dev%s' % (c.rev())
                except error.RepoError:
                    pass
            version = '%s.%s' % (version, hg_rev)
    return version

__version__ = get_version()
