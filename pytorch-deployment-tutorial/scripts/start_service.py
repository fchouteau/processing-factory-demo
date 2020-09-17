#!/usr/bin/python3

import argparse
from pathlib import Path
import json

from pesto.common.testing.service_manager import ServiceManager

port = 4000
service = "pytorch-deployment-tutorial:1.0.0.dev0"

parser = argparse.ArgumentParser(
    description="Start the PESTO webservice.Example: {} [-p gpu]".format(__file__),
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    "-p",
    "--profile",
    nargs="+",
    default="",
    help="List of profiles to apply. Use stateless to enable the asynchronous service",
)
args = parser.parse_args()

if len(args.profile):
    service = service + "-" + "-".join(args.profile)

nvidia = "gpu" in service
print("Launching service " + service)

with ServiceManager(docker_image=service, host_port=port, nvidia=nvidia) as service:
    input("Press Enter to quit ...")
