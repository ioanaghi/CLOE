# CLOE — M0.1: Hardware & SDK Feasibility

**Project:** Cognitive Load Occlusion Engine (CLOE)  
**Milestone:** M0 — Research & Hardware Feasibility  
**Experiment ID:** M0-01  
**Date:** 2026-10-27  
**Author:** Ghinet Ioana-Teodora  
**Status:** PASSED — Core Feasibility Verified

> **Documentation principle:** Information obtained from official documentation (SUPPORTED) must be distinguished from results obtained through local testing (OBSERVED). Tests are marked as PASS only when supported by evidence.

---

## 1. Objective

The objective of this milestone is to evaluate the development environment and verify that the Tobii Pro Nano eye tracker can be recognized, calibrated, and accessed programmatically on a Windows computer.

The experiment focuses on:

- Identifying the development computer's hardware specifications.
- Verifying operating system compatibility.
- Confirming Tobii Pro Nano USB recognition.
- Verifying eye-tracker calibration.
- Installing Python 3.10 and the official Tobii Pro SDK.
- Testing SDK import and connected-device discovery.
- Evaluating the feasibility of implementing CLOE's eye-tracking acquisition module.

Successful completion establishes the technical foundation for subsequent real-time gaze-data acquisition experiments.

## 2. Evidence from Documentation (SUPPORTED)

| Property | Documentation / Technical Information |
|---|---|
| Eye tracker | Tobii Pro Nano |
| Manufacturer | Tobii AB |
| Device status | Discontinued, but listed among compatible Tobii Pro SDK devices |
| Sampling frequency | 60 Hz nominal |
| Connection | USB 2.0 Type-A |
| SDK | Tobii Pro SDK |
| Python package | `tobii-research` |
| SDK version | 2.1.0 |
| Python compatibility | CPython 3.10, Windows x64 distribution |
| Calibration | Supported through Tobii's calibration tools |
| Gaze acquisition | Accessible using the SDK gaze-data subscription interface |

The nominal sampling interval can be calculated as:

\[
T=\frac{1}{f}=\frac{1}{60}\approx0.01667s=16.67ms
\]

Therefore, the eye tracker is expected to provide approximately 60 samples per second under nominal operation.

This value represents the sampling frequency, not the accuracy of gaze estimation.

### Sources (accessed 2026-10-27)

