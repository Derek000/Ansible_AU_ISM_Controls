#!/usr/bin/env python3
import argparse, os, csv, glob

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", required=True, help="Report dir containing host report.csv files")
    ap.add_argument("--out", required=True, help="Merged CSV path")
    args = ap.parse_args()

    fields = ["host","control","result"]
    rows = []
    for f in glob.glob(os.path.join(args.reports, "**/report.csv"), recursive=True):
        with open(f, newline="") as fh:
            rdr = csv.DictReader(fh)
            for r in rdr:
                rows.append({k:r.get(k,"") for k in fields})
    with open(args.out, "w", newline="") as oh:
        wr = csv.DictWriter(oh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)
    print(f"Merged {len(rows)} rows into {args.out}")

if __name__ == "__main__":
    main()
