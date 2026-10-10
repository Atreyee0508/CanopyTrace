"""CanopyTrace Escalation Package."""

from canopytrace.escalation.queue import enqueue_escalation, list_pending_escalations
from canopytrace.escalation.approval import approve_and_ingest_novel_finding

__all__ = [
    "enqueue_escalation",
    "list_pending_escalations",
    "approve_and_ingest_novel_finding",
]
