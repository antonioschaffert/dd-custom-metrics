# DD Custom Metrics

A Python wrapper for Datadog custom metrics with decorator support for easy instrumentation of latency and business metrics.

## Features

- **Official Datadog API Client**: Uses the official `datadog-api-client` for reliable metric submission
- **Decorator Support**: Automatically instrument method latency with `@instrument_latency`
- **Multiple Metric Types**: Support for gauge, increment, histogram, rate, and more
- **Namespace Support**: Add namespace prefixes to organize your metrics
- **Tag Support**: Add custom tags to your metrics for better filtering and analysis
- **Error Handling**: Built-in error handling and logging
- **Resource Management**: Automatic resource cleanup with context managers

## Installation

```bash
pip install dd-custom-metrics
```

## Quick Start

### Basic Usage

```python
from dd_custom_metrics import DatadogMetrics

# Initialize with your Datadog API key and app key
metrics = DatadogMetrics(
    api_key="your_api_key",
    app_key="your_app_key",
    host="your-hostname"
)

# Send different types of metrics
metrics.gauge("my.gauge", 42.5, tags=["env:prod", "service:myapp"])
metrics.increment("my.counter", tags=["env:prod", "service:myapp"])
metrics.histogram("my.histogram", 123.45, tags=["env:prod", "service:myapp"])
```

### Using Namespaces

You can add a namespace prefix to all your metrics for better organization:

```python
from dd_custom_metrics import DatadogMetrics

# Initialize with namespace prefix
metrics = DatadogMetrics(
    api_key="your_api_key",
    app_key="your_app_key",
    namespace="my_company",  # All metrics will be prefixed with "my_company."
    host="your-hostname"
)

# These metrics will be sent as "my_company.my.gauge", "my_company.my.counter", etc.
metrics.gauge("my.gauge", 42.5, tags=["env:prod", "service:myapp"])
metrics.increment("my.counter", tags=["env:prod", "service:myapp"])
```

You can also set the namespace via environment variable:
```bash
export DD_NAMESPACE="my_company"
```

### Decorator Usage

```python
from dd_custom_metrics import instrument_latency

@instrument_latency("my_task.latency", tags=["service:myapp"])
def my_airflow_task():
    # Your task logic here
    import time
    time.sleep(2)
    return "task completed"

# The decorator will automatically send a histogram metric with the execution time
```

### Airflow Integration

```python
from dd_custom_metrics import instrument_latency
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

@instrument_latency("airflow.task.latency", tags=["dag:my_dag"])
def my_airflow_function():
    # Your Airflow task logic
    pass

dag = DAG('my_dag', start_date=datetime(2023, 1, 1))

task = PythonOperator(
    task_id='my_task',
    python_callable=my_airflow_function,
    dag=dag
)
```

## API Reference

### DatadogMetrics Class

#### Initialization

```python
DatadogMetrics(
    api_key: str,
    app_key: str,
    host: str = None,
    tags: List[str] = None,
    namespace: str = None
)
```

#### Methods

- `gauge(metric_name: str, value: float, tags: List[str] = None)`: Send a gauge metric
- `increment(metric_name: str, value: int = 1, tags: List[str] = None)`: Increment a counter
- `decrement(metric_name: str, value: int = 1, tags: List[str] = None)`: Decrement a counter
- `histogram(metric_name: str, value: float, tags: List[str] = None)`: Send a histogram metric
- `timing(metric_name: str, value: float, tags: List[str] = None)`: Send a timing metric (alias for histogram)
- `rate(metric_name: str, value: float, tags: List[str] = None)`: Send a rate metric
- `set(metric_name: str, value: Union[int, float, str], tags: List[str] = None)`: Send a set metric
- `event(title: str, text: str, tags: List[str] = None, **kwargs)`: Send an event
- `close()`: Close the API client connection



### Decorators

#### @instrument_latency

```python
@instrument_latency(
    metric_name: str,
    tags: List[str] = None,
    include_args: bool = False,
    include_result: bool = False
)
```

**Parameters:**
- `metric_name`: Name of the metric to send
- `tags`: List of tags to attach to the metric
- `include_args`: Whether to include function arguments in tags (default: False)
- `include_result`: Whether to include function result in tags (default: False)

## Examples

### Business Metrics

```python
from dd_custom_metrics import DatadogMetrics

metrics = DatadogMetrics(
    api_key="your_api_key",
    app_key="your_app_key",
    tags=["env:prod", "service:myapp"]
)

# Track user registrations
def register_user(user_id: str, plan: str):
    # Registration logic here
    metrics.increment("user.registration", tags=[f"plan:{plan}"])
    metrics.gauge("user.count", get_total_users())

# Track order processing
def process_order(order_id: str, amount: float):
    # Order processing logic here
    metrics.increment("order.processed")
    metrics.histogram("order.amount", amount, tags=["currency:usd"])
```

### Performance Monitoring

```python
from dd_custom_metrics import instrument_latency

@instrument_latency("api.request.latency", tags=["endpoint:/users"])
def get_user_data(user_id: str):
    # API call logic here
    pass

@instrument_latency("database.query.latency", tags=["table:users"])
def query_user_database(user_id: str):
    # Database query logic here
    pass
```

## Configuration

### Environment Variables

You can also configure the client using environment variables:

```bash
export DD_API_KEY="your_api_key"
export DD_APP_KEY="your_app_key"
export DD_HOST="your-hostname"
```

Then initialize without parameters:

```python
from dd_custom_metrics import DatadogMetrics

metrics = DatadogMetrics()  # Uses environment variables
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 