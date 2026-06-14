from contpress import compact_json, compact_table, drop_nulls, json_to_csv_if_tabular, shorten_keys


def test_compact_json_and_table_helpers():
    data = [{"description": "Fix bug", "priority": None}, {"description": "Ship", "priority": "high"}]

    assert compact_json({"a": 1, "b": 2}) == '{"a":1,"b":2}'
    assert drop_nulls(data)[0] == {"description": "Fix bug"}
    assert shorten_keys(data, {"description": "d"})[0]["d"] == "Fix bug"
    assert json_to_csv_if_tabular(data).startswith("description,priority")
    assert compact_table(data) == "description|priority\nFix bug|\nShip|high"
