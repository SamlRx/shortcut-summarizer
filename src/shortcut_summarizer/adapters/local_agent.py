from datetime import datetime
from functools import cached_property
from typing import Optional

from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
    Pipeline,
    pipeline,
)

from shortcut_summarizer.domains.report import TicketReport
from shortcut_summarizer.domains.ticket import Comment, Ticket
from shortcut_summarizer.ports.summarizer import SummarizerPort

_TOKENIZER_MODEL = "facebook/bart-large-cnn"
_CLASSIFIER_MODEL = "facebook/bart-large-mnli"
_QA_MODEL = "deepset/roberta-base-squad2"


class LocalAgent(SummarizerPort):

    def __init__(
        self,
        tokenizer: BartTokenizer = BartTokenizer.from_pretrained(
            _TOKENIZER_MODEL
        ),
        model: BartForConditionalGeneration = BartForConditionalGeneration.from_pretrained(  # noqa
            _TOKENIZER_MODEL
        ),
        classifier: Pipeline = pipeline(
            "zero-shot-classification", model=_CLASSIFIER_MODEL
        ),
        qa_pipeline: Pipeline = pipeline(
            "question-answering", model=_QA_MODEL
        ),
    ):
        self._tokenizer = tokenizer
        self._model_not_evaluated = model
        self._classifier = classifier
        self._qa_pipeline = qa_pipeline

    @cached_property
    def _model(self) -> BartForConditionalGeneration:
        self._model_not_evaluated.eval()
        return self._model_not_evaluated

    def summarize(self, ticket: Ticket) -> TicketReport:
        start_date = datetime.now()

        return TicketReport(
            id=ticket.id,
            name=ticket.name,
            actor=ticket.comments[0].author,
            domain=self._classify_domain(ticket),
            ticket_url=ticket.url,
            ticket_created_at=ticket.created_at,
            ticket_updated_at=ticket.updated_at,
            summary=self._summarize_ticket(ticket),
            solution=self._extract_solution(ticket),
            issue_type=self._classify_issue_type(ticket),
            created_at=start_date,
        )

    def _summarize_ticket(self, ticket: Ticket) -> str:
        question = "What is the issue described here"
        result = self._qa_pipeline(
            question=question, context=ticket.description
        )
        return self._summarize(result["answer"], 50)

    def _classify_domain(
        self, ticket: Ticket
    ) -> Optional[TicketReport.Domain]:
        candidate_labels = [domain.value for domain in TicketReport.Domain]
        result = self._classifier(
            self._extract_ticket_text(ticket), candidate_labels
        )
        predicted_label = result["labels"][0]
        try:
            return TicketReport.Domain(
                predicted_label
            )  # Convert string to enum
        except ValueError:
            print(f"Warning: Unexpected domain label: {predicted_label}")
            return None

    def _classify_issue_type(
        self, ticket: Ticket
    ) -> Optional[TicketReport.IssueType]:
        candidate_labels = [domain.value for domain in TicketReport.IssueType]
        result = self._classifier(
            self._extract_ticket_text(ticket), candidate_labels
        )
        predicted_label = result["labels"][0]
        try:
            return TicketReport.IssueType(
                predicted_label
            )  # Convert string to enum
        except ValueError:  # Handle the case where the classification fails
            print(f"Warning: Unexpected issue type label: {predicted_label}")
            return None  # Or a default domain

    def _extract_ticket_text(self, ticket: Ticket) -> str:
        return (
            "Tickets Description: "
            + ticket.description
            + "Comments from the tickets: "
            + " ".join(
                self._transform_comment(comment) for comment in ticket.comments
            )
        )

    @staticmethod
    def _transform_comment(comment: Comment) -> str:
        return (
            f"[Author: {comment.author} "
            f"Comment: {comment.text} "
            f"created at: {comment.created_at}]"
        )

    def _extract_solution(self, ticket: Ticket) -> str:
        context = self._extract_ticket_text(ticket)
        question = (
            "What is the solution to the problem described in the ticket?"
        )
        result = self._qa_pipeline(question=question, context=context)
        return self._summarize(result["answer"])

    def _summarize(self, text: str, max_length: int = 10) -> str:
        inputs = self._tokenizer(
            text, return_tensors="pt", max_length=1024, truncation=True
        )
        summary_ids = self._model.generate(
            inputs.input_ids,
            max_length=max_length,
            min_length=5,
            length_penalty=1.0,
            num_beams=5,
            early_stopping=True,
        )
        return self._tokenizer.decode(summary_ids[0], skip_special_tokens=True)
