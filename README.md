# Internal Platform Service Reference

This is a small, tested reference implementation prepared for the **Senior Platform Engineer** opportunity surfaced by Hire Feed for a Micro1 internal-platform role. It demonstrates how I would treat an internal platform as a developer-facing product: opinionated defaults, explicit contracts, repeatable guardrails, and a clean boundary between policy and cloud-specific provisioning.

It is deliberately not presented as a Micro1 codebase or a deployment into their environment.

## The problem it addresses

A platform team commonly receives workload requests that are incomplete or unsafe to ship directly: a mutable image, one production replica, unclear ingress, or unscoped database access. The useful platform abstraction is not “a YAML generator”; it is a contract that converts the request into an auditable plan while blocking unsafe inputs early.

`src/platform_contract.py` models that contract.

```text
Developer request
      |
      v
Validation (name, pinned image, replica count)
      |
      v
Environment-aware platform policy
      |
      v
Plan: namespace + deployment capacity + access posture + release checks
      |
      v
Environment adapter (Kubernetes / Terraform / cloud API)
```

The last step is intentionally out of scope. It varies by organization; keeping it behind a small adapter lets the platform logic remain testable and portable across AWS, GCP, or Azure.

## What the implementation shows

- **Reproducible delivery:** container images must be immutable digest references; `latest` is rejected.
- **Production safety:** production workloads receive at least two replicas and must satisfy change approval, SLO/capacity, and rollback-readiness checks.
- **Secure defaults:** ingress is internal unless a request explicitly requires public exposure; database access becomes an explicit least-privilege policy.
- **Developer experience:** the output is a concise `PlatformPlan`, suitable for a pull-request comment, a deployment controller, or a GitOps renderer.
- **Tested behaviour:** tests cover resilient production defaults, private-by-default ingress, and rejection of mutable images.

## Run it

```bash
python3 -m unittest discover -s tests -v
```

No external packages or credentials are required.

## How I would take this to production

1. Expose the request as a versioned API or a Backstage-style self-service template.
2. Persist the resulting plan with the request ID and actor for auditability.
3. Render approved plans into a GitOps repository; an environment-specific controller reconciles them.
4. Connect the capacity check to real SLO, error-budget, and cluster utilization signals.
5. Enforce policy as code at CI and admission time, then measure developer lead time and override rates to improve the platform product.

This approach pairs well with Python or Go service boundaries, Kubernetes-based workloads, and cloud-managed platform services without coupling the core contract to one provider.

## Candidate links

- LinkedIn: https://www.linkedin.com/in/rahul-h-bhatia/
- Portfolio: https://rahulhbhatia.vercel.app
- Credly: https://www.credly.com/users/rahul-h-bhatia/badges
