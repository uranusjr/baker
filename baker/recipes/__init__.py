# -*- coding: utf-8 -*-

import tempfile
import os
import subprocess
import urllib.request
import shutil
import tarfile
import zipfile


def _extract_file(filename, packagename):
    print('Extracting', filename)
    if filename.endswith('.zip'):
        zipf = zipfile.ZipFile(filename)
        first = zipf.namelist()[0].split('/')[0]    # Don't use backslashes!
        zipf.extractall(packagename)
    elif filename.endswith('.tar.gz') or filename.endswith('.tar.bz2'):
        tar = tarfile.open(filename, 'r:*')
        first = tar.getnames()[0].split('/')[0]
        tar.extractall(packagename)
    else:
        raise NotImplementedError('Cannot extract', filename)
    root = os.path.join(os.getcwd(), packagename, first)
    if not os.path.isdir(root):
        root = os.path.dirname(root)
    return root


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
        self.name = name.lower()
        self.prefix = os.path.join(prefix.lower(), self.version)
        self.shelf = shelf.lower()

    @property
    def bin(self):
        return _get_or_create_dir(self.prefix, 'bin')

    @property
    def lib(self):
        return _get_or_create_dir(self.prefix, 'lib')

    @property
    def include(self):
        return _get_or_create_dir(self.prefix, 'include')

    @property
    def shelf_bin(self):
        return _get_or_create_dir(self.shelf, 'bin')

    @property
    def shelf_lib(self):
        return _get_or_create_dir(self.shelf, 'lib')

    @property
    def shelf_include(self):
        return _get_or_create_dir(self.shelf, 'include')

    def _get_targets(self):
        return (
            (self.bin, self.shelf_bin),
            (self.lib, self.shelf_lib),
            (self.include, self.shelf_include)
        )

    def get_source(self):
        """Retrieve source code for the recipe

        Recipes should provide a class variable ``url``, which is used in this
        method to download the source to the user's temp directory. The
        downloaded archive is then extracted. if the extraction succeeds, the
        working directory is changed to the first path returned by the archive.
        """
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

    def system(self, *cmds, **flags):
        cmd = ' '.join(cmds)
        print('>>>', cmd)
        try:
            with open(os.devnull, 'wb') as devnull:
                subprocess.check_call(cmds, stdout=devnull, shell=True)
        except Exception:
            if not flags.get('skip_on_error', False):
                raise

    def install(self):
        raise NotImplementedError('Recipe must implement method "install"')

    def uninstall(self):
        self.unlink()
        print('Removing {f}'.format(f=self.prefix))
        shutil.rmtree(self.prefix)

    def link(self):
        for pair in self._get_targets():
            for i in os.listdir(pair[0]):
                canonical = os.path.join(pair[0], i)
                target = os.path.join(pair[1], i)
                args = ['mklink']
                if os.path.isdir(canonical):
                    args.append('/d')
                args += [target, canonical]
                print('Putting {f} onto shelf...'.format(f=i))
                self.system(*args, skip_on_error=True)

    def unlink(self):
        for target in self._get_targets():
            for i in os.listdir(target[1]):
                canonical = os.path.join(target[1], i)
                if (os.path.islink(canonical) and
                        os.readlink(canonical).lower().startswith(target[0])):
                    print('Removing {f}'.format(f=canonical))
                    os.remove(canonical)
