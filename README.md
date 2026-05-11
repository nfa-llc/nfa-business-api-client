# NFA Commercial Python Example

Python example for managing commercial child users with an `nfa` product API key.

This is meant to model backend automation, not an end-user command line tool.
For example, when a customer signs up for your service, your backend can use
your NFA product key to create a child user and receive that child's one-time
Gexbot API key secret.

These examples call the API-key-authenticated routes:

- `GET /user/children`
- `GET /user/children/{childId}`
- `POST /user/children`
- `DELETE /user/children/{childId}`
- `POST /user/children/{childId}/key`
- `PATCH /user/children/{childId}/key`
- `DELETE /user/children/{childId}/key`
- `PATCH /user/children/keys`

## Setup

Requires Python 3.9 or newer. The example uses only the Python standard library.

```bash
cp .env.example .env
```

Keep `.env` in this directory, next to the `src/` folder:

```text
nfa-commercial-api-client/
  .env
  src/
```

Set:

```bash
export NFA_BASE_URL="https://business.gexbot.com"
export NFA_API_KEY="your_one_time_nfa_product_key_secret"
```

The API key is sent as:

```http
Authorization: Bearer <YOUR_NFA_PRODUCT_KEY>
```

## Run The Local Smoke Test

```bash
python3 src/demo.py
```

By default, `src/demo.py` only lists existing child users. That makes it safe to
run locally after you set `NFA_API_KEY`.

## Example Workflows

The demo file includes production-style functions you can adapt:

- `provision_child_for_customer(...)` creates a child user and child API key.
- `batch_provision_children(...)` creates child users for several customers.
- `rotate_child_key(...)` rotates a specific child key.
- `revoke_child_access(...)` revokes a child user's access.

Uncomment one workflow at a time in `src/demo.py` when testing creates,
rotations, or revocations.

To run the tiny create-only example:

```bash
python3 src/create_child.py
```

Secrets returned from create and rotate responses are shown once by the backend.
Store them immediately in your own secret manager.
