import frappe
from frappe.utils import flt

ITEM_VOLUME_FIELD = "custom_volume"
ITEM_UOM_FIELD = "custom_unit_of_measurement"
ITEM_TARIFF_FIELD = "custom_tariff_number"

def _to_liters_per_unit(volume_value):
    if volume_value is None:
        return 0.0
    try:
        v = float(str(volume_value).strip())
    except Exception:
        return 0.0
    return v / 1000.0 if v > 10 else v

def execute(filters=None):
    filters = filters or {}
    as_on_date = filters.get("as_on_date")
    warehouse = filters.get("warehouse")

    columns = [
        {"label":"Item Code","fieldname":"item_code","fieldtype":"Link","options":"Item","width":150},
        {"label":"Item Name","fieldname":"item_name","fieldtype":"Data","width":200},
        {"label":"Batch No","fieldname":"batch_no","fieldtype":"Link","options":"Batch","width":140},
        {"label":"Warehouse","fieldname":"warehouse","fieldtype":"Link","options":"Warehouse","width":160},
        {"label":"Qty","fieldname":"qty","fieldtype":"Float","precision":3,"width":100},
        {"label":"Liters","fieldname":"liters","fieldtype":"Float","precision":3,"width":110},
        {"label":"Unit of Measurement","fieldname":"uom_custom","fieldtype":"Data","width":200},
        {"label":"Tariff Number","fieldname":"tariff_number","fieldtype":"Data","width":180}
    ]

    conditions = ["sle.is_cancelled = 0"]
    params = {}
    if as_on_date:
        conditions.append("sle.posting_date <= %(as_on_date)s")
        params["as_on_date"] = as_on_date
    if warehouse:
        conditions.append("sle.warehouse = %(warehouse)s")
        params["warehouse"] = warehouse
    cond_sql = " AND ".join(conditions)

    rows = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            i.item_name,
            sle.batch_no,
            sle.warehouse,
            SUM(COALESCE(sle.actual_qty,0)) AS qty,
            COALESCE(i.`{ITEM_VOLUME_FIELD}`, 0) AS volume_value,
            COALESCE(i.`{ITEM_UOM_FIELD}`, "") AS uom_custom,
            COALESCE(i.`{ITEM_TARIFF_FIELD}`, "") AS tariff_number
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        WHERE {cond_sql}
        GROUP BY sle.item_code, i.item_name, sle.batch_no, sle.warehouse,
                 i.`{ITEM_VOLUME_FIELD}`, i.`{ITEM_UOM_FIELD}`, i.`{ITEM_TARIFF_FIELD}`
        HAVING ABS(SUM(COALESCE(sle.actual_qty,0))) > 0.0001
        ORDER BY sle.item_code, sle.batch_no, sle.warehouse
    """, params, as_dict=True)

    data = []
    for r in rows:
        liters_per_unit = _to_liters_per_unit(r.volume_value)
        liters = flt(r.qty) * liters_per_unit
        data.append({
            "item_code": r.item_code,
            "item_name": r.item_name,
            "batch_no": r.batch_no,
            "warehouse": r.warehouse,
            "qty": flt(r.qty),
            "liters": flt(liters),
            "uom_custom": r.uom_custom,
            "tariff_number": r.tariff_number
        })

    return columns, data
