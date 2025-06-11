from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
import enum

# 定义枚举
class UserRoles(enum.IntEnum):
    NEW_USER = 0
    STUDENT = 1
    TEACHER = 2
    ADMIN = 9

class DifficultyLevel(enum.IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    EXTREME = 5

class MasteryLevel(enum.IntEnum):
    BEGINNER = 1
    INTERMEDIATE = 3
    ADVANCED = 5
    EXPERT = 7
    MASTER = 10

class GameType(enum.StrEnum):
    FLASHCARD = "flashcard"
    MATCHING = "matching"
    QUIZ = "quiz"
    SPELLING = "spelling"

# 用户模型
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    email: str = Field(unique=True, index=True)
    role: UserRoles
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_groups: List["StudyGroup"] = Relationship(back_populates="creator")
    group_memberships: List["GroupMember"] = Relationship(back_populates="user")
    learning_progresses: List["LearningProgress"] = Relationship(back_populates="user")
    game_scores: List["GameScore"] = Relationship(back_populates="user")

# 学习小组模型
class StudyGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    creator: User = Relationship(back_populates="created_groups")
    members: List["GroupMember"] = Relationship(back_populates="group")
    game_sessions: List["GameSession"] = Relationship(back_populates="group")

# 小组成员关系模型
class GroupMember(SQLModel, table=True):
    group_id: int = Field(foreign_key="studygroup.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    group: StudyGroup = Relationship(back_populates="members")
    user: User = Relationship(back_populates="group_memberships")

# 词汇模型
class Vocabulary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str
    definition: str
    example: Optional[str] = None
    difficulty: DifficultyLevel
    category: Optional[str] = None
    learning_progresses: List["LearningProgress"] = Relationship(back_populates="vocabulary")

# 学习进度模型
class LearningProgress(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    vocab_id: int = Field(foreign_key="vocabulary.id", primary_key=True)
    mastery_level: MasteryLevel
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    user: User = Relationship(back_populates="learning_progresses")
    vocabulary: Vocabulary = Relationship(back_populates="learning_progresses")

# 游戏会话模型
class GameSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="studygroup.id")
    game_type: GameType
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    group: StudyGroup = Relationship(back_populates="game_sessions")
    scores: List["GameScore"] = Relationship(back_populates="session")

# 游戏成绩模型
class GameScore(SQLModel, table=True):
    session_id: int = Field(foreign_key="gamesession.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    score: int
    session: GameSession = Relationship(back_populates="scores")
    user: User = Relationship(back_populates="game_scores")
