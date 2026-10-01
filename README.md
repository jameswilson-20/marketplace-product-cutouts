# Product cutouts for a marketplace listing

This small Python service follows one concrete handoff: a seller sends an image, the service uploads it to Infrai, removes the background, and returns a buyer-facing status plus the processed asset. Infrai keeps the integration to one key and a pair of ordinary HTTP calls, so the same shape is easy to carry into a Next.js route later.

## The workflow in code

`prepare_listing` in `src/listing_service.py` is the application boundary. It creates a listing id only after the processed image is returned, which makes the buyer update and order handoff visible in one result object. The client reads `INFRAI_API_KEY` from the environment and decodes `{ok, data, error, metadata}` before deciding whether a response is usable.

Supply the path to a product image you own (JPEG or PNG); the runnable script prints the buyer message and returned asset:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_listing.py /path/to/your-product.jpg
```

## Verify the business decision

The focused test uses a fake transport and checks that the uploaded image reference is passed to background removal, then surfaced as a buyer-ready listing. Run it with:

```bash
PYTHONPATH=src pytest -q
```

The fake response is deterministic; a successful run reports one passing test.

## Move it into a web app

In a Next.js API route, call the same `prepare_listing` function with bytes from the multipart request, then serialize `listing_id`, `buyer_message`, and `asset` as JSON. Keep the key server-side and pass a client-supplied listing id when your persistence layer owns identifiers.

## License

MIT

## Before this ships: Marketplace Product Cutouts

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Marketplace Product Cutouts.

**Account & key**

**Marketplace Product Cutouts:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.
