from abc import abstractmethod
from typing import Any


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
        
    def finalize(self) -> None:
        """Finalize the logged data for processing."""
        self._finalize()
        self._values = []
        self._x_values = []

    def _finalize(self) -> None:
        """Process the logged data before submission. To be implemented by subclasses."""
        pass
