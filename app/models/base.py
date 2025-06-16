from typing import Optional, List, TypeVar, Type, Union, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from app.db.collections import db

# For typing support
ModelType = TypeVar("ModelType", bound="DocumentModel")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")


class DocumentModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PyObjectId
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[PyObjectId] = Field(default=None)

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @classmethod
    def collection(cls) -> AsyncIOMotorCollection:
        """Override this in child classes to return the MongoDB collection"""
        raise NotImplementedError("Subclasses must define their MongoDB collection.")

    # CREATE / INSERT
    async def save(self: ModelType) -> ModelType:
        data = self.dict(by_alias=True, exclude_none=True)
        result = await self.collection().insert_one(data)
        self.id = result.inserted_id
        return self

    # READ / GET BY ID
    @classmethod
    async def find_by_id(
        cls: Type[ModelType], _id: Union[str, ObjectId]
    ) -> Optional[ModelType]:
        if isinstance(_id, str):
            _id = ObjectId(_id)
        doc = await cls.collection().find_one({"_id": _id})
        return cls(**doc) if doc else None

    # READ / GET ALL (optional filters)
    @classmethod
    async def find_all(
        cls: Type[ModelType], filter: Dict[str, Any] = {}, limit: int = 100
    ) -> List[ModelType]:
        cursor = cls.collection().find(filter).sort("created_at", -1).limit(limit)
        return [cls(**doc) async for doc in cursor]

    # UPDATE (partial)
    async def update(self: ModelType, updates: Dict[str, Any]) -> ModelType:
        updates["updated_at"] = datetime.utcnow()
        await self.collection().update_one({"_id": self.id}, {"$set": updates})
        for key, value in updates.items():
            setattr(self, key, value)
        return self

    # DELETE
    async def delete(self: ModelType) -> bool:  # type: ignore
        result = await self.collection().delete_one({"_id": self.id})
        return result.deleted_count == 1

    # READ
    @classmethod
    async def find_one(
        cls: Type[ModelType], filter: Dict[str, Any]
    ) -> Optional[ModelType]:
        doc = await cls.collection().find_one(filter)
        return cls(**doc) if doc else None
