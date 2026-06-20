# Walmart Marketplace API — Cliente Python

Cliente Python para la API Global de Walmart Marketplace. Soporta autenticación OAuth 2.0, gestión de órdenes, inventario y precios.

## Requisitos

- Python 3.7+
- Credenciales de Seller en el [Developer Portal de Walmart](https://developer.walmart.com)

## Instalación

```bash
cd walmart_api
pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```
CLIENT_ID=tu_client_id
CLIENT_SECRET=tu_client_secret
```

## Uso

```bash
py main.py
```

## Estructura

| Archivo | Descripción |
|---|---|
| `auth.py` | Obtención y cache automático del token (renueva antes de los 15 min) |
| `client.py` | Cliente base con headers unificados por request |
| `orders.py` | Listar órdenes, obtener detalle, acknowledge, ship |
| `inventory.py` | Consultar y actualizar stock por SKU |
| `prices.py` | Actualizar precio por SKU |
| `main.py` | Ejemplo de uso de cada módulo |

## Seguridad

- Las credenciales van solo en `.env`, que está en `.gitignore`
- Nunca subir `.env` a un repositorio
