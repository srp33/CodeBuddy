SELECT COUNT(*) AS count
               FROM pragma_table_info("submissions")
               WHERE name = "pair_programming_partner_id"