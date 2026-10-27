# CLOE - Project Charter

**Project:** Cognitive Load Occlusion Engine  
**Version:** 0.1  
**Date:** 27 October 2026  
**Status:** Initial Research & Planning  
**Project Type:** Bachelor's Thesis / Research & Development

## 1. Problem Statement

Traditional productivity and learning interfaces generally maintain a fixed presentation of information, regardless of the user's changing cognitive demands.

CLOE investigates whether physiological and behavioral signals can be used to estimate cognitive workload and dynamically adapt the visual complexity of a learning interface.

## 2. Project Objective

Design, implement, and experimentally evaluate a real-time adaptive learning interface based on eye-tracking and webcam-derived features.

## 3. Research Questions

- RQ1: Can ocular and postural features support estimation of cognitive workload during learning tasks?
- RQ2: Can an adaptive interface reduce subjective workload compared with a static interface?
- RQ3: How does adaptation influence task performance and user experience?

## 4. Initial System Scope

The system will include:

- Tobii Pro Nano eye-tracking integration.
- Webcam-based blink and head-pose detection.
- Signal validation, synchronization, and feature extraction.
- An interpretable workload-estimation baseline.
- A learning interface with multiple visual complexity levels.
- Local experimental logging and an evaluation framework.

## 5. Out of Scope for the Initial MVP

- Operating-system-wide interface replacement.
- Reliable microsaccade detection using 60 Hz hardware.
- Medical or neurological diagnosis.
- Mandatory breaks or involuntary application locking.
- Cloud-based processing of webcam imagery.
- A complex machine learning model before obtaining validated data.

## 6. Success Criteria

A successful MVP should:

1. Acquire valid data from the selected sensors.
2. Extract reproducible ocular and postural features.
3. Estimate and display an interpretable state with uncertainty.
4. Adapt the learning interface without interrupting essential tasks.
5. Support controlled comparison against a static interface.
6. Produce documented experimental results, including limitations.

## 7. Key Risks

- Hardware and operating-system compatibility.
- Noisy or missing sensor data.
- Individual variability in physiological indicators.
- Confounding between workload, fatigue, and attention.
- Interface adaptations potentially increasing distraction.
- Limited experimental sample size and generalizability.

## 8. Engineering Principles

- Understand before implementing.
- Start simple and increase complexity based on evidence.
- Keep modules independently testable.
- Document architectural decisions.
- Preserve experimental reproducibility.
- Prioritize privacy and user control.
- Validate assumptions rather than presenting them as facts.

## 9. Immediate Next Milestone

**M0: Hardware and Research Feasibility**

Deliverables:

- Hardware inventory.
- Operating-system and SDK compatibility check.
- Successful Tobii connection and calibration.
- First valid gaze-data acquisition.
- Initial literature matrix.
- Updated architecture and risk register.