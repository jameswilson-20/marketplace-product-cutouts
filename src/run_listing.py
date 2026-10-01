import pathlib
import argparse
from listing_service import prepare_listing


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a listing from a local product image")
    parser.add_argument("image", type=pathlib.Path, help="path to a local product image")
    path = parser.parse_args().image
    result = prepare_listing(path.read_bytes(), path.name)
    print(result.buyer_message)
    print(result.asset)


if __name__ == "__main__":
    main()
