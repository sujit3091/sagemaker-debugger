# Standard Library

# Third Party
from tests.zero_code_change.horovod_tests.utils import build_json, launch_horovod_job
from torch.cuda import device_count

# First Party
from smdebug.trials import create_trial

"""
Tested on current DLAMI p3.8xlarge when run from the main directory
"""

HOROVOD_MNIST_SCRIPT_NAME = "horovod_mnist.py"


def basic_test(out_dir, mode):
    path = build_json(out_dir, include_workers="one", include_collections=["weights", "gradients"])
    num_workers = device_count()
    mode_args = []
    if mode == "cpu":
        mode_args += ["--use_only_cpu", "true"]
    launch_horovod_job(
        script_file_path=f"examples/pytorch/zero_code_change/{HOROVOD_MNIST_SCRIPT_NAME}",
        script_args=mode_args,
        num_workers=num_workers,
        config_file_path=path,
        mode=mode,
    )

    tr = create_trial(out_dir)
    print("Saved Tensor Names: {}".format(tr.tensor_names()))
    assert len(tr.workers()) == 1  # We expect only one worker because
    # it has been configured so in HOROVOD_MNIST_SCRIPT_NAME
    assert len(tr.tensor_names()) == 13
    assert len(tr.tensor(tr.tensor_names(collection="weights")[0]).workers(0)) == 1


def test_cpu(out_dir):
    basic_test(out_dir, "cpu")


def test_gpu(out_dir):
    basic_test(out_dir, "gpu")


def mode_allworkers(out_dir, mode):
    path = build_json(out_dir, include_workers="all", include_collections=["weights", "gradients"])
    num_workers = 1 if bool(device_count()) is False else device_count()
    mode_args = []
    if mode == "cpu":
        mode_args += ["--use_only_cpu", "true"]
    launch_horovod_job(
        script_file_path=f"examples/pytorch/zero_code_change/{HOROVOD_MNIST_SCRIPT_NAME}",
        script_args=mode_args,
        num_workers=num_workers,
        config_file_path=path,
        mode=mode,
    )
    tr = create_trial(out_dir)
    assert len(tr.workers()) == num_workers
    assert len(tr.tensor_names()) == 13
    assert len(tr.tensor(tr.tensor_names(collection="weights")[0]).workers(0)) == num_workers


def test_cpu_allworkers(out_dir):
    mode_allworkers(out_dir, "cpu")


def test_gpu_allworkers(out_dir):
    mode_allworkers(out_dir, "gpu")


def mode_allworkers_saveall(out_dir, mode):
    path = build_json(
        out_dir, include_workers="all", save_all=True, include_collections=["weights", "gradients"]
    )
    num_workers = 1 if bool(device_count()) is False else device_count()
    mode_args = []
    if mode == "cpu":
        mode_args += ["--use_only_cpu", "true"]
    launch_horovod_job(
        script_file_path=f"examples/pytorch/zero_code_change/{HOROVOD_MNIST_SCRIPT_NAME}",
        script_args=mode_args,
        num_workers=num_workers,
        config_file_path=path,
        mode=mode,
    )
    tr = create_trial(out_dir)
    assert len(tr.workers()) == num_workers
    assert len(tr.tensor_names()) > 25
    assert len(tr.tensor(tr.tensor_names(collection="weights")[0]).workers(0)) == num_workers
    assert len(tr.tensor(tr.tensor_names(collection="losses")[0]).workers(0)) == num_workers


def test_gpu_allworkers_saveall(out_dir):
    mode_allworkers_saveall(out_dir, "gpu")


def test_cpu_allworkers_saveall(out_dir):
    mode_allworkers_saveall(out_dir, "cpu")
