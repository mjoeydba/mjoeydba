#!/usr/bin/env python3
"""Utility script to validate Elastic connectivity for MSSQL telemetry indices."""
import argparse
import getpass
import json
import os

from elasticsearch import Elasticsearch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Test Elastic MSSQL telemetry queries")
    parser.add_argument("--url", required=True)
    parser.add_argument("--index", required=True)
    parser.add_argument("--q", required=True, help="Query string")
    parser.add_argument("--user", default=os.getenv("ES_USER"))
    parser.add_argument("--password", default=os.getenv("ES_PASS"))
    parser.add_argument("--ca", default=os.getenv("ES_CA_CERT"))
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--size", type=int, default=3)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    user = args.user or input("Username: ")
    pwd = args.password or getpass.getpass("Password: ")

    es = Elasticsearch(
        args.url,
        basic_auth=(user, pwd),
        ca_certs=args.ca if args.ca and not args.insecure else None,
        verify_certs=False if args.insecure else True,
        request_timeout=300,
    )

    body = {
        "query": {"query_string": {"query": args.q}},
        "size": args.size,
    }
    print("Outgoing body:\n", json.dumps(body, indent=2))

    response = es.search(index=args.index, q=args.q, size=args.size)
    print(json.dumps(response, indent=2, default=str))


if __name__ == "__main__":  # pragma: no cover - CLI utility
    main()
