from __future__ import annotations

import re
from dataclasses import dataclass

from app.retrieval.evidence import Evidence


@dataclass(slots=True)
class GeneratedAnswer:
    """
    Final deterministic answer.

    `answer` contains the human-readable response.
    `evidence` contains the evidence used to construct it.
    """

    answer: str
    evidence: list[Evidence]


class DeterministicAnswerGenerator:
    """
    Generates answers using deterministic rules.

    No LLM.
    No external API.
    No randomness.

    The generator does not perform retrieval.
    It only transforms selected evidence into an answer.
    """

    def generate(
        self,
        question: str,
        evidence: list[Evidence],
    ) -> GeneratedAnswer:

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        if not evidence:
            return GeneratedAnswer(
                answer=(
                    "I could not find enough "
                    "relevant information on the website "
                    "to answer this question."
                ),
                evidence=[],
            )

        question_type = self._classify_question(
            question
        )

        if question_type == "list":
            answer = self._generate_list_answer(
                evidence
            )

        elif question_type == "yes_no":
            answer = self._generate_yes_no_answer(
                question,
                evidence,
            )

        else:
            answer = self._generate_fact_answer(
                evidence
            )

        return GeneratedAnswer(
            answer=answer,
            evidence=evidence,
        )

    @staticmethod
    def _classify_question(
        question: str,
    ) -> str:
        """
        Classify common question patterns.
        """

        normalized = question.lower().strip()

        if normalized.startswith(
            (
                "what are",
                "which are",
                "what services",
                "what products",
                "what features",
            )
        ):
            return "list"

        if normalized.startswith(
            (
                "is ",
                "are ",
                "does ",
                "do ",
                "can ",
                "was ",
                "were ",
                "has ",
                "have ",
            )
        ):
            return "yes_no"

        return "fact"

    @staticmethod
    def _clean_sentence(
        sentence: str,
    ) -> str:
        """
        Normalize whitespace and punctuation.
        """

        sentence = re.sub(
            r"\s+",
            " ",
            sentence.strip(),
        )

        return sentence

    def _generate_fact_answer(
        self,
        evidence: list[Evidence],
    ) -> str:
        """
        Construct a concise factual answer.
        """

        sentences = [
            self._clean_sentence(
                item.sentence
            )
            for item in evidence
        ]

        return " ".join(sentences)

    def _generate_list_answer(
        self,
        evidence: list[Evidence],
    ) -> str:
        """
        Construct a deterministic list-style answer.
        """

        sentences = [
            self._clean_sentence(
                item.sentence
            )
            for item in evidence
        ]

        if len(sentences) == 1:
            return sentences[0]

        return " ".join(sentences)

    def _generate_yes_no_answer(
        self,
        question: str,
        evidence: list[Evidence],
    ) -> str:
        """
        Generate a deterministic answer for
        yes/no-style questions.

        This deliberately avoids pretending that
        absence of evidence proves "No".
        """

        strongest = evidence[0]

        sentence = self._clean_sentence(
            strongest.sentence
        )

        question_lower = question.lower()

        # Explicit negative language.
        negative_patterns = (
            r"\bnot\b",
            r"\bno\b",
            r"\bdoesn't\b",
            r"\bdoes not\b",
            r"\bdon't\b",
            r"\bdo not\b",
            r"\bnever\b",
            r"\bwithout\b",
            r"\bavoid\b",
        )

        if any(
            re.search(
                pattern,
                sentence.lower(),
            )
            for pattern in negative_patterns
        ):
            return f"No. {sentence}"

        # We have positive evidence, but do not
        # blindly assert certainty.
        if (
            question_lower.startswith("is ")
            or question_lower.startswith("are ")
            or question_lower.startswith("was ")
            or question_lower.startswith("were ")
        ):
            return f"Yes. {sentence}"

        return sentence