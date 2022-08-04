import contextlib
import functools
import pathlib
import tempfile
import uuid
from typing import Optional, Callable, List, Any

import kfp
import kfp.compiler
import kfp.dsl as dsl
from kfp.dsl import Sidecar
from kubernetes.client import (
    V1Affinity,
    V1NodeAffinity,
    V1PreferredSchedulingTerm,
    V1NodeSelectorTerm,
    V1NodeSelectorRequirement, V1EnvVar,
)

from . import core, utils
from .core import Task


class _KubeFlowHardwareProvider(core.HardwareProvider):
    def get_available_hardware(self) -> List[str]:
        return []


class _KubeFlowTask(core.Task):
    def __init__(
            self,
            kind: core.TaskKind,
            target: core.OptimizationTarget,
            op: dsl.ContainerOp,
            model_class=None
    ):
        super().__init__(kind, target, model_class, op.name, op.human_name)
        self._op = op
        self._op.add_pod_label("n8s.nebuly.ai/optimization-target", target)
        self._op.add_pod_label("n8s.nebuly.ai/sdk-version", "0.0.1")
        self._op.add_pod_label("n8s.nebuly.ai/nebulex-version", "v1")

    def set_hardware_kinds(self, kinds: List[str]):
        affinity = V1Affinity(
            node_affinity=V1NodeAffinity(preferred_during_scheduling_ignored_during_execution=[
                V1PreferredSchedulingTerm(
                    preference=V1NodeSelectorTerm(
                        match_expressions=[
                            V1NodeSelectorRequirement(
                                key="foo",
                                operator="in",
                                values=["bar_1", "bar_2"],
                            ),
                        ]
                    ),
                    weight=10,
                )
            ])
        )
        self._op.add_affinity(affinity)

    def set_optimization_strategy(self, strategy: str):
        if self.kind == core.TaskKind.TRAINING:
            self._op.container.add_env_variable(V1EnvVar(name="NEBULGYM_CONFIG", value=strategy))
            self._op.add_sidecar(Sidecar(
                name="Nebulgym injector",
                image="nebuly.ai/nebulgym-injector",
                command="somehow inject nebulgym :)",
            ))
        if self.kind == core.TaskKind.INFERENCE:
            self._op.container.add_env_variable(V1EnvVar(name="NEBULLVM_CONFIG", value=strategy))
            self._op.add_sidecar(Sidecar(
                name="Nebullvm injector",
                image="nebuly.ai/nebullvm-injector",
                command="somehow inject nebullvm :)",
            ))
        self._op.add_pod_label("n8s.nebuly.ai/optimized-for", self.kind.value)


class _KubeFlowOptimizer(core.TaskOptimizer):
    def __init__(self, hardware_provider: core.HardwareProvider = None):
        if hardware_provider is None:
            hardware_provider = _KubeFlowHardwareProvider()
        super().__init__(hardware_provider)
        self.tasks: List[core.Task] = []

    def register_op(
            self,
            operation: dsl.ContainerOp,
            kind: core.TaskKind,
            model=None,
            optimization_target=None
    ):
        task = _KubeFlowTask(kind, optimization_target, operation, model)
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        return self.tasks


_optimizer: Optional[_KubeFlowOptimizer] = None


def optimize_test(operation: dsl.ContainerOp, model_class: Optional = None, optimization_target: Optional = None):
    if _optimizer is not None:
        _optimizer.register_op(operation, core.TaskKind.TEST, model_class, optimization_target)


def optimize_inference(operation: dsl.ContainerOp, model_class: Optional = None, optimization_target: Optional = None):
    if _optimizer is not None:
        _optimizer.register_op(operation, core.TaskKind.INFERENCE, model_class, optimization_target)


def optimize_training(operation: dsl.ContainerOp, model_class: Optional = None, optimization_target: Optional = None):
    if _optimizer is not None:
        _optimizer.register_op(operation, core.TaskKind.TRAINING, model_class, optimization_target)


@contextlib.contextmanager
def _use_optimizer(optimizer: _KubeFlowOptimizer):
    global _optimizer
    __previous_optimizer = optimizer
    _optimizer = optimizer
    yield
    _optimizer = __previous_optimizer


def optimized_pipeline(pipeline_func: Callable, optimizer=_KubeFlowOptimizer()):
    @functools.wraps(pipeline_func)
    def _wrap(*args, **kwargs) -> Any:
        with _use_optimizer(optimizer):
            res = pipeline_func(*args, **kwargs)
            optimizer.optimize()
            return res

    return _wrap


class KubeflowWorkflow(core.Workflow):
    KIND = "Kubeflow Pipeline"

    def __init__(self, client: kfp.Client, pipeline_func: Callable):
        self._client = client
        self._optimizer = core.TaskOptimizer(_KubeFlowHardwareProvider())
        self._compiler = kfp.compiler.Compiler()
        self._pipeline_func = utils.without_decorator(pipeline_func, optimized_pipeline)
        name = getattr(pipeline_func, "_component_human_name")
        self._workdir_path = pathlib.Path(tempfile.mkdtemp())
        self._compiled_pipeline_path = self._workdir_path / pathlib.Path(f"{name}.yaml")
        tasks = self.__compile_pipeline()

        super().__init__(name, tasks, self.KIND)

    def __compile_pipeline(self) -> List[core.Task]:
        optimizer = _KubeFlowOptimizer()
        with _use_optimizer(optimizer):
            self._compiler.compile(self._pipeline_func, str(self._compiled_pipeline_path))
        return optimizer.tasks

    def publish(self):
        if self._client.get_pipeline_id(self.name) is not None:
            version_id = uuid.uuid4()
            self._client.upload_pipeline_version(str(self._compiled_pipeline_path), str(version_id))
        else:
            self._client.upload_pipeline(str(self._compiled_pipeline_path), self.name)

    def run(self):
        self._client.run_pipeline(
            experiment_id="...",
            job_name="...",
            pipeline_package_path=str(self._compiled_pipeline_path),
        )

    def optimize(self, optimization_options: core.OptimizationOptions = None):
        # TODO: handle optimization options
        optimizer = _KubeFlowOptimizer()
        wrapped = optimized_pipeline(self._pipeline_func, optimizer)
        self._compiler.compile(wrapped, str(self._compiled_pipeline_path))
        self.tasks = optimizer.tasks

    def get_run_metrics(self) -> core.WorkflowRunMetrics:
        pass