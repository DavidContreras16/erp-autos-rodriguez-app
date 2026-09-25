# ERP Autos Rodríguez

[Español](README.md) | **English**

A web application for Autos Rodríguez, a Honduran business that buys used vehicles at US auctions, imports them and sells them. It tracks each car's full life cycle in a single record: auction, shipping, customs, repair shop and sale.

It is a standalone app built on [Frappe](https://frappeframework.com) v16. It does not depend on ERPNext.

**Production site:** https://devops-ar.rdtech.lat

## Features

- **One record per vehicle.** The `Vehiculo` document has one tab per stage: General, Compra (purchase), Aduana (customs), Taller (repair shop) and Venta (sale).
- **Kanban board by status.** Each car is a card with its photo. You drag it from column to column, from *Solicitado* (requested) to *Vendido* (sold).
- **Automatic costs.** On save, the total cost is recalculated from the bid, freight, customs and spare parts.
- **Workflow validations.** A car cannot be marked *Vendido* without a customer and a sale price. The app also warns you if a car moves to *Listo para venta* (ready for sale) before its inspection is approved.
- **Automatic auction status.** When an auction is marked as won, the car moves to *Comprado* (bought). When it is lost, the car moves to *Cancelado* (cancelled).
- **Dashboard** with total vehicles, vehicles in inventory, vehicles sold, money invested in inventory and sales value, plus charts by status and sales per month.
- **Printable sales receipt** (*Comprobante de Venta*).
- **Two roles:** Administrator (System Manager) and Operador (operator).

## Data model

| DocType | Type | Description |
|---|---|---|
| `Vehiculo` | Main | Named by VIN. Holds all of the car's information, organized in tabs. |
| `Vehiculo Pago` | Child table | Purchase payments, with receipt. |
| `Vehiculo Repuesto` | Child table | Spare parts used in the repair shop (free text, quantity and unit cost). |
| `Vehiculo Checklist` | Child table | Quality inspection items. |
| `Vehiculo Cotizacion` | Child table | Quotes given to customers. |
| `Proveedor` | Master | Auction houses, customs brokers, repair shops, lenders and others. |
| `Cliente` | Master | Buyers. |
| `Almacen` | Master | Physical locations of the vehicle. |

The **Estado** (status) field has 14 values, in lifecycle order: Solicitado, Comprado, En subasta, Cancelado, En transito, En aduana, En bodega SPS, En taller, En reparacion, Esperando repuestos, Listo para venta, En negociacion, En tramite de credito and Vendido. The values are in Spanish because that is the language the business works in.

The business logic lives in the [`vehiculo.py`](erp_autos_rodriguez/autosrodriguez/doctype/vehiculo/vehiculo.py) controller. The app uses no Workflows and no Server Scripts.

## Installing with bench

Requirements: Frappe v16 and Python 3.14 or later.

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/DavidContreras16/erp-autos-rodriguez-app --branch main
bench --site <site> install-app erp_autos_rodriguez
bench --site <site> migrate
```

Migrating creates the fixtures:

- The Operador role.
- The dashboard Number Cards and charts.
- The "Vehiculos - Flujo" Kanban board.
- The "AutosRodriguez" sidebar.

### Demo data and setup

The `erp_autos_rodriguez/provision/` folder contains idempotent scripts, which you can run more than once without duplicating data:

| Script | What it does |
|---|---|
| `setup_roles.py` | Creates the Operador role and sets permissions. |
| `setup_ui.py` | Print format, Kanban as the default view, Number Cards, charts and Workspace. |
| `seed_demo.py` | Loads sample suppliers, locations, customers and a fleet of test vehicles. |
| `reshape.py` | Migrates an older install, with one document per stage, to the current model. |

```bash
bench --site <site> execute erp_autos_rodriguez.provision.setup_roles.run
bench --site <site> execute erp_autos_rodriguez.provision.setup_ui.all
bench --site <site> execute erp_autos_rodriguez.provision.seed_demo.seed   # development only
```

## Deployment

In production the app runs in containers built from the [frappe_docker](https://github.com/frappe/frappe_docker) images: MariaDB 11.8, Redis, backend, frontend, websocket, workers and scheduler. Everything sits behind nginx with HTTPS on an Azure virtual machine, and Portainer manages the stack.

The [`.github/workflows/build.yml`](.github/workflows/build.yml) workflow runs on every push to `main`, or manually from the Actions tab. It does the following:

1. Builds a Frappe `version-16` image with this app installed, using the frappe_docker Containerfile. The app list reaches the build as a secret (`secret-files: apps_json=apps.json`).
2. Pushes the image to Docker Hub.
3. Calls the Portainer webhook, which pulls the new image, recreates the containers and runs `bench migrate`.

The workflow needs these repository secrets:

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub user (also used as the image prefix). |
| `DOCKERHUB_TOKEN` | Docker Hub access token. |
| `PORTAINER_WEBHOOK_URL` | Webhook URL of the Portainer stack. |

## Project layout

```
erp_autos_rodriguez/
├── autosrodriguez/
│   ├── doctype/            # Vehiculo, child tables and masters
│   ├── print_format/       # Comprobante de Venta (sales receipt)
│   └── workspace/          # "Autos Rodriguez" workspace
├── fixtures/               # Role, Number Cards, charts, Kanban and sidebar
├── provision/              # Setup scripts and demo data
├── workspace_sidebar/
├── desktop_icon/
├── user_sidebar_cache.py   # Sidebar fix for non-admin users
└── hooks.py
```

`user_sidebar_cache.py` runs at login (the `on_session_creation` hook). It fixes a Frappe v16 bug where the workspace sidebar showed no links to users other than Administrator.

## Contributing

The repository uses `pre-commit` to format and lint the code:

```bash
cd apps/erp_autos_rodriguez
pre-commit install
```

The configured tools are ruff, eslint, prettier and pyupgrade.

## Authors

Lia Ramírez and David Zelaya, for the DevOps course.

## License

MIT
