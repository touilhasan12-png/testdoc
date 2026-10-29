#!/usr/bin/env python3
"""Push stage outputs to the user's Google Drive folder TrueCrime_Sample_01_v1.

The CI runner has no Drive credentials (by design - no token is ever committed).
This script therefore only needs rclone on a self-hosted runner, or it prints the exact
files + destination folders so the calling agent can upload them with the Drive connector.
It never fabricates an upload: if no remote is configured it exits 0 with status=manual_push.
"""
import json, os, subprocess, sys

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work")
FOLDERS = {
    "01_research": "1h6y4OLar88Ihr_UDvzkgdYnlXnaUyDpz",
    "02_script": "1uuNwO-XjHxNmrNJQVIhnCHM9fMJvF9Id",
    "03_audio": "1Toaxona3ffhZDkP0Uzz8NCbKHL1ZbS2q",
    "04_visuals": "1Q3r-xqq0sPc323ithlDs9AQ-BsC3ZJBd",
    "05_edit": "19V--JI1og-Zbey7gMOaQv5t6YwbVigja",
    "06_final": "1JY4FL1UmrxT0xDde2iqJxNxP_pfFCtr9",
    "07_logs": "1Bv7gBBk_1tAl71wEPLIUNVs_bkIUd3TP",
}
ROOT_FOLDER = "1r4SsBzKSpa2tzKD62QK7mPzW1dQK_RdY"

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    plan = []
    for name, fid in FOLDERS.items():
        d = os.path.join(WORK, stage) if stage and name == stage else None
        if d and os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                p = os.path.join(d, f)
                if os.path.isfile(p):
                    plan.append({"local": p, "drive_folder": name, "drive_folder_id": fid})
    print(json.dumps({"drive_root_id": ROOT_FOLDER,
                      "drive_root_url": f"https://drive.google.com/drive/folders/{ROOT_FOLDER}",
                      "status": "manual_push", "files": plan}, indent=1))

if __name__ == "__main__":
    main()
