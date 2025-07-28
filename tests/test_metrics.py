"""
Tests for the DatadogMetrics class using the official datadog-api-client v2.
"""

import pytest
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from dd_custom_metrics.metrics import DatadogMetrics


class TestDatadogMetrics:
    """Test cases for DatadogMetrics class."""

    def test_init_with_credentials(self):
        """Test initialization with explicit credentials."""
        metrics = DatadogMetrics(
            api_key="test_api_key", 
            app_key="test_app_key", 
            host="test-host"
        )

        assert metrics.api_key == "test_api_key"
        assert metrics.app_key == "test_app_key"
        assert metrics.host == "test-host"
        assert metrics.default_tags == []
        assert metrics.namespace is None

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "DD_API_KEY": "env_api_key",
                "DD_APP_KEY": "env_app_key",
                "DD_HOST": "env-host",
                "DD_NAMESPACE": "env_namespace",
            },
        ):
            metrics = DatadogMetrics()

            assert metrics.api_key == "env_api_key"
            assert metrics.app_key == "env_app_key"
            assert metrics.host == "env-host"
            assert metrics.namespace == "env_namespace"

    def test_init_with_default_tags(self):
        """Test initialization with default tags."""
        default_tags = ["env:test", "service:myapp"]
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            tags=default_tags
        )

        assert metrics.default_tags == default_tags

    def test_init_with_namespace(self):
        """Test initialization with namespace."""
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            namespace="my_company"
        )

        assert metrics.namespace == "my_company"

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValueError, match="API key and app key are required"):
            with patch.dict(os.environ, {}, clear=True):
                DatadogMetrics()

    def test_combine_tags(self):
        """Test tag combination functionality."""
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            tags=["env:test", "service:myapp"]
        )

        # Test with additional tags
        combined = metrics._combine_tags(["type:gauge"])
        assert combined == ["env:test", "service:myapp", "type:gauge"]

        # Test with no additional tags
        combined = metrics._combine_tags()
        assert combined == ["env:test", "service:myapp"]

        # Test with None
        combined = metrics._combine_tags(None)
        assert combined == ["env:test", "service:myapp"]

    def test_prefix_metric_name_with_namespace(self):
        """Test metric name prefixing with namespace."""
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            namespace="my_company"
        )

        prefixed = metrics._prefix_metric_name("example.gauge")
        assert prefixed == "my_company.example.gauge"

    def test_prefix_metric_name_without_namespace(self):
        """Test metric name prefixing without namespace."""
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key"
        )

        prefixed = metrics._prefix_metric_name("example.gauge")
        assert prefixed == "example.gauge"

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_gauge(self, mock_metrics_api_class, mock_api_client):
        """Test gauge metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.gauge("test.gauge", 42.5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.gauge"
        assert series.type.value == "gauge"  # v2 API uses enum
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == 42.5

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_gauge_with_namespace(self, mock_metrics_api_class, mock_api_client):
        """Test gauge metric sending with namespace."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            namespace="my_company"
        )

        metrics.gauge("test.gauge", 42.5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series has the namespace prefix
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "my_company.test.gauge"
        assert series.type == "gauge"
        assert series.tags == ["type:test"]

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_increment(self, mock_metrics_api_class, mock_api_client):
        """Test increment metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.increment("test.counter", 5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.counter"
        assert series.type == "count"
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == 5.0

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_increment_with_namespace(self, mock_metrics_api_class, mock_api_client):
        """Test increment metric sending with namespace."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            namespace="my_company"
        )

        metrics.increment("test.counter", 5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series has the namespace prefix
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "my_company.test.counter"
        assert series.type == "count"
        assert series.tags == ["type:test"]

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_decrement(self, mock_metrics_api_class, mock_api_client):
        """Test decrement metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.decrement("test.counter", 3, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series (decrement sends negative value)
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.counter"
        assert series.type == "count"
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == -3.0

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_histogram(self, mock_metrics_api_class, mock_api_client):
        """Test histogram metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.histogram("test.histogram", 123.45, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.histogram"
        assert series.type == "histogram"
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == 123.45

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_timing(self, mock_metrics_api_class, mock_api_client):
        """Test timing metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.timing("test.timing", 1.5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series (timing uses histogram type)
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.timing"
        assert series.type == "histogram"
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == 1.5

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_rate(self, mock_metrics_api_class, mock_api_client):
        """Test rate metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        metrics.rate("test.rate", 10.5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.rate"
        assert series.type == "rate"
        assert series.tags == ["type:test"]
        assert len(series.points) == 1
        assert series.points[0].value == 10.5

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_metric_with_default_tags(self, mock_metrics_api_class, mock_api_client):
        """Test metric sending with default tags."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        metrics = DatadogMetrics(
            api_key="test_key", 
            app_key="test_app_key", 
            tags=["env:test", "service:myapp"]
        )

        metrics.gauge("test.gauge", 42.5, tags=["type:test"])

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()
        
        # Get the call arguments
        call_args = mock_metrics_api.submit_metrics.call_args
        body = call_args[1]['body']
        
        # Verify the metric series has combined tags
        assert len(body.series) == 1
        series = body.series[0]
        assert series.metric == "test.gauge"
        assert series.tags == ["env:test", "service:myapp", "type:test"]

    @patch('dd_custom_metrics.metrics.ApiClient')
    @patch('dd_custom_metrics.metrics.MetricsApi')
    def test_metric_error_handling(self, mock_metrics_api_class, mock_api_client):
        """Test error handling in metric sending."""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        
        mock_metrics_api = MagicMock()
        mock_metrics_api_class.return_value = mock_metrics_api
        
        # Make submit_metrics raise an exception
        mock_metrics_api.submit_metrics.side_effect = Exception("API Error")
        
        metrics = DatadogMetrics(api_key="test_key", app_key="test_app_key")

        # This should not raise an exception
        metrics.gauge("test.gauge", 42.5)

        # Verify that submit_metrics was called
        mock_metrics_api.submit_metrics.assert_called_once()


