from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    # status = Column(String, nullable=False, default='pending')
    status = Column(String, nullable=False, server_default='pending')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)

    project = relationship('Project', back_populates='tasks')
    assignee = relationship('User', back_populates='assigned_tasks')