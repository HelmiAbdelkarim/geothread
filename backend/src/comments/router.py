from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status

from src.comments import service
from src.comments.schemas import (CommentCreateRequest, CommentEditRequest,
                                   CommentResponse, CommentTreeResponse,
                                   NestedCommentResponse)
from src.core.database import reddit_db
from src.core.dependencies import get_current_user_id, get_optional_user_id
from src.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from src.core.schemas import MessageResponse

router = APIRouter(prefix="/api/comments", tags=["Comments"])

_VOTE_MESSAGES = {"up": "Upvoted", "down": "Downvoted", "remove": "Vote removed"}


def _to_response(comment, user_id) -> CommentResponse:
    author = reddit_db.get_user(comment.author_id)
    return CommentResponse(
        comment_id=comment.comment_id,
        content=comment.content if not comment.is_deleted else "[deleted]",
        author_id=comment.author_id if not comment.is_deleted else None,
        author_username=author.username if author and not comment.is_deleted else "[deleted]",
        post_id=comment.post_id,
        parent_comment_id=comment.parent_comment_id,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat(),
        is_edited=comment.is_edited,
        is_deleted=comment.is_deleted,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        score=comment.score,
        user_vote=service.get_vote(comment.comment_id, user_id) if user_id else 0,
    )


def _inject_votes(thread: list, user_id: int) -> None:
    for c in thread:
        c["user_vote"] = service.get_vote(c["comment_id"], user_id)
        if c.get("children"):
            _inject_votes(c["children"], user_id)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentCreateRequest, user_id: int = Depends(get_current_user_id)):
    comment = service.create(user_id, body.post_id, body.content, body.parent_comment_id)
    if not comment:
        raise BadRequestError("Failed to create comment. Check post/parent exists.")
    return _to_response(comment, user_id)


@router.get("/post/{post_id}", response_model=CommentTreeResponse)
async def get_post_comments(
    post_id: int,
    sort: Literal["score", "time"] = Query("score"),
    user_id: int = Depends(get_optional_user_id),
):
    post = reddit_db.get_post(post_id)
    if not post:
        raise NotFoundError(f"Post {post_id} not found.")
    thread = service.get_post_thread(post_id, sort)
    if user_id:
        _inject_votes(thread, user_id)
    return CommentTreeResponse(
        post_id=post_id,
        total_comments=post.comments,
        max_depth=service.get_depth(post_id),
        comments=[NestedCommentResponse(**c) for c in thread],
    )


@router.get("/user/{user_id}", response_model=List[CommentResponse])
async def get_user_comments(user_id: int):
    return [_to_response(c, None) for c in service.get_user_comments(user_id)]


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, user_id: int = Depends(get_optional_user_id)):
    comment = service.get_by_id(comment_id)
    if not comment:
        raise NotFoundError(f"Comment {comment_id} not found.")
    return _to_response(comment, user_id)


@router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comment(comment_id: int, body: CommentEditRequest, user_id: int = Depends(get_current_user_id)):
    comment = service.get_by_id(comment_id)
    if not comment:
        raise NotFoundError(f"Comment {comment_id} not found.")
    if comment.author_id != user_id:
        raise ForbiddenError("You can only edit your own comments.")
    if comment.is_deleted:
        raise BadRequestError("Cannot edit a deleted comment.")
    service.edit(comment_id, body.content)
    return _to_response(service.get_by_id(comment_id), user_id)


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id)):
    comment = service.get_by_id(comment_id)
    if not comment:
        raise NotFoundError(f"Comment {comment_id} not found.")
    if comment.author_id != user_id:
        raise ForbiddenError("You can only delete your own comments.")
    service.delete(comment_id)
    return MessageResponse(message="Comment deleted.", success=True)


@router.post("/{comment_id}/vote", response_model=MessageResponse)
async def vote_on_comment(
    comment_id: int,
    direction: Literal["up", "down", "remove"],
    user_id: int = Depends(get_current_user_id),
):
    if not service.get_by_id(comment_id):
        raise NotFoundError(f"Comment {comment_id} not found.")
    service.vote(comment_id, user_id, direction)
    return MessageResponse(message=_VOTE_MESSAGES[direction], success=True)
