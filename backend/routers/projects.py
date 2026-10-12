from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from backend.database import get_db
from backend.models.models import Project, ProjectVersion, UserFeedback, ProjectStatus
from backend.schemas.schemas import ProjectResponse, ProjectCreate, ProjectUpdate, ProjectVersionResponse, UserFeedbackCreate, UserFeedbackResponse
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return projects

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    # In a real environment, we'd extract the user_id from the auth request state (request.state.user)
    # We mock user_id with a standard default UUID for demonstration
    mock_user_id = UUID("00000000-0000-0000-0000-000000000000")
    
    project = Project(
        id=uuid4(),
        user_id=mock_user_id,
        name=data.name,
        description=data.description,
        status=ProjectStatus.draft
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.patch("/{id}", response_model=ProjectResponse)
async def update_project(id: UUID, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    # Build update dict based on provided values
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    stmt = update(Project).where(Project.id == id).values(**update_data).execution_options(synchronize_session="fetch")
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    await db.commit()
    
    # Return updated project
    return await get_project(id, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = delete(Project).where(Project.id == id)
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    await db.commit()
    return None

@router.post("/{id}/generate")
async def trigger_generation(id: UUID, db: AsyncSession = Depends(get_db)):
    # 1. Check if project exists
    project = await get_project(id, db)
    
    # 2. Update status to processing
    project.status = ProjectStatus.processing
    await db.commit()
    await db.refresh(project)

    # 3. Queue LangGraph orchestrator task asynchronously
    from backend.agents.orchestrator.agent import run_pipeline_task
    
    job_id = str(uuid4())
    # Delay the task execution
    run_pipeline_task.delay(str(project.id), job_id, project.description or "No prompt provided")
    
    return {
        "detail": "Generation pipeline triggered successfully",
        "job_id": job_id,
        "project_id": project.id,
        "status": project.status
    }

@router.get("/{id}/versions", response_model=List[ProjectVersionResponse])
async def list_project_versions(id: UUID, db: AsyncSession = Depends(get_db)):
    # Ensure project exists
    await get_project(id, db)
    
    stmt = select(ProjectVersion).where(ProjectVersion.project_id == id).order_by(ProjectVersion.version_number.desc())
    result = await db.execute(stmt)
    versions = result.scalars().all()
    return versions

@router.post("/{id}/versions/{v}/feedback", response_model=UserFeedbackResponse)
async def post_version_feedback(id: UUID, v: int, data: UserFeedbackCreate, db: AsyncSession = Depends(get_db)):
    # Verify version exists
    stmt = select(ProjectVersion).where(ProjectVersion.project_id == id, ProjectVersion.version_number == v)
    result = await db.execute(stmt)
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project version not found"
        )

    feedback = UserFeedback(
        id=uuid4(),
        project_id=id,
        version_id=version.id,
        agent_name=data.agent_name,
        rating=data.rating,
        comment=data.comment
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback
