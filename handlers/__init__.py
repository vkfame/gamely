import pkgutil
import importlib
import os
from aiogram import Router

def get_all_rts() -> Router:
    main_router = Router()
    
    current_dir = os.path.dirname(__file__)
    package_name = __package__ or __name__

    for loader, module_name, is_pkg in pkgutil.walk_packages([current_dir]):
        full_module_name = f"{package_name}.{module_name}" if package_name else module_name
        module = importlib.import_module(full_module_name)
        
        for item_name in dir(module):
            item = getattr(module, item_name)
            
            if (isinstance(item, Router) and 
                item is not main_router and 
                getattr(item, "__module__", None) == full_module_name):
                
                main_router.include_router(item)
                
    return main_router