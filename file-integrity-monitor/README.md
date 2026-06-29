# File Integrity Monitor

A Python-based file integrity monitoring tool built as part of the SOC-in-a-Box project.

## What It Does

This tool monitors files for suspicious changes by comparing them against a trusted SHA-256 baseline.

It can detect:

- New files
- Modified files
- Deleted files
- Files that do not match the trusted baseline

## Commands

Create a trusted baseline:

```powershell
docker compose run --rm file-integrity-monitor python src/monitor.py --init-baseline