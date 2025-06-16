# Import necessary modules for type hints, data validation, MongoDB operations and datetime handling
from typing import Optional, List, TypeVar, Type, Union, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from app.db.collections import db

# Define a type variable for the document model to support type hints in class methods
ModelType = TypeVar("ModelType", bound="DocumentModel")


# Custom ObjectId class for Pydantic model compatibility
class PyObjectId(ObjectId):
    # Define validators for Pydantic to handle ObjectId type
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # Validate that the value is a valid ObjectId
    @classmethod
    def validate(cls, v, values, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    # Define JSON schema for OpenAPI documentation
    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")


# Base model for all database documents with common fields and functionality
class DocumentModel(BaseModel):
    # Common fields for all documents
    id: Optional[PyObjectId] = Field(default=None, alias="_id")  # MongoDB document ID
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )  # Document creation timestamp
    created_by: PyObjectId  # ID of user who created the document
    updated_at: Optional[datetime] = Field(default=None)  # Last update timestamp
    updated_by: Optional[PyObjectId] = Field(
        default=None
    )  # ID of user who last updated the document

    # Pydantic model configuration
    class Config:
        json_encoders = {
            ObjectId: str
        }  # Convert ObjectId to string for JSON serialization
        arbitrary_types_allowed = True  # Allow custom types like ObjectId
        allow_population_by_field_name = True  # Allow using alias names for fields

    @classmethod
    def collection(cls) -> AsyncIOMotorCollection:
        """Override this in child classes to return the MongoDB collection"""
        raise NotImplementedError("Subclasses must define their MongoDB collection.")

    # CREATE / INSERT
    # Save a new document to the database
    async def save(self: ModelType) -> ModelType:
        # Convert model to dictionary using MongoDB field names
        data = self.dict(by_alias=True, exclude_none=True)
        # Insert document into the database
        result = await self.collection().insert_one(data)
        # Update model with the generated MongoDB ID
        self.id = result.inserted_id
        return self

    # READ / GET BY ID
    @classmethod
    # Find a document by its MongoDB ID
    async def find_by_id(
        cls: Type[ModelType], _id: Union[str, ObjectId]
    ) -> Optional[ModelType]:
        # Convert string ID to ObjectId if necessary
        if isinstance(_id, str):
            _id = ObjectId(_id)
        # Find document in the database
        doc = await cls.collection().find_one({"_id": _id})
        # Return model instance if found, None otherwise
        return cls(**doc) if doc else None

    # READ / GET ALL (optional filters)
    @classmethod
    # Find all documents matching the filter criteria
    async def find_all(
        cls: Type[ModelType], filter: Dict[str, Any] = {}, limit: int = 100
    ) -> List[ModelType]:
        # Get cursor for filtered documents, sorted by creation date
        cursor = cls.collection().find(filter).sort("created_at", -1).limit(limit)
        # Convert documents to model instances
        return [cls(**doc) async for doc in cursor]

    # UPDATE (partial)
    # Update document fields in the database
    async def update(self: ModelType, updates: Dict[str, Any]) -> ModelType:
        # Add last update timestamp
        updates["updated_at"] = datetime.utcnow()
        # Update document in database
        await self.collection().update_one({"_id": self.id}, {"$set": updates})
        # Update model instance with new values
        for key, value in updates.items():
            setattr(self, key, value)
        return self

    # DELETE
    # Delete document from the database
    async def delete(self: ModelType) -> bool:  # type: ignore
        # Delete document by ID
        result = await self.collection().delete_one({"_id": self.id})
        # Return True if document was deleted
        return result.deleted_count == 1

    # READ
    @classmethod
    # Find a single document matching the filter criteria
    async def find_one(
        cls: Type[ModelType], filter: Dict[str, Any]
    ) -> Optional[ModelType]:
        # Find document in database
        doc = await cls.collection().find_one(filter)
        # Return model instance if found, None otherwise
        return cls(**doc) if doc else None
