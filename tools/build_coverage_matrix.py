#!/usr/bin/env python3
import argparse, yaml, pandas as pd, os, sys

def safe_read_excel(path):
    try:
        if path and os.path.exists(path):
            xls = pd.ExcelFile(path)
            sheets = {name: xls.parse(name) for name in xls.sheet_names}
            return sheets
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}", file=sys.stderr)
    return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ism-map", required=True, help="roles/ism_linux_audit/vars/control_map.yml")
    ap.add_argument("--ccm", default="", help="Cloud controls matrix template (xlsx)")
    ap.add_argument("--ssp", default="", help="System security plan annex template (xlsx)")
    ap.add_argument("--out", required=True, help="Output coverage_matrix.xlsx")
    args = ap.parse_args()

    with open(args.ism_map) as fh:
        controls = yaml.safe_load(fh).get("controls", {})

    # Tab 1: ISM_Checks (from role)
    df_checks = pd.DataFrame([
        {"ControlID": k, "Title": v.get("title",""), "ISMSection": v.get("ref",""), "ImplementedBy": "ism_linux_audit role", "Evidence": "/var/tmp/ism_audit"}
        for k,v in controls.items()
    ]).sort_values("ControlID")

    # Try to ingest user's CCM and SSP annex templates (best-effort)
    ccm_sheets = safe_read_excel(args.ccm)
    ssp_sheets = safe_read_excel(args.ssp)

    # Create a simple mapping tab that shows available sheet names for traceability
    df_refs = pd.DataFrame({
        "Catalogue": ["CCM","SSP Annex"],
        "AvailableSheets": [",".join(ccm_sheets.keys()), ",".join(ssp_sheets.keys())]
    })

    # If CCM has a sheet with 'Control' like columns, try to pull key columns
    df_ccm = pd.DataFrame()
    for name, df in ccm_sheets.items():
        cols = [c for c in df.columns if any(x in str(c).lower() for x in ["control","id","description","requirement"])]
        if cols:
            take = df[cols].copy()
            take.insert(0, "SourceSheet", name)
            df_ccm = pd.concat([df_ccm, take], ignore_index=True)

    # If SSP has a sheet with annex-like control listing, capture some columns
    df_ssp = pd.DataFrame()
    for name, df in ssp_sheets.items():
        cols = [c for c in df.columns if any(x in str(c).lower() for x in ["control","evidence","procedure","responsible","status"])]
        if cols:
            take = df[cols].copy()
            take.insert(0, "SourceSheet", name)
            df_ssp = pd.concat([df_ssp, take], ignore_index=True)

    with pd.ExcelWriter(args.out, engine="openpyxl") as xw:
        df_checks.to_excel(xw, index=False, sheet_name="ISM_Checks")
        df_refs.to_excel(xw, index=False, sheet_name="References")
        if not df_ccm.empty:
            df_ccm.to_excel(xw, index=False, sheet_name="Imported_CCM")
        if not df_ssp.empty:
            df_ssp.to_excel(xw, index=False, sheet_name="Imported_SSP")
    print(f"Wrote coverage matrix to {args.out}")

if __name__ == "__main__":
    main()
