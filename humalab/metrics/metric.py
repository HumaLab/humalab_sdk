from abc import abstractmethod
from typing import Any
from enum import Enum


class MetricType(Enum):
    """Metric types supported by Humalab."""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    # GAUGE = "gauge"
    # COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUSSIAN = "gaussian"
    HEATMAP = "heatmap"
    THREE_D_MAP = "3d_map"


class Metrics:
    def __init__(self) -> None:
        """
        Base class for different types of metrics.
        """
        self._values = []
        self._x_values = []
        self._step = -1
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        """Log a new data point for the metric. The behavior depends on the granularity.    

        Args:
            data (Any): The data point to log.
            x (Any | None): The x-axis value associated with the data point.
                if None, the current step is used.
            replace (bool): Whether to replace the last logged value.
        """
        if replace:
            self._values[-1] = data
            if x is not None:
                self._x_values[-1] = x
        else:
            self._values.append(data)
            if x is not None:
                self._x_values.append(x)
            else:
                self._x_values.append(self._step)
                self._step += 1
        
    def finalize(self) -> dict:
        """Finalize the logged data for processing."""
        ret_result = self._finalize()

        return ret_result

    def _finalize(self) -> dict:
        """Process the logged data before submission. To be implemented by subclasses."""
        ret_val = {
            "values": self._values,
            "x_values": self._x_values
        }
        self._values = []
        self._x_values = []
        self._step = -1
        return ret_val    
