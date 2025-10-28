
from humalab.metrics.metric import Metrics
from humalab.constants import MetricDimType, GraphType


class Summary(Metrics):
    def __init__(self, 
                 summary: str,
                 ) -> None:
        """
        A summary metric that captures a single value per episode or run.

        Args:
            name (str): The name of the metric.
            summary (str | None): Specify aggregate metrics added to summary.
                Supported aggregations include "min", "max", "mean", "last",
                "first", and "none". "none" prevents a summary
                from being generated.
            granularity (MetricGranularity): The granularity of the metric.
        """
        if summary not in {"min", "max", "mean", "last", "first", "none"}:
            raise ValueError(f"Unsupported summary type: {summary}. Supported types are 'min', 'max', 'mean', 'last', 'first', and 'none'.")
        super().__init__(metric_dim_type= MetricDimType.ZERO_D, 
                         graph_type=GraphType.NUMERIC)
        self._summary = summary
    
    @property
    def summary(self) -> str:
        return self._summary

    def _finalize(self) -> dict:
        if not self._values:
            return {
                "value": None,
                "summary": self.summary
            }
        final_val = None
        # For summary metrics, we only keep the latest value
        if self.summary == "last":
            final_val = self._values[-1]
        elif self.summary == "first":
            final_val = self._values[0]
        elif self.summary == "none":
            final_val = None
        elif self.summary in {"min", "max", "mean"}:
            if not self._values:
                final_val = None
            else:
                if self.summary == "min":
                    agg_value = min(self._values)
                elif self.summary == "max":
                    agg_value = max(self._values)
                elif self.summary == "mean":
                    agg_value = sum(self._values) / len(self._values)
                final_val = agg_value

        return {
            "value": final_val,
            "summary": self.summary
        }
