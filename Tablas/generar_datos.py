"""
Generador de datos CSV para el modelo de inventario/ventas de repuestos.
Produce archivos TSV (separados por TAB) con integridad referencial garantizada.
Tabla principal REPUESTO: ~100,000 registros.
"""

import csv
import random
import uuid
from datetime import date, timedelta
from itertools import product as iterproduct

# -- Semilla reproducible ------------------------------------------------------
random.seed(42)

# -- Parametros de volumen -----------------------------------------------------
N_REPUESTO          = 100_000
N_BODEGA            = 50
N_PROVEEDOR         = 200
N_CLIENTE           = 1_000
N_ORDEN_COMPRA      = 5_000
N_FACTURA_VENTA     = 10_000
# INVENTARIO y CATALOGO_PROVEEDOR se generan por combinaciones unicas controladas
MAX_INV_POR_BODEGA  = 2_000   # max repuestos distintos por bodega  -> <=100 k filas
MAX_CAT_POR_PROV    = 500     # max repuestos distintos por proveedor

# -- Datos de referencia -------------------------------------------------------
CATEGORIAS = ["Motor", "Transmision", "Frenos", "Suspension", "Electrico",
               "Carroceria", "Refrigeracion", "Direccion", "Neumaticos", "Filtros"]
MARCAS     = ["Bosch", "SKF", "Gates", "Valeo", "NGK", "Mahle", "Monroe",
               "Brembo", "Denso", "Mann-Filter", "Continental", "FAG"]
CIUDADES   = ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena",
               "Bucaramanga", "Pereira", "Manizales", "Cucuta", "Ibague"]
PAISES     = ["Colombia", "Mexico", "Brasil", "Argentina", "Chile",
               "Peru", "Ecuador", "Venezuela", "Panama", "Costa Rica"]
SEGMENTOS  = ["Retail", "Mayorista", "Industrial", "Taller", "Flotas"]
ESTADOS_OC = ["Pendiente", "Confirmada", "En_transito", "Recibida", "Cancelada"]

