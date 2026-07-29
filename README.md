# NFA Commercial Python Example

This repository contains a Python example for the GEXBOT commercial keybundle API.
It models backend automation.
It is not an end-user command-line application.

A commercial customer uses an `nfa` product API key to manage child seats.
Each child can have one current API key.
Every child key uses the `custom` integration.
A child tier can be `classic`, `state`, or `orderflow`.
Keybundle children do not receive Quant or WebSocket access.

## Supported API operations

The client supports these API-key-authenticated routes:

```text
GET    /user/children
GET    /user/children/{childId}
POST   /user/children
PATCH  /user/children/{childId}/subscription
DELETE /user/children/{childId}
POST   /user/children/{childId}/key
PATCH  /user/children/{childId}/key
DELETE /user/children/{childId}/key
PATCH  /user/children/keys
GET    /user/commercial-billing?month=YYYY-MM
```

`POST /user/children` creates one child and one custom API key.
The response contains the API key secret once.
Store the secret immediately.

`POST /user/children/{childId}/key` creates a key only when the child is keyless.
Revoking a key does not delete the child.
A keyless child remains an active billable seat.
Deleting the child stops future seat billing.

The contract controls allowed products, allowed child tiers, per-product key limits, and the total key limit.
The API returns an error when an operation exceeds the contract.

This repository does not implement server batch operations.
Call the individual operations separately.
Treat each successful mutation as final if a later request fails.

## Setup

Python 3.9 or newer is required.
The example uses only the Python standard library.

Copy the environment file:

```bash
cp .env.example .env
```

Set the API key in `.env`:

```text
NFA_API_KEY=your_nfa_product_key_secret
```

The client sends all requests to this public endpoint:

```text
https://business.gexbot.com
```

The client sends the key in this header:

```http
Authorization: Bearer <YOUR_NFA_PRODUCT_KEY>
```

## Run the safe smoke test

```bash
python3 src/demo.py
```

The default demo only lists existing children.
It does not create, rotate, or revoke a key.

## Example workflows

`src/demo.py` contains examples for these workflows:

- Create a child at an explicit tier.
- Change a child tier.
- Rotate a child key.
- Revoke a child by deleting the child account.
- Query current or historical billing.

Uncomment one workflow at a time.

Run the small create-only example with:

```bash
python3 src/create_child.py
```

The checked-in OpenAPI file describes the same public routes and request constraints.
