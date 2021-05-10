SELECT COUNT(*) AS count
               FROM pragma_table_info("assignments")
               WHERE name = "valid_ip_addresses"