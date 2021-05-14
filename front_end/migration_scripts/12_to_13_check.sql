SELECT COUNT(*) AS count
FROM pragma_table_info("submissions")
WHERE name = "partner_id"
