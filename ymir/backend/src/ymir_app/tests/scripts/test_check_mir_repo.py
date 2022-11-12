from app import check_mir_repo_version as m


def test_generate_msg_box() -> None:
    res = m.generate_msg_box("msg")
    assert res == "\n╔═════╗\n║ msg ║\n╚═════╝"
