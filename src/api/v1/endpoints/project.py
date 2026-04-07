from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.repositories.project_repository import project_repository
from src.api.deps import get_current_user_id

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, 
    user_id: str = Depends(get_current_user_id)
):
    return project_repository.create(
        name=payload.name, 
        user_id=user_id, 
        description=payload.description
    )

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(user_id: str = Depends(get_current_user_id)):
    return project_repository.list_by_user(user_id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project or project["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Projeto não encontrado."
        )
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project or project["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Projeto não encontrado."
        )
    success = project_repository.delete(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Erro ao deletar projeto."
        )
    return None

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project or project["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Projeto não encontrado."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    success = project_repository.update(project_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar projeto."
        )
    
    return project_repository.get_by_id(project_id)
