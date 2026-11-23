import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(__file__)
SCRIPT = os.path.join(HERE, "..", "scripts", "linkedin_cards.js")
FIXTURE = os.path.join(HERE, "fixtures", "linkedin_cards_2026.json")

# Runs the real browser script in node against a minimal fake DOM built from the fixture.
RUNNER = r"""
const fs = require('fs'), vm = require('vm');
const [script, fixture] = process.argv.slice(1);
const fx = JSON.parse(fs.readFileSync(fixture, 'utf8'));
const el = c => ({
  getAttribute: n => (n === 'componentkey' ? c.componentkey : null),
  innerText: c.text, querySelector: () => null, parentElement: null,
});
const nodes = fx.cards.flatMap(c => [el(c), el(c)]);  // outer and inner share the key
const document = {
  body: {},
  querySelector: s => (s.includes('job-card-component-ref-') ? nodes[0] : null),
  querySelectorAll: s => (s.includes('job-card-component-ref-') ? nodes : []),
};
const ctx = vm.createContext({ document, setTimeout: f => f() });
vm.runInContext(fs.readFileSync(script, 'utf8'), ctx).then(out => console.log(out));
"""


@unittest.skipUnless(shutil.which("node"), "node not installed")
class LinkedinCards(unittest.TestCase):
    def test_search_results_layout_2026(self):
        out = subprocess.run(["node", "-e", RUNNER, SCRIPT, FIXTURE], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        with open(FIXTURE, encoding="utf-8") as f:
            expected = json.load(f)["expected"]
        self.assertEqual(out.stdout.strip(), f"N={len(expected)};" + "|".join(expected))


if __name__ == "__main__":
    unittest.main()
