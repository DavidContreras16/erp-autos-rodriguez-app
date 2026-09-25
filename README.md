# ERP Autos Rodríguez

Aplicación web para Autos Rodríguez, un negocio hondureño que compra vehículos usados en subastas de Estados Unidos, los importa y los vende. Lleva el ciclo completo de cada carro en un solo registro: la subasta, el traslado, la aduana, el taller y la venta.

Está construida sobre [Frappe](https://frappeframework.com) v16 como una app independiente. No depende de ERPNext.

**Sitio en producción:** https://devops-ar.rdtech.lat

## Qué hace

- **Un registro por vehículo.** El documento `Vehiculo` tiene una pestaña por etapa: General, Compra, Aduana, Taller y Venta.
- **Tablero Kanban por estado.** Cada carro es una tarjeta con su foto. Se arrastra de columna en columna, desde *Solicitado* hasta *Vendido*.
- **Costos calculados solos.** Al guardar, el costo total se recalcula sumando la oferta, el flete, la aduana y los repuestos.
- **Validaciones de flujo.** El sistema no deja marcar un carro como *Vendido* sin cliente y precio de venta. También avisa si pasa a *Listo para venta* sin la inspección aprobada.
- **Estado automático de la subasta.** Si la subasta se marca como ganada, el carro pasa a *Comprado*; si se pierde, pasa a *Cancelado*.
- **Dashboard** con el total de vehículos, los que están en inventario, los vendidos, la inversión en inventario y el valor de las ventas, más gráficos por estado y ventas por mes.
- **Comprobante de Venta** imprimible.
- **Dos roles:** Administrador (System Manager) y Operador.

## Modelo de datos

| DocType | Tipo | Descripción |
|---|---|---|
| `Vehiculo` | Principal | Se identifica por el VIN. Contiene toda la información del carro, organizada en pestañas. |
| `Vehiculo Pago` | Tabla hija | Pagos de la compra, con su comprobante. |
| `Vehiculo Repuesto` | Tabla hija | Repuestos usados en el taller (texto libre, cantidad y costo unitario). |
| `Vehiculo Checklist` | Tabla hija | Puntos de la inspección de calidad. |
| `Vehiculo Cotizacion` | Tabla hija | Cotizaciones que se hacen a los clientes. |
| `Proveedor` | Maestro | Casas de subasta, tramitadores, talleres, financieras y otros. |
| `Cliente` | Maestro | Compradores. |
| `Almacen` | Maestro | Ubicaciones físicas del vehículo. |

El campo **Estado** tiene 14 valores, en este orden: Solicitado, Comprado, En subasta, Cancelado, En transito, En aduana, En bodega SPS, En taller, En reparacion, Esperando repuestos, Listo para venta, En negociacion, En tramite de credito y Vendido.

La lógica de negocio está en el controller [`vehiculo.py`](erp_autos_rodriguez/autosrodriguez/doctype/vehiculo/vehiculo.py). No se usan Workflows ni Server Scripts.

## Instalación con bench

Requisitos: Frappe v16 y Python 3.14 o superior.

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/DavidContreras16/erp-autos-rodriguez-app --branch main
bench --site <sitio> install-app erp_autos_rodriguez
bench --site <sitio> migrate
```

Al migrar se crean los fixtures:

- El rol Operador.
- Las Number Cards y los gráficos del dashboard.
- El Kanban "Vehiculos - Flujo".
- La barra lateral "AutosRodriguez".

### Datos de demostración y configuración

La carpeta `erp_autos_rodriguez/provision/` tiene scripts idempotentes, que se pueden correr varias veces sin duplicar datos:

| Script | Qué hace |
|---|---|
| `setup_roles.py` | Crea el rol Operador y asigna permisos. |
| `setup_ui.py` | Formato de impresión, Kanban como vista por defecto, Number Cards, gráficos y Workspace. |
| `seed_demo.py` | Carga proveedores, almacenes, clientes y una flota de vehículos de prueba. |
| `reshape.py` | Migra una instalación antigua, con documentos por etapa, al modelo actual. |

```bash
bench --site <sitio> execute erp_autos_rodriguez.provision.setup_roles.run
bench --site <sitio> execute erp_autos_rodriguez.provision.setup_ui.all
bench --site <sitio> execute erp_autos_rodriguez.provision.seed_demo.seed   # solo en desarrollo
```

## Despliegue

En producción la app corre en contenedores, con las imágenes de [frappe_docker](https://github.com/frappe/frappe_docker): MariaDB 11.8, Redis, backend, frontend, websocket, workers y scheduler. Todo está detrás de nginx con HTTPS, en una máquina virtual de Azure. El stack lo administra Portainer.

El workflow [`.github/workflows/build.yml`](.github/workflows/build.yml) se ejecuta en cada push a `main`, o a mano desde la pestaña Actions. Hace lo siguiente:

1. Construye una imagen de Frappe `version-16` con esta app instalada, a partir del Containerfile de frappe_docker. La lista de apps entra al build como secreto (`secret-files: apps_json=apps.json`).
2. Publica la imagen en Docker Hub.
3. Llama al webhook de Portainer, que descarga la imagen nueva, recrea los contenedores y ejecuta `bench migrate`.

El workflow necesita estos secretos en el repositorio:

| Secreto | Uso |
|---|---|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub (también es el prefijo de la imagen). |
| `DOCKERHUB_TOKEN` | Token de acceso de Docker Hub. |
| `PORTAINER_WEBHOOK_URL` | URL del webhook del stack en Portainer. |

## Estructura

```
erp_autos_rodriguez/
├── autosrodriguez/
│   ├── doctype/            # Vehiculo, tablas hijas y maestros
│   ├── print_format/       # Comprobante de Venta
│   └── workspace/          # Workspace "Autos Rodriguez"
├── fixtures/               # Rol, Number Cards, gráficos, Kanban y barra lateral
├── provision/              # Scripts de configuración y datos demo
├── workspace_sidebar/
├── desktop_icon/
├── user_sidebar_cache.py   # Corrección para la barra lateral de usuarios sin rol de administrador
└── hooks.py
```

`user_sidebar_cache.py` corre al iniciar sesión (hook `on_session_creation`). Corrige un error de Frappe v16: la barra lateral del workspace no mostraba sus enlaces a los usuarios que no eran Administrator.

## Contribuir

El repositorio usa `pre-commit` para dar formato y revisar el código:

```bash
cd apps/erp_autos_rodriguez
pre-commit install
```

Las herramientas configuradas son ruff, eslint, prettier y pyupgrade.

## Autores

Lia Ramírez y David Zelaya, para el curso de DevOps.

## Licencia

MIT