- [Tobii Pro Nano — Product Information](https://www.tobii.com/products/discontinued/tobii-pro-nano)
- [Tobii Pro Eye Tracker Manager](https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager)
- [Tobii Pro SDK](https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-sdk)
- [Tobii Research SDK 2.1.0 — PyPI](https://pypi.org/project/tobii-research/2.1.0/)
- [Tobii Python SDK — Step-by-Step Guide](https://developer.tobiipro.com/python/python-step-by-step-guide.html)

---

## 3. Computer Inventory (OBSERVED)

The following information was obtained using Windows PowerShell commands executed on the development computer.

| Component | Observed Configuration |
|---|---|
| Manufacturer | Lenovo |
| Computer model | 21FAS29R00 |
| Operating system | Microsoft Windows 11 Education |
| Architecture | 64-bit |
| Windows version | 10.0.26200 |
| Processor | 13th Gen Intel Core i9-13950HX |
| Physical CPU cores | 24 |
| Logical processors | 32 |
| Installed RAM | 63.7 GiB (PowerShell-reported) |
| Integrated GPU | Intel UHD Graphics |
| Dedicated GPU | NVIDIA GeForce RTX 4090 Laptop GPU |
| Virtual display adapter | Meta Virtual Monitor |
| Intel-reported display resolution | 3840 × 2400 |
| NVIDIA-reported display resolution | 3440 × 1440 |
| Monitor count / display mode | Pending verification |
| Python installations | 3.8, 3.10.11, 3.14, 3.15 |
| Eye tracker | Tobii Pro Nano |
| Tobii USB device name | EyeChip |
| USB device status | OK |
| Tobii Pro Lab | 26.18.3334 |
| Tobii Pro Nano Runtime | 1.8.15.0 |
| Tobii Pro SDK | 2.1.0 |
| Eye Tracker Manager version | Not independently identified |

### 3.1 Hardware Assessment

The development machine provides sufficient computing resources for the planned CLOE prototype.

The Intel Core i9-13950HX provides multi-core processing capabilities suitable for concurrent data acquisition and signal-processing operations.

The NVIDIA GeForce RTX 4090 Laptop GPU provides additional computational resources that may support future GPU-accelerated Computer Vision and machine learning experiments.

The system also contains approximately 64 GiB of physical memory, which is expected to be sufficient for the initial application components.

These characteristics indicate that computational hardware limitations are unlikely to represent the primary constraint during initial development.

Actual CPU utilization, GPU utilization, memory consumption, and processing latency will be evaluated during performance testing.

### 3.2 Display Configuration

Two display resolutions were reported by the graphics adapters:

- Intel UHD Graphics: 3840 × 2400
- NVIDIA RTX 4090 Laptop GPU: 3440 × 1440

These results do not independently confirm the number of connected physical monitors.

Further verification is required to identify the display used for Tobii calibration and to establish the correct mapping between normalized gaze coordinates and screen pixels.

---

## 4. Test Procedure and Results

### T01 — Operating System Detection

**Objective:** Identify the operating system, its architecture, and version.

**Command:**

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version
```

**Expected:** The command returns valid operating system information.

**Observed:**

```text
Caption        : Microsoft Windows 11 Education
OSArchitecture : 64-bit
Version        : 10.0.26200
```

**Result: PASS**

**Interpretation:**

The development computer runs Windows 11 Education with a 64-bit architecture.

Although the reviewed manufacturer configurations do not explicitly identify Windows Education as a supported edition, subsequent successful SDK testing demonstrates practical compatibility with the current system configuration.

This observation does not establish compatibility across all Windows Education installations.

### T02 — Hardware Inventory

**Objective:** Identify CPU, RAM, GPU, and computer model.

**Commands:**

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, @{Name='RAM_GB';Expression={[math]::Round($_.TotalPhysicalMemory/1GB,1)}}
```

```powershell
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
```

```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```

**Expected:** Valid computer and hardware information is returned.

**Observed:**

- Manufacturer: Lenovo
- Model: 21FAS29R00
- RAM: 63.7 GiB
- Processor: Intel Core i9-13950HX
- Physical cores: 24
- Logical processors: 32
- Dedicated GPU: NVIDIA GeForce RTX 4090 Laptop GPU

**Result: PASS**

**Interpretation:**

The machine has adequate hardware specifications for development and preliminary experimentation.

Actual system performance under concurrent eye-tracking and Computer Vision workloads remains to be measured.

### T03 — Windows Device Discovery

**Objective:** Verify that Windows recognizes the connected eye tracker.

**Initial command:**

```powershell
Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -match 'Tobii' } | Select-Object FriendlyName, Status, Class
```

**Initial observation:**

The command returned no matching devices.

This initially suggested that the tracker might not be registered under a friendly name containing "Tobii".

**Additional investigation:**

```powershell
Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match 'USB' } | Select-Object FriendlyName, Status, Class, InstanceId
```

**Observed:**

```text
FriendlyName : EyeChip
Status       : OK
Class        : USBDevice
```

The USB device identifier was also consistent with the connected Tobii Pro Nano hardware.

The complete identifier was intentionally excluded from this report to avoid publishing device-specific identification information.

**Result: PASS**

**Interpretation:**

The operating system successfully recognizes the device at the USB level.

The initial discovery attempt returned no result because the device's Windows friendly name is "EyeChip", rather than a name containing "Tobii".

This demonstrates the importance of distinguishing an unsuccessful name-based search from an actual hardware detection failure.

The test verifies USB enumeration but does not independently establish gaze-data quality.

### T04 — Eye Tracker Calibration

**Objective:** Verify that the eye tracker can be calibrated for the current user and display configuration.

**Expected:**

- The eye tracker is recognized by the acquisition software.
- Calibration completes successfully.
- The existing software can acquire eye-tracking data.

**Observed:**

The calibration procedure was successfully completed, as confirmed by the developer.

The device is also operational in an existing Tobii data acquisition workflow.

**Result: PASS — Calibration confirmed**

**Interpretation:**

The eye tracker can be calibrated under the current hardware and software configuration.

The exact calibration tool version and quantitative calibration accuracy have not yet been recorded.

Future experiments will document calibration conditions, tracking quality, and any available calibration validation metrics.

### T05 — Tobii Pro SDK Installation and Import

**Objective:** Install the official Tobii Pro SDK and verify that Python can import it successfully.

**Expected:**

- Python 3.10 is installed.
- Tobii Pro SDK 2.1.0 is installed.
- The Python module imports without errors.

**Step 1 — Python installation:**

```powershell
py install 3.10
```

**Observed:**

```text
Installing Python 3.10.11.
Downloading: SUCCESS
Extracting: SUCCESS
```

**Step 2 — Create the project directory:**

```powershell
New-Item -ItemType Directory -Path "$HOME\Documents\CLOE" -Force
Set-Location "$HOME\Documents\CLOE"
```

**Step 3 — Create a Python virtual environment:**

```powershell
py -3.10 -m venv .venv
```

**Step 4 — Install the SDK inside the virtual environment:**

```powershell
.\.venv\Scripts\python.exe -m pip install tobii-research==2.1.0
```

**Observed:**

```text
Successfully installed tobii-research-2.1.0
```

**Step 5 — Verify the SDK import:**

```powershell
.\.venv\Scripts\python.exe -c "import tobii_research; print('Tobii SDK import: OK')"
```

**Observed:**

```text
Tobii SDK import: OK
```

**Result: PASS — Virtual environment**

**Interpretation:**

The official Tobii Pro SDK was successfully installed and imported using Python 3.10 in a dedicated virtual environment.

This confirms compatibility between the selected Python interpreter and the installed SDK distribution.

### T05-B — SDK Installation Outside the Virtual Environment

**Objective:** Verify that Tobii Pro SDK can be accessed directly through Python 3.10 without activating a virtual environment.

**Command:**

```powershell
py -3.10 -m pip install --user tobii-research==2.1.0
```

**Observed:**

```text
Requirement already satisfied: tobii-research==2.1.0
```

The package was found in the Python 3.10 user-level site-packages directory.

Package verification confirmed:

- Package: `tobii-research`
- Version: `2.1.0`
- Installation scope: Python 3.10 user-level packages

**Result: PASS**

**Interpretation:** Tobii Pro SDK is available to the Python 3.10 interpreter outside the virtual environment.


### T06 — SDK Device Discovery

**Objective:** Verify that the official Python SDK can discover the connected eye tracker.

**Command:**

```powershell
.\.venv\Scripts\python.exe -c "import tobii_research as tr; print('Detected eye trackers:', len(tr.find_all_eyetrackers()))"
```

**Expected:** At least one eye tracker is discovered.

**Observed:**

```text
Detected eye trackers: 1
```

**Result: PASS — Virtual environment**

**Interpretation:**

The Tobii Pro SDK successfully discovered one connected eye tracker.

This confirms that device discovery works through the Python SDK on the development computer.

The tracker model has not yet been independently retrieved from the SDK metadata.

Successful discovery also does not guarantee that gaze-data subscriptions will produce continuous valid samples.

### T06-B — SDK Device Discovery Outside the Virtual Environment

**Objective:** Verify that Python 3.10 can discover the connected eye tracker directly.

**Command:**

```powershell
py -3.10 -c "import tobii_research as tr; print('Detected eye trackers:', len(tr.find_all_eyetrackers()))"
```

**Observed:**

```text
Detected eye trackers: 1
```

**Result: PASS**

**Interpretation:** Tobii Pro SDK successfully discovers one connected eye tracker through the Python 3.10 user-level installation.

The result independently confirms device discovery outside the virtual environment. The next experiment will verify tracker metadata and actual gaze-data acquisition.

---

## Final Milestone Verification

| Test | Description | Result |
|---|---|---|
| T01 | Operating system identification | PASS |
| T02 | Hardware inventory | PASS |
| T03 | USB device discovery | PASS |
| T04 | Eye tracker calibration | PASS |
| T05 | SDK import inside virtual environment | PASS |
| T05-B | SDK available outside virtual environment | PASS |
| T06 | SDK device discovery inside virtual environment | PASS |
| T06-B | SDK device discovery outside virtual environment | PASS |

**Milestone M0.1 Status: PASSED**

**Go / No-Go Decision: GO**

The development environment is ready for implementing the first eye-tracking data acquisition module.

**Remaining limitations:**

- Exact tracker model has not yet been retrieved from SDK metadata.
- Continuous gaze-data streaming has not yet been tested in CLOE.
- Sampling stability and validity rates have not yet been measured.

**Next Milestone:** M0.2 — Eye-Tracking Data Acquisition and Validation.

---

## 5. Risks and Troubleshooting Log

| Date | Symptom / Risk | Investigation | Resolution / Mitigation | Status |
|---|---|---|---|---|
| 2026-10-27 | Eye tracker not found using name-based PnP filtering | Inspected the complete USB device list | Identified the device under the name "EyeChip" | RESOLVED |
| 2026-10-27 | Python 3.10 was initially unavailable | Checked installed Python versions | Installed Python 3.10.11 | RESOLVED |
| 2026-10-27 | Tobii SDK was not installed in the inspected Python 3.8 environment | Executed `pip show` using Python 3.8 | Installed SDK 2.1.0 in a Python 3.10 virtual environment | RESOLVED |
| 2026-10-27 | Windows Education not explicitly listed in reviewed compatibility configurations | Verified USB recognition and SDK discovery | Practical compatibility confirmed for the tested workflow | MITIGATED |
| 2026-10-27 | SDK availability outside the virtual environment not yet verified | Independent installation proposed | Verify import and device discovery directly through Python 3.10 | OPEN |
| 2026-10-27 | Gaze-data quality not yet validated | No CLOE acquisition experiment completed | Measure sample rate, validity and timestamps during M0.2 | OPEN |

### Risk Assessment

The major hardware integration risks have been reduced by successful USB enumeration, calibration and Python SDK device discovery.

Remaining technical risks include:

- Missing or invalid gaze samples.
- Differences between nominal and observed sampling rates.
- Calibration accuracy under different conditions.
- Multiple-monitor coordinate mapping.
- Concurrent application access to the eye tracker.
- Synchronization between eye-tracking and webcam data.

These risks will be investigated in subsequent experiments.

---

## 6. Conclusions

### Hardware Readiness

**Status: VERIFIED FOR INITIAL DEVELOPMENT**

The development machine provides sufficient computational resources for the initial CLOE prototype.

The Tobii Pro Nano is recognized by Windows, and its calibration has been completed successfully.

### SDK Readiness

**Status: VERIFIED IN PYTHON 3.10 VIRTUAL ENVIRONMENT**

The Tobii Pro SDK 2.1.0 was successfully installed, imported and used to discover one connected eye tracker.

The SDK installation outside the virtual environment remains to be independently verified.

### Go / No-Go Decision

**Decision: GO**

The project can proceed to the next development milestone.

The initial hardware and software integration tests demonstrate that a Python application can discover the connected eye tracker.

However, real-time gaze-data acquisition and measurement quality must still be validated.

### Next Milestone

**M0.2 — Eye-Tracking Data Acquisition and Validation**

Planned objectives:

1. Retrieve and verify the eye tracker model using the Python SDK.
2. Understand SDK callbacks and gaze-data subscriptions.
3. Acquire gaze samples for a controlled time interval.
4. Inspect timestamps and gaze coordinates.
5. Evaluate the observed sampling rate.
6. Calculate the percentage of valid samples.
7. Store experimental data in a reproducible format.
8. Document measurement limitations.

---

## 7. Learning Reflection

*This section should be completed independently after reviewing the theoretical concepts.*

**Question 1 — What is the difference between a gaze point, fixation and saccade?**

Student explanation:

Gaze point: is a point where the person is looking on the screen
Fixation: is where a person's look is stable and stays for longer
Saccade: is ejrn watching a screen the eyes move faste so when reading a text you follow the words, that is what saccade is

**Question 2 — Why does 60 Hz correspond to approximately 16.67 ms between samples?**

Student explanation:

It is because te meaning of 60Hz indicates 60 samples taken per seconf so 1/60 means 16.67 ms

**Question 3 — What does calibration correct for?**

Student explanation:

Every person is different, every environment is different, so we calibrate in order to get better estimations on where the person is actually looking onto the screen. eliminating as much as possible the error in estimation.


**Question 4 — Why is an SDK import not proof that the eye tracker is connected?**

Student explanation:

Because the SDK is just the software that detects the eyetracher and let's you communicate with it not creates the connectivity.

**Question 5 — What is one possible cause of invalid gaze samples?**

Student explanation:

not being in the area where the sensor is, covering the eyes

### Engineering Reflection

The initial device discovery attempt demonstrated that hardware diagnostics must account for differences between manufacturer product names and operating system device names.

The experiments also highlighted the importance of managing Python versions and package compatibility.

Successful SDK import and device discovery were tested separately, providing more precise evidence about software readiness.

---

## 8. Evidence and Reproducibility

Recommended evidence files:

- `docs/evidence/m0-01-windows-info.png`
- `docs/evidence/m0-01-cpu-gpu-info.png`
- `docs/evidence/m0-01-usb-detection.png`
- `docs/evidence/m0-01-calibration.png`
- `docs/evidence/m0-01-sdk-installation.png`
- `docs/evidence/m0-01-sdk-import.png`
- `docs/evidence/m0-01-device-discovery.png`
- `docs/evidence/m0-01-global-sdk-verification.png` — pending

Screenshots and terminal logs should be stored without unnecessary personal information.

**Privacy requirements:**

- Do not publish hardware serial numbers.
- Do not commit participant identifiers or unconsented face recordings.
- Avoid exposing local Windows usernames and personal directory structures.
- Store raw experimental data separately from public source code when necessary.

---

## 9. Milestone Summary

| Test | Description | Result |
|---|---|---|
| T01 | Operating system detection | PASS |
| T02 | Hardware inventory | PASS |
| T03 | Windows USB device discovery | PASS |
| T04 | Eye tracker calibration | PASS — developer confirmed |
| T05 | SDK installation and import in virtual environment | PASS |
| T05-B | SDK installation and import outside virtual environment | PENDING |
| T06 | SDK device discovery in virtual environment | PASS |
| T06-B | SDK device discovery outside virtual environment | PENDING |

**Final milestone status:** PASSED — Core Hardware and SDK Feasibility

**Remaining verification:** Independent Python installation and gaze-data acquisition.

**Next experiment:** M0.2 — First Gaze Data Acquisition.