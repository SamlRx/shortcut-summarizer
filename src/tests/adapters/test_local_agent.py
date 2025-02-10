from datetime import datetime
from unittest.mock import MagicMock

import pytest
from transformers import BartForConditionalGeneration, BartTokenizer, Pipeline

from shortcut_summarizer.adapters.local_agent import LocalAgent
from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Comment, Ticket


@pytest.fixture
def local_agent() -> LocalAgent:
    tokenizer_mock = MagicMock(spec=BartTokenizer)
    tokenizer_mock.return_value = MagicMock()
    tokenizer_mock.decode.return_value = "Test summary"
    model_mock = MagicMock(spec=BartForConditionalGeneration)
    classifier_mock = MagicMock(spec=Pipeline)
    classifier_mock.side_effect = [
        {"labels": ["search"]},
        {"labels": ["bug"]},
    ]
    qa_pipeline_mock = MagicMock(spec=Pipeline)
    qa_pipeline_mock.return_value = {"answer": "Test answer"}

    agent = LocalAgent(
        tokenizer=tokenizer_mock,
        model=model_mock,
        classifier=classifier_mock,
        qa_pipeline=qa_pipeline_mock,
    )
    return agent


def test_summarize(local_agent: LocalAgent) -> None:
    # Given a LocalAgent instance and a mock Ticket

    fake_ticket = Ticket(
        id="123",
        name="Login Failure",
        url="http://example.com/ticket/123",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description="Users report an authentication failure when logging in.",
        comments=[
            Comment(
                id="c1",
                author="Alice",
                text="This might be related to the OAuth system.",
                created_at=datetime.now(),
            )
        ],
    )

    # When calling summarize
    report = local_agent.summarize(fake_ticket)

    # Then it should return a TicketReport with expected values
    assert report.id == fake_ticket.id
    assert report.name == fake_ticket.name
    assert report.actor == fake_ticket.comments[0].author
    assert report.domain == TicketReport.Domain.SEARCH
    assert report.issue_type == TicketReport.IssueType.BUG
    assert report.summary == "Test summary"
    assert report.solution == "Test summary"
