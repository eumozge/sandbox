# sandbox

A test sandbox for Python experiments.

## Quick Start

```bash
just install 
just test 
just lint 
just py 
```

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Infrastructure

```bash
just storages-up    
just storages-down 
```

## Branches

Each branch is a separate sandbox. `main` holds the shared setup — create new branches from it for new experiments.
