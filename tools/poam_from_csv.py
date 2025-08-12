#!/usr/bin/env python3
import argparse, yaml, csv, datetime

DEFAULT_COLUMNS = [
  "ControlID","Title","Host","Status","Severity","Finding","Recommendation","Owner","DueDate","EvidencePath"
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Merged CSV from merge_reports.py")
    ap.add_argument("--map", required=True, help="roles/ism_linux_audit/vars/control_map.yml")
    ap.add_argument("--out", required=True, help="Output POAM CSV")
    ap.add_argument("--owner", default="System Owner")
    ap.add_argument("--due-days", type=int, default=90)
    args = ap.parse_args()

    with open(args.map) as fh:
        controls = yaml.safe_load(fh).get("controls", {})

    # Build a simple POAM, one row per failed control per host
    today = datetime.date.today()
    due = today + datetime.timedelta(days=args.due_days)

    rows = []
    with open(args.input, newline="") as fh:
        rdr = csv.DictReader(fh)
        for r in rdr:
            ctrl = r["control"]
            result = r["result"].strip().lower() in ("true","1","yes")
            if ctrl.startswith("ISM-") and not result:
                meta = controls.get(ctrl, {})
                rows.append({
                    "ControlID": ctrl,
                    "Title": meta.get("title",""),
                    "Host": r["host"],
                    "Status": "Open",
                    "Severity": "Medium",
                    "Finding": f"{ctrl} not satisfied on {r['host']}",
                    "Recommendation": f"Implement control '{meta.get('title','')}' per ISM section '{meta.get('ref','')}'.",
                    "Owner": args.owner,
                    "DueDate": due.isoformat(),
                    "EvidencePath": "/var/tmp/ism_audit"
                })

    with open(args.out, "w", newline="") as oh:
        wr = csv.DictWriter(oh, fieldnames=DEFAULT_COLUMNS)
        wr.writeheader()
        wr.writerows(rows)
    print(f"Wrote POAM with {len(rows)} rows to {args.out}")

if __name__ == "__main__":
    main()
