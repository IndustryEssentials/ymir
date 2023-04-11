import unittest

from id_definition import task_id


class TestTaskId(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._user_id = 1
        self._repo_id = 2

    def test_gen_seq_id_00(self) -> None:
        user_hash = task_id.gen_user_hash(self._user_id)
        repo_hash = task_id.gen_repo_hash(self._repo_id)

        sids = task_id.gen_seq_hashes(count=2, user_id=self._user_id, repo_id=self._repo_id)
        sid_typed = task_id.TaskId.from_task_id(sids[0])
        self.assertEqual(task_id.IDType.ID_TYPE_SEQ_TASK.value, sid_typed.id_type)
        self.assertEqual(2, int(sid_typed.seq_task_count))
        self.assertEqual(0, int(sid_typed.sub_task_id))
        self.assertEqual(user_hash, sid_typed.user_id)
        self.assertEqual(repo_hash, sid_typed.repo_id)

        self.assertEqual(2, len(sids[1]))
        for idx, sid in enumerate(sids[1]):
            sid_typed = task_id.TaskId.from_task_id(sid)
            self.assertEqual(task_id.IDType.ID_TYPE_SEQ_TASK.value, sid_typed.id_type)
            self.assertEqual(2, int(sid_typed.seq_task_count))
            self.assertEqual(idx + 1, int(sid_typed.sub_task_id))
            self.assertEqual(user_hash, sid_typed.user_id)
            self.assertEqual(repo_hash, sid_typed.repo_id)

    def test_gen_seq_id_01(self) -> None:
        with self.assertRaises(ValueError):
            task_id.gen_seq_hashes(count=0, user_id=self._user_id, repo_id=self._repo_id)
        with self.assertRaises(ValueError):
            task_id.gen_seq_hashes(count=1, user_id=self._user_id, repo_id=self._repo_id)
        with self.assertRaises(ValueError):
            task_id.gen_seq_hashes(count=10, user_id=self._user_id, repo_id=self._repo_id)
