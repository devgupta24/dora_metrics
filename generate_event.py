"""
generate_event.py — Called automatically by GitHub Actions.

Usage examples:
  python generate_event.py --type deploy --status success --lead-time 6.2 --commit abc123
  python generate_event.py --type deploy --status failed  --lead-time 3.1 --commit def456
  python generate_event.py --type incident --mttr 29
  python generate_event.py --type etl --rows 3 --status success
"""
import json, argparse, os, uuid
from datetime import datetime, timezone

METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics.json')

def load():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {"deployments": [], "incidents": [], "etl_runs": []}

def save(data):
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[OK] {METRICS_FILE} updated")

def add_deploy(status, lead_time, commit, branch):
    data = load()
    event = {
        "id":              f"deploy-{uuid.uuid4().hex[:8]}",
        "timestamp":       datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "commit_sha":      commit or uuid.uuid4().hex[:7],
        "branch":          branch,
        "status":          status,
        "lead_time_hours": float(lead_time),
        "environment":     "production"
    }
    data.setdefault("deployments", []).append(event)
    data["deployments"] = data["deployments"][-100:]   # keep last 100
    save(data)
    print(f"[DEPLOY] {event['id']} | {status} | lead_time={lead_time}h | commit={commit}")

def add_incident(mttr, severity):
    data = load()
    event = {
        "id":               f"incident-{uuid.uuid4().hex[:8]}",
        "started_at":       datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "resolved_at":      datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "mttr_minutes":     int(mttr),
        "severity":         severity,
        "caused_by_deploy": True
    }
    data.setdefault("incidents", []).append(event)
    data["incidents"] = data["incidents"][-50:]
    save(data)
    print(f"[INCIDENT] {event['id']} | MTTR={mttr}min | severity={severity}")

def add_etl(rows, status):
    data = load()
    event = {
        "id":             f"etl-{uuid.uuid4().hex[:8]}",
        "timestamp":      datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "rows_processed": int(rows),
        "status":         status,
        "script":         "etl_pipeline.py"
    }
    data.setdefault("etl_runs", []).append(event)
    data["etl_runs"] = data["etl_runs"][-50:]
    save(data)
    print(f"[ETL] {event['id']} | rows={rows} | status={status}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--type",     required=True, choices=["deploy","incident","etl"])
    p.add_argument("--status",   default="success", choices=["success","failed"])
    p.add_argument("--lead-time",default=7.0,   type=float, dest="lead_time")
    p.add_argument("--mttr",     default=30,    type=int)
    p.add_argument("--rows",     default=3,     type=int)
    p.add_argument("--commit",   default=None)
    p.add_argument("--branch",   default="main")
    p.add_argument("--severity", default="P2")
    a = p.parse_args()

    if a.type == "deploy":
        add_deploy(a.status, a.lead_time, a.commit, a.branch)
    elif a.type == "incident":
        add_incident(a.mttr, a.severity)
    elif a.type == "etl":
        add_etl(a.rows, a.status)