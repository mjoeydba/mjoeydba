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
    parser.add_argument(
        "--compat-version",
        type=int,
        default=int(os.getenv("ES_COMPAT_VERSION", 8)),
        help="Elasticsearch compatibility version for Accept/Content-Type headers",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    user = args.user or input("Username: ")
    pwd = args.password or getpass.getpass("Password: ")

    headers = None
    if args.compat_version:
        media_type = f"application/vnd.elasticsearch+json; compatible-with={args.compat_version}"
        headers = {"Accept": media_type, "Content-Type": media_type}

    client_kwargs = {
        "basic_auth": (user, pwd),
        "ca_certs": args.ca if args.ca and not args.insecure else None,
        "verify_certs": False if args.insecure else True,
        "request_timeout": 300,
    }
    if headers:
        client_kwargs["headers"] = headers

    es = Elasticsearch(args.url, **client_kwargs)

    body = {
        "query": {"query_string": {"query": args.q}},
        "size": args.size,
    }
    print("Outgoing body:\n", json.dumps(body, indent=2))

    response = es.search(index=args.index, q=args.q, size=args.size)
    print(json.dumps(response, indent=2, default=str))


if __name__ == "__main__":  # pragma: no cover - CLI utility
    main()
