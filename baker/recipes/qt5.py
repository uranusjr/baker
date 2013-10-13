# -*- coding: utf-8 -*-

from . import Recipe


class Qt5(Recipe):
    url = 'http://download.qt-project.org/official_releases/qt/5.1/5.1.1/single/qt-everywhere-opensource-src-5.1.1.zip'
    version = '5.1'

    def install(self):
        self.system(
            'configure', '-prefix', self.prefix, '-platform win32-g++',
            '-opensource', '-debug', '-debug-and-release', '-no-vcproj',
            '-no-opengl', '-no-openvg', '-nomake examples'
        )
        self.system('mingw32-make')
        self.system('mingw32-make', 'install')
