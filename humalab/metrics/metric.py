from typing import Any
from humalab.constants import MetricDimType, GraphType


class Metrics:
    def __init__(self,
                 metric_dim_type: MetricDimType= MetricDimType.ONE_D,
                 graph_type: GraphType=GraphType.LINE) -> None:
        """
        Base class for different types of metrics.

        Args:
            metric_dim_type (MetricDimType): The dimensionality of the metric data
                (e.g., ZERO_D, ONE_D, TWO_D, THREE_D). Defaults to ONE_D.
            graph_type (GraphType): The type of graph to use for visualization
                (e.g., LINE, BAR, HISTOGRAM, SCATTER). Defaults to LINE.
        """
        self._values = []
        self._x_values = []
        self._step = -1
        self._metric_dim_type = metric_dim_type
        self._graph_type = graph_type

    @property
    def metric_dim_type(self) -> MetricDimType:
        """The dimensionality of the metric data.

        Returns:
            MetricDimType: The metric dimension type.
        """
        return self._metric_dim_type

    @property
    def graph_type(self) -> GraphType:
        """The type of graph used for visualization.

        Returns:
            GraphType: The graph type.
        """
        return self._graph_type
    
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
