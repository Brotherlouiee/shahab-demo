"""Bounded owner-run deployment audit: no SMS, credentials, load or configuration writes.

Six public HTTP requests plus local Docker/proxy inspection. Only booleans,
statuses and image identities leave memory; no environment, config or body dump.
The Secure/HttpOnly session-cookie evidence is reused from the T06 live check.
"""

import json
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ORIGIN = "https://shahabfintech.ir"


class AuditFailed(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check(name, passed):
    if not passed:
        raise AuditFailed(name)
    print("PASS " + name, flush=True)


def command(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=20).stdout


def api_block(config):
    """Inspect the actual API location, not directives in an unrelated vhost."""
    config = re.sub(r"#[^\n]*", "", config)
    matches = list(re.finditer(r"location\s+/api/v1/\s*\{", config))
    if len(matches) != 1:
        raise AuditFailed("ambiguous_api_location")
    start = matches[0].end()
    depth = 1
    for index in range(start, len(config)):
        depth += (config[index] == "{") - (config[index] == "}")
        if depth == 0:
            return config[start:index]
    raise AuditFailed("invalid_api_location")


def inspect_proxy(config):
    block = api_block(config)
    for header, value in (("X-Forwarded-Proto", "$scheme"), ("X-Forwarded-For", "$remote_addr")):
        values = re.findall(r"proxy_set_header\s+" + header + r"\s+([^;]+);", block, re.I)
        check("proxy_overwrites_" + header.lower(), values == [value])
    check("proxy_api_internal", bool(re.search(r"proxy_pass\s+http://api:8000\s*;", block)))
    for name, limit in (("connect", 10), ("read", 60), ("send", 60)):
        values = re.findall(r"proxy_" + name + r"_timeout\s+([0-9]+)s;", block)
        check("bounded_proxy_" + name + "_timeout", len(values) == 1 and 0 < int(values[0]) <= limit)
    zone = re.search(r"limit_req\s+zone=([a-zA-Z0-9_]+)\b", block)
    check("api_rate_limit_attached", zone is not None)
    zone_name = re.escape(zone.group(1))
    check(
        "api_rate_limit_defined",
        bool(
            re.search(
                r"limit_req_zone\s+\$binary_remote_addr\s+zone=" + zone_name + r":[^;]+\brate=[1-9][0-9]*r/s\s*;",
                config,
            )
        ),
    )
    check("body_limit_configured", bool(re.search(r"client_max_body_size\s+1m\s*;", config)))
    check("tls_protocols_restricted", bool(re.search(r"ssl_protocols\s+TLSv1\.2\s+TLSv1\.3\s*;", config)))


def inspect_containers():
    template = (
        '{"name":{{json .Name}},"ports":{{json .NetworkSettings.Ports}},'
        '"networks":{{json .NetworkSettings.Networks}},"cmd":{{json .Config.Cmd}},'
        '"image":{{json .Config.Image}}}'
    )
    rows = command(
        "docker",
        "inspect",
        "--format",
        template,
        *("shahab-prod-" + name + "-1" for name in ("api", "frontend", "postgres", "redis")),
    )
    services = {
        row["name"].removeprefix("/shahab-prod-").removesuffix("-1"): row
        for row in (json.loads(line) for line in rows.splitlines())
    }
    for name in ("api", "postgres", "redis"):
        check(name + "_has_no_host_port", not any((services[name]["ports"] or {}).values()))
    bindings = [binding for group in (services["frontend"]["ports"] or {}).values() for binding in (group or [])]
    check(
        "frontend_host_ports_loopback_only",
        bool(bindings) and all(binding["HostIp"] in {"127.0.0.1", "::1"} for binding in bindings),
    )
    peers = {value["IPAddress"] for value in services["frontend"]["networks"].values()}
    args = services["api"]["cmd"]
    index = args.index("--forwarded-allow-ips")
    allowed = set(args[index + 1].split(","))
    check("api_trusts_only_frontend_peer", bool(allowed) and allowed <= peers and "*" not in allowed)
    inspect_proxy(command("docker", "exec", "shahab-prod-frontend-1", "nginx", "-T", "-c", "/tmp/vm.conf"))
    # Check host listeners as well as Docker publish rules; no process details are printed.
    listeners = command("ss", "-H", "-lnt")
    unsafe = []
    for line in listeners.splitlines():
        fields = line.split()
        if len(fields) >= 4:
            address, _, port = fields[3].rpartition(":")
            if port in {"5432", "6379", "8000"} and address not in {"127.0.0.1", "[::1]", "::1"}:
                unsafe.append(port)
    check("no_public_db_redis_api_listener", not unsafe)
    print(json.dumps({"deployedImages": {name: row["image"] for name, row in services.items()}}, sort_keys=True))


def request(opener, method, url, headers=None, data=None):
    req = Request(url, method=method, headers=headers or {}, data=data)
    try:
        response = opener.open(req, timeout=15)
    except HTTPError as error:
        response = error
    with response:
        return response.code, response.headers


def inspect_https():
    opener = build_opener(ProxyHandler({}), NoRedirect())
    path = "/api/v1/health/live"
    status, headers = request(opener, "GET", "http://shahabfintech.ir" + path)
    check(
        "http_redirects_to_canonical_https", status in {301, 302, 307, 308} and headers.get("Location") == ORIGIN + path
    )
    for name, extra in (
        ("https_health", {}),
        (
            "spoofed_forwarding",
            {
                "X-Forwarded-Proto": "http",
                "X-Forwarded-Host": "not-shahab.invalid",
                "X-Forwarded-For": "192.0.2.1",
                "Forwarded": "proto=http;host=not-shahab.invalid",
            },
        ),
    ):
        status, headers = request(opener, "GET", ORIGIN + path, extra)
        check(name + "_200_tls_valid", status == 200)
        hsts = headers.get_all("Strict-Transport-Security", [])
        check(
            name + "_hsts",
            bool(hsts)
            and all((m := re.search(r"max-age=([0-9]+)", value)) and int(m.group(1)) >= 15552000 for value in hsts),
        )
        check(name + "_nosniff", headers.get("X-Content-Type-Options", "").lower() == "nosniff")
        check(name + "_frame_denied", headers.get("X-Frame-Options", "").upper() == "DENY")
        check(name + "_no_store", "no-store" in headers.get("Cache-Control", "").lower())
    status, headers = request(opener, "GET", ORIGIN + "/api/v1/account-access/session")
    check("anonymous_session_401_no_store", status == 401 and "no-store" in headers.get("Cache-Control", "").lower())
    target = ORIGIN + "/api/v1/account-access/logout"
    bad_origin = "https://not-shahab.invalid"
    status, headers = request(
        opener, "OPTIONS", target, {"Origin": bad_origin, "Access-Control-Request-Method": "POST"}
    )
    check(
        "untrusted_cors_not_allowed", status in {400, 403, 405} and headers.get("Access-Control-Allow-Origin") is None
    )
    status, _ = request(
        opener,
        "POST",
        target,
        {"Origin": bad_origin, "Sec-Fetch-Site": "cross-site", "Content-Type": "application/json"},
        b"{}",
    )
    check("cross_origin_mutation_403", status == 403)


def main():
    try:
        inspect_containers()
        inspect_https()
    except AuditFailed as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    except (Exception, KeyboardInterrupt):
        print("FAIL inspection_or_transport_error; no config/body/credentials printed", file=sys.stderr)
        return 1
    print(json.dumps({"task": "US-11.T02H", "result": "host_checks_passed", "httpRequests": 6, "smsRequests": 0}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
