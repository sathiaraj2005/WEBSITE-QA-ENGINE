from app.answer.generator import (
    DeterministicAnswerGenerator,
)
from app.retrieval.evidence import Evidence


def make_evidence(
    sentence: str,
    score: float = 0.9,
) -> Evidence:

    return Evidence(
        sentence=sentence,
        score=score,
        source_url="https://example.com/services",
        title="Services",
        chunk_id=0,
    )


def test_fact_answer():

    generator = DeterministicAnswerGenerator()

    evidence = [
        make_evidence(
            "The company was founded in 2018."
        )
    ]

    result = generator.generate(
        "When was the company founded?",
        evidence,
    )

    assert (
        result.answer
        == "The company was founded in 2018."
    )

    assert len(result.evidence) == 1


def test_multiple_evidence_sentences():

    generator = DeterministicAnswerGenerator()

    evidence = [
        make_evidence(
            "We provide web development services."
        ),
        make_evidence(
            "We also provide software engineering."
        ),
    ]

    result = generator.generate(
        "Tell me about the services.",
        evidence,
    )

    assert (
        "web development services"
        in result.answer
    )

    assert (
        "software engineering"
        in result.answer
    )


def test_no_evidence():

    generator = DeterministicAnswerGenerator()

    result = generator.generate(
        "What is the company revenue?",
        [],
    )

    assert (
        "could not find enough"
        in result.answer.lower()
    )

    assert result.evidence == []


def test_yes_no_positive():

    generator = DeterministicAnswerGenerator()

    evidence = [
        make_evidence(
            "The company is headquartered "
            "in Chennai."
        )
    ]

    result = generator.generate(
        "Is the company headquartered in Chennai?",
        evidence,
    )

    assert result.answer.startswith("Yes.")


def test_yes_no_negative():

    generator = DeterministicAnswerGenerator()

    evidence = [
        make_evidence(
            "The company does not provide "
            "mobile application development."
        )
    ]

    result = generator.generate(
        "Does the company provide mobile application development?",
        evidence,
    )

    assert result.answer.startswith("No.")


def test_empty_question():

    generator = DeterministicAnswerGenerator()

    try:
        generator.generate(
            "",
            [],
        )
        assert False
    except ValueError as error:
        assert (
            str(error)
            == "Question cannot be empty."
        )

def test_yes_no_avoid_negative():

    generator = DeterministicAnswerGenerator()

    evidence = [
        make_evidence(
            "Avoid use in operations."
        )
    ]

    result = generator.generate(
        "Is this website intended for operations?",
        evidence,
    )

    assert result.answer.startswith("No.")