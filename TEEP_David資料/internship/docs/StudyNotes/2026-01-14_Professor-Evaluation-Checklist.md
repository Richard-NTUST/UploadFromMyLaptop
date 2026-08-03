# Professor Recommendation: Weekly Evaluation Checklist (4 Weeks)

This note archives the professor-provided evaluation checklist. When running software-first (no RU hardware), treat the “measurement equipment” items as “software estimator + logging pipeline readiness”, and treat AC/DC measurement specifics as future validation.

---

Below is a **weekly student / intern evaluation checklist** converted directly from the
**“RU Power Consumption Measurements – 1-Month Study Plan”**.

It is suitable for:

* Telecom / RF / RAN laboratory internships
* Master-level experimental courses
* Industry PoC or vendor evaluation labs

The checklist emphasizes **measurement rigor, repeatability, data quality, and engineering reasoning**.

---

# RU Power Consumption Measurements

## Weekly Student / Intern Evaluation Checklist (4 Weeks)

**Student Name:** Jesaya David
**Program / Lab:** BMW NTUST Internship
**Evaluator:** Prof. Ray Guang-Cheng, Mr. Ian, Mr. Joshevan
**Evaluation Date:** February 2026

---

## Week 1 – Measurement Scope, Standards & Test Setup

### Conceptual Understanding

| Item                                                | ✓ |
| --------------------------------------------------- | - |
| Understands RU architecture and major power domains | ☑ |
| Can explain idle vs active RU power consumption     | ☑ |
| Understands basic power metrics (W, Wh, energy/bit) | ☑ |
| Understands importance of calibration & safety      | ☑ |
| Aware of repeatability and measurement uncertainty  | ☑ |

---

### Practical Tasks

| Item                                              | ✓ |
| ------------------------------------------------- | - |
| RU model and operating conditions clearly defined | ☑ |
| Measurement points selected (AC input / DC rails) | ☑ |
| Test variables identified (load, TX power, BW)    | ☑ |
| Measurement equipment prepared and verified       | ☑ |
| Draft test plan and test matrix completed         | ☑ |

---

### Evidence Submitted

| Item                                   | ✓ |
| -------------------------------------- | - |
| Measurement scope document             | ☑ |
| Test plan & test matrix                | ☑ |
| Equipment list with calibration status | ☑ |
| Safety checklist                       | ☑ |

---

### Week 1 Evaluation

**Status:** ☑ Pass ☐ Conditional ☐ Fail
**Comments:**

---

---

## Week 2 – Baseline & Idle Power Measurements

### Conceptual Understanding

| Item                                             | ✓ |
| ------------------------------------------------ | - |
| Understands RU warm-up and thermal stabilization | ☑ |
| Understands impact of sampling rate & averaging  | ☑ |
| Can explain idle and low-load power contributors | ☑ |

---

### Practical Tasks

| Item                                    | ✓ |
| --------------------------------------- | - |
| Warm-up procedure executed correctly    | ☑ |
| Idle power measurements completed       | ☑ |
| Low-load traffic measurements completed | ☑ |
| Measurements repeated for consistency   | ☑ |
| Ambient conditions recorded             | ☑ |

---

### Evidence Submitted

| Item                               | ✓ |
| ---------------------------------- | - |
| Raw power logs (CSV or equivalent) | ☑ |
| Baseline & idle power plots        | ☑ |
| Repeatability observations         | ☑ |
| Updated test procedure notes       | ☑ |

---

### Week 2 Evaluation

**Status:** ☑ Pass ☐ Conditional ☐ Fail
**Comments:**

---

---

## Week 3 – Load-Dependent & Scenario-Based Measurements

### Conceptual Understanding

| Item                                                       | ✓ |
| ---------------------------------------------------------- | - |
| Understands power scaling with traffic load                | ☑ |
| Understands relationship between RF output and input power | ☑ |
| Understands concept of energy efficiency                   | ☑ |

---

### Practical Tasks

| Item                                      | ✓ |
| ----------------------------------------- | - |
| Controlled load sweeps executed           | ☑ |
| TX power / bandwidth scenarios tested     | ☑ |
| Power and traffic metrics logged together | ☑ |
| Power vs load curves generated            | ☑ |
| Energy per bit calculated (if applicable) | ☑ |

---

### Evidence Submitted

| Item                                | ✓ |
| ----------------------------------- | - |
| Load-dependent measurement datasets | ☑ |
| Power vs load / TX power plots      | ☑ |
| Preliminary efficiency analysis     | ☑ |
| Annotated test logs                 | ☑ |

---

### Week 3 Evaluation

**Status:** ☑ Pass ☐ Conditional ☐ Fail
**Comments:**

---

---

## Week 4 – Data Analysis, Validation & Reporting

### Conceptual Understanding

| Item                                                | ✓ |
| --------------------------------------------------- | - |
| Understands measurement uncertainty & error sources | ☑ |
| Can interpret linear vs non-linear power behavior   | ☑ |
| Understands implications for RU design & operation  | ☑ |

---

### Practical Tasks

| Item                                       | ✓ |
| ------------------------------------------ | - |
| Data consistency and outliers checked      | ☑ |
| Idle vs active power ratios analyzed       | ☑ |
| Results interpreted with clear assumptions | ☑ |
| Final plots and tables prepared            | ☑ |
| Conclusions and limitations clearly stated | ☑ |

---

### Evidence Submitted

| Item                               | ✓ |
| ---------------------------------- | - |
| Final measurement report (PDF)     | ☐ |
| Summary tables & plots             | ☑ |
| Reproducible measurement procedure | ☑ |
| Dataset archive with metadata      | ☑ |

---

### Week 4 Evaluation

**Status:** ☐ Pass ☑ Conditional ☐ Fail
**Comments:**

---

---

# Final Evaluation Summary

| Category                         | Score (0–5) |
| -------------------------------- | ----------- |
| RU & RAN Technical Understanding | ___ / 5     |
| Measurement Methodology & Rigor  | ___ / 5     |
| Data Quality & Analysis          | ___ / 5     |
| Documentation & Reporting        | ___ / 5     |
| Experimental Independence        | ___ / 5     |

**Final Result:**
☐ Excellent ☐ Good ☐ Satisfactory ☐ Needs Improvement

---

## Optional Supervisor Add-Ons

* O-RAN energy efficiency KPI alignment
* Comparison between two RU configurations or vendors
* Automation & scripting bonus criteria
* Master thesis / industry validation rubric
