# Work 1 — Hadoop MapReduce (mrjob)

Processing large datasets using the MapReduce paradigm on Hadoop, implemented in Python with the **mrjob** library. The work covers two problem domains: a public movie ratings dataset and a synthetic business dataset modeled after an electric vehicle parts importer.

---

## Technology Stack

| Tool | Version | Role |
|------|---------|------|
| Python | 3.x | Implementation language |
| mrjob | latest | MapReduce abstraction over Hadoop |
| Hadoop | 2.x / 3.x | Distributed processing engine |

---

## Business Context

The business dataset represents an **electric vehicle spare parts importer and distributor** operating in Colombia. The company:

- Sources products from **multiple international suppliers**, each with their own catalog and pricing.
- Sells exclusively to **businesses, specialized workshops, and authorized distributors**.
- Manages a network of **50 warehouses** distributed across Colombian cities.
- Tracks all purchases and sales through an **electronic invoicing system**.

---

## Data Model

All business data is stored as **tab-separated (TSV) files**. These files are **not included** in the repository — generate them locally before running any script (see [Generating the Dataset](#generating-the-dataset) below).

| Table | Rows | Description |
|-------|------|-------------|
| `REPUESTO.tsv` | 100,000 | Spare parts catalog — id, SKU, name, category, brand |
| `BODEGA.tsv` | 50 | Warehouses — id, name, city, country |
| `INVENTARIO.tsv` | ~50,000 | Stock per warehouse/part — available, reserved, reorder point, avg cost |
| `PROVEEDOR.tsv` | 200 | Suppliers — id, company name, country of origin |
| `CATALOGO_PROVEEDOR.tsv` | ~50,000 | Supplier catalog — FOB price, estimated lead time per part |
| `ORDEN_COMPRA.tsv` | 5,000 | Purchase orders — order id, supplier, date, status |
| `DETALLE_ORDEN_COMPRA.tsv` | ~30,000 | Purchase order line items — quantities, agreed prices |
| `CLIENTE.tsv` | 1,000 | Customers — id, company name, segment |
| `FACTURA_VENTA.tsv` | 10,000 | Sales invoices — id, customer, UUID, date, total |
| `DETALLE_VENTA.tsv` | ~50,000 | Sales invoice line items — quantities, unit prices |

**Part categories:** Motor, Transmision, Frenos, Suspension, Electrico, Carroceria, Refrigeracion, Direccion, Neumaticos, Filtros

**Purchase order statuses:** Pendiente, Confirmada, En_transito, Recibida, Cancelada

---

## MovieLens Dataset

`u.data` is the [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/) dataset with the schema:

```
user_id   movie_id   rating   timestamp
```

Fields are tab-separated. This file is **not included** in the repository — download it from the link above and place it in this directory before running `Ej_movies.py`.

---

## Scripts

### `Ej_movies.py` — Movie Ratings Ranking (MovieLens)

Ranks all movies by their **total accumulated rating score** (sum of all ratings received), sorted from highest to lowest.

- **Input:** `u.data`
- **Map:** Emits `(movie_id, rating)` for each record.
- **Reduce 1:** Sums all ratings per movie → `(None, (total, movie_id))`.
- **Reduce 2:** Sorts movies by total rating descending.
- **Output:** `movie_id → total_rating`

---

### `Procesamiento1.py` — Parts Count by Category

Counts how many spare parts belong to each product category.

- **Input:** `REPUESTO.tsv`
- **Map:** Emits `(categoria, 1)` per row.
- **Reduce:** Sums counts per category.
- **Output:** `categoria → count`

---

### `Procesamiento2.py` — Available Stock by Warehouse

Calculates the total available inventory units stored in each warehouse.

- **Input:** `INVENTARIO.tsv`
- **Map:** Emits `(id_bodega, stock_disponible)` per row.
- **Reduce:** Sums available stock per warehouse.
- **Output:** `id_bodega → total_stock`

---

### `Procesamiento3.py` — Total Units Sold per Part

Aggregates the total quantity of each spare part sold across all sales invoices.

- **Input:** `DETALLE_VENTA.tsv`
- **Map:** Emits `(id_repuesto, cantidad)` per row.
- **Reduce:** Sums quantities per part.
- **Output:** `id_repuesto → total_sold`

---

### `Procesamiento4.py` — Purchase Orders by Status

Counts how many purchase orders exist for each order status.

- **Input:** `ORDEN_COMPRA.tsv`
- **Map:** Emits `(estado, 1)` per row.
- **Reduce:** Sums counts per status.
- **Output:** `estado → count`

---

## Generating the Dataset

Run the data generator inside the `Tablas/` folder to produce all TSV files:

```bash
cd Tablas
python generar_datos.py
```

This produces ~10 TSV files totalling roughly **245,000+ rows** of referentially consistent synthetic data.

---

## How to Run

### Locally (no Hadoop cluster needed)

```bash
pip install mrjob

python Ej_movies.py u.data
python Procesamiento1.py Tablas/REPUESTO.tsv
python Procesamiento2.py Tablas/INVENTARIO.tsv
python Procesamiento3.py Tablas/DETALLE_VENTA.tsv
python Procesamiento4.py Tablas/ORDEN_COMPRA.tsv
```

### On a Hadoop Cluster

Upload input files to HDFS first:

```bash
hdfs dfs -mkdir -p /user/root/input
hdfs dfs -put Tablas/REPUESTO.tsv /user/root/input/
hdfs dfs -put Tablas/INVENTARIO.tsv /user/root/input/
# ... repeat for all TSV files
```

Then run with the Hadoop runner:

```bash
python Ej_movies.py -r hadoop hdfs:///user/root/input/u.data
python Procesamiento1.py -r hadoop hdfs:///user/root/input/REPUESTO.tsv
python Procesamiento2.py -r hadoop hdfs:///user/root/input/INVENTARIO.tsv
python Procesamiento3.py -r hadoop hdfs:///user/root/input/DETALLE_VENTA.tsv
python Procesamiento4.py -r hadoop hdfs:///user/root/input/ORDEN_COMPRA.tsv
```

---

## File Structure

```
Trabajo_1/
├── Ej_movies.py            # MovieLens: rank movies by total rating
├── Procesamiento1.py       # Business: parts count by category
├── Procesamiento2.py       # Business: available stock by warehouse
├── Procesamiento3.py       # Business: units sold per part
├── Procesamiento4.py       # Business: purchase orders by status
└── Tablas/
    └── generar_datos.py    # Synthetic data generator (run this first)
```

> **Note:** TSV dataset files are excluded from the repository (`.gitignore`). Run `Tablas/generar_datos.py` to generate them locally.
