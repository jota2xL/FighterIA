# Import all models so SQLAlchemy Base registers them before create_all() is called
from app.models.user import User
from app.models.discipline import Discipline, Technique
from app.models.biomechanical import BiomechanicalReference
from app.models.analysis import Analysis, AnalysisJointResult, AnalysisFeedback, AnalysisComment
from app.models.gamification import Badge, UserBadge
from app.models.instructor import InstructorGroup, GroupMember

__all__ = [
    "User",
    "Discipline", "Technique",
    "BiomechanicalReference",
    "Analysis", "AnalysisJointResult", "AnalysisFeedback", "AnalysisComment",
    "Badge", "UserBadge",
    "InstructorGroup", "GroupMember",
]
