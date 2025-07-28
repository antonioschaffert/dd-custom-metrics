#!/usr/bin/env python3
"""
Airflow integration examples for dd-custom-metrics.
"""

from datetime import datetime, timedelta
from dd_custom_metrics import instrument_latency, instrument_counter, DatadogMetrics

# Note: This example assumes you have Airflow installed
# pip install apache-airflow

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print(
        "Airflow not available. This example shows the pattern for Airflow integration."
    )


@instrument_latency(
    "airflow.task.latency", tags=["dag:example_dag", "task:data_processing"]
)
def process_data_task():
    """Example Airflow task for data processing."""
    import time
    import random

    print("Processing data...")
    time.sleep(random.uniform(1, 3))

    # Simulate some data processing
    records_processed = random.randint(100, 1000)
    print(f"Processed {records_processed} records")

    return {"records_processed": records_processed}


@instrument_counter(
    "airflow.task.executions", tags=["dag:example_dag", "task:data_validation"]
)
def validate_data_task():
    """Example Airflow task for data validation."""
    import time
    import random

    print("Validating data...")
    time.sleep(random.uniform(0.5, 1.5))

    # Simulate validation
    is_valid = random.choice([True, True, True, False])  # 75% success rate
    if not is_valid:
        raise ValueError("Data validation failed")

    print("Data validation successful")
    return {"validated": True}


@instrument_latency(
    "airflow.task.latency",
    tags=["dag:example_dag", "task:report_generation"],
    include_result=True,
)
def generate_report_task():
    """Example Airflow task for report generation."""
    import time
    import random

    print("Generating report...")
    time.sleep(random.uniform(2, 4))

    report_size = random.randint(1000, 5000)
    print(f"Generated report with {report_size} lines")

    return {"report_size": report_size, "status": "completed"}


def business_metrics_task():
    """Example Airflow task that tracks business metrics."""
    import random

    metrics = DatadogMetrics(tags=["env:prod", "service:airflow"])

    # Simulate business operations
    orders_processed = random.randint(50, 200)
    revenue = orders_processed * random.uniform(10, 100)

    # Track business metrics
    metrics.increment("orders.processed", orders_processed)
    metrics.gauge("revenue.daily", revenue)
    metrics.histogram("order.value", revenue / orders_processed)

    print(f"Processed {orders_processed} orders with ${revenue:.2f} revenue")
    return {"orders": orders_processed, "revenue": revenue}


# Airflow DAG definition (if Airflow is available)
if AIRFLOW_AVAILABLE:
    default_args = {
        "owner": "data-team",
        "depends_on_past": False,
        "start_date": datetime(2023, 1, 1),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    dag = DAG(
        "example_metrics_dag",
        default_args=default_args,
        description="Example DAG with Datadog metrics instrumentation",
        schedule_interval=timedelta(hours=1),
        catchup=False,
        tags=["example", "metrics"],
    )

    # Define tasks
    process_task = PythonOperator(
        task_id="process_data", python_callable=process_data_task, dag=dag
    )

    validate_task = PythonOperator(
        task_id="validate_data", python_callable=validate_data_task, dag=dag
    )

    report_task = PythonOperator(
        task_id="generate_report", python_callable=generate_report_task, dag=dag
    )

    business_task = PythonOperator(
        task_id="track_business_metrics", python_callable=business_metrics_task, dag=dag
    )

    # Define task dependencies
    process_task >> validate_task >> report_task
    process_task >> business_task


def run_examples_without_airflow():
    """Run the examples without Airflow for demonstration."""
    print("=== Airflow Integration Examples (Standalone) ===")

    try:
        # Run data processing task
        print("\n1. Running data processing task...")
        result1 = process_data_task()
        print(f"   Result: {result1}")

        # Run data validation task
        print("\n2. Running data validation task...")
        result2 = validate_data_task()
        print(f"   Result: {result2}")

        # Run report generation task
        print("\n3. Running report generation task...")
        result3 = generate_report_task()
        print(f"   Result: {result3}")

        # Run business metrics task
        print("\n4. Running business metrics task...")
        result4 = business_metrics_task()
        print(f"   Result: {result4}")

        print("\nAll tasks completed successfully!")

    except Exception as e:
        print(f"Task failed: {e}")


def main():
    """Main function to run examples."""
    print("DD Custom Metrics - Airflow Integration Examples")
    print("=" * 60)

    if AIRFLOW_AVAILABLE:
        print("Airflow is available. You can use this DAG in your Airflow instance.")
        print("The DAG definition is included in this file.")
    else:
        print("Airflow is not available. Running standalone examples...")

    # Run examples
    run_examples_without_airflow()

    print("\nCheck your Datadog dashboard for the following metrics:")
    print("- airflow.task.latency")
    print("- airflow.task.executions")
    print("- orders.processed")
    print("- revenue.daily")
    print("- order.value")


if __name__ == "__main__":
    main()
