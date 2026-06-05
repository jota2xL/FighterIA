# Import all models so SQLAlchemy Base registers them before create_all() is called
from app.models.user import User
from app.models.discipline import Discipline, Technique
from app.models.biomechanical import BiomechanicalReference
from app.models.analysis import Analysis, AnalysisJointResult, AnalysisFeedback, AnalysisComment
from app.models.gamification import Badge, UserBadge
from app.models.instructor import InstructorGroup, GroupMember

# v2 modules
from app.models.crm import Gym, Trainer, Lead
from app.models.blockchain import Certificate

__all__ = [
    "User",
    "Discipline", "Technique",
    "BiomechanicalReference",
    "Analysis", "AnalysisJointResult", "AnalysisFeedback", "AnalysisComment",
    "Badge", "UserBadge",
    "InstructorGroup", "GroupMember",
    # v2
    "Gym", "Trainer", "Lead",
    "Certificate",
]
