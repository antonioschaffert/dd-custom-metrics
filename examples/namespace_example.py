#!/usr/bin/env python3
"""
Example demonstrating namespace functionality with dd-custom-metrics.
"""

import os
from dd_custom_metrics import DatadogMetrics


def namespace_example():
    """Example of using namespace prefixes for metrics."""
    print("=== Namespace Example ===")

    # Initialize with namespace prefix
    metrics = DatadogMetrics(
        api_key=os.getenv("DD_API_KEY"),
        app_key=os.getenv("DD_APP_KEY"),
        namespace="my_company",  # All metrics will be prefixed with "my_company."
        tags=["env:dev", "service:example"],
    )

    # These metrics will be sent as:
    # - my_company.example.gauge
    # - my_company.example.counter
    # - my_company.example.histogram
    metrics.gauge("example.gauge", 42.5, tags=["type:test"])
    metrics.increment("example.counter", tags=["type:test"])
    metrics.histogram("example.histogram", 123.45, tags=["type:test"])

    print("Sent namespaced metrics to Datadog (prefixed with 'my_company.')")


def environment_namespace_example():
    """Example using namespace from environment variable."""
    print("=== Environment Namespace Example ===")

    # Set namespace via environment variable
    os.environ["DD_NAMESPACE"] = "env_company"

    # Initialize without explicit namespace (will use DD_NAMESPACE)
    metrics = DatadogMetrics(
        api_key=os.getenv("DD_API_KEY"),
        app_key=os.getenv("DD_APP_KEY"),
        tags=["env:dev", "service:example"],
    )

    # These metrics will be sent as:
    # - env_company.example.gauge
    # - env_company.example.counter
    metrics.gauge("example.gauge", 100.0, tags=["type:env_test"])
    metrics.increment("example.counter", tags=["type:env_test"])

    print("Sent namespaced metrics to Datadog (prefixed with 'env_company.')")


def main():
    """Run namespace examples."""
    print("DD Custom Metrics - Namespace Examples")
    print("=" * 50)

    # Check if API keys are set
    if not os.getenv("DD_API_KEY") or not os.getenv("DD_APP_KEY"):
        print("Error: DD_API_KEY and DD_APP_KEY environment variables must be set")
        return

    # Run examples
    namespace_example()
    environment_namespace_example()

    print("\nExamples completed! Check your Datadog dashboard for metrics.")
    print("Look for metrics with prefixes: 'my_company.' and 'env_company.'")


if __name__ == "__main__":
    main() 