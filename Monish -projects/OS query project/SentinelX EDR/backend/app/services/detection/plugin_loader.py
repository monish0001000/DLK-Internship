"""
SentinelX EDR - Plugin Loader
==============================
Dynamically loads and manages custom detection plugins.
"""

import os
import importlib.util
import inspect
import logging
from typing import List, Dict, Any

from app.plugins.base_plugin import BaseDetectorPlugin

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins: List[BaseDetectorPlugin] = []
        
    def load_plugins(self, plugin_dir: str) -> int:
        """Discover and load all plugins in the given directory."""
        if not os.path.exists(plugin_dir):
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            return 0
            
        count = 0
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(plugin_dir, filename)
                module_name = filename[:-3]
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find classes that inherit from BaseDetectorPlugin
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BaseDetectorPlugin) and obj != BaseDetectorPlugin:
                                plugin_instance = obj()
                                self.plugins.append(plugin_instance)
                                logger.info(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
                                count += 1
                except Exception as e:
                    logger.error(f"Failed to load plugin {filename}: {e}")
                    
        return count
        
    def evaluate_event(self, event: Dict[str, Any], category: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the event through all loaded plugins."""
        matches = []
        for plugin in self.plugins:
            try:
                result = plugin.detect(event, category, context)
                if result:
                    # If the plugin returned a single dict, wrap it in a list
                    if isinstance(result, dict):
                        result = [result]
                    matches.extend(result)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed during evaluation: {e}")
                
        return matches
