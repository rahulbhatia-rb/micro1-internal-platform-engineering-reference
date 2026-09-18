import unittest

from src.platform_contract import WorkloadRequest, build_plan


class PlatformContractTests(unittest.TestCase):
    def request(self, **overrides):
        base = dict(
            service="catalog-api",
            environment="development",
            image="registry.example/catalog@sha256:abc123",
            replicas=1,
        )
        base.update(overrides)
        return WorkloadRequest(**base)

    def test_production_requires_resilience_and_release_gates(self):
        plan = build_plan(self.request(environment="production"))
        self.assertEqual(plan.deployment_replicas, 2)
        self.assertIn("slo-capacity-check", plan.required_checks)
        self.assertIn("rollback-ready", plan.required_checks)

    def test_non_production_is_internal_by_default(self):
        plan = build_plan(self.request())
        self.assertEqual(plan.ingress, "internal")
        self.assertEqual(plan.namespace, "development-catalog-api")

    def test_unpinned_image_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "pinned by digest"):
            build_plan(self.request(image="registry.example/catalog:latest"))


if __name__ == "__main__":
    unittest.main()
