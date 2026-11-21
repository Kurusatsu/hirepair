import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "install_skill.py")
SKILL = os.path.join(os.path.dirname(__file__), "..", "skills", "hirepair", "SKILL.md")


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)


class InstallSkill(unittest.TestCase):
    def test_install_twice_then_uninstall(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run("--target", d).returncode, 0)
            self.assertTrue(os.path.isfile(os.path.join(d, "hirepair", "SKILL.md")))
            self.assertIn("already installed", run("--target", d).stdout)
            self.assertEqual(run("--target", d, "--uninstall").returncode, 0)
            self.assertFalse(os.path.lexists(os.path.join(d, "hirepair")))

    def test_never_overwrites_existing_folder(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "hirepair"))
            r = run("--target", d)
            self.assertEqual(r.returncode, 1)
            self.assertTrue(os.path.isdir(os.path.join(d, "hirepair")))

    def test_uninstall_refuses_real_folder(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "hirepair"))
            self.assertEqual(run("--target", d, "--uninstall").returncode, 1)
            self.assertTrue(os.path.isdir(os.path.join(d, "hirepair")))

    def test_skill_has_frontmatter(self):
        text = open(SKILL, encoding="utf-8").read()
        self.assertTrue(text.startswith("---\nname: hirepair\ndescription: "))


if __name__ == "__main__":
    unittest.main()
