# -*- coding: utf-8 -*-

from . import Recipe


class Fart(Recipe):
    url = 'http://downloads.sourceforge.net/project/fart-it/fart-it/1.99b/fart199b_source.zip'

    def install(self):
        self.system('gcc', 'fart.cpp', 'fart_shared.c', 'wildmat.c')
        self.system('copy', 'a.exe', self.bin)
