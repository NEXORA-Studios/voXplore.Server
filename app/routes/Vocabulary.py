from fastapi import APIRouter, HTTPException, status, Request

from app.database.sql import async_session, get_entities
from app.database.modal import Vocabulary, LearningProgress, UserRoles
from app.middlewares.verification import RequireRole
from utils.logging import logger

router = APIRouter(prefix="/api/vocab", tags=["Vocabulary Learning"])

@router.get("/sets")
@RequireRole(UserRoles.STUDENT)
async def get_vocabulary_sets():
    """获取词汇集合接口"""
    async with async_session() as session:
        vocab_sets = await get_entities(session, Vocabulary)
        
        logger.debug(f"Retrieved {len(vocab_sets)} vocabulary sets")
        return {"sets": [{"id": v.id, "word": v.word, "category": v.category} for v in vocab_sets]}

@router.post("/progress")
@RequireRole(UserRoles.STUDENT)
async def record_progress(progress_data: dict, request: Request):
    """记录学习进度接口"""
    async with async_session() as session:
        # 获取当前用户
        current_user = request.state.user
        
        # 检查词汇是否存在
        vocab = await get_entity_by_id(session, Vocabulary, progress_data["vocab_id"])
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary not found"
            )
        
        # 更新或创建学习进度
        progress = await get_entities(session, LearningProgress, user_id=current_user.id, vocab_id=vocab.id)
        
        if progress:
            progress.mastery_level = progress_data["mastery_level"]
        else:
            progress = LearningProgress(
                user_id=current_user.id,
                vocab_id=vocab.id,
                mastery_level=progress_data["mastery_level"]
            )
            session.add(progress)
        
        await session.commit()
        
        logger.info(f"Progress recorded for user {current_user.username} on vocab {vocab.word}")
        return {"message": "Progress recorded successfully"}

@router.get("/stats")
@RequireRole(UserRoles.STUDENT)
async def get_learning_stats(request: Request):
    """获取学习统计接口"""
    async with async_session() as session:
        # 获取当前用户
        current_user = request.state.user
        
        # 获取用户的所有学习进度
        progresses = await get_entities(session, LearningProgress, user_id=current_user.id)
        
        # 计算统计数据
        total_vocab = len(progresses)
        mastered_vocab = len([p for p in progresses if p.mastery_level >= 8])
        practicing_vocab = len([p for p in progresses if 4 <= p.mastery_level < 8])
        new_vocab = len([p for p in progresses if p.mastery_level < 4])
        
        logger.debug(f"Retrieved learning stats for user {current_user.username}")
        return {
            "total_vocab": total_vocab,
            "mastered_vocab": mastered_vocab,
            "practicing_vocab": practicing_vocab,
            "new_vocab": new_vocab
        }