#!/usr/bin/env python3
"""Install the Hirepair skill by symlinking skills/hirepair into a skills folder. Stdlib only.

Usage: python3 scripts/install_skill.py [--target ~/.claude/skills] [--uninstall]

Only creates or removes one symlink named 'hirepair'; never overwrites a real file or folder.
The skill still reads prompts/docs from this repo, so keep the repo where it is.
"""
import argparse
import os
import sys

SRC = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "skills", "hirepair"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="~/.claude/skills")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()
    target = os.path.expanduser(a.target)
    link = os.path.join(target, "hirepair")

    if a.uninstall:
        if os.path.islink(link):
            os.remove(link)
            print(f"removed {link}")
            return 0
        print(f"nothing to remove: {link} is not a symlink created by this script")
        return 1

    if not os.path.isfile(os.path.join(SRC, "SKILL.md")):
        print(f"error: {SRC}/SKILL.md not found")
        return 1
    if os.path.lexists(link):
        if os.path.islink(link) and os.path.realpath(link) == SRC:
            print(f"already installed: {link}")
            return 0
        print(f"error: {link} already exists and is not this skill; remove it yourself first")
        return 1
    os.makedirs(target, exist_ok=True)
    os.symlink(SRC, link)
    print(f"installed {link} -> {SRC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
