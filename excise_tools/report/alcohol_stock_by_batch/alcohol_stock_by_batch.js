frappe.query_reports["Alcohol Stock by Batch (Auditor)"] = {
  "filters": [
    {
      "fieldname": "as_on_date",
      "label": "As On Date",
      "fieldtype": "Date",
      "default": frappe.datetime.get_today(),
      "reqd": 1
    },
    {
      "fieldname": "warehouse",
      "label": "Warehouse",
      "fieldtype": "Link",
      "options": "Warehouse"
    }
  ]
}
