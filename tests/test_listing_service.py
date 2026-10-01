from listing_service import ListingResult, prepare_listing


class FakeClient:
    def upload(self, image, filename):
        assert filename == "shoe.jpg"
        return {"id": "img_123"}

    def background_remove(self, image, format="png"):
        assert image == "img_123"
        assert format == "png"
        return {"url": "https://cdn.example/cutout.png"}


def test_prepare_listing_hands_off_ready_asset():
    result = prepare_listing(b"pixels", "shoe.jpg", FakeClient())
    assert isinstance(result, ListingResult)
    assert result.asset["url"].endswith("cutout.png")
    assert "ready for buyer review" in result.buyer_message
