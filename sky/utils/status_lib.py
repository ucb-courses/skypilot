"""Statuses enum for SkyPilot resources."""

import enum
from typing import List

import colorama


class ClusterStatus(enum.Enum):
    """Cluster status as recorded in local cache.

    This can be different from the actual cluster status, and can be refreshed
    by running ``sky status --refresh``.
    """
    # NOTE: these statuses are as recorded in our local cache, the table
    # 'clusters'.  The actual cluster state may be different (e.g., an UP
    # cluster getting killed manually by the user or the cloud provider).

    INIT = 'INIT'
    """Initializing.

    This means a provisioning has started but has not successfully finished. The
    cluster may be undergoing setup, may have failed setup, may be live or down.
    """

    UP = 'UP'
    """The cluster is up. This means a provisioning has previously succeeded."""

    STOPPED = 'STOPPED'
    """The cluster is stopped."""

    def colored_str(self):
        color = _STATUS_TO_COLOR[self]
        return f'{color}{self.value}{colorama.Style.RESET_ALL}'


_STATUS_TO_COLOR = {
    ClusterStatus.INIT: colorama.Fore.BLUE,
    ClusterStatus.UP: colorama.Fore.GREEN,
    ClusterStatus.STOPPED: colorama.Fore.YELLOW,
}


class StorageStatus(enum.Enum):
    """Storage status as recorded in table 'storage'."""

    # Initializing and uploading storage
    INIT = 'INIT'

    # Initialization failed
    INIT_FAILED = 'INIT_FAILED'

    # Failed to Upload to Cloud
    UPLOAD_FAILED = 'UPLOAD_FAILED'

    # Finished uploading, in terminal state
    READY = 'READY'


class JobStatus(enum.Enum):
    """Job status enum."""

    # 3 in-flux states: each can transition to any state below it.
    # The `job_id` has been generated, but the generated ray program has
    # not started yet. skylet can transit the state from INIT to FAILED
    # directly, if the ray program fails to start.
    # In the 'jobs' table, the `submitted_at` column will be set to the current
    # time, when the job is firstly created (in the INIT state).
    INIT = 'INIT'
    """The job has been submitted, but not started yet."""
    # The job is waiting for the required resources. (`ray job status`
    # shows RUNNING as the generated ray program has started, but blocked
    # by the placement constraints.)
    PENDING = 'PENDING'
    """The job is waiting for required resources."""
    # Running the user's setup script (only in effect if --detach-setup is
    # set). Our update_job_status() can temporarily (for a short period) set
    # the status to SETTING_UP, if the generated ray program has not set
    # the status to PENDING or RUNNING yet.
    SETTING_UP = 'SETTING_UP'
    """The job is running the user's setup script (detach_setup is set)."""
    # The job is running.
    # In the 'jobs' table, the `start_at` column will be set to the current
    # time, when the job is firstly transitioned to RUNNING.
    RUNNING = 'RUNNING'
    """The job is running."""
    # 3 terminal states below: once reached, they do not transition.
    # The job finished successfully.
    SUCCEEDED = 'SUCCEEDED'
    """The job finished successfully."""
    # The job fails due to the user code or a system restart.
    FAILED = 'FAILED'
    """The job fails due to the user code."""
    # The job setup failed (only in effect if --detach-setup is set). It
    # needs to be placed after the `FAILED` state, so that the status
    # set by our generated ray program will not be overwritten by
    # ray's job status (FAILED).
    # This is for a better UX, so that the user can find out the reason
    # of the failure quickly.
    FAILED_SETUP = 'FAILED_SETUP'
    """The job setup failed (detach_setup is set)."""
    # The job is cancelled by the user.
    CANCELLED = 'CANCELLED'
    """The job is cancelled by the user."""

    @classmethod
    def nonterminal_statuses(cls) -> List['JobStatus']:
        return [cls.INIT, cls.SETTING_UP, cls.PENDING, cls.RUNNING]

    def is_terminal(self):
        return self not in self.nonterminal_statuses()

    def __lt__(self, other):
        return list(JobStatus).index(self) < list(JobStatus).index(other)

    def colored_str(self):
        color = _JOB_STATUS_TO_COLOR[self]
        return f'{color}{self.value}{colorama.Style.RESET_ALL}'


_JOB_STATUS_TO_COLOR = {
    JobStatus.INIT: colorama.Fore.BLUE,
    JobStatus.SETTING_UP: colorama.Fore.BLUE,
    JobStatus.PENDING: colorama.Fore.BLUE,
    JobStatus.RUNNING: colorama.Fore.GREEN,
    JobStatus.SUCCEEDED: colorama.Fore.GREEN,
    JobStatus.FAILED: colorama.Fore.RED,
    JobStatus.FAILED_SETUP: colorama.Fore.RED,
    JobStatus.CANCELLED: colorama.Fore.YELLOW,
}
