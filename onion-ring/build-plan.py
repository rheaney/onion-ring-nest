#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Emit a local-first upstream build command; never run it or touch a device."""
import argparse
import hashlib
import ipaddress
import json
import shlex
from pathlib import Path
from urllib.parse import urlsplit


def endpoint(value: str) -> str:
    try:
        url = urlsplit(value)
        address = ipaddress.IPv4Address(url.hostname or '')
        port = url.port
    except ValueError as error:
        raise argparse.ArgumentTypeError('Use a private IPv4 LAN URL with an explicit port') from error
    # RFC1918 only: no hosted fallback, loopback, link-local or public address.
    private = any(address in ipaddress.ip_network(network) for network in
                  ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))
    if (not private or url.scheme not in ('http', 'https') or not port
            or url.username is not None or url.password is not None
            or url.path not in ('', '/') or url.query or url.fragment):
        raise argparse.ArgumentTypeError('Use http(s)://PRIVATE_IPV4:PORT without credentials or a path')
    return f'{url.scheme}://{address}:{port}'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-url', required=True, type=endpoint)
    parser.add_argument('--generation', required=True, choices=('gen1', 'gen2', 'both'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    profile = json.loads((root / 'onion-ring/profile.json').read_text())
    for name, expected in profile['bundled_images_sha256'].items():
        actual = hashlib.sha256((root / 'firmware/installer/resources/firmware' / name).read_bytes()).hexdigest()
        if actual != expected:
            parser.error(f'Upstream bundled image changed: {name}; review provenance before building')
    flags = ['--api-url', args.api_url, '--generation', args.generation, '--force-build', '--yes']
    print(json.dumps({
        'variant': profile['variant'], 'version': profile['version'],
        'upstream_commit': profile['upstream']['commit'],
        'build_command': shlex.join(['bash', 'docker-build.sh', *flags]),
        'working_directory': 'isolated copy of firmware/builder, outside the checkout',
        'root_access': False, 'backplate_simulator': False,
        'bootloaders': 'upstream prebuilt unless separately rebuilt and qualified',
        'tls': 'HTTPS requires separate local-CA trust work; upstream embeds its own CA',
        'status': 'build plan only; no build, flash, configuration write or network call performed',
    }, indent=2))


if __name__ == '__main__':
    main()
