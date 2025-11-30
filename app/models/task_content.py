from typing import TypedDict, Literal

from pydantic import BaseModel, RootModel


class TextMark(BaseModel):
    type: Literal["em", "strong", "code"]


class TextNode(BaseModel):
    type: Literal["text"]
    text: str
    marks: list[TextMark] | None = None


class LinkAttrs(BaseModel):
    href: str
    description: str | None = None
    media: str | None = None


class LinkNode(BaseModel):
    type: Literal["link"]
    attrs: LinkAttrs
    content: list[TextNode]


class HardBreakNode(BaseModel):
    type: Literal["hard_break"]
    marks: list[TextMark] | None = None


class ParagraphNode(BaseModel):
    type: Literal["paragraph"]
    content: list[TextNode | LinkNode | HardBreakNode]


class TaskContent(RootModel[list[ParagraphNode]]):
    root: list[ParagraphNode]

    def to_plain_text(self) -> str:
        text_parts = []
        for paragraph in self.root:
            for node in paragraph.content:
                if isinstance(node, TextNode):
                    text_parts.append(node.text)
                elif isinstance(node, LinkNode):
                    # Extract text from link content
                    for link_text in node.content:
                        text_parts.append(link_text.text)
                elif isinstance(node, HardBreakNode):
                    text_parts.append("\n")
        return "".join(text_parts)

