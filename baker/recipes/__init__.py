# -*- coding: utf-8 -*-

import tempfile
import os
import os.path
import urllib.request
import tarfile
import zipfile


def _extract_file(filename, packagename):
    print('Extracting', filename)
    if filename.endswith('.zip'):
        zipf = zipfile.ZipFile(filename)
        zipf.extractall(packagename)
        return zipf.namelist()[0]
    elif filename.endswith('.tar.gz') or filename.endswith('.tar.bz2'):
        tar = tarfile.open(filename, 'r:*')
        tar.extractall(packagename)
        root = tar.getnames()[0]
        if not os.path.isdir(root):
            root = os.path.dirname(root)
        return root
    raise NotImplementedError('Cannot extract', filename)


def _get_or_create_dir(*components):
    path = os.path.join(*components)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


class Recipe(object):
    """Base class for all baking recipes"""

    # Variables that subclasses MUST provide
    version = None
    url = None
    homepage = None
    checksum = None

    def __init__(self, name, prefix, shelf):
        """Initialize a Recipe instance

        Many runtime-determined paths defined here can be used for building.
        All of the parameters passed here are assigned as instance variables,
        so that you can used them in various stages of the recipe's lifespan.

        :param name: Name of the recipe.
        :param prefix: Prefix for the recipe. Useful when calling the configure
            script during building. There are also some properties that are
            based on this variable that can be useful, e.g. ``self.bin``,
            ``self.lib``.
        :param shelf: The root of bakery shelf. Usually you do not need
            to access this variable directly, but would use properties based
            on it instead, e.g. ``self.shelf_bin`` and ``self.shelf_lib``.
            ``
        """
        self.name = name
        self.prefix = prefix
        self.shelf = shelf

    @property
    def bin(self):
        return _get_or_create_dir(self.prefix, 'bin')

    @property
    def lib(self):
        return _get_or_create_dir(self.prefix, 'lib')

    @property
    def shelf_bin(self):
        return _get_or_create_dir(self.shelf, 'bin')

    @property
    def shelf_lib(self):
        return _get_or_create_dir(self.shelf, 'lib')

    def get_source(self):
        os.chdir(tempfile.gettempdir())
        cachename = os.path.basename(self.url)
        if not os.path.exists(cachename):
            print('Downloading from', self.url)
            urllib.request.urlretrieve(self.url, cachename)
        else:
            print('Cache found in', cachename)
        # TODO: Checksum package
        filename = _extract_file(cachename, self.name)
        path = os.path.join(self.name, filename)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        assert os.path.exists(path)
        return path


    def system(self, *cmds):
        cmd = ' '.join(cmds)
        code = os.system(cmd)
        if code:
            raise SystemError(
                'System command `%s` failed with exit code %d' % (cmd, code)
            )


    def install(self):
        print(os.getcwd())
        raise NotImplementedError('Recipe must implement method "install"')

    def uninstall(self):
        # TODO: Remove baked loaf from the shelf
        pass

    def link(self):
        for i in os.listdir(self.bin):
            canonical = os.path.join(self.bin, i)
            target = os.path.join(self.shelf_bin, i)
            args = ['mklink']
            if os.path.isdir(canonical):
                args.append('/d')
            args += [target, canonical]
            print('Putting {f} onto shelf...'.format(f=i))
            self.system(*args)
            # TODO: Need to track the links so that we can uninstall them
