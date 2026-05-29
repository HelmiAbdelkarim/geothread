from typing import Optional


class CommentTree:
    def __init__(self, root_id: int):
        self._children: dict[int, list[int]] = {root_id: []}
        self._parent: dict[int, Optional[int]] = {root_id: None}
        self._deleted: dict[int, bool] = {root_id: False}
        self._root = root_id

    # --- Observers ---

    def is_empty(self) -> bool:
        return len(self._children) == 0

    def has_comment(self, comment_id: int) -> bool:
        return comment_id in self._children

    def is_root(self, comment_id: int) -> bool:
        return comment_id == self._root

    def root_of(self) -> int:
        return self._root

    def parent_of(self, comment_id: int) -> Optional[int]:
        return self._parent.get(comment_id)

    def children_of(self, comment_id: int) -> list[int]:
        return self._children.get(comment_id, [])

    def is_deleted(self, comment_id: int) -> bool:
        return self._deleted.get(comment_id, False)

    # --- Algorithm 1: FindComment (recursive DFS) ---

    def find_comment(self, target_id: int) -> bool:
        return self._find_dfs(self._root, target_id)

    def _find_dfs(self, current_id: int, target_id: int) -> bool:
        if current_id == target_id:
            return True
        return any(self._find_dfs(child_id, target_id) for child_id in self.children_of(current_id))

    # --- Algorithm 2: AddReply (O(1) direct lookup) ---

    def add_reply(self, parent_id: int, child_id: int) -> None:
        if parent_id not in self._children:
            return
        self._children[child_id] = []
        self._parent[child_id] = parent_id
        self._deleted[child_id] = False
        self._children[parent_id].append(child_id)

    # --- Algorithm 3: DeleteComment (hard if leaf, soft if has replies) ---

    def delete_comment(self, comment_id: int) -> None:
        if not self.children_of(comment_id):
            self._hard_delete(comment_id)
        else:
            self._soft_delete(comment_id)

    def _hard_delete(self, comment_id: int) -> None:
        parent_id = self._parent.get(comment_id)
        if parent_id is not None:
            self._children[parent_id].remove(comment_id)
        del self._children[comment_id]
        del self._parent[comment_id]
        del self._deleted[comment_id]

    def _soft_delete(self, comment_id: int) -> None:
        self._deleted[comment_id] = True

    # --- Algorithm 4: MaxDepth (recursive) ---

    def max_depth(self) -> int:
        return self._depth(self._root)

    def _depth(self, current_id: int) -> int:
        if not self.children_of(current_id):
            return 1
        return 1 + max(self._depth(child_id) for child_id in self.children_of(current_id))

    def get_all_comment_ids(self) -> list[int]:
        return self._collect_ids(self._root)

    def _collect_ids(self, current_id: int) -> list[int]:
        ids = [current_id]
        for child_id in self.children_of(current_id):
            ids.extend(self._collect_ids(child_id))
        return ids

    def count_comments(self) -> int:
        return len(self._children) - 1
