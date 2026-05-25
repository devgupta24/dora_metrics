# import requests
# import time
# from prometheus_client import start_http_server, Gauge

# # GitHub Repo Details
# OWNER = "devgupta24"
# REPO = "dora_metrics"

# # Metrics
# deployment_frequency = Gauge(
#     'github_deployment_frequency',
#     'Total workflow runs'
# )

# failed_deployments = Gauge(
#     'github_failed_deployments',
#     'Failed workflow runs'
# )

# successful_deployments = Gauge(
#     'github_successful_deployments',
#     'Successful workflow runs'
# )

# def fetch_github_metrics():
#     url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"

#     response = requests.get(url)

#     data = response.json()

#     runs = data.get("workflow_runs", [])

#     total_runs = len(runs)

#     failed = len([
#         run for run in runs
#         if run["conclusion"] == "failure"
#     ])

#     success = len([
#         run for run in runs
#         if run["conclusion"] == "success"
#     ])

#     deployment_frequency.set(total_runs)
#     failed_deployments.set(failed)
#     successful_deployments.set(success)

#     print(f"Total Runs: {total_runs}")
#     print(f"Failed Runs: {failed}")
#     print(f"Successful Runs: {success}")

# if __name__ == "__main__":
#     start_http_server(8010)

#     while True:
#         fetch_github_metrics()
#         time.sleep(60)

# from prometheus_client import start_http_server, Gauge
# import time

# deployment_metric = Gauge(
#     'github_deployment_frequency',
#     'Dummy deployment metric'
# )

# if __name__ == "__main__":
#     print("Starting exporter on port 8010")

#     start_http_server(8010)

#     print("Exporter started successfully")

#     value = 1

#     while True:
#         deployment_metric.set(value)
#         print(f"Metric updated: {value}")

#         value += 1

#         time.sleep(5)

from prometheus_client import start_http_server, Gauge
import time

deployment_frequency = Gauge(
    'github_deployment_frequency',
    'Deployment frequency metric'
)

failed_deployments = Gauge(
    'github_failed_deployments',
    'Failed deployments metric'
)

successful_deployments = Gauge(
    'github_successful_deployments',
    'Successful deployments metric'
)

if __name__ == "__main__":

    print("Starting exporter on port 8000")

    start_http_server(8000)

    print("Exporter started successfully")

    value = 1

    while True:

        deployment_frequency.set(value)
        failed_deployments.set(1)
        successful_deployments.set(value - 1)

        print(f"Metrics updated: {value}")

        value += 1

        time.sleep(10)