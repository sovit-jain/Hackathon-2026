from app.routes.jobs import _parse_required_skills


def test_parse_required_skills_handles_json_strings():
    parsed = _parse_required_skills('["Python", "SQL", "API"]')
    assert parsed == ["Python", "SQL", "API"]


def test_parse_required_skills_handles_python_list_strings():
    parsed = _parse_required_skills("['Excel', 'Support', 'Troubleshooting']")
    assert parsed == ["Excel", "Support", "Troubleshooting"]
