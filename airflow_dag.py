from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl_pipeline import get_df
from validation import validate_df

log = logging.getLogger(__name__)


def run_validation(**context):
	df = get_df()
	report = validate_df(df)
	# push report to XCom
	ti = context['ti']
	ti.xcom_push(key='validation_report', value=report)

	log.info('Validation report: %s', report)

	# Fail the task on critical issues
	if report.get('missing_columns'):
		raise ValueError(f"Missing columns: {report['missing_columns']}")
	if report.get('age_non_numeric_count', 0) > 0:
		raise ValueError('Non-numeric ages found')
	if report.get('invalid_name_count', 0) > 0:
		raise ValueError('Invalid name values found')
	if report.get('unknown_roles'):
		raise ValueError(f"Unknown roles: {report['unknown_roles']}")


default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
}

with DAG(
	dag_id='dora_metrics_validation',
	default_args=default_args,
	start_date=datetime(2026, 1, 1),
	schedule_interval=None,
	catchup=False,
) as dag:

	validate_task = PythonOperator(
		task_id='run_df_validation',
		python_callable=run_validation,
		provide_context=True,
	)

	validate_task

