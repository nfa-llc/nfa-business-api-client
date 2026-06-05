# NFA Business API Python Example

Reference Python client for commercial partners using the NFA Business API.

Use your business key to manage child users and commercial API keys from your
own backend. For example, when a customer signs up for your service, your
backend can create a child user and receive that child's one-time Gexbot API key
secret.

Do not expose your business key in browsers, mobile apps, desktop plugins, or
other customer-controlled environments.

## Endpoint Reference

For the structured endpoint layout, request bodies, and response schemas, see
[`business-prod-business.yaml`](business-prod-business.yaml). This README shows
the practical Python usage for the same API surface.

The example client calls these API-key-authenticated business routes:

- `GET /user/children`
- `GET /user/children/{childId}`
- `POST /user/children`
- `DELETE /user/children/{childId}`
- `POST /user/children/{childId}/key`
- `PATCH /user/children/{childId}/key`
- `DELETE /user/children/{childId}/key`

## Setup

Requires Python 3.9 or newer. This repo uses only the Python standard library.

```bash
cp .env.example .env
```

Keep `.env` in this directory, next to the `src/` folder:

```text
nfa-business-api-client/
  .env
  src/
```

Set:

```bash
export NFA_BASE_URL="https://business.gexbot.com"
export NFA_API_KEY="your_business_key_secret"
```

Keep `NFA_BASE_URL` at the host root. The Python client adds each `/user` route
path for you.

Requests authenticate with your business key:

```http
Authorization: Bearer <YOUR_BUSINESS_KEY>
```

## Check Your Access

```bash
python3 src/demo.py
```

By default, `src/demo.py` only lists existing child users. It does not create,
rotate, or revoke anything, so it is the safest first command after setting
`NFA_API_KEY`.

## Example Workflows

Use `src/demo.py` as the starting point for backend automation:

- `provision_child_for_customer(...)` creates a child user and child API key.
- `batch_provision_children(...)` creates child users for several customers.
- `rotate_child_key(...)` rotates a specific child key.
- `revoke_child_access(...)` revokes a child user's access.

Uncomment one workflow at a time when testing actions that create, rotate, or
revoke access.

To create one child user and print the response:

```bash
python3 src/create_child.py
```

Secrets returned from create and rotate responses are shown once. Store them
immediately in your own secret manager, along with the returned `child_id` and
API key `id`; rotations and revocations need those identifiers later.
