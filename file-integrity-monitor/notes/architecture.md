# Architecture

## Goal

Monitor files for unauthorized changes.

## Components

- Monitor Engine
- Hash Engine
- Alert Engine
- Reporting Engine

## Data Flow

File Change
    ↓
Monitor Detects Event
    ↓
Hash Verification
    ↓
Alert Generation
    ↓
Report Storage