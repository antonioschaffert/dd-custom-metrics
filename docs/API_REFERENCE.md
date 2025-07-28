# API Reference

## DatadogMetrics Class

The main class for sending metrics to Datadog.

### Constructor

```python
DatadogMetrics(
    api_key: Optional[str] = None,
    app_key: Optional[str] = None,
    host: Optional[str] = None,
    tags: Optional[List[str]] = None,
    use_statsd: bool = True,
    statsd_host: str = "localhost",
    statsd_port: int = 8125
)
```

**Parameters:**
- `api_key`: Datadog API key. If not provided, will try to get from `DD_API_KEY` environment variable.
- `app_key`: Datadog app key. If not provided, will try to get from `DD_APP_KEY` environment variable.
- `host`: Host name for metrics. If not provided, will try to get from `DD_HOST` environment variable.
- `tags`: Default tags to include with all metrics.
- `use_statsd`: Whether to use StatsD (default) or HTTP API.
- `statsd_host`: StatsD host address.
- `statsd_port`: StatsD port.

### Methods

#### gauge(metric_name, value, tags=None)

Send a gauge metric to Datadog.

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (Union[int, float]): Value to send.
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.gauge("my.gauge", 42.5, tags=["env:prod", "service:myapp"])
```

#### increment(metric_name, value=1, tags=None)

Increment a counter metric.

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (int): Value to increment by (default: 1).
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.increment("my.counter", 5, tags=["env:prod", "service:myapp"])
```

#### decrement(metric_name, value=1, tags=None)

Decrement a counter metric.

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (int): Value to decrement by (default: 1).
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.decrement("my.counter", 3, tags=["env:prod", "service:myapp"])
```

#### histogram(metric_name, value, tags=None)

Send a histogram metric.

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (Union[int, float]): Value to record.
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.histogram("my.histogram", 123.45, tags=["env:prod", "service:myapp"])
```

#### timing(metric_name, value, tags=None)

Send a timing metric (alias for histogram).

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (Union[int, float]): Time value in seconds.
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.timing("my.timing", 1.5, tags=["env:prod", "service:myapp"])
```

#### set(metric_name, value, tags=None)

Send a set metric (counts unique values).

**Parameters:**
- `metric_name` (str): Name of the metric.
- `value` (Union[int, float, str]): Unique value to count.
- `tags` (Optional[List[str]]): Additional tags for this metric.

**Example:**
```python
metrics.set("my.set", "unique_value", tags=["env:prod", "service:myapp"])
```

#### event(title, text, tags=None, **kwargs)

Send an event to Datadog.

**Parameters:**
- `title` (str): Event title.
- `text` (str): Event description.
- `tags` (Optional[List[str]]): Additional tags for this event.
- `**kwargs`: Additional event parameters (alert_type, priority, etc.).

**Example:**
```python
metrics.event("Deployment", "New version deployed", tags=["env:prod"], alert_type="info")
```

## Decorators

### @instrument_latency

Automatically instrument function latency.

```python
@instrument_latency(
    metric_name: str,
    tags: Optional[List[str]] = None,
    include_args: bool = False,
    include_result: bool = False,
    metrics_client: Optional[DatadogMetrics] = None
)
```

**Parameters:**
- `metric_name`: Name of the metric to send.
- `tags`: Additional tags to include with the metric.
- `include_args`: Whether to include function arguments as tags.
- `include_result`: Whether to include function result as tags.
- `metrics_client`: Custom DatadogMetrics instance. If not provided, creates a default one.

**Example:**
```python
@instrument_latency("my_task.latency", tags=["service:myapp"])
def my_function():
    time.sleep(1)
    return "done"
```

### @instrument_counter

Automatically increment a counter based on function execution.

```python
@instrument_counter(
    metric_name: str,
    tags: Optional[List[str]] = None,
    increment_on_success: bool = True,
    increment_on_failure: bool = False,
    metrics_client: Optional[DatadogMetrics] = None
)
```

**Parameters:**
- `metric_name`: Name of the metric to increment.
- `tags`: Additional tags to include with the metric.
- `increment_on_success`: Whether to increment on successful execution.
- `increment_on_failure`: Whether to increment on failed execution.
- `metrics_client`: Custom DatadogMetrics instance. If not provided, creates a default one.

**Example:**
```python
@instrument_counter("api.calls", tags=["endpoint:/users"])
def get_user_data():
    # API call logic
    pass
```

### @instrument_gauge

Automatically send a gauge metric based on function result.

```python
@instrument_gauge(
    metric_name: str,
    value_func: Callable[[Any], Union[int, float]],
    tags: Optional[List[str]] = None,
    metrics_client: Optional[DatadogMetrics] = None
)
```

**Parameters:**
- `metric_name`: Name of the metric to send.
- `value_func`: Function to extract value from function result.
- `tags`: Additional tags to include with the metric.
- `metrics_client`: Custom DatadogMetrics instance. If not provided, creates a default one.

**Example:**
```python
@instrument_gauge("queue.size", lambda result: len(result))
def get_queue_items():
    return ["item1", "item2", "item3"]
```

### @instrument_histogram

Automatically send a histogram metric based on function result.

```python
@instrument_histogram(
    metric_name: str,
    value_func: Callable[[Any], Union[int, float]],
    tags: Optional[List[str]] = None,
    metrics_client: Optional[DatadogMetrics] = None
)
```

**Parameters:**
- `metric_name`: Name of the metric to send.
- `value_func`: Function to extract value from function result.
- `tags`: Additional tags to include with the metric.
- `metrics_client`: Custom DatadogMetrics instance. If not provided, creates a default one.

**Example:**
```python
@instrument_histogram("response.size", lambda result: len(result))
def api_call():
    return "large response data"
```

## Error Handling

All methods in the `DatadogMetrics` class include built-in error handling. If a metric fails to send (e.g., due to network issues), the error is logged but does not raise an exception. This ensures that your application continues to function even if Datadog is temporarily unavailable.

## Environment Variables

The following environment variables can be used to configure the client:

- `DD_API_KEY`: Datadog API key
- `DD_APP_KEY`: Datadog app key
- `DD_HOST`: Host name for metrics

## Tag Format

Tags should be in the format `key:value`. Examples:
- `env:prod`
- `service:myapp`
- `version:1.0.0`
- `region:us-east-1`

## Metric Naming Conventions

Follow these conventions for metric names:
- Use dots to separate components: `service.operation.result`
- Use lowercase letters and underscores: `api_request_latency`
- Be descriptive but concise: `user_registration_success_rate`
- Include the unit in the name when relevant: `response_time_seconds`

## Best Practices

1. **Use meaningful metric names**: Choose names that clearly describe what is being measured.
2. **Add relevant tags**: Use tags to provide context and enable filtering.
3. **Avoid high cardinality**: Don't use unique values (like user IDs) as tags for high-volume metrics.
4. **Monitor metric volume**: Be mindful of the number of unique metric combinations you create.
5. **Use appropriate metric types**: Choose the right metric type for your use case.
6. **Handle errors gracefully**: The library handles errors internally, but you may want to add additional error handling for your specific use case. 