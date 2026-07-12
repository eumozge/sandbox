# sandbox — Queues in Practice

A demo project showcasing queue-based architectures — from in-process coordination to a message broker — using a trade data pipeline for the SPIMEX exchange.

## What it demonstrates

Two queue levels working together:

1. **`asyncio.Queue`** — coordinates page-number producer and consumer within a single process (bounded buffer, sentinel termination)
2. **RabbitMQ** — decouples the collector service from the parser service (topic exchange, durable queue, ack/nack)

## Pipeline

```
SPIMEX (HTTP)
  → SpimexPageRepository (fetch HTML)
  → CollectTradesUseCase (asyncio.Queue + Semaphore)
  → RabbitMQTradePagePublisher (exchange: spimex, routing_key: page.fetched)
  → RabbitMQTradePageConsumer (queue: spimex.pages)
  → ParseTradesUseCase
  → StubTradePageParser (stub — replace with real parser)
```

## Commands

```bash
just install          
just storages-up     
just py trades collect --to-page 500   # fetch SPIMEX pages → RabbitMQ
just py trades parse                   # consume from RabbitMQ (2nd terminal)
just storages-down   
just test             
just lint
```

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker (for RabbitMQ)
