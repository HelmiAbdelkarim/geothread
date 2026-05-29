from typing import List, Optional

from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    post_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1, max_length=10000)
    parent_comment_id: Optional[int] = None


class CommentEditRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class CommentResponse(BaseModel):
    comment_id: int
    content: str
    author_id: Optional[int]
    author_username: str
    post_id: int
    parent_comment_id: Optional[int]
    created_at: str
    updated_at: str
    is_edited: bool
    is_deleted: bool
    upvotes: int
    downvotes: int
    score: int
    user_vote: int = 0


class NestedCommentResponse(CommentResponse):
    children: List["NestedCommentResponse"] = []


class CommentTreeResponse(BaseModel):
    post_id: int
    total_comments: int
    max_depth: int
    comments: List[NestedCommentResponse]


NestedCommentResponse.model_rebuild()
