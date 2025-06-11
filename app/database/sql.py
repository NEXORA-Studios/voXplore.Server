import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .modal import * # type: ignore # 仅导入模型，实际不使用

# 全局变量，方便其他模块使用
engine = None 
async_session = None

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Type, TypeVar

# 通用类型变量，方便通用读取函数
T = TypeVar("T", bound=SQLModel)


async def init_engine(path: str):
    global engine, async_session
    DATABASE_URL = f"sqlite+aiosqlite:///" + os.path.join(path, "data", "app.db")
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 初始化数据库（创建所有表）
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# 创建对象，写入数据库
async def create_entity(session: AsyncSession, entity: T) -> T:
    session.add(entity)
    await session.commit()
    await session.refresh(entity)  # 刷新得到数据库最新状态（比如自增id）
    return entity

# 根据主键读取单个对象
async def get_entity_by_id(session: AsyncSession, model: Type[T], id: int) -> Optional[T]:
    result = await session.get(model, id)
    return result

# 查询所有对象，带分页示范
async def get_entities(session: AsyncSession, model: Type[T], offset: int = 0, limit: int = 100) -> List[T]:
    q = await session.execute( #type: ignore
        model.select().offset(offset).limit(limit) #type: ignore
    )
    return q.scalars().all() #type: ignore

# 更新某个对象的指定字段
async def update_entity(session: AsyncSession, model: Type[T], id: int, **fields) -> Optional[T]: #type: ignore
    obj = await get_entity_by_id(session, model, id)
    if not obj:
        return None
    for key, value in fields.items(): #type: ignore
        setattr(obj, key, value)
    await session.commit()
    await session.refresh(obj)
    return obj

# 删除对象
async def delete_entity(session: AsyncSession, model: Type[T], id: int) -> bool:
    obj = await get_entity_by_id(session, model, id)
    if not obj:
        return False
    await session.delete(obj)
    await session.commit()
    return True
