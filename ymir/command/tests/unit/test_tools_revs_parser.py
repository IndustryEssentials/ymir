from typing import Tuple
import unittest

from mir.tools import revs_parser
from mir.tools.errors import MirRuntimeError


def _typ_rev_tid(t: Tuple[str, str, str]) -> revs_parser.TypRevTid:
    typ_rev_tid = revs_parser.TypRevTid()
    typ_rev_tid.typ, typ_rev_tid.rev, typ_rev_tid.tid = t
    return typ_rev_tid


class TestRevsParser(unittest.TestCase):
    # public: test cases
    def test_single_00(self):
        self.assertEqual(_typ_rev_tid(('tr', 'b', 'c')), revs_parser.parse_single_arg_rev('tr:b@c', need_tid=False))
        self.assertEqual(_typ_rev_tid(('tr', 'b', '')), revs_parser.parse_single_arg_rev('tr:b', need_tid=False))
        self.assertEqual(_typ_rev_tid(('tr', 'b', '')), revs_parser.parse_single_arg_rev('tr:b@', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', 'c')), revs_parser.parse_single_arg_rev('b@c', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', 'c')), revs_parser.parse_single_arg_rev(':b@c', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', '')), revs_parser.parse_single_arg_rev('b', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', '')), revs_parser.parse_single_arg_rev(':b', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', '')), revs_parser.parse_single_arg_rev('b@', need_tid=False))
        self.assertEqual(_typ_rev_tid(('', 'b', '')), revs_parser.parse_single_arg_rev(':b@', need_tid=False))

        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('', need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':', need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('@', need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':@', need_tid=False)

        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a;b;c", need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a:b:c", need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a@b@c", need_tid=False)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a:b@c", need_tid=False)

    def test_single_01(self):
        self.assertEqual(_typ_rev_tid(('tr', 'b', 'c')), revs_parser.parse_single_arg_rev('tr:b@c', need_tid=True))
        self.assertEqual(_typ_rev_tid(('', 'b', 'c')), revs_parser.parse_single_arg_rev('b@c', need_tid=True))
        self.assertEqual(_typ_rev_tid(('', 'b', 'c')), revs_parser.parse_single_arg_rev(':b@c', need_tid=True))

        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('tr:b', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('tr:b@', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('b', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':b', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('b@', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':b@', need_tid=True)

        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev('@', need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev(':@', need_tid=True)

        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a;b;c", need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a:b:c", need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a@b@c", need_tid=True)
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_single_arg_rev("a:b@c", need_tid=True)

    def test_property(self):
        self.assertEqual('', _typ_rev_tid(('', '', '')).rev_tid)
        self.assertEqual('b', _typ_rev_tid(('', 'b', '')).rev_tid)
        self.assertEqual('b@c', _typ_rev_tid(('', 'b', 'c')).rev_tid)
        self.assertEqual('@c', _typ_rev_tid(('', '', 'c')).rev_tid)
        self.assertEqual('b@c', _typ_rev_tid(('tr', 'b', 'c')).rev_tid)

    def test_multiple_00(self):
        self.assertEqual([_typ_rev_tid(
            ('tr', 'b', 'c')), _typ_rev_tid(('tr', 'b', 'c'))], revs_parser.parse_arg_revs('tr:b@c;tr:b@c'))
        self.assertEqual([_typ_rev_tid(
            ('tr', 'b', 'c')), _typ_rev_tid(('tr', 'b', 'c'))], revs_parser.parse_arg_revs(('tr:b@c ; tr:b@c')))
        self.assertEqual([_typ_rev_tid(('tr', 'b', 'c'))], revs_parser.parse_arg_revs('tr:b@c'))
        with self.assertRaises(MirRuntimeError):
            revs_parser.parse_arg_revs('')