# -- Helpers -------------------------------------------------------------------
def rand_date(start_year=2020, end_year=2025):
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def write_tsv(filename, fieldnames, rows):
    """Escribe lista de dicts a un archivo TSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  OK  {filename}  ({len(rows):,} filas)")

# =============================================================================
# 1. REPUESTO  (tabla principal - 100 k registros)
# =============================================================================
print("Generando REPUESTO ...")
repuestos = []
for i in range(1, N_REPUESTO + 1):
    cat   = random.choice(CATEGORIAS)
    marca = random.choice(MARCAS)
    repuestos.append({
        "id_repuesto": i,
        "sku_interno": f"SKU-{i:07d}",
        "nombre":      f"{cat} {marca} #{i}",
        "categoria":   cat,
        "marca":       marca,
    })
write_tsv("REPUESTO.tsv", ["id_repuesto","sku_interno","nombre","categoria","marca"], repuestos)
repuesto_ids = [r["id_repuesto"] for r in repuestos]

# =============================================================================
# 2. BODEGA
# =============================================================================
print("Generando BODEGA ...")
bodegas = []
for i in range(1, N_BODEGA + 1):
    bodegas.append({
        "id_bodega": i,
        "nombre":    f"Bodega-{i:03d}",
        "ciudad":    random.choice(CIUDADES),
        "pais":      "Colombia",
    })
write_tsv("BODEGA.tsv", ["id_bodega","nombre","ciudad","pais"], bodegas)
bodega_ids = [b["id_bodega"] for b in bodegas]

# =============================================================================
# 3. INVENTARIO  (PK compuesta: id_bodega + id_repuesto  -> sin duplicados)
# =============================================================================
print("Generando INVENTARIO ...")
inventario = []
used_inv: set = set()

# Por cada bodega asignamos un subconjunto aleatorio de repuestos
for bid in bodega_ids:
    n = random.randint(500, MAX_INV_POR_BODEGA)
    sample = random.sample(repuesto_ids, min(n, len(repuesto_ids)))
    for rid in sample:
        key = (bid, rid)
        if key in used_inv:
            continue
        used_inv.add(key)
        stock_disp = random.randint(0, 500)
        stock_res  = random.randint(0, min(stock_disp, 100))
        inventario.append({
            "id_bodega":        bid,
            "id_repuesto":      rid,
            "stock_disponible": stock_disp,
            "stock_reservado":  stock_res,
            "punto_reorden":    random.randint(5, 50),
            "costo_promedio":   round(random.uniform(5.0, 2000.0), 2),
        })

write_tsv("INVENTARIO.tsv",
          ["id_bodega","id_repuesto","stock_disponible","stock_reservado","punto_reorden","costo_promedio"],
          inventario)

# Indice rapido de pares validos (bodega, repuesto) para usarlo despues
inv_pairs = list(used_inv)          # [(id_bodega, id_repuesto), ...]

# =============================================================================
# 4. PROVEEDOR
# =============================================================================
print("Generando PROVEEDOR ...")
proveedores = []
for i in range(1, N_PROVEEDOR + 1):
    proveedores.append({
        "id_proveedor": i,
        "razon_social": f"Proveedor S.A. #{i:04d}",
        "pais_origen":  random.choice(PAISES),
    })
write_tsv("PROVEEDOR.tsv", ["id_proveedor","razon_social","pais_origen"], proveedores)
proveedor_ids = [p["id_proveedor"] for p in proveedores]

# =============================================================================
# 5. CATALOGO_PROVEEDOR  (PK compuesta: id_proveedor + id_repuesto -> sin dup.)
# =============================================================================
print("Generando CATALOGO_PROVEEDOR ...")
catalogo = []
used_cat: set = set()

for pid in proveedor_ids:
    n = random.randint(10, MAX_CAT_POR_PROV)
    sample = random.sample(repuesto_ids, min(n, len(repuesto_ids)))
    for rid in sample:
        key = (pid, rid)
        if key in used_cat:
            continue
        used_cat.add(key)
        catalogo.append({
            "id_proveedor":       pid,
            "id_repuesto":        rid,
            "ultimo_costo_fob":   round(random.uniform(2.0, 1500.0), 2),
            "lead_time_estimado": random.randint(7, 90),
        })

write_tsv("CATALOGO_PROVEEDOR.tsv",
          ["id_proveedor","id_repuesto","ultimo_costo_fob","lead_time_estimado"],
          catalogo)

# Pares validos para usar en DETALLE_ORDEN_COMPRA
cat_pairs_by_prov: dict = {}
for pid, rid in used_cat:
    cat_pairs_by_prov.setdefault(pid, []).append(rid)

# =============================================================================
# 6. ORDEN_COMPRA
# =============================================================================
print("Generando ORDEN_COMPRA ...")
ordenes = []
for i in range(1, N_ORDEN_COMPRA + 1):
    ordenes.append({
        "id_orden":      i,
        "id_proveedor":  random.choice(proveedor_ids),
        "fecha_pedido":  rand_date(),
        "estado":        random.choice(ESTADOS_OC),
    })
write_tsv("ORDEN_COMPRA.tsv",
          ["id_orden","id_proveedor","fecha_pedido","estado"],
          ordenes)
orden_ids           = [o["id_orden"]     for o in ordenes]
orden_proveedor_map = {o["id_orden"]: o["id_proveedor"] for o in ordenes}

# =============================================================================
# 7. DETALLE_ORDEN_COMPRA
#    Restriccion: id_repuesto debe existir en CATALOGO_PROVEEDOR del proveedor
#    asociado a la orden; y (id_bodega, id_repuesto) debe existir en INVENTARIO.
# =============================================================================
print("Generando DETALLE_ORDEN_COMPRA ...")
# Indice inverso: repuesto -> bodegas donde existe en inventario
rep_to_bodegas: dict = {}
for bid, rid in inv_pairs:
    rep_to_bodegas.setdefault(rid, []).append(bid)

detalles_oc = []
pk_doc = 1
lineas_por_orden = 3   # promedio de lineas por orden

for oid in orden_ids:
    pid    = orden_proveedor_map[oid]
    rids   = cat_pairs_by_prov.get(pid, [])
    if not rids:
        continue
    n_lineas = random.randint(1, lineas_por_orden * 2)
    sample   = random.sample(rids, min(n_lineas, len(rids)))
    for rid in sample:
        bids = rep_to_bodegas.get(rid, [])
        if not bids:
            continue
        bid = random.choice(bids)
        detalles_oc.append({
            "id_detalle_oc":   pk_doc,
            "id_orden":        oid,
            "id_bodega":       bid,
            "id_repuesto":     rid,
            "cantidad_pedida": random.randint(1, 200),
            "precio_pactado":  round(random.uniform(2.0, 1500.0), 2),
        })
        pk_doc += 1

write_tsv("DETALLE_ORDEN_COMPRA.tsv",
          ["id_detalle_oc","id_orden","id_bodega","id_repuesto","cantidad_pedida","precio_pactado"],
          detalles_oc)

# =============================================================================
# 8. CLIENTE
# =============================================================================
print("Generando CLIENTE ...")
clientes = []
for i in range(1, N_CLIENTE + 1):
    clientes.append({
        "id_cliente":  i,
        "razon_social": f"Cliente S.A.S #{i:05d}",
        "segmento":    random.choice(SEGMENTOS),
    })
write_tsv("CLIENTE.tsv", ["id_cliente","razon_social","segmento"], clientes)
cliente_ids = [c["id_cliente"] for c in clientes]

# =============================================================================
# 9. FACTURA_VENTA
# =============================================================================
print("Generando FACTURA_VENTA ...")
facturas = []
for i in range(1, N_FACTURA_VENTA + 1):
    facturas.append({
        "id_factura":      i,
        "id_cliente":      random.choice(cliente_ids),
        "uuid_electronico": str(uuid.uuid4()),
        "fecha_emision":   rand_date(),
        "total_venta":     0.0,   # se recalcula al generar detalles
    })

# --- Construir detalles primero, luego actualizar totales --------------------
print("Generando DETALLE_VENTA ...")
detalles_venta   = []
factura_total    = {f["id_factura"]: 0.0 for f in facturas}
pk_dv            = 1
lineas_por_fac   = 5

for fac in facturas:
    fid      = fac["id_factura"]
    n_lineas = random.randint(1, lineas_por_fac * 2)
    sample   = random.sample(inv_pairs, min(n_lineas, len(inv_pairs)))
    for (bid, rid) in sample:
        cantidad = random.randint(1, 20)
        precio   = round(random.uniform(10.0, 3000.0), 2)
        detalles_venta.append({
            "id_detalle_venta": pk_dv,
            "id_factura":       fid,
            "id_bodega":        bid,
            "id_repuesto":      rid,
            "cantidad":         cantidad,
            "precio_unitario":  precio,
        })
        factura_total[fid] += round(cantidad * precio, 2)
        pk_dv += 1

# Actualizar totales en facturas
for fac in facturas:
    fac["total_venta"] = round(factura_total[fac["id_factura"]], 2)

write_tsv("FACTURA_VENTA.tsv",
          ["id_factura","id_cliente","uuid_electronico","fecha_emision","total_venta"],
          facturas)
write_tsv("DETALLE_VENTA.tsv",
          ["id_detalle_venta","id_factura","id_bodega","id_repuesto","cantidad","precio_unitario"],
          detalles_venta)

# =============================================================================
# Resumen final
# =============================================================================
print("\n--- RESUMEN --------------------------------------------------------")
print(f"  REPUESTO              : {len(repuestos):>10,} filas  <- tabla principal")
print(f"  BODEGA                : {len(bodegas):>10,} filas")
print(f"  INVENTARIO            : {len(inventario):>10,} filas  (PK compuesta unica)")
print(f"  PROVEEDOR             : {len(proveedores):>10,} filas")
print(f"  CATALOGO_PROVEEDOR    : {len(catalogo):>10,} filas  (PK compuesta unica)")
print(f"  ORDEN_COMPRA          : {len(ordenes):>10,} filas")
print(f"  DETALLE_ORDEN_COMPRA  : {len(detalles_oc):>10,} filas")
print(f"  CLIENTE               : {len(clientes):>10,} filas")
print(f"  FACTURA_VENTA         : {len(facturas):>10,} filas")
print(f"  DETALLE_VENTA         : {len(detalles_venta):>10,} filas")
total = (len(repuestos) + len(bodegas) + len(inventario) + len(proveedores) +
         len(catalogo)  + len(ordenes) + len(detalles_oc) + len(clientes)   +
         len(facturas)  + len(detalles_venta))
print(f"  {'TOTAL':22}: {total:>10,} filas")
print("--------------------------------------------------------------------")
print("  Todos los archivos generados como TSV (separados por TAB).")
