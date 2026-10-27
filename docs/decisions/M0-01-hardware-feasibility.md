# CLOE — M0.1: Hardware & SDK Feasibility

**Project:** Cognitive Load Occlusion Engine (CLOE)  
**Milestone:** M0 — Research & Hardware Feasibility  
**Experiment ID:** M0-01  
**Date opened:** 2026-10-27  
**Author:** Ghinet Ioana-Teodora 
**Status:** Planned / In progress / Passed / Blocked

> **Regula de documentare:** informațiile din surse (SUPPORTED) sunt diferite de rezultatele măsurate pe calculatorul propriu (OBSERVED). Nu marca `PASSED` fără dovadă.

## 1. Objective

Check whether Tobii Pro Nano can be detected and calibrated on the development Windows computer, and whether the official Tobii Pro SDK can be imported and discover the device from Python 3.10 x64.

## 2. Evidence from documentation (SUPPORTED; not yet tested locally)

| Property | Evidence / interpretation |
| --- | --- |
| Hardware | Tobii Pro Nano is discontinued, but is listed among compatible Tobii Pro SDK devices. |
| Frequency | 60 Hz nominal gaze sampling frequency. |
| Interface | USB 2.0 Type-A. |
| OS | Tobii documentation lists Windows 10/11 64-bit Pro and Enterprise in supported configurations. Windows Home requires local validation. |
| Python | Tobii Pro SDK `tobii-research` 2.1.0 provides a Windows x64 wheel for CPython 3.10. |
| Configuration tool | Tobii Pro Eye Tracker Manager supports device detection, display setup, track status and calibration. |

**Sources (accessed 2026-10-27):**
- https://www.tobii.com/products/discontinued/tobii-pro-nano
- https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager
- https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-sdk
- https://pypi.org/project/tobii-research/2.1.0/
- https://developer.tobiipro.com/python/python-step-by-step-guide.html

## 3. Computer inventory (OBSERVED — fill after running commands)

| Field | Actual value | Evidence |
| --- | --- | --- |
| Windows edition, build and 64-bit status | Microsoft Windows 11 Education | PowerShell output |
| Processor | TODO | PowerShell output |
| RAM (GB) |  63.7 | PowerShell output |
| Screen resolution | TODO | Windows Display settings |
| Monitor count / Extend-Duplicate | TODO | Windows Display settings |
| Direct USB Type-A port available | TODO | Physical inspection |
| Python installations | TODO | `py -0p` or `python --version` |
| Eye Tracker Manager version | TODO | About / installed apps |
| Tobii Pro SDK version | TODO | `python -m pip show tobii-research` using venv Python |

## 4. Test procedure

### Test T01 — OS detection
- **Action:** In PowerShell run `Get-CimInstance Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version`.
- **Expected:** A readable OS edition, architecture and version.
- **Observed:** Microsoft Windows 11 Education 64-bit         10.0.26200
- **Result:**  PASS 

### Test T02 — hardware inventory
- **Action:** In PowerShell run `Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, @{Name='RAM_GB';Expression={[math]::Round($_.TotalPhysicalMemory/1GB,1)}}`.
- **Expected:** Computer information and available physical memory.
- **Observed:** LENOVO       21FAS29R00   63.7
- **Result:**  PASS

### Test T03 — Windows device discovery
- **Action:** Connect Nano directly to USB Type-A. Run `Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -match 'Tobii' } | Select-Object FriendlyName,Status,Class`.
- **Expected:** A relevant Tobii device may appear. An empty result is inconclusive; inspect Device Manager and Eye Tracker Manager.
- **Observed:** 
- **Result:** NOT RUN / PASS / FAIL / INCONCLUSIVE

### Test T04 — Tobii Eye Tracker Manager
- **Action:** Install official Windows x64 Tobii Pro Eye Tracker Manager; set correct display, check device discovery, run calibration, test gaze visualization if available.
- **Expected:** Tracker detected, calibration completed, gaze visual responds to gaze shifts.
- **Observed:** Done
- **Result:**  PASS

### Test T05 — SDK installation and import
- **Action:** Create a dedicated CPython 3.10 x64 virtual environment, install `tobii-research==2.1.0`, import module.
- **Expected:** `import tobii_research` succeeds.
- **Observed:** TODO
- **Result:** NOT RUN / PASS / FAIL

### Test T06 — SDK device discovery
- **Action:** Call `tobii_research.find_all_eyetrackers()`.
- **Expected:** At least one tracker; identify model. Do not publish serial numbers.
- **Observed:** TODO
- **Result:** NOT RUN / PASS / FAIL

## 5. Risks / Troubleshooting Log

| Date | Symptom | Hypothesis | Investigation | Resolution | Status |
| --- | --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | TODO | OPEN |

Possible factors: Windows edition, USB port/hub, missing vendor drivers, incorrect display setup, calibration, Python architecture or version. Avoid updating firmware unless the manufacturer directs you to do so.

## 6. Conclusions

- **Hardware readiness:** UNKNOWN until T01–T04 completed.
- **SDK readiness:** UNKNOWN until T05–T06 completed.
- **Go / No-Go decision:** TBD
- **Next action:** TBD

## 7. Learning reflection (complete yourself)

1. What is the difference between a gaze point, fixation and saccade?
2. Why does 60 Hz correspond to approximately 16.67 ms between samples?
3. What does calibration correct for?
4. Why is an SDK import not proof that the device is connected?
5. What is one possible cause of invalid gaze samples?

## 8. Screenshots & reproducibility

- `docs/evidence/m0-01-windows-info.png` — optional; hide identifying information.
- `docs/evidence/m0-01-manager-detection.png` — optional; hide serial number.
- `docs/evidence/m0-01-calibration.png` — optional; do not include participant images without permission.

**Privacy:** Do not commit raw face video, participant identifiers, or hardware serial numbers to a public Git repository.
