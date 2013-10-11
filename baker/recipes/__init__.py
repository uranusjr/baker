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
        return tar.getnames()[0]
    raise NotImplementedError('Cannot extract', filename)


class Recipe(object):
    """Base class for all baking recipes"""

    version = None
    url = None
    homepage = None
    checksum = None

    # Path info to use when compiling. Supplied at runtime.
    prefix = None

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
        assert os.path.exists(filename)
        return os.path.join(self.name, filename)


    def install(self):
        print(os.getcwd())
        raise NotImplementedError('Recipe must implement method "install"')

    def uninstall(self):
        # TODO: Remove baked loaf from the shelf
        pass
