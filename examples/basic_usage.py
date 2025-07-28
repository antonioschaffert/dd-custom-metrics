#!/usr/bin/env python3
"""
Basic usage examples for dd-custom-metrics.
"""

import time
import random
from dd_custom_metrics import DatadogMetrics, instrument_latency, instrument_counter


def basic_metrics_example():
    """Example of basic metric sending."""
    print("=== Basic Metrics Example ===")

    # Initialize with your Datadog credentials
    metrics = DatadogMetrics(
        api_key="your_api_key_here",
        app_key="your_app_key_here",
        tags=["env:dev", "service:example"],
    )

    # Send different types of metrics
    metrics.gauge("example.gauge", 42.5, tags=["type:test"])
    metrics.increment("example.counter", tags=["type:test"])
    metrics.histogram("example.histogram", 123.45, tags=["type:test"])

    print("Sent basic metrics to Datadog")


def namespace_metrics_example():
    """Example of metrics with namespace prefix."""
    print("=== Namespace Metrics Example ===")

    # Initialize with namespace prefix
    metrics = DatadogMetrics(
        api_key="your_api_key_here",
        app_key="your_app_key_here",
        namespace="my_company",
        tags=["env:dev", "service:example"],
    )

    # These metrics will be prefixed with "my_company."
    metrics.gauge("example.gauge", 42.5, tags=["type:test"])
    metrics.increment("example.counter", tags=["type:test"])
    metrics.histogram("example.histogram", 123.45, tags=["type:test"])

    print("Sent namespaced metrics to Datadog (prefixed with 'my_company.')")

    # Send different types of metrics
    metrics.gauge("example.gauge", 42.5, tags=["type:test"])
    metrics.increment("example.counter", tags=["type:test"])
    metrics.histogram("example.histogram", 123.45, tags=["type:test"])

    print("Sent basic metrics to Datadog")


@instrument_latency("example.task.latency", tags=["service:example"])
def slow_task():
    """Example task that takes some time to complete."""
    print("Executing slow task...")
    time.sleep(random.uniform(0.5, 2.0))
    return "task completed"


@instrument_counter("example.api.calls", tags=["endpoint:/users"])
def api_call():
    """Example API call that gets instrumented."""
    print("Making API call...")
    # Simulate API call
    time.sleep(0.1)
    return {"users": [{"id": 1, "name": "John"}]}


@instrument_latency("example.database.query", tags=["table:users"], include_args=True)
def database_query(user_id: int):
    """Example database query with argument tracking."""
    print(f"Querying database for user {user_id}...")
    time.sleep(0.2)
    return {"id": user_id, "name": "John Doe"}


def business_metrics_example():
    """Example of business metrics tracking."""
    print("\n=== Business Metrics Example ===")

    metrics = DatadogMetrics(tags=["env:dev", "service:business"])

    # Simulate user registration
    def register_user(user_id: str, plan: str):
        print(f"Registering user {user_id} with plan {plan}")
        metrics.increment("user.registration", tags=[f"plan:{plan}"])
        metrics.gauge("user.count", random.randint(1000, 5000))
        return True

    # Simulate order processing
    def process_order(order_id: str, amount: float):
        print(f"Processing order {order_id} for ${amount}")
        metrics.increment("order.processed")
        metrics.histogram("order.amount", amount, tags=["currency:usd"])
        return {"order_id": order_id, "status": "processed"}

    # Execute business operations
    register_user("user123", "premium")
    register_user("user124", "basic")
    process_order("order001", 99.99)
    process_order("order002", 149.99)


def main():
    """Run all examples."""
    print("DD Custom Metrics Examples")
    print("=" * 50)

    # Basic metrics
    basic_metrics_example()

    # Namespace metrics
    namespace_metrics_example()

    # Decorator examples
    print("\n=== Decorator Examples ===")

    # Latency instrumentation
    result = slow_task()
    print(f"Task result: {result}")

    # Counter instrumentation
    api_result = api_call()
    print(f"API result: {api_result}")

    # Database query with argument tracking
    db_result = database_query(123)
    print(f"Database result: {db_result}")

    # Business metrics
    business_metrics_example()

    print("\nExamples completed! Check your Datadog dashboard for metrics.")


if __name__ == "__main__":
    main()
