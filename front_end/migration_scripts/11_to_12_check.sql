SELECT COUNT(*) AS count
               FROM pragma_table_info("valid_ip_addresses")
               WHERE name = "ip_address"