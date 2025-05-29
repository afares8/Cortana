from typing import Dict, List, Optional, Any, TypeVar, Generic, Type, Union
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class InMemoryDB(Generic[T]):
    """
    A simple in-memory database for development and testing.
    """
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.data: Dict[int, T] = {}
        self.counter = 1

    def get(self, id: int) -> Optional[T]:
        """Get an item by ID."""
        return self.data.get(id)

    def get_multi(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get multiple items with optional filtering."""
        items = list(self.data.values())
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    items = [item for item in items if getattr(item, key) == value]
        
        return items[skip : skip + limit]

    def create(self, *, obj_in: BaseModel) -> T:
        """Create a new item."""
        db_obj = self.model_class(**obj_in.model_dump())
        db_obj.id = self.counter
        self.data[self.counter] = db_obj
        self.counter += 1
        return db_obj

    def update(self, *, id: int, obj_in: Union[BaseModel, Dict[str, Any]]) -> Optional[T]:
        """Update an existing item."""
        db_obj = self.get(id)
        if db_obj is None:
            return None
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.data[id] = db_obj
        return db_obj

    def remove(self, *, id: int) -> Optional[T]:
        """Remove an item."""
        if id in self.data:
            obj = self.data[id]
            del self.data[id]
            return obj
        return None
