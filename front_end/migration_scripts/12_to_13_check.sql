SELECT COUNT(*) AS count
               FROM pragma_table_info("assignments")
               WHERE name = "enable_pair_programming"