# InterrogatorQA - Extracted Confluence Documentation

**Extracted:** December 8, 2024  
**Source:** Confluence - PRISMATEAM Space  
**Purpose:** Complete reference for automation priorities

---

# 📚 Table of Contents

1. [InterrogatorQA - Product Level Overview](#1-interrogatorqa---product-level-overview)
2. [InterrogatorQA - Technical Level Overview](#2-interrogatorqa---technical-level-overview)
3. [Start Using QA Framework - Easy Start](#3-start-using-qa-framework---easy-start)
4. [Logs Collector](#4-logs-collector)
5. [Monitoring Architecture](#5-monitoring-architecture)
6. [Data Analysis & Recovery Tools](#6-data-analysis--recovery-tools)

---

# 1. InterrogatorQA - Product Level Overview

**Page ID:** 2098462722  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098462722

## What InterrogatorQA is

InterrogatorQA is Prisma automated test framework that runs end-to-end validation of a Prisma deployment. It brings up the system (Supervisor, RabbitMQ, Telegraf, players/mocks), exercises core behaviors, and validates health, performance, and reliability using clear pass/fail criteria.

The framework includes comprehensive mocking capabilities through **AlgoMock**, **Control Center Mock**, and **Alerts Player** to simulate real-world scenarios without requiring full production hardware setups.

## Areas Covered (What We Verify)

| **Area** | **Description** |
|----------|-----------------|
| **Bring-up and basic health** | Services start, keep-alive and heartbeats are correct, no critical routing keys leak into the bus. |
| **Message bus health** | RabbitMQ queues are active, publish rates are within expected ranges, no prolonged silences or buffer overflows. |
| **Resource usage** | CPU, memory, disk, GPU, and swap stay within allowed peaks and averages; charts and summaries are produced with detailed peak analysis and range validation. |
| **Alerts and HeatMaps** | Mocked alerts are played and both alerts and heatmap flows are validated against expectations (cycles, timing, sizes). |
| **PRP recording checks** | PRP files are created and compare correctly when applicable, with sophisticated matrix-based comparison algorithms. |
| **Stability and recoverability** | Detects process crashes, measures recovery, and (optionally) orchestrates a planned restart to test resilience. Includes crash monitoring with configurable recovery timeouts. |
| **Database integrity** | MongoDB collections are validated for alerts and other critical data. |
| **System monitoring** | Comprehensive hardware monitoring including GPU temperature, power consumption, and system-wide resource tracking. |
| **Bit test verification** | Validates BIT (Built-In Test) logs for both status and test operations. |
| **External integrations** | Validates connectivity to external systems like RabbitMQ management endpoints and REST APIs. |

## Standalone Tools

- **Preprocessor Analysis** – Data dump analysis and crash investigation tools. Includes stability validation and performance regression detection.
- **Data Recovery** – Tools for extracting and analyzing test data post-execution.
- **PRP Comparison Utilities** – Multiple comparison algorithms for different validation needs

## Test Suites at a Glance

| **Test Suite** | **Description** |
|----------------|-----------------|
| **Smoke** | Short, fast checks to validate a deployment. Verifies service bring-up, essential metrics, average publish rates, and basic file outputs. |
| **Long-term** | Longer run with richer monitoring. Aggregates snapshots, validates sustained behavior, alert phases, and heatmap/PRP expectations with tighter criteria. |
| **Reliability** | Like smoke, but includes an intentional service restart (or observes an external one) and verifies the system's resilience around downtime. |
| **Recoverability** | Focused on detecting and summarizing crashes and recovery only; other cyclic checkers are disabled to isolate the signal. Configurable crash monitoring with dead process limits and recovery time thresholds. |

## How it Decides PASS/FAIL

All validations are data-driven via YAML "PF criteria" per suite. Examples include:

- Queue publish rates: min/max avg, max silence time, max buffer size.
- Heartbeats/keep-alive frequencies and timestamps.
- Expected alerts (IDs, timing windows) and optional heatmap expectations.
- PRP and Heatmaps recordings validation.
- Resource consumption max, avg limits for CPU/memory/disk/GPU/swap.
- GPU metrics: temperature, power usage, memory utilization, and performance states.
- Crash recovery: maximum dead processes allowed, recovery time limits.
- Bit test log validation for both status and operational tests.

The framework supports **parent configuration inheritance**, allowing common settings to be shared across test suites while enabling suite-specific overrides.

## What You Get After a Run

- **Execution log** – Quick view of failures and their context with detailed error categorization.
- **Resource charts and summaries** – Visual confirmation of CPU/memory/disk/GPU/swap behavior, including peaks, averages, and allowed ranges.
- **Queues analysis** – Average rates, silences, and buffers by queue; helps attribute messaging issues to specific components.
- **PRP/heatmap comparisons** – Evidence for data-path correctness and storage performance using matrix-based comparison algorithms.
- **System monitoring reports** – Comprehensive hardware analysis including GPU metrics, crash recovery logs, and stability indicators.
- **Xray export** – JSON report ready to be posted to Jira Xray for traceability.
- **Data dumps** – Background-collected data for offline analysis and debugging.

## Tested Versions

- **Power**: Versions 11.15, 11.17, 11.19
- **Flow**: Version 11.50

## Where It Can Be Run

- **AWS EC2** – Cloud-based execution with Jenkins CI or RDP.
- **Prisma Lab** – Physical PC machines for production-like hardware validation.
- **Local PC** – Developer or tester workstations for local debugging and validation.

## Typical When to Use Which Suite

- **On CI pre-merge (possible on developer machine)** – Run Smoke.
- **Before a release, overnight CI** – Run Long-term.
- **When changing infrastructure components (e.g., RabbitMQ)** – Run Reliability.
- **When investigating stability issues** – Run Recoverability.
- **Initial setup validation** – Run Pre-test.

## Key Benefits

- **Confidence** – Repeatable, data-driven PASS/FAIL across environments with comprehensive mocking capabilities.
- **Speed** – One command to bring up the system and validate the essentials, with parallel execution support.
- **Signal** – Suites tuned for fast checks, sustained behavior, resilience, or crash detection.
- **Flexibility** – Configurable through YAML files with environment variable support and inheritance.
- **Integration** – Built-in support for external systems validation and test management tools.
- **Monitoring** – Advanced resource and system monitoring with detailed analytics and reporting.

## End-to-End Timeline (What Happens During a Run)

1. Configuration is loaded: effective params and selected PF criteria for the chosen suite.
2. Services are prepared and started (Supervisor, RabbitMQ, Telegraf; optional players/mocks). Includes broker URI detection and service dependency management.
3. The orchestrator runs the suite:
   - Cyclic health checks (services, queues, heartbeats, keep-alive, PRP when enabled)
   - Resource monitoring in the background
   - Suite-specific behaviors (long-term alert phases; reliability restarts; recoverability crash monitor)
   - Background data collection for comprehensive analysis
   - Optional player execution with PRP data simulation
4. Post-run validations and summaries:
   - Queue average-rate checks (in smoke), artifacts collection, charts and tables
   - PRP/heatmap comparisons using advanced matrix algorithms
   - Resource usage validation with peak and range analysis
   - Crash recovery analysis and reporting
   - PASS/FAIL evaluation across all enabled checks and criteria
5. Teardown: services are stopped per policy and final reports are written (optionally exported to Xray).

## Upcoming: Split System

Split System enables distributed execution of tests across **two independent machines**:
- **INTG [Interrogator]** - acquisition, player control, recorders, publishing streams to RabbitMQ.
- **ANLZ [Analyzer]** - algorithmic processing, heatmaps, downstream metrics, reporting.

---

# 2. InterrogatorQA - Technical Level Overview

**Page ID:** 2098790423  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2098790423

## Prerequisites

- Windows 10/11 Pro, Python 3.8, Visual Studio components per internal setup guide
- Prisma stack: Supervisor, RabbitMQ, Telegraf (optional mocks for Alerts, ControlCentre, ALGO)
- Repository access: PZ (nc_pz), OPS (nc_ops), InterrogatorQA

## Quick Start

1. Activate your Python environment before running anything:

```batch
cd %userprofile%\nc_pz
call virtualenvs\pzdev\Scripts\activate.bat
```

2. Run tests via pytest (elevated shell recommended to allow service management):

```batch
python -m pytest .\tests --config %PRISMA_CONFIG%\<pc_name>_effective_params.yaml --suite smoke
```

## CLI Options (from tests/conftest.py)

| Option | Description |
|--------|-------------|
| `--config <path>` | Effective params YAML (defaults to `<HOSTNAME>_effective_params.yaml` from `framework.paths.CONFIG_DIR`) |
| `--suite {smoke,sanity,recoverability,longterm,reliability}` | Select test suite |
| `--hold` | Pause before teardown for manual inspection |
| `--preclean` | Remove PRP recordings before run |
| `--xray <output_dir>` | Save and send Xray report (requires credentials via `tools.xray.get_xray_token`) |
| `--test-time <duration>` | Override test duration (e.g., `30m`, `01:30:00`, `90s`) |
| `--rulerun` | (Dev) regenerate `supervisor.yaml` via RuleRunner |

## Suites and Their Behavior

- **smoke**: Short run; post-run queue average checks; core cyclic checks enabled; quick PF thresholds
- **longterm**: Longer run; snapshot aggregation; alert phases; heatmap/PRP expectations; stricter criteria
- **reliability**: Like smoke, plus planned or observed restart for a target service; reliability manager downgrades broker-down AMQP errors to skipped and excludes downtime from averages
- **recoverability**: Crash/restore detection only; other cyclic checkers disabled

## Suite Toggles and Inheritance

- PF criteria can inherit from a parent file (via `parent_config` pattern in effective params), allowing a base policy per environment with suite-specific overrides.
- Common toggles:
  - `cyclic_checkers.*`: enable/disable specific checkers
  - `resource_monitoring.enabled` and `interval`
  - `queues_monitoring.queue_stats` and `queues_to_ignore`
  - `supervisor.*` and `telegraf.*` lifecycle controls
  - `reliability` and `recovery_monitor` blocks

## Configuration Files (Inputs)

- **Effective params**: Resolved by `framework.configurator.Configurator` (supports inheritance via `parent_config`, env var substitution, and suite-specific toggles)
- **PF criteria** per suite and per vertical: `tests/<suite>_<vertical>_PF_criteria.yaml`

## What the Framework Wires Together

- `framework.orchestrator.Orchestrator`: Setup → run → teardown; starts Supervisor/Telegraf/RabbitMQ (via `service_control`/`sv_cli_wrapper`), players/mocks, and checkers
- `framework.configurator.Configurator`: Loads effective params and PF criteria; exposes getters and suite toggles
- `framework.cyclic_checker.*`: Background validators for services, keep-alive, heartbeats, queues, PRP, and critical messages
- `framework.system_monitor` + `framework.telegraf_monitor`: Resource sampling and Telegraf metrics collection; summaries and plots via `resource_*` modules
- `libs.algo_mock` and `libs.alerts_player`: Optional mocks and players to optionally seed alerts and heatmap flows when ALGO is mocked

## Execution Flow (Expanded)

1. Pytest parses CLI, loads `Configurator` with effective params and PF criteria.
2. `Orchestrator` starts required services and mocks/players based on config.
3. Requested cyclic checkers are instantiated and started.
4. Long-running phase proceeds (time-boxed by suite or `--test-time`), with background monitoring.
5. Post-run: queue averages computed (smoke/reliability), resources summarized, plots generated, PF evaluated.
6. Teardown: services stopped per policy; report persisted; optional Xray push.

## Outputs and Reporting

- Console logs and per-test PASS/FAIL with reasons
- Artifacts: metrics, charts, and JSON summaries saved under test/output directories
- Xray export: a JSON report is produced; if `--xray` is set, it is posted to Xray using a bearer token

## Adding a New Suite

1. Create new PF criteria YAML with suite-specific thresholds.
2. Add a test file under `tests/` that wires to the common fixtures and marks (add Xray marks).
3. Ensure `--suite` allows selecting it (if beyond the standard set, gate via test collection and PF toggles).

## Troubleshooting and Tips

- Run in an elevated shell to avoid service management failures.
- If RabbitMQ is intentionally down (reliability), connection errors are downgraded to skipped; verify `reliability` block.
- Use `--hold` to pause before teardown and inspect services and queues.
- Use `--test-time` to shorten or extend a run without editing YAMLs.
- For known noisy Telegraf log patterns, add to `telegraf.ignore_errors` in PF criteria.

## Notes and Caveats

- Run with elevated privileges to manage Windows services
- Swap failures require both OS and Telegraf to exceed limits; single-source exceedance is a warning by design
- Reliability suite marks some known tests as expected-to-fail or downgrades AMQP broker-down errors to skipped during planned downtime

---

# 3. Start Using QA Framework - Easy Start

**Page ID:** 2114355204  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2114355204

## Preparation for the First Run

As a starting point, let's assume that the PZ, OPS, pz-core-libs repositories, along with all required packages, have already been downloaded and the full deployment for the selected ALGO version has been completed. Effective Params File ready (referred later as EP/EPF), which allows us to run Supervisor and the entire product.

## STEPS

Let's use dir `C:\Prisma` as our workspace (you are free to use any directory)

### Clone repository

```batch
cd C:\Prisma
git clone https://bitbucket.org/prismaphotonics/interrogatorqa/
cd interrogatorqa
```

Note in case of credentials issues you may clone on your PC and copy to remote machine

### Set environment variables

Open **cmd** terminal as **Administrator**

```batch
setx PRISMA_QA C:\Prisma\interrogatorqa /M
setx PRISMA_TEST_DATA C:\test_data /M
```

(open a new terminal for changes to take effect) - Open **cmd** terminal as **Administrator**

### Create folders for test data

```batch
mkdir C:\heatmaps
mkdir %PRISMA_TEST_DATA%
```

### Download test data from S3

```batch
aws s3 sync s3://pz-edge-qa/test_data/ %PRISMA_TEST_DATA% --quiet
```

### (optional) If you are not using PZ-shell, activate virtual environment

```batch
%userprofile%\virtualenvs\pzdev\Scripts\activate.bat
```

### Install python dependencies defined in pyproject.toml

```batch
python -m pip install --upgrade pip
python -m pip install .
```

## Running a Test

```batch
cd %PRISMA_QA%
python -m pytest .\tests\test_smoke.py --config <EPF_path>.yaml --suite smoke -vv -s -rA --log-level=INFO

==== 19 passed, 1 skipped, 1 xfailed, 2 xpassed in 366.78s (0:06:06) ====
```

## Files, Parameters and Paths

### pytest – Python/pytest entry point (test set)

```
tests/
├── test_smoke.py            # Smoke test suite
├── test_longterm.py         # Long-term stability tests
└── test_recoverability.py   # Recovery testing
```

### --suite <suite> ; selector for Pass/Fail criteria

```
tests/
├─ smoke_power_PF_criteria.yaml          -> PF criteria for smoke suite
├─ longterm_power_PF_criteria.yaml       -> PF criteria for longterm suite
└─ recoverability_power_PF_criteria.yaml -> PF criteria for recoverability
```

You can create new criteria files for other verticals by copying and adjusting limits i.e. `smoke_power_PF_criteria.yaml` -> `smoke_flow_PF_criteria.yaml`

### Other options

| Option | Description |
|--------|-------------|
| `-vv ; -s ; -rA; --log-level` | pytest verbosity logging options |
| `--preclean` | Cleans recordings from previous test run **⚠️ CAUTION: erases all data from recordings and heatmaps directories** |
| `--test-time <time>` | (longterm only) specify duration e.g `<time>=1h15m` |
| `--rulerun` | Regenerate supervisor.yaml (dev only) **⚠️ CAUTION: your yaml's will be overwritten** |
| `--hold` | Pause before teardown for manual inspection |
| `--xray <path>` | (CI only) push results to Jira/Xray |

## Results Interpretation

```
======= 2 failed, 16 passed, 2 skipped, 2 xfailed, 1 xpassed, 10 warnings in 341.08s (0:05:41) =====
```

| Status | Meaning |
|--------|---------|
| `<N> failed` | Number of FAILED tests from the suite |
| `<N> passed` | Tests that PASSED successfully |
| `<N> skipped` | Tests SKIPPED (not executed, marked 'skip') |
| `<N> xfailed` | Expected failures (marked 'xfail' and did fail) |
| `<N> xpassed` | Unexpected passes (marked 'xfail' but passed) |
| `<N> warnings` | Warnings during execution (no impact on result) |

**Note:** Tests marked `xfail` are expected to fail (e.g. graceful shutdown) or are unstable.
Tests marked `skip` may need update (obsolete), or marked dynamically as some process/functionality may be disabled by the configuration.

---

# 4. Logs Collector

**Page ID:** 2248114178  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2248114178

## What is Logs Collector

**Logs Collector** is a Python utility used to collect and filter log files within a specific time window. Filters log files (`.log`, `.txt`) based on timestamps inside file content.

It scans all logs in the source directory, extracts only lines between the selected start and end timestamps, and saves them into a destination folder or directly to **Amazon S3**.

## Repository Link

https://bitbucket.org/prismaphotonics/interrogatorqa/src/master/standalone/

Script is a standalone instance, you may copy only this one file and use it:

```batch
python logs_collector.py --src <path> --dst <path or S3> --st <time> --et <time>
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--src` | Source directory with logs (default: environment variable `%PRISMA_LOGS%`). |
| `--dst` | Destination path – local folder or `s3://bucket/prefix`. |
| `--st` | **Start time [obligatory]** – beginning of the filtering window (required). |
| `--et` | **End time** – end of the filtering window (optional, defaults to current time). |
| `--noarchive` | Skip creation of the `.7z` archive (in case of S3 it will push plain logs) |
| `--include-zips` | Include archive files (`.zip`, `.7z`, `.rar`, `.tar`, `.tar.gz`). |

**Note:** The only obligatory parameter is `--st`

## Accepted Time Formats

| Type | Example | Meaning |
|------|---------|---------|
| Full date and time (underscored) | `20250101_12000` | 2025-01-01 12:00:00 |
| Full date and time (dashes or dots) | `2025-01-01_120000`, `2025.01.01_120000` | 2025-01-01 12:00:00 |
| Month/Day + time | `0112_1200` | Jan 12, 12:00 (current year) |
| Time only (with colons) | `12:34:56`, `12:34` | Today at 12:34:56 or 12:34 |
| Time only (compact) | `123456`, `1234` | Today at 12:34:56 or 12:34 |
| Date only | **NOT ALLOWED** | |

## Usage Examples

### Store on Local Drive

```batch
python .\logs_collector.py --src c:\Prisma\logs --st 11.04_12:00 --et 11.04_16:00 --dst ..\prisma_logs_2025-11-04___12-16
```

### Store *.7z to S3

```batch
python .\logs_collector.py --src c:\Prisma\logs --st 11.04_12:00 --et 11.04_16:00 --dst s3://pz-edge-qa/logs/prisma_logs_2025-11-04___12-16
```

### Store Files Tree to S3 (--noarchive)

```batch
python .\logs_collector.py --src c:\Prisma\logs --st 11.04_12:00 --et 11.04_16:00 --dst s3://pz-edge-qa/logs/prisma_logs_2025-11-04___12-16 --noarchive
```

---

# 5. Monitoring Architecture

**Page ID:** 2338226184  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2338226184

## Advanced Monitoring Architecture

### Resource Monitoring Framework

InterrogatorQA implements a comprehensive three-tier monitoring system designed to provide complete visibility into system behavior during test execution.

### System Monitor Component

Provides OS-level resource tracking with configurable sampling intervals:

**CPU Monitoring:**
- Overall CPU utilization percentage
- Per-core usage breakdown
- Sustained high-usage detection
- Process-specific CPU consumption

**Memory Management:**
- RAM usage tracking with peak detection
- Swap file utilization monitoring
- Memory leak identification
- Process memory mapping

**Storage & I/O:**
- Disk usage percentages by mount point
- I/O operations per second (IOPS)
- Read/write throughput metrics
- File system health checks

### Telegraf Integration

TelegrafMonitor performs threshold validation, sustained-usage checks, and integrates collected metrics with PF criteria for automatic pass/fail evaluation.

**RabbitMQ Metrics:**
- Queue depth monitoring
- Message throughput rates
- Connection pool status
- Exchange and binding health

**System Performance:**
- Network interface statistics
- System load averages
- Disk performance metrics
- Custom application counters

### Resource Validation Engine

Automated validation against Pass/Fail criteria with intelligent alerting:

**Threshold Management:**
- Configurable warning and critical thresholds
- Time-window based validation (e.g., sustained high usage)
- Trend analysis for gradual degradation detection
- Anomaly detection using statistical methods

**Reporting Features:**
- Time-series charts generated after the test run
- Per-resource peak and average reports
- Failure summaries based on PF criteria
- Exportable logs and snapshots for debugging

### Configuration Structure

Resource monitoring is configured through YAML-based Pass/Fail criteria files:

```yaml
resource_monitoring:
  enabled: true
  interval: 6
  cpu:
    percent_overall:
      max: 90
      avg: 75
  memory:
    percent_used:
      max: 90
      avg: 75
  disk:
    percent_used:
      max: 95
      avg: 85
```

---

# 6. Data Analysis & Recovery Tools

**Page ID:** 2337177613  
**URL:** https://prismaphotonics.atlassian.net/wiki/spaces/PRISMATEAM/pages/2337177613

## Long-Term Data Analysis

**Tool:** `tools/data_analyze_longterm.py`

**Purpose:** Analyzes data from long-term tests for performance trends and resource usage.

**Capabilities:**
- Component memory usage pattern analysis
- System resource utilization tracking over time
- Detection of memory growth trends, peak spikes, and long-term performance degradation
- Data collection efficiency validation

**Usage:**
```batch
python -m tools.data_analyze_longterm [options]
```

## PRP File Comparison Tools

**Tools:**
- `tools/prp_compare.py` - Direct PRP file comparison
- `tools/prp_compare_matrix.py` - Multi-file matrix comparison

**Capabilities:**
- PRP chunk header validation
- Bitwise file comparison
- Metadata consistency checking
- Chunk synchronization analysis
- UUID offset detection and validation

**Usage:**
```batch
python -m tools.prp_compare file1.prp file2.prp
python -m tools.prp_compare_matrix [directory_path]
```

## Heatmap Validation

**Tool:** `tools/heatmaps_validator.py`

**Capabilities:**
- Heatmap file metadata loading
- Structural validation of heatmap data
- File integrity verification
- Path resolution for heatmap storage directories
- Publish rate verification (expected interval between heatmap file generations)

**Usage:**
```batch
python -m tools.heatmaps_validator [heatmap_file]
```

## Data Recovery Utilities

**Tool:** `tools/data_recover.py`

**Capabilities:**
- Recovery of data from test pickle files
- Component data extraction
- JSON export of recovered data
- Directory-based recovery operations

**Commands:**
- `list` - List all components and attributes in pickle file
- `extract` - Extract specific component data
- `recover` - Recover all data to directory structure

**Usage:**
```batch
python -m tools.data_recover pickle_file.pkl list
python -m tools.data_recover pickle_file.pkl extract component attribute --output file.json
python -m tools.data_recover pickle_file.pkl recover --output-dir recovered_data
```

## Time Management Utilities

**Tool:** `tools/time_management.py`

**Capabilities:**
- Timestamp management and validation
- Time-based event correlation
- Temporal analysis utilities

**Usage:**
```batch
python -m tools.time_management [time]
```

## Additional Analysis Tools

**Tools:**
- `tools/pylib_validator.py` - Python library validation
- `tools/utils.py` - General utility functions
- `tools/xray.py` - Xray test management integration

**Integration:**
All tools integrate with:
- Framework configurator for path resolution
- Logging system for operation tracking
- JSON/CSV export capabilities

---

# 🎯 Mapping to Your Priorities

Based on the extracted documentation, here's how it maps to your automation priorities:

## Priority 1: Path Mapping & Simulation

**Relevant Information:**
- Product Overview shows data flow: Signal → Processing → Alert → Recording
- Framework uses `libs.algo_mock` and `libs.alerts_player` for simulation
- Player configuration in PF criteria controls PRP data playback
- `alerts_to_play` and `alerts_to_detect` in PF criteria define expected flows

## Priority 2: Failure Injection & Recovery

**Relevant Information:**
- **Recoverability suite** - focused on crash/recovery detection
- **Reliability suite** - intentional service restart testing
- `recovery_monitor` configuration in PF criteria:
  - `max_dead_proc_allowed`: maximum dead processes
  - `short_recover_time`: normal recovery timeout
  - `long_recovery_time`: extended recovery timeout
- Data Recovery Tools for post-failure analysis

## Priority 3: BIT Testing

**Relevant Information:**
- `bit_test_verification: enabled` in PF criteria
- BIT logs: `pz.bit_status.log`, `pz.bit_system.log`, `pz.bit_test.log`
- Framework validates BIT logs for both status and test operations
- Logs Collector can extract BIT logs for analysis

## Priority 4: Alarms with SVC

**Relevant Information:**
- `framework.orchestrator` starts Supervisor via `sv_cli_wrapper`
- `libs.alerts_player` for alert generation
- `alerts_to_detect` configuration for expected alert validation
- `externalizer_mode: amqp` or `http` for alert collection

## Priority 5: NOC Issue Simulation

**Relevant Information:**
- `control_center_mock: enabled` for CC metrics collection
- External integrations validation
- Reliability suite tests system behavior during broker-down scenarios
- `libs.control_center_mock` for NOC simulation

---

**Document Created:** December 8, 2024  
**Last Updated:** December 8, 2024
