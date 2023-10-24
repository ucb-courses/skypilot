"""Metadata"""
import dataclasses
import typing
from typing import Generic, List, Optional

from sky import backends
from sky.utils import status_lib

_ResourceHandleType = typing.TypeVar('_ResourceHandleType',
                                     bound=backends.ResourceHandle)


@dataclasses.dataclass
class ClusterInfo(Generic[_ResourceHandleType]):
    """Information about a cluster."""
    name: str
    """Cluster name."""
    status: status_lib.ClusterStatus
    """Status of the cluster."""
    launched_at: int
    """Timestamp of when the cluster was launched."""
    handle: _ResourceHandleType
    """Handle of the cluster."""
    last_use: str
    """The command that was last used to interact with the cluster."""
    autostop: int
    """Idle time before autostop"""
    to_down: bool
    """Whether autodown is used instead of autostop"""
    owner: Optional[List[str]]
    """Owner of the cluster"""
    metadata: dict
    """Metadata of the cluster"""
    _cluster_hash: str
    """Hash of the cluster (only used for internal purposes)"""


@dataclasses.dataclass
class JobInfo:
    """Information about a job."""
    job_id: int
    """Job ID."""
    job_name: str
    """Job name."""
    username: str
    """Username launched the job on the remote VM."""
    submitted_at: int
    """Timestamp of when the job was submitted."""
    start_at: int
    """Timestamp of when the job was started."""
    resources: str
    """Resources used by the job."""
    status: status_lib.JobStatus
    """Status of the job."""
    log_path: str
    """Path to the log file of the job on the remote VM."""
