#!/usr/bin/env python3
"""Dry-run / live pipeline throughput for large-scale Redis batching.

Usage:
  python scripts/load_pipeline_dry.py --dry-run --keys 10000
  REDIS_URL=redis://localhost:6380/0 python scripts/load_pipeline_dry.py --keys 5000
"""

from __future__ import annotations

import argparse
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))


def main() -> None:
    p = argparse.ArgumentParser(description="Redis pipeline batch load / dry-run")
    p.add_argument("--keys", type=int, default=10_000)
    p.add_argument("--ttl", type=int, default=60)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--batch-size", type=int, default=500)
    args = p.parse_args()

    print("=== Redis pipeline scale plan ===")
    print(f"  keys: {args.keys}")
    print(f"  batch_size: {args.batch_size}")
    print(f"  rounds: {(args.keys + args.batch_size - 1) // args.batch_size}")
    print("  note: pipeline collapses N commands into ~1 RTT per batch")

    if args.dry_run:
        seq_s = args.keys * 0.0002
        batch_s = ((args.keys + args.batch_size - 1) // args.batch_size) * 0.002
        print(f"  estimated sequential wall: {seq_s:.3f}s")
        print(f"  estimated pipeline wall:   {batch_s:.3f}s")
        print(f"  speedup ~ {seq_s / max(batch_s, 1e-9):.1f}x (model)")
        print("DRY-RUN OK")
        return

    from redis_app.batch import mget_via_pipeline, msetex_via_pipeline
    from redis_app.client import RedisClient

    client = RedisClient()
    assert client.ping(), "Redis ping failed — is data-stack up on :6380?"
    items = {f"load:{i}": f"v{i}" for i in range(args.keys)}
    keys = list(items.keys())
    t0 = time.perf_counter()
    written = 0
    for i in range(0, len(keys), args.batch_size):
        chunk = {k: items[k] for k in keys[i : i + args.batch_size]}
        written += msetex_via_pipeline(client, chunk, ttl_seconds=args.ttl)
    t1 = time.perf_counter()
    read = 0
    for i in range(0, len(keys), args.batch_size):
        got = mget_via_pipeline(client, keys[i : i + args.batch_size])
        read += len(got)
    t2 = time.perf_counter()
    print(f"  wrote={written} in {t1 - t0:.3f}s ({written / (t1 - t0):.0f} keys/s)")
    print(f"  read={read} in {t2 - t1:.3f}s ({read / (t2 - t1):.0f} keys/s)")
    client.close()
    print("LIVE OK")


if __name__ == "__main__":
    main()
