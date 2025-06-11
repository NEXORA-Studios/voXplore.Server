from fastapi import APIRouter, Request, HTTPException, status

from app.database.sql import async_session, get_entities
from app.database.modal import StudyGroup, GroupMember, UserRoles
from app.middlewares.verification import RequireRole
from utils.logging import logger

router = APIRouter(prefix="/api/groups", tags=["Study Groups"])

@router.post("/")
@RequireRole(UserRoles.STUDENT)
async def create_group(group_data: dict, request: Request):
    """创建学习小组接口"""
    async with async_session() as session:
        # 获取当前用户
        current_user = request.state.user
        
        # 创建新小组
        new_group = StudyGroup(
            name=group_data["name"],
            description=group_data.get("description"),
            created_by=current_user.id
        )
        session.add(new_group)
        await session.commit()
        
        # 自动将创建者加入小组
        membership = GroupMember(
            group_id=new_group.id,
            user_id=current_user.id
        )
        session.add(membership)
        await session.commit()
        
        logger.info(f"New group created by {current_user.username}: {group_data['name']}")
        return {"message": "Group created successfully", "group_id": new_group.id}

@router.get("/{group_id}/members")
@RequireRole(UserRoles.STUDENT)
async def get_group_members(group_id: int):
    """获取小组成员接口"""
    async with async_session() as session:
        members = await get_entities(session, GroupMember, group_id=group_id)
        if not members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found or has no members"
            )
        
        member_list = []
        for member in members:
            user = await get_entity_by_id(session, User, member.user_id)
            member_list.append({
                "user_id": user.id,
                "username": user.username,
                "joined_at": member.joined_at
            })
        
        logger.debug(f"Retrieved members for group ID: {group_id}")
        return {"members": member_list}

@router.post("/{group_id}/invite")
@RequireRole(UserRoles.STUDENT)
async def invite_member(group_id: int, invite_data: dict, request: Request):
    """邀请成员加入小组接口"""
    async with async_session() as session:
        # 验证小组是否存在
        group = await get_entity_by_id(session, StudyGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # 获取被邀请用户
        invited_user = await get_entity_by_id(session, User, username=invite_data["username"])
        if not invited_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 检查是否已经是成员
        existing_member = await get_entities(session, GroupMember, user_id=invited_user.id, group_id=group_id)
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this group"
            )
        
        # 添加成员
        membership = GroupMember(
            group_id=group_id,
            user_id=invited_user.id
        )
        session.add(membership)
        await session.commit()
        
        logger.info(f"User {invited_user.username} invited to group {group_id} by {request.state.user.username}")
        return {"message": "User invited successfully"}