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
    """Install subcommand

    :param argv: A list of arguments the user supplied after *install*. For
        example, ``bake install me`` yields ``argv == ['me']``.
    """
    recipe = _get_recipe_instance(argv.pop(0))
    os.chdir(recipe.get_source())
    recipe.install()
    recipe.link()


def uninstall(argv):
    """Uninstall subcommand

    :param argv: A list of arguments the user supplied after *uninstall*. For
        example, ``bake uninstall me`` yields ``argv == ['me']``.
    """
    recipe = _get_recipe_instance(argv.pop(0))
    recipe.uninstall()


def link(argv):
    recipe = _get_recipe_instance(argv.pop(0))
    recipe.link()


def unlink(argv):
    recipe = _get_recipe_instance(argv.pop(0))
    recipe.unlink()


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
    elif subcommand == 'uninstall':
        uninstall(argv)
    elif subcommand == 'link':
        link(argv)
    elif subcommand == 'unlink':
        unlink(argv)
    else:
        raise SyntaxError('No matching command: %s' % subcommand)


if __name__ == '__main__':
    try:
        main(sys.argv.copy())
    except Exception as e:
        print(e)
    finally:
        input('Press Enter to end...')
