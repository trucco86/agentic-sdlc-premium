from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class GovernanceTests(unittest.TestCase):
    def test_skill_and_agent_contracts_exist(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/agentic-editorial-curation/SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "editorial/agent-workflow.md").read_text(encoding="utf-8")
        for role in ("learning-architect", "knowledge-curator", "content-author", "technical-reviewer", "editorial-qa", "release-guardian"):
            self.assertIn(role, agents)
        for requirement in ("source_run_id", "approved", "incorporated", "Definition of Done"):
            self.assertIn(requirement, skill)
        for requirement in ("Aprovação explícita", "source_run_id=null", "published"):
            self.assertIn(requirement, workflow)
    def test_site_workflow_has_no_publish_step(self):
        workflow = (ROOT / ".github/workflows/site-prototype.yml").read_text(encoding="utf-8")
        self.assertNotIn("deploy-pages", workflow)
        self.assertNotIn("pages: write", workflow)
        self.assertNotIn("push origin main", workflow)

if __name__ == "__main__":
    unittest.main()
