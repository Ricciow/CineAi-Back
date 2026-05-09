from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from src.schemas.project import (
    ProjectCreate, ProjectResponse, ProjectUpdate, 
    MemberAddRequest, MemberUpdateRequest, TransferOwnershipRequest,
    ProjectPermissions
)
from src.repositories.project_repository import project_repository
from src.repositories.user_repository import user_repository
from src.api.deps import get_current_user_id, get_current_user

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
    user: dict = Depends(get_current_user)
):
    project = project_repository.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Projeto não encontrado."
        )
    
    # Check if user is owner or member
    is_owner = project["user_id"] == user["id"]
    is_member = any(m["user_id"] == user["id"] for m in project.get("members", []))
    
    if not is_owner and not is_member:
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
            detail="Projeto não encontrado ou você não tem permissão para excluí-lo."
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
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Only owner and admins can update project info
    is_owner = project["user_id"] == user_id
    is_admin = any(m["user_id"] == user_id and m["role"] == "admin" for m in project.get("members", []))
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Você não tem permissão para atualizar este projeto."
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return project_repository.get_by_id(project_id)
        
    try:
        success = project_repository.update(project_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado ao tentar atualizar."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao atualizar projeto: {str(e)}"
        )
    
    return project_repository.get_by_id(project_id)

# --- Members Management ---

@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: str,
    payload: MemberAddRequest,
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Check permissions: Owner can add admin/member, Admin can only add member
    is_owner = project["user_id"] == user_id
    is_admin = any(m["user_id"] == user_id and m["role"] == "admin" for m in project.get("members", []))
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão para adicionar membros")
    
    if payload.role == "admin" and not is_owner:
        raise HTTPException(status_code=403, detail="Apenas o dono pode adicionar administradores")

    # Check if user to add exists
    new_user = user_repository.get_by_email(payload.email)
    if not new_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado. Ele deve se registrar primeiro.")
    
    new_user_id = str(new_user["_id"])
    
    # Check if already a member or owner
    if project["user_id"] == new_user_id:
        raise HTTPException(status_code=400, detail="O usuário já é o dono do projeto")
    
    if any(m["user_id"] == new_user_id for m in project.get("members", [])):
        raise HTTPException(status_code=400, detail="O usuário já é um membro do projeto")

    member_data = {
        "user_id": new_user_id,
        "email": payload.email,
        "role": payload.role,
        "permissions": payload.permissions.model_dump() if payload.permissions else ProjectPermissions().model_dump()
    }
    
    project_repository.add_member(project_id, member_data)
    return {"message": "Membro adicionado com sucesso"}

@router.put("/{project_id}/members/{email}")
async def update_member(
    project_id: str,
    email: str,
    payload: MemberUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    is_owner = project["user_id"] == user_id
    is_admin = any(m["user_id"] == user_id and m["role"] == "admin" for m in project.get("members", []))
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    # Find the member to update
    target_member = next((m for m in project.get("members", []) if m["email"] == email), None)
    if not target_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    # Admins cannot edit other admins or the owner
    if is_admin and not is_owner:
        if target_member["role"] == "admin":
            raise HTTPException(status_code=403, detail="Admins não podem editar outros admins")
        if payload.role == "admin":
            raise HTTPException(status_code=403, detail="Admins não podem promover outros a admin")

    update_data = payload.model_dump(exclude_unset=True)
    project_repository.update_member(project_id, email, update_data)
    return {"message": "Permissões atualizadas"}

@router.delete("/{project_id}/members/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: str,
    email: str,
    user_id: str = Depends(get_current_user_id)
):
    project = project_repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    is_owner = project["user_id"] == user_id
    is_admin = any(m["user_id"] == user_id and m["role"] == "admin" for m in project.get("members", []))
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    target_member = next((m for m in project.get("members", []) if m["email"] == email), None)
    if not target_member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    if is_admin and not is_owner and target_member["role"] == "admin":
        raise HTTPException(status_code=403, detail="Admins não podem remover outros admins")

    project_repository.remove_member(project_id, email)
    return None

@router.post("/{project_id}/transfer-ownership")
async def transfer_ownership(
    project_id: str,
    payload: TransferOwnershipRequest,
    user: dict = Depends(get_current_user)
):
    project = project_repository.get_by_id(project_id)
    if not project or project["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Apenas o dono pode transferir a propriedade")

    new_owner = user_repository.get_by_email(payload.new_owner_email)
    if not new_owner:
        raise HTTPException(status_code=404, detail="Novo dono não encontrado")
    
    new_owner_id = str(new_owner["_id"])
    if new_owner_id == user["id"]:
        raise HTTPException(status_code=400, detail="Você já é o dono")

    # Update logic
    # 1. Update project user_id
    # 2. Add old owner as admin in members
    project_repository.update(project_id, {"user_id": new_owner_id})
    
    # Remove new owner from members if they were there
    project_repository.remove_member(project_id, payload.new_owner_email)
    
    # Add old owner as admin
    old_owner_member = {
        "user_id": user["id"],
        "email": user["email"],
        "role": "admin",
        "permissions": ProjectPermissions().model_dump()
    }
    project_repository.add_member(project_id, old_owner_member)
    
    return {"message": f"Propriedade transferida para {payload.new_owner_email}"}
