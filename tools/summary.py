import json, os
p = "tools/tool_status.json"
if not os.path.exists(p):
    print("no status file"); raise SystemExit
d = json.load(open(p))
print(f"generated: {d.get('generated_utc')}  python {d.get('python')}")
print("")
print("| # | tool | status | licence (detected) |")
print("|---|---|---|---|")
for v in sorted(d["tools"].values(), key=lambda x: x["n"]):
    print(f"| {v['n']} | {v['name']} | {v['status']} | {v.get('license') or v.get('declared_license')} |")
print("")
for k, v in d.get("install_checks", {}).items():
    print(f"* install `{k}` rc={v['returncode']} :: {v['tail'][:1]}")
