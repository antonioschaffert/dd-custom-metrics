"""
Core Datadog metrics wrapper class using the official datadog-api-client v2.
"""

import os
import logging
import urllib3
from datetime import datetime
from typing import List, Optional, Union

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries

# Disable SSL warnings to avoid certificate verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class DatadogMetrics:
    """
    A wrapper around Datadog's official API client v2 for easy metric sending.

    This class provides a simplified interface for sending various types of metrics
    to Datadog, including gauges, counters, histograms, and timing metrics.
    """

    # Mapping of string metric types to Datadog MetricIntakeType enum
    METRIC_TYPE_MAP = {
        "count": MetricIntakeType.COUNT,
        "gauge": MetricIntakeType.GAUGE,
        "rate": MetricIntakeType.RATE,
        "histogram": MetricIntakeType.GAUGE,  # Histogram maps to gauge in v2
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        host: Optional[str] = None,
        tags: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        site: str = "datadoghq.com",
    ):
        """
        Initialize the Datadog metrics client.

        Args:
            api_key: Datadog API key. If not provided, will try to get from DD_API_KEY env var.
            app_key: Datadog app key. If not provided, will try to get from DD_APP_KEY env var.
            host: Host name for metrics. If not provided, will try to get from DD_HOST env var.
            tags: Default tags to include with all metrics.
            namespace: Namespace prefix for all metrics (e.g., "my_company").
            site: Datadog site (default: datadoghq.com, use datadoghq.eu for EU).
        """
        self.api_key = api_key or os.getenv("DD_API_KEY")
        self.app_key = app_key or os.getenv("DD_APP_KEY")
        self.host = host or os.getenv("DD_HOST")
        self.default_tags = tags or []
        self.namespace = namespace or os.getenv("DD_NAMESPACE")
        self.site = site

        if not self.api_key or not self.app_key:
            raise ValueError("API key and app key are required")

        # Initialize the configuration
        self.configuration = Configuration()
        self.configuration.api_key["apiKeyAuth"] = self.api_key
        self.configuration.api_key["appKeyAuth"] = self.app_key
        self.configuration.server_variables["site"] = self.site
        
        # Disable SSL verification to avoid certificate issues on macOS
        self.configuration.verify_ssl = False

    def _combine_tags(self, tags: Optional[List[str]] = None) -> List[str]:
        """Combine default tags with provided tags."""
        combined = self.default_tags.copy()
        if tags:
            combined.extend(tags)
        return combined

    def _prefix_metric_name(self, metric_name: str) -> str:
        """Add namespace prefix to metric name if namespace is set."""
        if self.namespace:
            return f"{self.namespace}.{metric_name}"
        return metric_name

    def _send_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        metric_type: Union[str, MetricIntakeType],
        tags: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Send a metric to Datadog using the official API v2.

        Args:
            metric_name: Name of the metric.
            value: Value to send.
            metric_type: Type of metric ("gauge", "count", "rate", "histogram") or MetricIntakeType enum.
            tags: Additional tags for this metric.
            timestamp: Timestamp for the metric (default: current time).
        """
        try:
            prefixed_name = self._prefix_metric_name(metric_name)
            combined_tags = self._combine_tags(tags)
            
            # Convert string metric type to enum if needed
            if isinstance(metric_type, str):
                metric_type = self.METRIC_TYPE_MAP.get(metric_type.lower(), MetricIntakeType.COUNT)
            
            # Use current timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now()

            # Create metric series
            series = MetricSeries(
                metric=prefixed_name,
                type=metric_type,
                points=[MetricPoint(
                    timestamp=int(timestamp.timestamp()),
                    value=float(value)
                )],
                tags=combined_tags
            )

            # Create payload
            body = MetricPayload(series=[series])
            
            # Send metric using context manager for proper resource cleanup
            with ApiClient(self.configuration) as api_client:
                api_instance = MetricsApi(api_client)
                api_instance.submit_metrics(body=body)

            logger.debug(
                f"Sent {metric_type} metric: {prefixed_name}={value}, tags={combined_tags}"
            )
        except Exception as e:
            logger.error(f"Failed to send {metric_type} metric {prefixed_name}: {e}")

    def gauge(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Send a gauge metric to Datadog.

        Args:
            metric_name: Name of the metric.
            value: Value to send.
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, value, "gauge", tags)

    def increment(
        self, metric_name: str, value: int = 1, tags: Optional[List[str]] = None
    ) -> None:
        """
        Increment a counter metric.

        Args:
            metric_name: Name of the metric.
            value: Value to increment by (default: 1).
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, value, "count", tags)

    def decrement(
        self, metric_name: str, value: int = 1, tags: Optional[List[str]] = None
    ) -> None:
        """
        Decrement a counter metric.

        Args:
            metric_name: Name of the metric.
            value: Value to decrement by (default: 1).
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, -value, "count", tags)

    def histogram(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Send a histogram metric.

        Args:
            metric_name: Name of the metric.
            value: Value to record.
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, value, "histogram", tags)

    def timing(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Send a timing metric (alias for histogram).

        Args:
            metric_name: Name of the metric.
            value: Time value in seconds.
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, value, "histogram", tags)

    def rate(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Send a rate metric.

        Args:
            metric_name: Name of the metric.
            value: Value to send.
            tags: Additional tags for this metric.
        """
        self._send_metric(metric_name, value, "rate", tags)

    def set(
        self,
        metric_name: str,
        value: Union[int, float, str],
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Send a set metric (counts unique values).

        Args:
            metric_name: Name of the metric.
            value: Unique value to count.
            tags: Additional tags for this metric.
        """
        # For set metrics, we'll use a gauge with the value
        # Note: The official API doesn't have a direct "set" type
        # This is a simplified implementation
        self._send_metric(metric_name, 1, "gauge", tags)

    def event(
        self, title: str, text: str, tags: Optional[List[str]] = None, **kwargs
    ) -> None:
        """
        Send an event to Datadog.

        Args:
            title: Event title.
            text: Event description.
            tags: Additional tags for this event.
            **kwargs: Additional event parameters (alert_type, priority, etc.).
        """
        try:
            combined_tags = self._combine_tags(tags)
            
            # Import here to avoid circular imports
            from datadog_api_client.v2.api.events_api import EventsApi
            from datadog_api_client.v2.model.event_create_request import EventCreateRequest
            from datadog_api_client.v2.model.event_create_request_attributes import EventCreateRequestAttributes
            
            # Create event attributes
            attributes = EventCreateRequestAttributes(
                title=title,
                text=text,
                tags=combined_tags,
                **kwargs
            )
            
            # Create event request
            event_request = EventCreateRequest(data=attributes)
            
            # Send event using context manager
            with ApiClient(self.configuration) as api_client:
                events_api = EventsApi(api_client)
                events_api.create_event(body=event_request)
            
            logger.debug(f"Sent event: {title}, tags={combined_tags}")
        except Exception as e:
            logger.error(f"Failed to send event {title}: {e}")


