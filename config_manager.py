"""
Configuration Manager for Story Generator Desktop App
Handles cross-platform user data storage
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Try to import appdirs, fall back to manual paths
try:
    import appdirs
    HAS_APPDIRS = True
except ImportError:
    HAS_APPDIRS = False
    print("⚠️  Warning: 'appdirs' not installed. Using fallback paths.")
    print("   Install with: pip install appdirs")


class ConfigManager:
    """Manages application configuration and user data paths"""
    
    APP_NAME = "StoryGenerator"
    APP_AUTHOR = "YourName"  # Change this to your name/company
    
    def __init__(self):
        self.data_dir = self._get_user_data_dir()
        self.cache_dir = self._get_cache_dir()
        self.config_file = os.path.join(self.data_dir, "config.json")
        
        # Create necessary directories
        self._ensure_directories()
        
        # Load or create config
        self.config = self._load_config()
    
    def _get_user_data_dir(self) -> str:
        """Get platform-appropriate user data directory"""
        if HAS_APPDIRS:
            return appdirs.user_data_dir(self.APP_NAME, self.APP_AUTHOR)
        else:
            # Fallback for common platforms
            home = Path.home()
            if os.name == 'nt':  # Windows
                return str(home / "AppData" / "Roaming" / self.APP_NAME)
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':  # macOS
                    return str(home / "Library" / "Application Support" / self.APP_NAME)
                else:  # Linux
                    return str(home / ".local" / "share" / self.APP_NAME)
            else:
                return str(home / ".storygenerator")
    
    def _get_cache_dir(self) -> str:
        """Get platform-appropriate cache directory"""
        if HAS_APPDIRS:
            return appdirs.user_cache_dir(self.APP_NAME, self.APP_AUTHOR)
        else:
            home = Path.home()
            if os.name == 'nt':  # Windows
                return str(home / "AppData" / "Local" / self.APP_NAME / "Cache")
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':  # macOS
                    return str(home / "Library" / "Caches" / self.APP_NAME)
                else:  # Linux
                    return str(home / ".cache" / self.APP_NAME)
            else:
                return str(home / ".storygenerator" / "cache")
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs = [
            self.data_dir,
            os.path.join(self.data_dir, "stories"),
            os.path.join(self.data_dir, "profiles"),
            os.path.join(self.data_dir, "exports"),
            self.cache_dir
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
        
        print(f"📁 User data directory: {self.data_dir}")
        print(f"📁 Cache directory: {self.cache_dir}\n")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print("✓ Configuration loaded")
                return config
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "version": "1.0.0",
            "model": "gpt2-large",
            "genre": "mystery",
            "use_enhanced_prompts": True,
            "low_power_mode": False,
            "auto_save": True,
            "max_stories": 50,
            "max_story_age_days": 90,
            "story_cleanup_enabled": True,
            "port": 5001,
            "theme": "fallout_green",
            "typing_speed": 30,
            "enable_sound": False
        }
        
        self.save_config(default_config)
        print("✓ Default configuration created")
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config:
            self.config = config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()
    
    def get_story_path(self, story_id: str) -> str:
        """Get full path for a story file"""
        return os.path.join(self.data_dir, "stories", f"{story_id}.json")
    
    def get_profile_path(self) -> str:
        """Get full path for player profiles file"""
        return os.path.join(self.data_dir, "profiles", "player_profiles.json")
    
    def get_all_story_paths(self) -> list:
        """Get paths to all saved stories"""
        story_dir = os.path.join(self.data_dir, "stories")
        if not os.path.exists(story_dir):
            return []
        
        return [
            os.path.join(story_dir, f)
            for f in os.listdir(story_dir)
            if f.endswith('.json')
        ]
    
    def cleanup_old_stories(self):
        """Remove old stories based on config settings"""
        if not self.get("story_cleanup_enabled", True):
            return
        
        import time
        
        max_stories = self.get("max_stories", 50)
        max_age_days = self.get("max_story_age_days", 90)
        
        story_dir = os.path.join(self.data_dir, "stories")
        if not os.path.exists(story_dir):
            return
        
        # Get all story files with their modification times
        stories = []
        for filename in os.listdir(story_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(story_dir, filename)
                mtime = os.path.getmtime(filepath)
                stories.append((filepath, mtime))
        
        # Sort by modification time (newest first)
        stories.sort(key=lambda x: x[1], reverse=True)
        
        # Remove stories beyond max count or max age
        removed_count = 0
        for i, (filepath, mtime) in enumerate(stories):
            age_days = (time.time() - mtime) / 86400
            
            if i >= max_stories or age_days > max_age_days:
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {filepath}: {e}")
        
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old stories")
    
    def export_story(self, story_id: str, export_path: Optional[str] = None) -> str:
        """Export a story to a file"""
        story_path = self.get_story_path(story_id)
        
        if not os.path.exists(story_path):
            raise FileNotFoundError(f"Story {story_id} not found")
        
        if not export_path:
            export_dir = os.path.join(self.data_dir, "exports")
            export_path = os.path.join(export_dir, f"{story_id}_export.json")
        
        import shutil
        shutil.copy2(story_path, export_path)
        
        return export_path
    
    def get_disk_usage(self) -> Dict[str, int]:
        """Get disk usage statistics"""
        def get_dir_size(path):
            total = 0
            try:
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
            except Exception:
                pass
            return total
        
        return {
            "stories_mb": get_dir_size(os.path.join(self.data_dir, "stories")) / 1024 / 1024,
            "profiles_mb": get_dir_size(os.path.join(self.data_dir, "profiles")) / 1024 / 1024,
            "cache_mb": get_dir_size(self.cache_dir) / 1024 / 1024,
            "total_mb": get_dir_size(self.data_dir) / 1024 / 1024
        }
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._create_default_config()
        print("✓ Configuration reset to defaults")
    
    def __str__(self):
        """String representation"""
        return f"ConfigManager(data_dir={self.data_dir}, cache_dir={self.cache_dir})"


# Singleton instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get or create global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# Example usage
if __name__ == "__main__":
    print("Story Generator - Configuration Manager Test\n")
    print("=" * 60)
    
    config = get_config_manager()
    
    print("\n📋 Current Configuration:")
    print(json.dumps(config.config, indent=2))
    
    print("\n💾 Disk Usage:")
    usage = config.get_disk_usage()
    print(f"  Stories: {usage['stories_mb']:.2f} MB")
    print(f"  Profiles: {usage['profiles_mb']:.2f} MB")
    print(f"  Cache: {usage['cache_mb']:.2f} MB")
    print(f"  Total: {usage['total_mb']:.2f} MB")
    
    print("\n📁 Story Files:")
    stories = config.get_all_story_paths()
    print(f"  Found {len(stories)} saved stories")
    
    print("\n✓ Configuration manager working correctly!")
