from pathlib import Path
from typing import Union

from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl, BaseModel

from app.config import settings


class Resp(BaseModel):
    code: int
    message: str
    result: Union[AnyHttpUrl, str]


def test_upload_file(client: TestClient, tmp_path, normal_user_token_headers) -> None:
    p = tmp_path / "uploaded_stuff.doc"
    with open(p, "wb") as tmp:
        tmp.write(b"content")
    with open(p, "rb") as tmp:
        files = {"file": tmp}
        r = client.post(
            f"{settings.API_V1_STR}/uploadfile/",
            headers=normal_user_token_headers,
            files=files,
        )
    assert r.status_code == 200
    j = r.json()
    Resp.validate(j)
    Path(j["result"]).unlink()
