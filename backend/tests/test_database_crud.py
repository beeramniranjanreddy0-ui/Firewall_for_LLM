from __future__ import annotations

import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.database import crud
from app.database.session import Base
from app.models.prompt_log import PromptLog
from app.models.security_event import SecurityEvent


class DatabaseCrudTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        self.session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.session_factory()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_tables_are_created_from_models(self) -> None:
        tables = set(inspect(self.engine).get_table_names())

        self.assertIn(PromptLog.__tablename__, tables)
        self.assertIn(SecurityEvent.__tablename__, tables)

    def test_prompt_log_crud(self) -> None:
        created = crud.create_prompt_log(
            self.db,
            prompt="Explain machine learning",
            response="Machine learning is...",
            risk_score=0,
            risk_level="SAFE",
            decision="ALLOWED",
            user_ip="127.0.0.1",
            reason="Prompt Allowed",
        )
        self.db.commit()

        fetched = crud.get_prompt_log(self.db, created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.prompt, "Explain machine learning")

        updated = crud.update_prompt_log(self.db, created.id, response="Updated response", risk_score=15)
        self.db.commit()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.response, "Updated response")
        self.assertEqual(updated.risk_score, 15)

        logs, total = crud.list_prompt_logs(self.db, search="machine", limit=10, offset=0)
        self.assertEqual(total, 1)
        self.assertEqual(len(logs), 1)

        self.assertTrue(crud.delete_prompt_log(self.db, created.id))
        self.db.commit()
        self.assertIsNone(crud.get_prompt_log(self.db, created.id))

    def test_security_event_crud(self) -> None:
        created = crud.create_security_event(
            self.db,
            event_type="PROMPT_BLOCKED",
            severity="HIGH",
            details='{"reason":"test"}',
        )
        self.db.commit()

        fetched = crud.get_security_event(self.db, created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.event_type, "PROMPT_BLOCKED")

        updated = crud.update_security_event(self.db, created.id, severity="CRITICAL")
        self.db.commit()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.severity, "CRITICAL")

        events, total = crud.list_security_events(self.db, severity="CRITICAL", limit=10, offset=0)
        self.assertEqual(total, 1)
        self.assertEqual(len(events), 1)

        self.assertTrue(crud.delete_security_event(self.db, created.id))
        self.db.commit()
        self.assertIsNone(crud.get_security_event(self.db, created.id))


if __name__ == "__main__":
    unittest.main()
