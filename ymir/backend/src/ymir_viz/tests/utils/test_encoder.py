from src.encoder import JSONEncoder
from src.swagger_models.asset_info import AssetInfo


class TestJSONEncoder:
    def test_default(self):
        data = AssetInfo(asset_id="mock_asset_id", class_ids=[1, 2, 3])
        rep = JSONEncoder().default(data)

        expected_data = {"asset_id": "mock_asset_id", "class_ids": [1, 2, 3]}

        assert expected_data == rep
