# Demo Shop: shopping cart app for Robot Framework demos

A small shopping cart web app built as a target for live test automation demos.
It is intentionally simple, ships with seed data, and every element a test needs
has a stable `id`.

| Layer    | Tech                    | Container image                  |
|----------|-------------------------|----------------------------------|
| Frontend | React 18 (Vite) + nginx | `localhost/shopcart-frontend:1.0` |
| Backend  | FastAPI (Python 3.12)   | `localhost/shopcart-backend:1.0`  |
| Database | MongoDB 7               | `docker.io/library/mongo:7.0`     |
| SFTP     | OpenSSH (atmoz/sftp)    | `localhost/shopcart-sftp:1.0`     |

```
 browser ──► frontend (nginx :80) ──/api──► backend (FastAPI :8000) ──► mongo (:27017)
                                                 │
 sftp client ──► sftp (:22) ◄────── reads CSV ───┘   (admin clicks "Import catalog")
```

## Features

**Admin** (`admin / admin123`)
- Catalog page: add, edit and delete products (SKU, name, price, description).
- SFTP ingestion page: pick a CSV that was uploaded to the SFTP server and import it.
  Rows are upserted by SKU; invalid rows are rejected and listed with their line number.
  "Replace catalog" also removes products that are not in the file.
- "Reset demo data" restores the 6 sample products and empties all carts.

**User** (`user / user123`, `user2 / user123`)
- Browse and search the catalog, choose a quantity, add to cart.
- Cart page: change quantities, remove items, empty the cart, see the total.
- Each user has their own cart, stored in MongoDB.

Roles are enforced by the API too: a user gets `403` on admin endpoints and vice versa.

## Run it on kind with Podman Desktop

### 0. Prerequisites

