from pathlib import Path
import unittest


class DeploymentConfigTests(unittest.TestCase):
    def test_container_runs_unprivileged_with_healthcheck(self):
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
        self.assertIn("USER app", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)
        self.assertIn('scripts.run_town_ui", "--production', dockerfile)

    def test_compose_persists_results_and_requires_access_token(self):
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("mind-virus-data:/app/results", compose)
        self.assertIn("MIND_VIRUS_ACCESS_TOKEN:?", compose)

    def test_ci_runs_tests_and_builds_container(self):
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("docker/build-push-action@v6", workflow)

    def test_recovery_runbook_and_drill_exist(self):
        runbook = Path("docs/production-runbook.md").read_text(encoding="utf-8")
        drill = Path("scripts/validate_phase13_recovery.py").read_text(encoding="utf-8")
        self.assertIn("Incident recovery", runbook)
        self.assertIn("ProductionStore.restore", drill)

    def test_render_staging_blueprint_has_durable_storage_and_health_gate(self):
        blueprint = Path("render.yaml").read_text(encoding="utf-8")
        self.assertIn("runtime: docker", blueprint)
        self.assertIn("autoDeployTrigger: checksPass", blueprint)
        self.assertIn("healthCheckPath: /api/v1/health", blueprint)
        self.assertIn("mountPath: /app/results", blueprint)
        self.assertIn("generateValue: true", blueprint)
        self.assertIn("MIND_VIRUS_TICK_SECONDS", blueprint)


if __name__ == "__main__":
    unittest.main()
