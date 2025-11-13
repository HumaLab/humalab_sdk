<div align="center">

# HumaLab SDK

**Python SDK for Adaptive AI Validation**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.3-orange.svg)](https://pypi.org/project/humalab/)

[Homepage](https://humalab.ai) • [Application](https://app.humalab.ai) • [Documentation](https://docs.humalab.ai) • [Tutorial Video](https://youtu.be/F-7j2eWypEQ)

</div>

---

## Overview

HumaLab SDK is a comprehensive Python library for creating, managing, and evaluating adaptive AI validation scenarios. Designed for researchers and developers in robotics, machine learning, and embodied AI, it provides a robust framework for systematic exploration of AI system behavior through probabilistic scenario generation and advanced metrics tracking.

### Key Features

- **Adaptive Scenarios**: Define parameter spaces using probability distributions for systematic testing
- **Comprehensive Metrics**: Track time-series data, distributions, and custom statistics
- **Episode Management**: Organize experiments into runs and episodes with automatic lifecycle tracking
- **Platform Integration**: Seamless upload and visualization through the HumaLab platform
- **Asset Management**: Handle URDF, MJCF, mesh, USD, and other simulation resources
- **Reproducibility**: Built-in seed management and version tracking for experiments

---

## Installation

Install HumaLab SDK via pip:

```bash
pip install humalab
```

**Requirements**: Python 3.8 or higher

---

## Quick Start

### Tutorial Video

Get started quickly with our comprehensive tutorial:

[![HumaLab Tutorial](https://img.youtube.com/vi/uaxiDEXRH1w/0.jpg)](https://youtu.be/F-7j2eWypEQ)

### Basic Example

```python
import humalab as hl

# Initialize with API key and project configuration
with hl.init(
    api_key="your_api_key",
    project="robotics_validation",
    name="parameter_sweep_v1",
    scenario={
        "gravity": "${uniform: -10, -9}",
        "friction": "${gaussian: 0.5, 0.1}",
        "wind_speed": "${uniform: 0, 5}"
    }
) as run:

    # Execute multiple episodes
    for i in range(100):
        with run.create_episode() as episode:
            # Access sampled parameters
            gravity = episode.gravity
            friction = episode.friction
            wind_speed = episode.wind_speed

            # Run your validation logic
            result = run_simulation(gravity, friction, wind_speed)

            # Log results
            episode.log({
                "success": result.success,
                "distance": result.distance,
                "time": result.time
            })

print("Experiment complete! View results at https://app.humalab.ai")
```

---

## Core Concepts

### Scenarios

Scenarios define parameterized configurations using probability distributions, enabling systematic exploration of your AI system's behavior space.

**Supported Distributions:**

- **Uniform**: `${uniform: min, max}` - Uniform sampling between bounds
- **Gaussian**: `${gaussian: mean, std}` - Normal distribution
- **Truncated Gaussian**: `${truncated_gaussian: mean, std, min, max}` - Bounded normal distribution
- **Log-Uniform**: `${log_uniform: min, max}` - Logarithmic scale sampling
- **Bernoulli**: `${bernoulli: p}` - Binary distribution
- **Categorical**: `${categorical: [choices], [weights]}` - Discrete categorical sampling
- **Discrete**: `${discrete: low, high}` - Integer sampling

**Multi-dimensional variants** (1D, 2D, 3D) are available for spatial parameters.

**Example:**

```python
from humalab.scenarios import Scenario

scenario = Scenario()
scenario.init(
    scenario={
        "environment": {
            "gravity": "${uniform: -9.8, -8.8}",
            "temperature": "${gaussian: 20, 5}"
        },
        "robot": {
            "position": "${uniform_2d: [-1, -1], [1, 1]}",
            "mass": "${log_uniform: 0.5, 2.0}"
        }
    },
    seed=42  # For reproducibility
)
```

### Runs and Episodes

**Run**: A complete validation experiment containing multiple episodes, metrics, and metadata.

**Episode**: A single execution with specific parameter values sampled from scenario distributions.

```python
# Create a run
run = hl.Run(
    scenario=scenario,
    project="my_project",
    name="experiment_1",
    description="Testing parameter variations",
    tags=["baseline", "v1"]
)

# Execute episodes
with run:
    for i in range(50):
        with run.create_episode() as episode:
            # Episode-specific logic
            result = validate(episode)
            episode.log({"metric": result.value})
```

### Metrics

Track and analyze experimental results with various metric types:

**Standard Metrics**: Time-series data with configurable visualizations

```python
from humalab.constants import GraphType

metric = hl.metrics.Metrics(graph_type=GraphType.LINE)
run.add_metric("training_loss", metric)

for step in range(1000):
    loss = train_step()
    run.log({"training_loss": loss}, x={"training_loss": step})
```

**Summary Metrics**: Aggregate data into single statistics

```python
from humalab.metrics import Summary

max_reward = Summary(summary="max")
avg_score = Summary(summary="mean")

run.add_metric("best_reward", max_reward)
run.add_metric("average_score", avg_score)
```

**Scenario Statistics**: Automatically tracked parameter distributions and correlations

---

## Authentication

Configure authentication before using the SDK:

```python
import humalab as hl

# One-time configuration
hl.login(api_key="your_api_key", host="https://api.humalab.ai")

# Then use init without credentials
with hl.init(project="my_project", scenario={...}) as run:
    pass
```

Get your API key from [app.humalab.ai](https://app.humalab.ai).

---

## Advanced Usage

### Custom Episode IDs

```python
episode = run.create_episode(episode_id="custom_episode_001")
```

### Code Artifact Tracking

```python
with open("agent.py", "r") as f:
    code = f.read()

run.log_code(key="agent_code", code_content=code)
```

### Error Handling

```python
from humalab.humalab_api_client import EpisodeStatus

with run.create_episode() as episode:
    try:
        result = validate(episode)
        episode.log({"score": result.score})
        episode.finish(status=EpisodeStatus.FINISHED)
    except Exception as e:
        episode.finish(status=EpisodeStatus.ERRORED, err_msg=str(e))
```

### Multiple Graph Types

```python
from humalab.constants import GraphType

# Line graph for time-series
line_metric = hl.metrics.Metrics(graph_type=GraphType.LINE)

# Histogram for distributions
hist_metric = hl.metrics.Metrics(graph_type=GraphType.HISTOGRAM)

# Scatter for 2D relationships
scatter_metric = hl.metrics.Metrics(graph_type=GraphType.SCATTER)

# 3D visualization
map_3d = hl.metrics.Metrics(graph_type=GraphType.THREE_D_MAP)
```

---

## Platform Features

### Web Application

Access the HumaLab web application at [app.humalab.ai](https://app.humalab.ai) to:

- Visualize experiment results and metrics
- Manage scenarios, runs, and resources
- Create and configure API keys
- Analyze scenario statistics and episode outcomes
- Share and collaborate on validation experiments

### Resource Management

Upload and manage simulation assets including URDF files, meshes, USD files, and more through the platform's resource manager.

---

## Documentation

Comprehensive documentation is available at the following resources:

- **Homepage**: [humalab.ai](https://humalab.ai)
- **Full Documentation**: [docs.humalab.ai](https://docs.humalab.ai)
- **Tutorial Video**: [YouTube Tutorial](https://youtu.be/F-7j2eWypEQ)
- **Application**: [app.humalab.ai](https://app.humalab.ai)

### Documentation Topics

- [Introduction](https://docs.humalab.ai/docs) - Overview and key concepts
- [Quick Start Guide](https://docs.humalab.ai/docs/quickstart) - Get up and running quickly
- [Scenarios](https://docs.humalab.ai/docs/scenarios) - Define adaptive test scenarios
- [Runs & Episodes](https://docs.humalab.ai/docs/runs) - Manage experiment lifecycle
- [Metrics](https://docs.humalab.ai/docs/metrics) - Track and analyze results
- [API Reference](https://docs.humalab.ai/docs/api) - Complete API documentation

---

## Use Cases

HumaLab SDK is designed for:

- **Robotics Validation**: Test robotic systems across varying environmental conditions
- **Reinforcement Learning**: Evaluate RL agents in diverse scenarios
- **Simulation Testing**: Systematic parameter sweeps for physics simulations
- **AI Safety Research**: Stress-test AI systems with edge case generation
- **Hyperparameter Optimization**: Explore hyperparameter spaces with probabilistic sampling
- **Embodied AI**: Validate embodied agents in adaptive environments

---

## Example: Complete Workflow

```python
import humalab as hl
from humalab.constants import GraphType
from humalab.humalab_api_client import EpisodeStatus

# Configure authentication
hl.login(api_key="your_api_key", host="https://api.humalab.ai")

# Define scenario
scenario = hl.scenarios.Scenario()
scenario.init(
    scenario={
        "learning_rate": "${log_uniform: 0.0001, 0.1}",
        "batch_size": "${categorical: [32, 64, 128], [0.3, 0.5, 0.2]}",
        "dropout": "${uniform: 0.1, 0.5}"
    },
    seed=42
)

# Create run with metrics
with hl.init(
    project="hyperparameter_search",
    name="lr_batch_dropout_sweep",
    description="Systematic hyperparameter exploration",
    tags=["training", "optimization", "v1"],
    scenario=scenario
) as run:

    # Add run-level metrics
    success_metric = hl.metrics.Metrics(graph_type=GraphType.LINE)
    run.add_metric("success_rate", success_metric)

    # Execute episodes
    successes = 0
    for i in range(100):
        with run.create_episode() as episode:
            # Train model with sampled parameters
            model = train_model(
                lr=episode.learning_rate,
                batch_size=episode.batch_size,
                dropout=episode.dropout
            )

            # Log episode results
            episode.log({
                "accuracy": model.accuracy,
                "loss": model.final_loss,
                "epochs": model.epochs
            })

            # Update run metrics
            if model.accuracy > 0.9:
                successes += 1

            run.log({"success_rate": successes / (i + 1)})

print(f"Completed 100 episodes. Success rate: {successes}%")
print("View detailed results at https://app.humalab.ai")
```

---

## Development

### Package Structure

```
humalab/
├── __init__.py          # Main package exports
├── humalab.py          # Core init/login/finish functions
├── run.py              # Run class implementation
├── episode.py          # Episode class implementation
├── scenarios/          # Scenario management
├── metrics/            # Metrics and statistics
├── dists/              # Probability distributions
└── assets/             # Asset management utilities
```

### Contributing

Contributions are welcome! Please submit issues and pull requests to the GitHub repository.

### Requirements

- Python >= 3.8
- See `requirements.txt` for dependencies

---

## Project Information

**Version**: 0.1.3

**License**: MIT

**Author**: HumaLab Team

**Contact**: info@humalab.ai

**Repository**: [github.com/humalab/humalab_sdk](https://github.com/humalab/humalab_sdk)

**Bug Tracker**: [github.com/humalab/humalab_sdk/issues](https://github.com/humalab/humalab_sdk/issues)

---

## Support

For support and questions:

- **Email**: info@humalab.ai
- **GitHub Issues**: [github.com/humalab/humalab_sdk/issues](https://github.com/humalab/humalab_sdk/issues)
- **Documentation**: [docs.humalab.ai](https://docs.humalab.ai)

---

## Citation

If you use HumaLab SDK in your research, please cite:

```bibtex
@software{humalab_sdk,
  title = {HumaLab SDK: Python Library for Adaptive AI Validation},
  author = {HumaLab Team},
  year = {2025},
  url = {https://github.com/humalab/humalab_sdk}
}
```

---

<div align="center">

**[Get Started Now](https://app.humalab.ai)** | **[View Documentation](https://docs.humalab.ai)** | **[Watch Tutorial](https://youtu.be/F-7j2eWypEQ)**

</div>
