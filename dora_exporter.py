import json, time, os, sys
from datetime import datetime, timezone
from prometheus_client import start_http_server, Gauge

# ── Import your existing validation.py ─────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
try:
    from validation import validate_df
    import pandas as pd
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# ── Prometheus Gauges — these become Grafana panels ──────────────────────────
DEPLOY_FREQ    = Gauge('dora_deploy_frequency_per_day',    'Deployments per day (7-day window)')
LEAD_TIME      = Gauge('dora_lead_time_hours',             'Avg hours from commit to production')
CFR            = Gauge('dora_change_failure_rate_percent', 'Pct of deploys that caused failures')
MTTR           = Gauge('dora_mttr_minutes',                'Mean time to recovery in minutes')
TOTAL_DEPLOYS  = Gauge('dora_total_deployments',           'Total deployments recorded')
ETL_ROWS       = Gauge('dora_etl_pipeline_rows_processed', 'Rows processed by etl_pipeline.py')
VALIDATION_OK  = Gauge('dora_validation_checks_passed',    '1 if last validation clean, 0 if issues')

METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics.json')


def load():
    try:
        with open(METRICS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] metrics.json not found at {METRICS_FILE} — run generate_event.py first")
        return {"deployments": [], "incidents": [], "etl_runs": []}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Bad JSON in metrics.json: {e}")
        return {"deployments": [], "incidents": [], "etl_runs": []}


def calculate(data):
    deps = data.get("deployments", [])
    incs = data.get("incidents",   [])
    etls = data.get("etl_runs",    [])

    # 1. Deploy frequency — how many deploys in last 7 days
    now = datetime.now(timezone.utc)
    recent = []
    for d in deps:
        try:
            ts = datetime.fromisoformat(d["timestamp"].replace("Z","+00:00"))
            if (now - ts).total_seconds() / 86400 <= 7:
                recent.append(d)
        except (KeyError, ValueError):
            pass
    deploy_freq = round(len(recent) / 7.0, 2) if recent else 0

    # 2. Lead time — avg commit-to-deploy hours
    lt_vals = [d.get("lead_time_hours", 0) for d in deps if d.get("lead_time_hours")]
    avg_lt = round(sum(lt_vals) / len(lt_vals), 2) if lt_vals else 0

    # 3. Change failure rate
    failed = [d for d in deps if d.get("status") == "failed"]
    cfr_val = round(len(failed) / len(deps) * 100, 2) if deps else 0

    # 4. MTTR
    mttr_vals = [i.get("mttr_minutes", 0) for i in incs if i.get("mttr_minutes")]
    avg_mttr = round(sum(mttr_vals) / len(mttr_vals), 1) if mttr_vals else 0

    # 5. ETL rows from etl_pipeline runs
    latest_rows = etls[-1].get("rows_processed", 0) if etls else 0

    return deploy_freq, avg_lt, cfr_val, avg_mttr, len(deps), latest_rows


def run_validation_check():
    """Run your existing validation.py against sample ETL data."""
    if not VALIDATION_AVAILABLE:
        return 0
    try:
        df = pd.DataFrame(
            [["Alice", 48, "Engineer"], ["Bob", 28, "Designer"]],
            columns=["Name", "Age", "Role"]
        )
        report = validate_df(df)
        issues = (
            len(report.get("missing_columns", [])) +
            report.get("duplicate_rows", 0) +
            report.get("age_out_of_range", 0) +
            len(report.get("unknown_roles", []))
        )
        return 1 if issues == 0 else 0
    except Exception as e:
        print(f"[WARN] Validation check failed: {e}")
        return 0


def loop():
    print("=" * 55)
    print(" DORA Exporter — devgupta24/dora_metrics")
    print(f" Metrics endpoint: http://localhost:8000/metrics")
    print(f" Reading from:     {METRICS_FILE}")
    print(" Refresh interval: 15 seconds")
    print("=" * 55)
    while True:
        data = load()
        df, lt, cfr_v, mttr_v, total, rows = calculate(data)
        val_ok = run_validation_check()

        DEPLOY_FREQ.set(df)
        LEAD_TIME.set(lt)
        CFR.set(cfr_v)
        MTTR.set(mttr_v)
        TOTAL_DEPLOYS.set(total)
        ETL_ROWS.set(rows)
        VALIDATION_OK.set(val_ok)

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] Freq={df}/day | LeadTime={lt}h | "
              f"CFR={cfr_v}% | MTTR={mttr_v}min | "
              f"TotalDeploys={total} | Validation={'OK' if val_ok else 'ISSUES'}")
        time.sleep(15)


if __name__ == "__main__":
    start_http_server(8000)
    loop()