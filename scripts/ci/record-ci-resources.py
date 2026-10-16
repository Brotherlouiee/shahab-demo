"""Record numeric container resource counters for the targeted diagnostic only."""

import json
import signal
import time
from pathlib import Path
from threading import Event

stopped = Event()
signal.signal(signal.SIGTERM, lambda *_: stopped.set())
signal.signal(signal.SIGINT, lambda *_: stopped.set())
output = Path("test-results/diagnostic-resources.jsonl")
output.parent.mkdir(parents=True, exist_ok=True)
paths = {
    "host_memory": "/proc/meminfo",
    "memory_detail": "/sys/fs/cgroup/memory.stat",
    "cpu": "/sys/fs/cgroup/cpu.stat",
    "cpu_limit": "/sys/fs/cgroup/cpu.max",
    "memory_bytes": "/sys/fs/cgroup/memory.current",
    "memory_peak": "/sys/fs/cgroup/memory.peak",
    "memory_limit": "/sys/fs/cgroup/memory.max",
    "memory_events": "/sys/fs/cgroup/memory.events",
    "pids": "/sys/fs/cgroup/pids.current",
    "cpu_pressure": "/proc/pressure/cpu",
    "memory_pressure": "/proc/pressure/memory",
    "io_pressure": "/proc/pressure/io",
    "phase": "/tmp/shahab-diagnostic-phase",
}
with output.open("a") as stream:
    while True:
        sample = {"monotonic_seconds": time.monotonic()}
        for key, path in paths.items():
            try:
                sample[key] = Path(path).read_text().strip()
            except OSError:
                sample[key] = "unavailable"
        stream.write(json.dumps(sample) + "\n")
        stream.flush()
        if stopped.wait(2):
            break
