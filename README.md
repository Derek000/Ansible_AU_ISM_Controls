# ISM Linux Audit – Ansible Role - DRAFT Work In Progress

## Why
Evidence-driven verification of Linux host alignment to ASD ISM controls, producing JSON/CSV/JUnit artefacts and syslog events for chain-of-custody.

## Who
- Ops/SecOps to run and triage.
- IRAP/CISO to ingest artefacts into SAR/POAM and board reporting.

## What
- Audits SSH, logging/SIEM & time, patch posture/EOL, TLS expectations, and backup immutability signals.
- Optional dev-sec/linux-baseline 2.9.0 (InSpec) run for complementary checks.
- Molecule tests for CI.
- Tools to merge reports, generate POAM, and build a coverage matrix against your control catalogue and SSP annex templates.

## Quickstart
```bash
# 1) Install Ansible
python3 -m venv .venv && . .venv/bin/activate
pip install ansible molecule ansible-lint pytest jinja2 pyyaml pandas openpyxl

# 2) Run against inventory
ansible-playbook -i inventory.ini site.yml

# 3) Reports
ls -l /var/tmp/ism_audit

# 4) Merge reports and build POAM
python3 tools/merge_reports.py --reports /var/tmp/ism_audit --out merged.csv
python3 tools/poam_from_csv.py --input merged.csv --map roles/ism_linux_audit/vars/control_map.yml --out poam.csv

# 5) Build coverage matrix (tries to import your uploaded catalogues)
python3 tools/build_coverage_matrix.py   --ism-map roles/ism_linux_audit/vars/control_map.yml   --ccm "/mnt/data/Cloud controls matrix template (June 2025).xlsx"   --ssp "/mnt/data/System security plan annex template (June 2025).xlsx"   --out coverage_matrix.xlsx

# 6) Molecule (local verify of role logic)
molecule -v test
```
