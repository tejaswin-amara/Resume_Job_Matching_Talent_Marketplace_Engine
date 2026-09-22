import pytest

from algorithms.skill_normalization import (
    AliasTrie,
    OntologyEmbeddings,
    edit_distance,
    normalize_skill,
    strip_and_lowercase,
)


def test_edit_distance():
    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("flaw", "lawn") == 2
    assert edit_distance("react", "reactjs") == 2


def test_strip_and_lowercase():
    assert strip_and_lowercase(" React.JS ") == "reactjs"


def test_alias_trie():
    trie = AliasTrie()
    trie.add_alias("reactjs", "skill_react")
    assert trie.exact_lookup("reactjs").skill_id == "skill_react"
    assert trie.exact_lookup("react") is None

    entries = trie.all_entries_within_length_window("react", window=2)
    assert len(entries) == 1
    assert entries[0] == ("reactjs", "skill_react")


def test_normalize_skill_tier1():
    trie = AliasTrie()
    trie.add_alias("python", "s1")
    embeddings = OntologyEmbeddings()
    res = normalize_skill(" Python ", trie, embeddings)
    assert res["tier"] == 1
    assert res["skill_id"] == "s1"


def test_normalize_skill_tier2():
    trie = AliasTrie()
    trie.add_alias("reactjs", "s2")
    embeddings = OntologyEmbeddings()
    res = normalize_skill("react", trie, embeddings)
    assert res["tier"] == 2
    assert res["skill_id"] == "s2"
