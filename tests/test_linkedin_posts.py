import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "linkedin_posts.js")
FIXTURE = os.path.join(HERE, "fixtures", "linkedin_posts_2026.json")

# Runs the real browser script in node against a minimal fake DOM built from the fixture.
RUNNER = r"""
const fs = require('fs'), vm = require('vm');
const [script, fixture] = process.argv.slice(1);
const fx = JSON.parse(fs.readFileSync(fixture, 'utf8'));
const nodes = fx.posts.map(p => ({ getAttribute: () => p.componentkey, innerText: p.text }));
const document = {
  body: { scrollHeight: 0 },
  querySelectorAll: s => nodes.filter(n => s.includes('componentkey^="expanded"') && n.innerText && n.getAttribute().startsWith('expanded')),
};
const ctx = vm.createContext({ document, window: { scrollTo() {} }, setTimeout: f => f() });
vm.runInContext(fs.readFileSync(script, 'utf8'), ctx).then(out => console.log(out));
"""


@unittest.skipUnless(shutil.which("node"), "node not installed")
class LinkedinPosts(unittest.TestCase):
    def test_age_keyword_emails_and_reposts(self):
        out = subprocess.run(["node", "-e", RUNNER, SCRIPT, FIXTURE], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        with open(FIXTURE, encoding="utf-8") as f:
            expected = json.load(f)["expected"]
        self.assertEqual(out.stdout.strip(), f"N={len(expected)};" + "|".join(expected))


if __name__ == "__main__":
    unittest.main()
