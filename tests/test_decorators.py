"""
Tests for the decorators module.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from dd_custom_metrics.decorators import (
    instrument_latency,
    instrument_counter,
    instrument_gauge,
    instrument_histogram,
)


class TestInstrumentLatency:
    """Test cases for instrument_latency decorator."""

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_basic_latency_instrumentation(self, mock_metrics_class):
        """Test basic latency instrumentation."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency")
        def test_function():
            time.sleep(0.1)
            return "success"

        result = test_function()

        assert result == "success"
        mock_client.timing.assert_called_once()
        call_args = mock_client.timing.call_args
        assert call_args[0][0] == "test.latency"
        assert call_args[0][1] > 0  # Should be positive execution time
        assert "success:True" in call_args[1]["tags"]  # Should include success tag

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_with_custom_tags(self, mock_metrics_class):
        """Test latency instrumentation with custom tags."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency", tags=["service:test", "env:dev"])
        def test_function():
            return "success"

        test_function()

        call_args = mock_client.timing.call_args
        tags = call_args[1]["tags"]
        assert "service:test" in tags
        assert "env:dev" in tags
        assert "success:True" in tags

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_with_args_inclusion(self, mock_metrics_class):
        """Test latency instrumentation with argument inclusion."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency", include_args=True)
        def test_function(user_id, plan="basic"):
            return f"user_{user_id}_{plan}"

        test_function(123, "premium")

        call_args = mock_client.timing.call_args
        tags = call_args[1]["tags"]
        assert "arg_0:123" in tags
        assert "arg_1:premium" in tags

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_with_result_inclusion(self, mock_metrics_class):
        """Test latency instrumentation with result inclusion."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency", include_result=True)
        def test_function():
            return "test_result"

        test_function()

        call_args = mock_client.timing.call_args
        tags = call_args[1]["tags"]
        assert "result:test_result" in tags

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_with_exception(self, mock_metrics_class):
        """Test latency instrumentation with exception handling."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency")
        def test_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_function()

        call_args = mock_client.timing.call_args
        tags = call_args[1]["tags"]
        assert "exception:ValueError" in tags
        assert "success:False" in tags

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_with_custom_client(self, mock_metrics_class):
        """Test latency instrumentation with custom metrics client."""
        custom_client = MagicMock()

        @instrument_latency("test.latency", metrics_client=custom_client)
        def test_function():
            return "success"

        test_function()

        custom_client.timing.assert_called_once()
        mock_metrics_class.assert_not_called()  # Should not create new client


class TestInstrumentCounter:
    """Test cases for instrument_counter decorator."""

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_counter_on_success(self, mock_metrics_class):
        """Test counter instrumentation on successful execution."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_counter("test.counter")
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"
        mock_client.increment.assert_called_once_with(
            "test.counter", tags=["status:success"]
        )

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_counter_on_failure(self, mock_metrics_class):
        """Test counter instrumentation on failed execution."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_counter("test.counter", increment_on_failure=True)
        def test_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_function()

        mock_client.increment.assert_called_once_with(
            "test.counter", tags=["status:error", "error:ValueError"]
        )

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_counter_with_custom_tags(self, mock_metrics_class):
        """Test counter instrumentation with custom tags."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_counter("test.counter", tags=["service:test"])
        def test_function():
            return "success"

        test_function()

        call_args = mock_client.increment.call_args
        tags = call_args[1]["tags"]
        assert "service:test" in tags
        assert "status:success" in tags


class TestInstrumentGauge:
    """Test cases for instrument_gauge decorator."""

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_gauge_instrumentation(self, mock_metrics_class):
        """Test gauge instrumentation."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_gauge("test.gauge", lambda result: len(result))
        def test_function():
            return ["item1", "item2", "item3"]

        result = test_function()

        assert result == ["item1", "item2", "item3"]
        mock_client.gauge.assert_called_once_with("test.gauge", 3, tags=[])

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_gauge_with_custom_tags(self, mock_metrics_class):
        """Test gauge instrumentation with custom tags."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_gauge(
            "test.gauge", lambda result: result["count"], tags=["service:test"]
        )
        def test_function():
            return {"count": 42, "status": "ok"}

        test_function()

        mock_client.gauge.assert_called_once_with(
            "test.gauge", 42, tags=["service:test"]
        )


class TestInstrumentHistogram:
    """Test cases for instrument_histogram decorator."""

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_histogram_instrumentation(self, mock_metrics_class):
        """Test histogram instrumentation."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_histogram("test.histogram", lambda result: result["size"])
        def test_function():
            return {"size": 1024, "type": "data"}

        result = test_function()

        assert result == {"size": 1024, "type": "data"}
        mock_client.histogram.assert_called_once_with("test.histogram", 1024, tags=[])

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_histogram_with_custom_tags(self, mock_metrics_class):
        """Test histogram instrumentation with custom tags."""
        mock_client = MagicMock()
        mock_metrics_class.return_value = mock_client

        @instrument_histogram(
            "test.histogram", lambda result: result["value"], tags=["service:test"]
        )
        def test_function():
            return {"value": 99.5, "unit": "percent"}

        test_function()

        mock_client.histogram.assert_called_once_with(
            "test.histogram", 99.5, tags=["service:test"]
        )


class TestDecoratorErrorHandling:
    """Test error handling in decorators."""

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_latency_metric_sending_failure(self, mock_metrics_class):
        """Test that latency decorator handles metric sending failures gracefully."""
        mock_client = MagicMock()
        mock_client.timing.side_effect = Exception("Network error")
        mock_metrics_class.return_value = mock_client

        @instrument_latency("test.latency")
        def test_function():
            return "success"

        # Should not raise an exception
        result = test_function()
        assert result == "success"

    @patch("dd_custom_metrics.decorators.DatadogMetrics")
    def test_gauge_metric_sending_failure(self, mock_metrics_class):
        """Test that gauge decorator handles metric sending failures gracefully."""
        mock_client = MagicMock()
        mock_client.gauge.side_effect = Exception("Network error")
        mock_metrics_class.return_value = mock_client

        @instrument_gauge("test.gauge", lambda result: len(result))
        def test_function():
            return ["item1", "item2"]

        # Should not raise an exception
        result = test_function()
        assert result == ["item1", "item2"]
