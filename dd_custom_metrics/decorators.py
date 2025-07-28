"""
Decorators for automatic metric instrumentation.
"""

import time
import functools
import logging
from typing import List, Optional, Callable, Any, Union
from .metrics import DatadogMetrics

logger = logging.getLogger(__name__)


def instrument_latency(
    metric_name: str,
    tags: Optional[List[str]] = None,
    include_args: bool = False,
    include_result: bool = False,
    metrics_client: Optional[DatadogMetrics] = None,
) -> Callable:
    """
    Decorator to automatically instrument function latency.

    Args:
        metric_name: Name of the metric to send.
        tags: Additional tags to include with the metric.
        include_args: Whether to include function arguments as tags.
        include_result: Whether to include function result as tags.
        metrics_client: Custom DatadogMetrics instance. If not provided, creates a default one.

    Returns:
        Decorated function that automatically tracks execution time.

    Example:
        @instrument_latency("my_task.latency", tags=["service:myapp"])
        def my_function():
            time.sleep(1)
            return "done"
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create metrics client if not provided
            client = metrics_client or DatadogMetrics()

            # Prepare tags
            combined_tags = tags or []

            # Add argument tags if requested
            if include_args:
                arg_tags = []
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float)):
                        arg_tags.append(f"arg_{i}:{arg}")
                    elif hasattr(arg, "__class__"):
                        arg_tags.append(f"arg_{i}_type:{arg.__class__.__name__}")

                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float)):
                        arg_tags.append(f"kwarg_{key}:{value}")
                    elif hasattr(value, "__class__"):
                        arg_tags.append(f"kwarg_{key}_type:{value.__class__.__name__}")

                combined_tags.extend(arg_tags)

            start_time = time.time()
            result = None
            exception_occurred = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                exception_occurred = True
                combined_tags.append(f"exception:{e.__class__.__name__}")
                raise
            finally:
                execution_time = time.time() - start_time

                # Add result tag if requested
                if include_result and not exception_occurred:
                    if isinstance(result, (str, int, float)):
                        combined_tags.append(f"result:{result}")
                    elif result is not None:
                        combined_tags.append(f"result_type:{type(result).__name__}")

                # Add success/failure tag
                combined_tags.append(f"success:{not exception_occurred}")

                # Send the timing metric
                try:
                    client.timing(metric_name, execution_time, tags=combined_tags)
                    logger.debug(
                        f"Instrumented {func.__name__}: {execution_time:.3f}s, "
                        f"metric={metric_name}, tags={combined_tags}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send latency metric for {func.__name__}: {e}"
                    )

        return wrapper

    return decorator


def instrument_counter(
    metric_name: str,
    tags: Optional[List[str]] = None,
    increment_on_success: bool = True,
    increment_on_failure: bool = False,
    metrics_client: Optional[DatadogMetrics] = None,
) -> Callable:
    """
    Decorator to automatically increment a counter based on function execution.

    Args:
        metric_name: Name of the metric to increment.
        tags: Additional tags to include with the metric.
        increment_on_success: Whether to increment on successful execution.
        increment_on_failure: Whether to increment on failed execution.
        metrics_client: Custom DatadogMetrics instance. If not provided, creates a default one.

    Returns:
        Decorated function that automatically increments counter.

    Example:
        @instrument_counter("api.calls", tags=["endpoint:/users"])
        def get_user_data():
            # API call logic
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create metrics client if not provided
            client = metrics_client or DatadogMetrics()

            # Prepare tags
            combined_tags = tags or []

            try:
                result = func(*args, **kwargs)
                if increment_on_success:
                    client.increment(
                        metric_name, tags=combined_tags + ["status:success"]
                    )
                return result
            except Exception as e:
                if increment_on_failure:
                    client.increment(
                        metric_name,
                        tags=combined_tags
                        + ["status:error", f"error:{e.__class__.__name__}"],
                    )
                raise
            finally:
                logger.debug(f"Instrumented counter for {func.__name__}: {metric_name}")

        return wrapper

    return decorator


def instrument_gauge(
    metric_name: str,
    value_func: Callable[[Any], Union[int, float]],
    tags: Optional[List[str]] = None,
    metrics_client: Optional[DatadogMetrics] = None,
) -> Callable:
    """
    Decorator to automatically send a gauge metric based on function result.

    Args:
        metric_name: Name of the metric to send.
        value_func: Function to extract value from function result.
        tags: Additional tags to include with the metric.
        metrics_client: Custom DatadogMetrics instance. If not provided, creates a default one.

    Returns:
        Decorated function that automatically sends gauge metric.

    Example:
        @instrument_gauge("queue.size", lambda result: len(result))
        def get_queue_items():
            return ["item1", "item2", "item3"]
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create metrics client if not provided
            client = metrics_client or DatadogMetrics()

            # Prepare tags
            combined_tags = tags or []

            try:
                result = func(*args, **kwargs)
                value = value_func(result)
                client.gauge(metric_name, value, tags=combined_tags)
                logger.debug(
                    f"Instrumented gauge for {func.__name__}: {metric_name}={value}"
                )
                return result
            except Exception as e:
                logger.error(f"Failed to send gauge metric for {func.__name__}: {e}")
                # Don't raise the exception, just return the result
                return result

        return wrapper

    return decorator


def instrument_histogram(
    metric_name: str,
    value_func: Callable[[Any], Union[int, float]],
    tags: Optional[List[str]] = None,
    metrics_client: Optional[DatadogMetrics] = None,
) -> Callable:
    """
    Decorator to automatically send a histogram metric based on function result.

    Args:
        metric_name: Name of the metric to send.
        value_func: Function to extract value from function result.
        tags: Additional tags to include with the metric.
        metrics_client: Custom DatadogMetrics instance. If not provided, creates a default one.

    Returns:
        Decorated function that automatically sends histogram metric.

    Example:
        @instrument_histogram("response.size", lambda result: len(result))
        def api_call():
            return "large response data"
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create metrics client if not provided
            client = metrics_client or DatadogMetrics()

            # Prepare tags
            combined_tags = tags or []

            try:
                result = func(*args, **kwargs)
                value = value_func(result)
                client.histogram(metric_name, value, tags=combined_tags)
                logger.debug(
                    f"Instrumented histogram for {func.__name__}: {metric_name}={value}"
                )
                return result
            except Exception as e:
                logger.error(
                    f"Failed to send histogram metric for {func.__name__}: {e}"
                )
                # Don't raise the exception, just return the result
                return result

        return wrapper

    return decorator
