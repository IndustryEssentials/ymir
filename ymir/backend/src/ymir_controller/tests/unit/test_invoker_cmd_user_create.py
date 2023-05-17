import os
import shutil
import unittest

from controller.utils.invoker_call import make_invoker_cmd_call
from controller.utils.invoker_mapping import RequestTypeToInvoker
from id_definition.error_codes import CTLResponseCode
from proto import backend_pb2
import tests.utils as test_utils


class TestInvokerUserCreate(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        # dir structure:
        # test_involer_CLSNAME_sandbox_root
        # └── test_user
        super().__init__(methodName=methodName)
        self._user_name = "user"
        self._task_id = 't000aaaabbbbbbzzzzzzzzzzzzzzz5'

        self._sandbox_root = test_utils.dir_test_root(self.id().split(".")[-3:])
        self._user_root = os.path.join(self._sandbox_root, self._user_name)

    def setUp(self):
        test_utils.check_commands()
        self._prepare_dirs()

    def tearDown(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)

    # protected: env prepare
    def _prepare_dirs(self):
        if os.path.isdir(self._sandbox_root):
            shutil.rmtree(self._sandbox_root)
        os.makedirs(self._sandbox_root)

    def test_invoker_init_00(self):
        response = make_invoker_cmd_call(sandbox_root=self._sandbox_root,
                                         req_type=backend_pb2.USER_CREATE,
                                         invoker=RequestTypeToInvoker[backend_pb2.USER_CREATE],
                                         user_id=self._user_name,
                                         task_id=self._task_id)

        self.assertEqual(response.code, CTLResponseCode.CTR_OK)
        self.assertTrue(os.path.isdir(self._user_root))
