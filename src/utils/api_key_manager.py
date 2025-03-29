import os
import json
import platform
from pathlib import Path

class ApiKeyManager:
    """Handles storing and retrieving the API key"""
    
    ENV_KEY_NAME = "GEMINI_API_KEY"
    
    @classmethod
    def get_api_key(cls):
        """
        Get the API key from environment variables or config file
        Returns the API key or empty string if not found
        """
        # First try environment variable
        api_key = os.getenv(cls.ENV_KEY_NAME, "")
        if api_key:
            return api_key
            
        # If not in environment, try config file
        config_file = cls._get_config_path()
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
            except Exception:
                return ""
                
        return ""
    
    @classmethod
    def save_api_key(cls, api_key, save_to_environment=True):
        """
        Save the API key to environment variables and/or config file
        Returns True if successful, False otherwise
        """
        success = False
        
        # Always store in memory for current session
        os.environ[cls.ENV_KEY_NAME] = api_key
        
        # If save_to_environment is True, save to config file
        if save_to_environment:
            config_file = cls._get_config_path()
            
            # Create directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Load existing config if any
                config = {}
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                
                # Update config with new API key
                config['api_key'] = api_key
                
                # Save updated config
                with open(config_file, 'w') as f:
                    json.dump(config, f)
                    
                success = True
            except Exception:
                success = False
        
        return success
    
    @classmethod
    def _get_config_path(cls):
        """Get the path to the config file based on platform"""
        system = platform.system()
        
        # Get base path based on operating system
        home = str(Path.home())
        if system == "Windows":
            appdata = os.getenv('APPDATA')
            base_path = Path(appdata if appdata else home)
        elif system == "Darwin":  # macOS
            base_path = Path(home) / "Library" / "Application Support"
        else:  # Linux and others
            base_path = Path(home) / ".config"
            
        return base_path / "RisonCopyChecker" / "config.json"