#!/usr/bin/env python3
"""
 EQ12 CRYPTO MODEL UPDATER
Automated system to download and update Coral Edge TPU models
Weekly model refresh for optimal performance
"""

import os
import json
import logging
import requests
import hashlib
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import zipfile
import tempfile


class CryptoModelUpdater:
    """
     Automated Coral TPU model updater for cryptocurrency analysis
    Downloads and installs latest quantized models
    """
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        
        # Configuration
        self.config = self._load_config(config_path)
        
        # Directories
        self.models_dir = "C:\\EQ12\\models\\crypto"
        self.backup_dir = "C:\\EQ12\\models\\backup"
        self.temp_dir = "C:\\EQ12\\temp\\models"
        
        # Model repository
        self.model_registry = {
            "price_trend_lstm": {
                "url": "https://github.com/EQ12/coral-crypto-models/releases/download/v1.0/price_trend_lstm_edgetpu.tflite",
                "hash": "sha256:placeholder_hash_1",
                "description": "LSTM model for price trend prediction",
                "version": "1.0"
            },
            "volatility_classifier": {
                "url": "https://github.com/EQ12/coral-crypto-models/releases/download/v1.0/volatility_classifier_edgetpu.tflite",
                "hash": "sha256:placeholder_hash_2",
                "description": "Volatility classification model",
                "version": "1.0"
            },
            "sentiment_analyzer": {
                "url": "https://github.com/EQ12/coral-crypto-models/releases/download/v1.0/sentiment_microbert_edgetpu.tflite",
                "hash": "sha256:placeholder_hash_3",
                "description": "MicroBERT sentiment analysis model",
                "version": "1.0"
            },
            "anomaly_detector": {
                "url": "https://github.com/EQ12/coral-crypto-models/releases/download/v1.0/anomaly_detector_edgetpu.tflite",
                "hash": "sha256:placeholder_hash_4",
                "description": "Market anomaly detection model",
                "version": "1.0"
            },
            "portfolio_optimizer": {
                "url": "https://github.com/EQ12/coral-crypto-models/releases/download/v1.0/portfolio_ev_edgetpu.tflite",
                "hash": "sha256:placeholder_hash_5",
                "description": "Portfolio EV optimization model",
                "version": "1.0"
            }
        }
        
        # Initialize directories
        self._setup_directories()
        
        self.logger.info(" EQ12 Crypto Model Updater initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        
        log_dir = "C:\\EQ12\\logs\\crypto\\models"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"model_updater_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load model updater configuration"""
        
        default_config = {
            "update_settings": {
                "auto_update": True,
                "check_frequency_days": 7,
                "backup_old_models": True,
                "verify_checksums": True
            },
            "sources": {
                "primary_repo": "https://github.com/EQ12/coral-crypto-models",
                "mirror_repo": "https://huggingface.co/EQ12/coral-crypto-models",
                "local_cache": True
            },
            "deployment": {
                "restart_services": True,
                "validate_models": True,
                "rollback_on_failure": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _setup_directories(self):
        """Setup model directories"""
        
        dirs = [self.models_dir, self.backup_dir, self.temp_dir]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    def check_model_versions(self) -> Dict[str, Dict[str, Any]]:
        """Check current vs available model versions"""
        
        version_status = {}
        
        for model_name, model_info in self.model_registry.items():
            current_version = self._get_current_model_version(model_name)
            available_version = model_info["version"]
            
            model_file = os.path.join(self.models_dir, f"{model_name}_edgetpu.tflite")
            
            version_status[model_name] = {
                "current_version": current_version,
                "available_version": available_version,
                "needs_update": current_version != available_version,
                "model_exists": os.path.exists(model_file),
                "description": model_info["description"]
            }
        
        return version_status
    
    def _get_current_model_version(self, model_name: str) -> str:
        """Get current version of installed model"""
        
        version_file = os.path.join(self.models_dir, f"{model_name}_version.json")
        
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    version_info = json.load(f)
                    return version_info.get("version", "unknown")
            except Exception:
                pass
        
        return "not_installed"
    
    def download_model(self, model_name: str, model_info: Dict[str, Any]) -> bool:
        """Download a specific model"""
        
        self.logger.info(f" Downloading model: {model_name}")
        
        try:
            # Create temporary file
            temp_file = os.path.join(self.temp_dir, f"{model_name}_temp.tflite")
            
            # Download model
            response = requests.get(model_info["url"], stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum if enabled
            if self.config["update_settings"]["verify_checksums"]:
                if not self._verify_checksum(temp_file, model_info["hash"]):
                    os.remove(temp_file)
                    self.logger.error(f" Checksum verification failed for {model_name}")
                    return False
            
            # Move to models directory
            final_path = os.path.join(self.models_dir, f"{model_name}_edgetpu.tflite")
            
            # Backup existing model if enabled
            if self.config["update_settings"]["backup_old_models"] and os.path.exists(final_path):
                self._backup_model(model_name, final_path)
            
            # Install new model
            os.rename(temp_file, final_path)
            
            # Save version info
            self._save_version_info(model_name, model_info)
            
            self.logger.info(f" Successfully updated model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f" Failed to download {model_name}: {e}")
            
            # Cleanup temp file
            temp_file = os.path.join(self.temp_dir, f"{model_name}_temp.tflite")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return False
    
    def _verify_checksum(self, file_path: str, expected_hash: str) -> bool:
        """Verify file checksum"""
        
        if expected_hash.startswith("placeholder"):
            # Skip verification for placeholder hashes
            return True
        
        try:
            hash_type, expected_value = expected_hash.split(":", 1)
            
            hasher = hashlib.new(hash_type)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            actual_hash = hasher.hexdigest()
            return actual_hash == expected_value
            
        except Exception as e:
            self.logger.error(f"Checksum verification error: {e}")
            return False
    
    def _backup_model(self, model_name: str, model_path: str):
        """Backup existing model"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{model_name}_backup_{timestamp}.tflite"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Copy model to backup directory
            import shutil
            shutil.copy2(model_path, backup_path)
            
            self.logger.info(f" Backed up model: {model_name} -> {backup_name}")
            
        except Exception as e:
            self.logger.error(f" Failed to backup {model_name}: {e}")
    
    def _save_version_info(self, model_name: str, model_info: Dict[str, Any]):
        """Save model version information"""
        
        version_file = os.path.join(self.models_dir, f"{model_name}_version.json")
        
        version_data = {
            "model_name": model_name,
            "version": model_info["version"],
            "description": model_info["description"],
            "installed_date": datetime.now().isoformat(),
            "source_url": model_info["url"],
            "hash": model_info["hash"]
        }
        
        try:
            with open(version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save version info for {model_name}: {e}")
    
    def validate_model(self, model_name: str) -> bool:
        """Validate model can be loaded"""
        
        model_path = os.path.join(self.models_dir, f"{model_name}_edgetpu.tflite")
        
        if not os.path.exists(model_path):
            return False
        
        try:
            # Try to load model with TFLite
            import tflite_runtime.interpreter as tflite
            
            interpreter = tflite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            
            # Basic validation - check input/output tensors
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            if not input_details or not output_details:
                return False
            
            self.logger.info(f" Model validation passed: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f" Model validation failed for {model_name}: {e}")
            return False
    
    def update_all_models(self) -> Dict[str, bool]:
        """Update all available models"""
        
        self.logger.info(" Starting model update process...")
        
        # Check versions
        version_status = self.check_model_versions()
        
        update_results = {}
        
        for model_name, status in version_status.items():
            if status["needs_update"] or not status["model_exists"]:
                self.logger.info(f" Updating {model_name}: {status['current_version']}  {status['available_version']}")
                
                model_info = self.model_registry[model_name]
                success = self.download_model(model_name, model_info)
                
                if success and self.config["deployment"]["validate_models"]:
                    success = self.validate_model(model_name)
                
                update_results[model_name] = success
                
            else:
                self.logger.info(f" {model_name} is up to date")
                update_results[model_name] = True
        
        # Summary
        successful_updates = sum(1 for success in update_results.values() if success)
        total_models = len(update_results)
        
        self.logger.info(f" Update complete: {successful_updates}/{total_models} models updated successfully")
        
        return update_results
    
    def rollback_model(self, model_name: str) -> bool:
        """Rollback model to previous backup"""
        
        self.logger.info(f" Rolling back model: {model_name}")
        
        # Find latest backup
        backup_pattern = f"{model_name}_backup_"
        backup_files = []
        
        for file in os.listdir(self.backup_dir):
            if file.startswith(backup_pattern) and file.endswith(".tflite"):
                backup_files.append(file)
        
        if not backup_files:
            self.logger.error(f" No backup found for {model_name}")
            return False
        
        # Get latest backup (sorted by timestamp)
        latest_backup = sorted(backup_files)[-1]
        backup_path = os.path.join(self.backup_dir, latest_backup)
        model_path = os.path.join(self.models_dir, f"{model_name}_edgetpu.tflite")
        
        try:
            import shutil
            shutil.copy2(backup_path, model_path)
            
            self.logger.info(f" Successfully rolled back {model_name} from {latest_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f" Rollback failed for {model_name}: {e}")
            return False
    
    def clean_old_backups(self, keep_count: int = 5):
        """Clean old model backups, keeping only recent ones"""
        
        self.logger.info(f" Cleaning old backups (keeping {keep_count} most recent)")
        
        # Group backups by model
        model_backups = {}
        
        for file in os.listdir(self.backup_dir):
            if file.endswith("_backup_" + file.split("_backup_")[-1]):
                model_name = file.split("_backup_")[0]
                if model_name not in model_backups:
                    model_backups[model_name] = []
                model_backups[model_name].append(file)
        
        # Clean each model's backups
        for model_name, backups in model_backups.items():
            # Sort by timestamp (newest first)
            backups.sort(reverse=True)
            
            # Remove old backups
            for old_backup in backups[keep_count:]:
                try:
                    os.remove(os.path.join(self.backup_dir, old_backup))
                    self.logger.info(f" Removed old backup: {old_backup}")
                except Exception as e:
                    self.logger.error(f"Failed to remove backup {old_backup}: {e}")
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get model update system status"""
        
        version_status = self.check_model_versions()
        
        return {
            "models_directory": self.models_dir,
            "backup_directory": self.backup_dir,
            "total_models": len(self.model_registry),
            "installed_models": sum(1 for status in version_status.values() if status["model_exists"]),
            "models_needing_update": sum(1 for status in version_status.values() if status["needs_update"]),
            "auto_update_enabled": self.config["update_settings"]["auto_update"],
            "last_check": datetime.now().isoformat(),
            "model_details": version_status
        }


def main():
    """Main model updater function"""
    
    print(" EQ12 Crypto Model Updater")
    
    updater = CryptoModelUpdater()
    
    # Display current status
    status = updater.get_update_status()
    print(f"\n Current Status:")
    print(f"Models Directory: {status['models_directory']}")
    print(f"Total Models: {status['total_models']}")
    print(f"Installed: {status['installed_models']}")
    print(f"Need Update: {status['models_needing_update']}")
    
    # Check for updates
    if status['models_needing_update'] > 0:
        print(f"\n Updating {status['models_needing_update']} models...")
        update_results = updater.update_all_models()
        
        # Display results
        print("\n Update Results:")
        for model_name, success in update_results.items():
            status_emoji = "" if success else ""
            print(f"{status_emoji} {model_name}")
    else:
        print("\n All models are up to date!")
    
    # Clean old backups
    updater.clean_old_backups()


if __name__ == "__main__":
    main()