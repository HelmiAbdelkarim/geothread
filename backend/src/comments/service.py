from datetime import datetime
from typing import Dict, List, Literal, Optional

from sqlalchemy.orm import Session

from src.algorithms.tree import CommentTree
from src.core.models import CommentModel, CommentVoteModel, PostModel, UserModel


def _build_tree(post_id: int, comments: List[CommentModel]) -> CommentTree:
    """Build CommentTree from a flat list of DB comments (ASNAP DFS algorithm)."""
    root_id = -post_id
    tree = CommentTree(root_id)
    for comment in sorted(comments, key=lambda c: c.created_at):
        parent = comment.parent_comment_id if comment.parent_comment_id else root_id
        tree.add_reply(parent, comment.comment_id)
    return tree


def create(db: Session, author_id: int, post_id: int, content: str, parent_comment_id: Optional[int] = None) -> Optional[CommentModel]:
    post = db.query(PostModel).filter(PostModel.post_id == post_id).first()
    if not post:
        return None
    if parent_comment_id:
        parent = db.query(CommentModel).filter(
            CommentModel.comment_id == parent_comment_id, CommentModel.post_id == post_id
        ).first()
        if not parent:
            return None
    now = datetime.now()
    comment = CommentModel(content=content, author_id=author_id, post_id=post_id,
                           parent_comment_id=parent_comment_id, created_at=now, updated_at=now)
    db.add(comment)
    post.comment_count += 1
    db.commit()
    db.refresh(comment)
    return comment


def get_by_id(db: Session, comment_id: int) -> Optional[CommentModel]:
    return db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()


def edit(db: Session, comment_id: int, content: str) -> bool:
    comment = db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()
    if not comment or comment.is_deleted:
        return False
    comment.content = content
    comment.updated_at = datetime.now()
    comment.is_edited = True
    db.commit()
    return True


def delete(db: Session, comment_id: int) -> bool:
    comment = db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()
    if not comment:
        return False
    has_children = db.query(CommentModel).filter(CommentModel.parent_comment_id == comment_id).count() > 0
    post = db.query(PostModel).filter(PostModel.post_id == comment.post_id).first()
    if has_children:
        comment.is_deleted = True
        comment.content = "[deleted]"
    else:
        db.delete(comment)
        if post:
            post.comment_count = max(0, post.comment_count - 1)
    db.commit()
    return True


def get_post_thread(db: Session, post_id: int, sort_by: str = "score") -> List[Dict]:
    comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
    if not comments:
        return []

    # Build CommentTree from flat list, then traverse with DFS
    tree = _build_tree(post_id, comments)
    cmap = {c.comment_id: c for c in comments}

    user_cache: Dict[int, str] = {}

    def get_username(author_id: int) -> str:
        if author_id not in user_cache:
            u = db.query(UserModel).filter(UserModel.user_id == author_id).first()
            user_cache[author_id] = u.username if u else "[deleted]"
        return user_cache[author_id]

    def build_subtree(cid: int) -> Dict:
        c = cmap.get(cid)
        if not c:
            return {}
        data = c.to_dict()
        data["author_username"] = get_username(c.author_id) if not c.is_deleted else "[deleted]"
        children = tree.children_of(cid)
        if sort_by == "score":
            children = sorted(children, key=lambda x: cmap[x].score if x in cmap else 0, reverse=True)
        else:
            children = sorted(children, key=lambda x: cmap[x].created_at if x in cmap else datetime.min)
        data["children"] = [build_subtree(x) for x in children]
        return data

    root_children = tree.children_of(-post_id)
    if sort_by == "score":
        root_children = sorted(root_children, key=lambda x: cmap[x].score if x in cmap else 0, reverse=True)
    else:
        root_children = sorted(root_children, key=lambda x: cmap[x].created_at if x in cmap else datetime.min)
    return [build_subtree(cid) for cid in root_children]


def vote(db: Session, comment_id: int, user_id: int, direction: Literal["up", "down", "remove"]) -> None:
    comment = db.query(CommentModel).filter(CommentModel.comment_id == comment_id).first()
    if not comment:
        return
    row = db.query(CommentVoteModel).filter(CommentVoteModel.user_id == user_id, CommentVoteModel.comment_id == comment_id).first()
    current = row.value if row else 0

    if direction == "up":
        new_val = 0 if current == 1 else 1
    elif direction == "down":
        new_val = 0 if current == -1 else -1
    else:
        new_val = 0

    if current == 1:
        comment.upvotes -= 1
    elif current == -1:
        comment.downvotes -= 1
    if new_val == 1:
        comment.upvotes += 1
    elif new_val == -1:
        comment.downvotes += 1

    if new_val == 0:
        if row:
            db.delete(row)
    elif row:
        row.value = new_val
    else:
        db.add(CommentVoteModel(user_id=user_id, comment_id=comment_id, value=new_val))

    author = db.query(UserModel).filter(UserModel.user_id == comment.author_id).first()
    if author:
        author.comment_karma = sum(
            c.upvotes - c.downvotes
            for c in db.query(CommentModel).filter(CommentModel.author_id == comment.author_id).all()
        )

    db.commit()


def get_vote(db: Session, comment_id: int, user_id: int) -> int:
    if not user_id:
        return 0
    row = db.query(CommentVoteModel).filter(CommentVoteModel.user_id == user_id, CommentVoteModel.comment_id == comment_id).first()
    return row.value if row else 0


def get_depth(db: Session, post_id: int) -> int:
    comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
    if not comments:
        return 0
    return max(0, _build_tree(post_id, comments).max_depth() - 1)


def get_user_comments(db: Session, user_id: int) -> List[CommentModel]:
    return db.query(CommentModel).filter(CommentModel.author_id == user_id).all()
