from app.services.literature import format_literature_context, literature_reply, search_literature


def test_search_literature_finds_step_one():
    hits = search_literature("Step One powerless alcohol", limit=3)

    assert hits
    assert any("Step One" in hit.title for hit in hits)
    assert all(hit.source in {"Alcoholics Anonymous World Services", "Анонимные Алкоголики России / aarussia.ru"} for hit in hits)


def test_search_literature_finds_russian_downloadable_literature():
    hits = search_literature("вопросы новых членов новичок", limit=3)

    assert hits
    assert any(hit.language == "ru" for hit in hits)
    assert any("Вопросы новых членов" in hit.title for hit in hits)


def test_literature_reply_includes_source_and_title():
    reply = literature_reply("Step One powerless alcohol", lang="ru")

    assert "Нашёл опору в литературе АА" in reply
    assert "Источник: Alcoholics Anonymous World Services" in reply
    assert "https://www.aa.org/" in reply


def test_format_literature_context_is_bounded():
    hits = search_literature("resentment inventory Step Four", limit=3)
    context = format_literature_context(hits, max_chars=900)

    assert context
    assert len(context) <= 1100
    assert "Источник:" in context or "Source:" in context
