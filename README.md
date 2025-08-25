# facturx-gen

Simple microservice to build minimal Factur-X (BASIC profile) XML invoices from structured JSON.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the service:

```bash
uvicorn app.main:app --reload
```

POST invoice data to `/generate_facturx` to receive Factur-X XML.
