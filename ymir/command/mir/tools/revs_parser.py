from typing import List
from mir.tools.code import MirCode

from mir.tools.errors import MirRuntimeError


class TypRevTid:
    __slots__ = ("typ", "rev", "tid")

    def __init__(self, typ: str = '', rev: str = '', tid: str = '') -> None:
        self.typ = typ
        self.rev = rev
        self.tid = tid

    def __repr__(self) -> str:
        return f"(t: {self.typ}, r: {self.rev}, t: {self.tid})"

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TypRevTid):
            return self.typ == o.typ and self.rev == o.rev and self.tid == o.tid
        elif isinstance(o, tuple):
            return self.typ == o[0] and self.rev == o[1] and self.tid == o[2]
        else:
            return False

    @property
    def rev_tid(self) -> str:
        return join_rev_tid(self.rev, self.tid)

    @property
    def typ_rev_tid(self) -> str:
        return f"{self.typ}:{self.rev_tid}" if self.typ else self.rev_tid


# public: parse methods
def parse_arg_revs(src_revs: str) -> List[TypRevTid]:
    typ_rev_tids: List[TypRevTid] = []
    if not src_revs:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty src or dst revs')

    comments = src_revs.split(";")
    for single_src_rev in comments:
        single_src_rev = single_src_rev.strip()
        if not single_src_rev:
            continue
        typ_rev_tids.append(__parse_single_arg_rev(single_src_rev))
    return typ_rev_tids


def parse_single_arg_rev(src_rev: str, need_tid: bool) -> TypRevTid:
    if ";" in src_rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"src or dst rev not single: {src_rev}")

    typ_rev_tid = __parse_single_arg_rev(src_rev)
    if need_tid and not typ_rev_tid.tid:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"src or dst rev have no tid: {src_rev}")
    return typ_rev_tid


def join_rev_tid(rev: str, tid: str) -> str:
    return f"{rev}@{tid}" if tid else rev


# private: parse methods
def __parse_single_arg_rev(src_rev: str) -> TypRevTid:
    typ_rev_tid = TypRevTid()

    if not src_rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message='empty src or dst rev')

    # parse typ and rev_and_tid
    contents = src_rev.split(':')
    if len(contents) > 2:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"invalid arg: {src_rev}")
    rev_and_tid = ''
    if len(contents) == 1:
        # rev, rev@tid or @tid
        rev_and_tid = contents[0]
    elif len(contents) == 2:
        # typ:rev, typ:rev@tid or :rev@tid
        typ_rev_tid.typ = contents[0]
        rev_and_tid = contents[1]

    # parse rev and tid
    contents = rev_and_tid.split('@')
    if len(contents) > 2:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS, error_message=f"invalid arg: {src_rev}")
    if len(contents) == 1:
        # rev
        typ_rev_tid.rev = contents[0]
    elif len(contents) == 2:
        # rev or rev@tid
        typ_rev_tid.rev = contents[0]
        typ_rev_tid.tid = contents[1]

    if not typ_rev_tid.rev:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"src or dst rev have no rev: {src_rev}")
    if typ_rev_tid.typ and typ_rev_tid.typ not in {"tr", "va", "te"}:
        raise MirRuntimeError(error_code=MirCode.RC_CMD_INVALID_ARGS,
                              error_message=f"invalid typ in src or dst rev: {src_rev}")

    return typ_rev_tid
