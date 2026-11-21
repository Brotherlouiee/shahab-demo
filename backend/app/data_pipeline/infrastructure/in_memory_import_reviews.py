"""Local/test import review adapter; never wired into production composition."""

from backend.app.data_pipeline.application.operations import ReviewedImport


class InMemoryImportReviewRepository:
    """Preserve first actor/time and immutable evidence on identical retries."""

    def __init__(self) -> None:
        self._records: dict[str, ReviewedImport] = {}

    def get_by_id(self, import_id: str) -> ReviewedImport | None:
        return self._records.get(import_id)

    def save_if_absent(self, record: ReviewedImport) -> ReviewedImport:
        previous = self._records.get(record.import_id)
        if previous is not None:
            if (
                previous.preparation != record.preparation
                or previous.actor_reference != record.actor_reference
                or previous.reason != record.reason
            ):
                raise ValueError("import ID conflicts with existing evidence")
            return previous
        self._records[record.import_id] = record
        return record
