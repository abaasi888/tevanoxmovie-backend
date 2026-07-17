from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/categories")
async def get_all_categories(
    type: Optional[str] = Query(None, regex="^(movie|series|music)$"),
    parent_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    query = {}
    if type:
        query["type"] = type
    if parent_id:
        query["parent_id"] = parent_id
    if is_active is not None:
        query["is_active"] = is_active
    
    categories = await db.categories.find(query).sort("display_order", 1).to_list(length=100)
    
    result = []
    for cat in categories:
        subcategories = await db.categories.find({
            "parent_id": str(cat["_id"]),
            "is_active": True
        }).sort("display_order", 1).to_list(length=100)
        
        result.append({
            "id": str(cat["_id"]),
            "name": cat["name"],
            "slug": cat["slug"],
            "type": cat["type"],
            "parent_id": cat.get("parent_id"),
            "icon": cat.get("icon"),
            "color": cat.get("color"),
            "description": cat.get("description"),
            "is_active": cat.get("is_active", True),
            "display_order": cat.get("display_order", 0),
            "is_deletable": cat.get("is_deletable", True),
            "subcategories": [
                {
                    "id": str(sub["_id"]),
                    "name": sub["name"],
                    "slug": sub["slug"],
                    "icon": sub.get("icon"),
                    "color": sub.get("color"),
                    "is_active": sub.get("is_active", True)
                }
                for sub in subcategories
            ],
            "created_at": cat["created_at"]
        })
    
    return result

@router.post("/categories")
async def create_category(
    category_data: CategoryCreate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    existing = await db.categories.find_one({"slug": category_data.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Category with this slug already exists")
    
    category = {
        "name": category_data.name,
        "slug": category_data.slug,
        "type": category_data.type,
        "parent_id": category_data.parent_id,
        "icon": category_data.icon,
        "color": category_data.color,
        "description": category_data.description,
        "display_order": category_data.display_order,
        "is_active": True,
        "is_deletable": True,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.categories.insert_one(category)
    category["_id"] = str(result.inserted_id)
    
    return {"message": "Category created successfully", "category": category}

@router.put("/categories/{category_id}")
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    update_data = {k: v for k, v in category_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.categories.update_one({"_id": category_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category updated successfully"}

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    subcategories = await db.categories.find({"parent_id": category_id}).to_list(length=1)
    if subcategories:
        raise HTTPException(status_code=400, detail="Cannot delete category with subcategories")
    
    movies = await db.movies.find({"category_id": category_id}).to_list(length=1)
    if movies:
        raise HTTPException(status_code=400, detail="Cannot delete category with associated content")
    
    result = await db.categories.delete_one({"_id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}