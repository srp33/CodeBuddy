SELECT COUNT(*) AS count
	FROM (SELECT COUNT(*) AS col_count
		FROM pragma_table_info("users"))
			WHERE col_count = 7
