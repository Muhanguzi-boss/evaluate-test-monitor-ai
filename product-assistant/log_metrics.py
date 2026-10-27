"""Read logs/app.log and report request, latency and tool metrics.

Run: python log_metrics.py [path/to/app.log]
"""

import re
import sys
from pathlib import Path

from logging_config import LOG_FILE

START_RE = re.compile(r"^(\S+ \S+) .*\[(\w+)\] Request started .*input=(.*)$")
DONE_RE = re.compile(
    r"\[(\w+)\] Request completed \| status=(\w+) \| latency=([\d.]+)s"
    r"(?: \| tool_calls=(\d+) \| tool_failures=(\d+))?"
)
# Agent-level tool lines, so only tool calls made inside a request are counted.
TOOL_RE = re.compile(r"\[(\w+)\] Tool (\w+) -> is_error=(\w+)")
BLOCKED_RE = re.compile(r"Security: blocked answer")


def parse(path: Path) -> tuple[list[dict], int, int, int]:
    requests: dict[str, dict] = {}
    tool_calls = tool_failures = blocked = 0

    for line in path.read_text(encoding="utf-8").splitlines():
        if m := START_RE.search(line):
            requests[m.group(2)] = {"id": m.group(2), "time": m.group(1), "input": m.group(3)}
        elif m := DONE_RE.search(line):
            req = requests.setdefault(m.group(1), {"id": m.group(1), "time": "?", "input": "?"})
            req.update(status=m.group(2), latency=float(m.group(3)),
                       tool_failures=int(m.group(5) or 0))
        elif m := TOOL_RE.search(line):
            tool_calls += 1
            tool_failures += m.group(3) == "True"
        elif BLOCKED_RE.search(line):
            blocked += 1

    return list(requests.values()), tool_calls, tool_failures, blocked


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else LOG_FILE
    requests, tool_calls, tool_failures, blocked = parse(path)
    completed = [r for r in requests if "status" in r]
    failures = [r for r in completed if r["status"] != "success"]

    print(f"Log file: {path}\n")
    print(f"{'Request':<10}{'Started':<21}{'Status':<9}{'Latency':>9}  Input")
    for r in requests:
        latency = f"{r['latency']:.2f}s" if "latency" in r else "-"
        print(f"{r['id']:<10}{r['time'][:19]:<21}{r.get('status', 'running'):<9}{latency:>9}  {r['input']}")

    latencies = sorted(r["latency"] for r in completed)
    print(f"\nTotal requests:     {len(requests)}")
    print(f"Completed:          {len(completed)}")
    print(f"Failures:           {len(failures)}")
    if latencies:
        print(f"Latency avg / min / max: {sum(latencies) / len(latencies):.2f}s / "
              f"{latencies[0]:.2f}s / {latencies[-1]:.2f}s")
    print(f"Tool calls:         {tool_calls}")
    print(f"Tool failures:      {tool_failures}")
    print(f"Blocked answers:    {blocked}  (price guardrail)")


if __name__ == "__main__":
    main()
