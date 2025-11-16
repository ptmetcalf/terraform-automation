# Terraform Module Standards

These rules apply to every change produced by the agents:

## 1. Module structure
- All Terraform resources must live in re-usable modules under `modules/<domain>/<resource>`.
- Root stacks (`stacks/<env>`) may only instantiate modules and set environment-specific variables.
- Each module must include:
  - `main.tf` with resources and data sources.
  - `variables.tf` defining typed inputs with descriptions and validation.
  - `outputs.tf` exposing all identifiers required by other modules.
  - `README.md` documenting purpose, inputs, outputs, examples.

## 2. Naming & tags
- Use Azure CAF naming via the naming tool; no ad-hoc names.
- Apply standard tags: `owner`, `environment`, `cost_center`, `ticket_id`.
- Variables for tags should default to an object map to encourage propagation.

## 3. Versioning & providers
- Declare provider requirements and module versions in `versions.tf`.
- Lock provider versions to avoid drift.
- Pin remote modules via versions or commit SHAs.

## 4. Testing & validation
- Run `terraform fmt`, `terraform validate`, and security scans (Checkov/tfsec) per module.
- For complex modules add `examples/` with smoke tests executed via `terraform plan` in CI.

## 5. GitOps workflow
- Never edit compiled state files.
- Changes must go through the GitOps agent which enforces branch naming: `<ticket-id>/<description>`.
- One ticket per branch; do not batch unrelated module updates.

## 6. Review expectations
- Architects confirm module reuse before coding starts.
- Coding agent must call the Terraform standards tool to ensure latest rules are respected and reference the doc in user-facing summaries.
- Plan reviewers reject changes violating these standards.
