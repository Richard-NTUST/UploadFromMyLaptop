# Groundhog Taiwan Company Visit

**Date:** 2026-07-15

## Purpose

This day was reserved for the Groundhog Taiwan company visit. No live WINLAB OCloud E2E experiment was treated as completed evidence for this date.

## Main Value for the Project

The visit was useful as industry context for the current TEEP work:

- how lab automation and infrastructure monitoring are presented from an operational point of view;
- how production teams think about service reliability, repeatability, and observability;
- why an automated test service should preserve run artifacts instead of relying on screenshots or terminal output only;
- why power, temperature, workload, and service state should be treated as one experiment record instead of separate manual notes.

## Connection to WINLAB Work

The current WINLAB rApp direction matches the same operational pattern:

1. define a test intent;
2. execute it through an automation service;
3. collect workload output and infrastructure data;
4. preserve enough artifacts for later review;
5. produce a compact summary suitable for reporting.

For the Pegatron RU `[O]` experiment, the practical version of this is:

- trigger the E2E test through the rApp endpoint;
- run traffic through the HPE/OCloud and UE path;
- collect UE iPerf, VNF/PNF logs, and generated plots;
- export Outlet 2 `active_power` from InfluxDB/CortexDC;
- merge throughput and power into one summary table.

## Notes

The day should be recorded as a company visit day, not as a lab execution day. Technical progress resumed afterward by stabilizing the Dockerized rApp, OCloud pods, and throughput-power merge pipeline.
