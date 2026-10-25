"""Run the procurement sandbox: python -m procurement_sandbox [--port 8081]."""

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Procurement sandbox - not SAP connected")
    parser.add_argument("--host", default=os.environ.get("PROC_SANDBOX_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PROC_SANDBOX_PORT", "8081")))
    parser.add_argument("--db", default=os.environ.get("PROC_SANDBOX_DB"), help="SQLite path (default: procurement_sandbox/data/sandbox.sqlite)")
    args = parser.parse_args()
    if args.db:
        os.environ["PROC_SANDBOX_DB"] = args.db
    uvicorn.run("procurement_sandbox.app:app", host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
