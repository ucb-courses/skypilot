"""RunPod library wrapper, formats the input/output of the RunPod library for SkyPilot."""

import os
import json
from typing import Dict

from sky.adaptors import runpod


GPU_NAME_MAP = {
    "A100-80GB": "NVIDIA A100 80GB PCIe",
    "A100-40GB": "NVIDIA A100-PCIE-40GB",
    "A100-80GB-SXM4": "NVIDIA A100-SXM4-80GB",
    "A30": "NVIDIA A30",
    "A40": "NVIDIA A40",
    "RTX3070": "NVIDIA GeForce RTX 3070",
    "RTX3080": "NVIDIA GeForce RTX 3080",
    "RTX3080Ti": "NVIDIA GeForce RTX 3080 Ti",
    "RTX3090": "NVIDIA GeForce RTX 3090",
    "RTX3090Ti": "NVIDIA GeForce RTX 3090 Ti",
    "RTX4070Ti": "NVIDIA GeForce RTX 4070 Ti",
    "RTX4080": "NVIDIA GeForce RTX 4080",
    "RTX4090": "NVIDIA GeForce RTX 4090",
    "H100-80GB-HBM3": "NVIDIA H100 80GB HBM3",
    "H100-PCIe": "NVIDIA H100 PCIe",
    "L4": "NVIDIA L4",
    "L40": "NVIDIA L40",
    "RTX4000-Ada-SFF": "NVIDIA RTX 4000 SFF Ada Generation",
    "RTX6000-Ada": "NVIDIA RTX 6000 Ada Generation",
    "RTXA4000": "NVIDIA RTX A4000",
    "RTXA4500": "NVIDIA RTX A4500",
    "RTXA5000": "NVIDIA RTX A5000",
    "RTXA6000": "NVIDIA RTX A6000",
    "RTX5000": "Quadro RTX 5000",
    "V100-16GB-FHHL": "Tesla V100-FHHL-16GB",
    "V100-16GB-SXM2": "V100-SXM2-16GB",
    "RTXA2000": "NVIDIA RTX A2000",
    "V100-16GB-PCIe": "Tesla V100-PCIE-16GB"
}


TAG_FILE = os.path.expanduser("~/.runpod/skypilot_tags.json")

if not os.path.exists(TAG_FILE):
    with open(TAG_FILE, "w", encoding="UTF-8") as tags:
        json.dump({}, tags)


def list_instances():
    """Lists instances associated with API key."""
    instances = runpod.rp_wrapper().get_pods()

    instance_list = {}
    for instance in instances:
        instance_list[instance["id"]] = {}

        instance_list[instance["id"]]["status"] = instance["desiredStatus"]
        instance_list[instance["id"]]["name"] = instance["name"]

        if instance["desiredStatus"] == "RUNNING" and instance.get("runtime", None):
            for port in instance["runtime"]["ports"]:
                if port["privatePort"] == 22:
                    instance_list[instance["id"]]["ip"] = port["ip"]
                    instance_list[instance["id"]]["ssh_port"] = port["publicPort"]

        # Set tags
        with open(TAG_FILE, "r", encoding="UTF-8") as open_tag_file:
            instance_tags = json.load(open_tag_file)
        instance_list[instance["id"]]["tags"] = instance_tags[instance["id"]]

    return instance_list


def launch(name: str, instance_type: str, region: str):
    """Launches an instance with the given parameters.

    Converts the instance_type to the RunPod GPU name, finds the specs for the GPU, and launches the instance.
    """
    gpu_type = GPU_NAME_MAP[instance_type.split("_")[1]]
    gpu_quantity = int(instance_type.split("_")[0].replace("x", ""))
    cloud_type = instance_type.split("_")[2]

    gpu_specs = runpod.rp_wrapper().get_gpu(gpu_type)

    new_instance = runpod.rp_wrapper().create_pod(
        name=name,
        image_name="runpod/base:0.0.0",
        gpu_type_id=gpu_type,
        cloud_type=cloud_type,
        min_vcpu_count=4*gpu_quantity,
        min_memory_in_gb=gpu_specs["memoryInGb"]*gpu_quantity,
        country_code=region,
        ports="22/tcp",
        support_public_ip=True,
    )

    return new_instance["id"]


def set_tags(instance_id: str, tags: Dict):
    """Sets the tags for the given instance."""
    with open(TAG_FILE, "r", encoding="UTF-8") as tag_list:
        instance_tags = json.load(tag_list)

    instance_tags[instance_id] = tags

    with open(TAG_FILE, "w", encoding="UTF-8") as tag_list:
        json.dump(instance_tags, tag_list)


def remove(instance_id: str):
    """Terminates the given instance."""
    runpod.rp_wrapper().terminate_pod(instance_id)