- [Podman Desktop](https://podman-desktop.io) with a running Podman machine.
  On macOS and Windows, kind needs a **rootful** machine
  (Settings → Resources → Podman machine → Edit → Machine with root privileges).
- `kind` and `kubectl` on your PATH (Podman Desktop can install both:
  Settings → CLI Tools). Run all commands below from the repository root.

### 1. Create the cluster

The provided config maps the web app to **http://localhost:8080** and SFTP to **localhost:2222**:

```bash
KIND_EXPERIMENTAL_PROVIDER=podman kind create cluster --config kind/kind-config.yaml
kubectl cluster-info --context kind-shopcart
```

> Already created a cluster from the Podman Desktop UI? That works too. Use its name
> in step 3 (`CLUSTER=kind-cluster`, or whatever you named it) and see
> [Accessing the app without the port mappings](#accessing-the-app-without-the-port-mappings).

### 2. Build the images

```bash
./scripts/build-images.sh
```

This runs `podman build -t localhost/shopcart-<component>:1.0 -f <component>/Containerfile <component>`
for `backend`, `frontend` and `sftp`.

### 3. Load the images into kind

kind cannot pull from podman's local image store, so the images are saved to tar files and loaded:

```bash
./scripts/load-images.sh                 # cluster named "shopcart"
CLUSTER=kind-cluster ./scripts/load-images.sh   # cluster created from the Podman Desktop UI
```

Per image this is `podman save -o img.tar <image>` then `kind load image-archive img.tar --name <cluster>`.
(In Podman Desktop you can also right-click an image → **Push image to Kind cluster**.)

### 4. Deploy

```bash
./scripts/deploy.sh
```

This runs `kubectl apply -k k8s`, waits for the four deployments, and prints the pods and services.
Open **http://localhost:8080** and log in.

### 5. Upload a catalog through SFTP

Three sample files are already on the SFTP server when it starts (from `sample-data/`):

| File                         | What it shows                                            |
|------------------------------|----------------------------------------------------------|
| `catalog.csv`                | 10 products, the "full" catalog                          |
| `catalog-price-update.csv`   | changes 2 prices and adds 1 product                      |
| `catalog-with-errors.csv`    | 2 valid rows and 5 invalid ones (missing SKU, bad price, duplicate) |

To upload your own file (password `catalog123`):

```bash
./scripts/upload-catalog.sh sample-data/catalog.csv
# or by hand:
sftp -P 2222 catalog@localhost
sftp> put my-catalog.csv upload/
```

Any SFTP client works (FileZilla, WinSCP): host `localhost`, port `2222`, user `catalog`,
password `catalog123`, folder `upload`. Then, as admin, open **SFTP ingestion**, press
**Refresh list**, pick the file and press **Import catalog**.

CSV format: a header row with `sku,name,price,description` (description optional), UTF-8.
SKU: letters, digits, `-` or `_`. Price: a number greater than 0.

### Updating after a code change

```bash
./scripts/build-images.sh && ./scripts/load-images.sh && ./scripts/deploy.sh
```

### Accessing the app without the port mappings

If the cluster was not created with `kind/kind-config.yaml`, use port-forwarding (keep the terminals open):

```bash
kubectl -n shopcart port-forward svc/frontend 8080:80
kubectl -n shopcart port-forward svc/sftp 2222:22
```

Or, if you enabled the ingress controller when creating the cluster in Podman Desktop,
`kubectl apply -f k8s/optional/ingress.yaml` and open the HTTP port Podman Desktop shows (default http://localhost:9090).

### Clean up

```bash
./scripts/teardown.sh            # delete the app (namespace shopcart)
./scripts/teardown.sh --cluster  # also delete the kind cluster
```

## Run it without Kubernetes (quick check)

```bash
podman compose up --build     # or: docker compose up --build
```

Same ports: web on http://localhost:8080, SFTP on localhost:2222.

## Writing tests against it

Every page has `#page-title` and a single feedback area `#flash-message` (text in `#flash-text`,
with `data-type` = `success`, `warning` or `error`). Ids that include a SKU use the SKU as-is,
for example `add-to-cart-MUG-001`.

| Page | URL | Key element ids |
|------|-----|-----------------|
| Login | `/login` | `username`, `password`, `login-button`, `login-error` |
| Header | all | `current-user`, `current-role`, `logout-button`, `nav-shop`, `nav-cart`, `cart-count`, `nav-products`, `nav-ingestion` |
| Shop (user) | `/shop` | `search-input`, `product-table`, `product-row-<SKU>`, `product-name-<SKU>`, `product-price-<SKU>`, `qty-<SKU>`, `add-to-cart-<SKU>`, `no-products` |
| Cart (user) | `/cart` | `cart-table`, `cart-row-<SKU>`, `cart-qty-<SKU>`, `update-qty-<SKU>`, `cart-subtotal-<SKU>`, `remove-<SKU>`, `clear-cart`, `cart-item-count`, `cart-total`, `cart-empty` |
| Catalog (admin) | `/admin/products` | `add-product-button`, `product-count`, `admin-row-<SKU>`, `edit-<SKU>`, `delete-<SKU>`, `confirm-yes`, `confirm-no` |
| Product form | dialog | `product-sku`, `product-name`, `product-price`, `product-description`, `save-product`, `cancel-product`, `product-form-error` |
| Ingestion (admin) | `/admin/ingestion` | `ingest-file`, `refresh-files`, `ingest-replace`, `ingest-button`, `reset-demo-button`, `ingest-result`, `ingest-created`, `ingest-updated`, `ingest-deleted`, `ingest-rejected`, `ingest-error-line-<N>`, `ingestion-history` |

Prices are shown as `$9.50`. Rows also carry `data-sku="<SKU>"`.

The REST API has interactive docs at http://localhost:8080/api/docs. Useful endpoints for test setup: `POST /api/auth/login`, `POST /api/admin/reset` (admin token).

## Local development

```bash
# backend (needs a MongoDB on localhost:27017, e.g. podman run -p 27017:27017 mongo:7.0)
cd backend && pip install -r requirements-dev.txt
pytest                              # API tests use an in-memory mongomock database
uvicorn app.main:app --reload       # http://localhost:8000/api/docs

# frontend (proxies /api to localhost:8000)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

## Configuration

Backend settings are environment variables (see `backend/app/config.py`); in Kubernetes they come
from `k8s/secrets.yaml` and `k8s/backend.yaml`. The demo credentials are deliberately simple:
change `JWT_SECRET`, the SFTP password and `SEED_USERS` for anything beyond a local demo.
If you change `SFTP_USER`, also change the upload mount path in `k8s/sftp.yaml` (`/home/<user>/upload`).

## Project layout

```
backend/     FastAPI app (app/), API tests (tests/), Containerfile
frontend/    React app (src/), nginx config, Containerfile
sftp/        SFTP image that seeds the sample CSV files on start
sample-data/ example catalog files
k8s/         Kubernetes manifests (kubectl apply -k k8s)
kind/        kind cluster config with port mappings
scripts/     build, load, deploy, upload and teardown helpers
compose.yaml run everything with podman compose
```
