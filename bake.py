# -*- coding: utf-8 -*-

"""Main baking script

Called by the main entry point ``bake.bat``.
"""

import importlib
import os
import os.path
import sys
from baker.recipes import Recipe


BAKER_ROOT = os.path.dirname(__file__)


def _get_recipe_instance(name):
    """Get recipe class for :name and instantiate"""
    recipe_name = name.lower()
    module = importlib.import_module(
        '.'.join(['baker', 'recipes', recipe_name])
    )
    names = [n for n in dir(module)
                if n.lower() == recipe_name
                and issubclass(getattr(module, n), Recipe)
                and getattr(module, n) is not Recipe]
    assert len(names) == 1
    prefix = os.path.join(BAKER_ROOT, 'oven', names[0].lower())
    return getattr(module, names[0])(
        recipe_name, prefix, os.path.join(BAKER_ROOT, 'shelf')
    )


def install(argv):
    """Runs the installing subcommand

    :param argv: A list of arguments the user supplied after *install*. For
        example, ``bake install me`` yields ``argv == ['me']``.
    """
    recipe = _get_recipe_instance(argv.pop(0))
    os.chdir(recipe.get_source())
    recipe.install()
    recipe.link()


def main(argv):
    """Main entry point for ``bake``

    :param argv: A list of arguments the user supplied when executing this
        script. This is independent to ``sys.argv`` (actually a *copy* of it),
        so you can modify it freely without breaking anything not using it.
    """
    argv.pop(0)     # Path to this file
    subcommand = argv.pop(0)

    if subcommand == 'install':
        install(argv)
    else:
        raise SyntaxError('No matching command: %s' % subcommand)


if __name__ == '__main__':
    main(sys.argv.copy())
