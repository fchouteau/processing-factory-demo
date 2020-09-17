from pathlib import Path

from pesto.common.testing.test_runner import TestRunner

nvidia = False
service = "pytorch-deployment-tutorial:1.0.0.dev0"
# service = "pytorch-deployment-tutorial:1.0.0.dev0-stateful" # test stateful profile

test_dir = Path(__file__).parent.parent / "pesto" / "tests" / "resources"

print("Running in {}".format(test_dir))

# Mimic Pesto Test
results = TestRunner(docker_image_name=service, nvidia=nvidia).run_all(test_dir)

ok_dict = {"NoDifference": True}


def test_describe():
    assert results.get("describe") == ok_dict


def test_processing():
    for test_key in results.keys():
        if "test_" in test_key:
            assert results.get(test_key) == ok_dict
