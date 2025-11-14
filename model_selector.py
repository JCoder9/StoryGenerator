"""
Intelligent Model Selection System
Detects hardware capabilities and selects best model that will work
"""

import psutil
import platform
import os
from typing import Dict, List, Tuple


class ModelSelector:
    """Automatically select best story model based on available hardware"""
    
    # Model database with size, quality, and requirements
    # NOTE: Only includes models compatible with transformers 4.30.2
    MODELS = [
        {
            "name": "gpt2-large",
            "size_gb": 3.0,
            "quality_score": 75,
            "ram_required_gb": 5.5,
            "description": "Largest GPT-2, best for storytelling",
            "strengths": ["solid coherence", "creative prose", "widely supported"],
            "type": "causal"
        },
        {
            "name": "gpt2-medium",
            "size_gb": 1.5,
            "quality_score": 55,
            "ram_required_gb": 3.5,
            "description": "Medium GPT-2, balanced",
            "strengths": ["balanced performance", "stable", "fast"],
            "type": "causal"
        },
        {
            "name": "gpt2",
            "size_gb": 0.5,
            "quality_score": 45,
            "ram_required_gb": 2.0,
            "description": "Base GPT-2, most compatible",
            "strengths": ["very fast", "minimal RAM", "always works"],
            "type": "causal"
        },
        {
            "name": "distilgpt2",
            "size_gb": 0.35,
            "quality_score": 35,
            "ram_required_gb": 1.5,
            "description": "Smallest model, emergency fallback",
            "strengths": ["extremely fast", "tiny footprint", "emergency fallback"],
            "type": "causal"
        }
    ]
    
    @staticmethod
    def get_system_info() -> Dict:
        
        # Get total RAM
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # Get available RAM (more important than total)
        available_ram_gb = psutil.virtual_memory().available / (1024**3)
        
        # Get CPU info
        cpu_count = psutil.cpu_count(logical=False)  # Physical cores
        cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 0
        
        # Get platform info
        system = platform.system()
        machine = platform.machine()
        
        # Detect if it's an old Mac (be more nuanced)
        is_old_mac = False
        mac_year_estimate = None
        if system == "Darwin":
            mac_ver = platform.mac_ver()[0]
            # macOS version → approximate Mac era
            # 10.14 (Mojave) = 2012-2018 Macs
            # 10.15 (Catalina) = 2012-2019 Macs
            # 11.x (Big Sur) = 2013-2020 Macs
            # 12.x+ (Monterey+) = 2015+ Macs
            if mac_ver:
                major_ver = int(mac_ver.split('.')[0])
                if major_ver < 11:
                    is_old_mac = True
                    mac_year_estimate = "2012-2018"
                elif major_ver == 11:
                    # Big Sur - could be old or newish
                    # Conservative if available RAM is low
                    if available_ram_gb < 8:
                        is_old_mac = True
                    mac_year_estimate = "2013-2020"
                else:
                    mac_year_estimate = "2015+"
        
        # Estimate usable RAM for models (leave buffer for OS)
        # More RAM = smaller buffer percentage needed
        if ram_gb >= 16:
            os_buffer_gb = 3.0  # 16GB+ systems can spare more
        elif ram_gb >= 12:
            os_buffer_gb = 2.5
        else:
            os_buffer_gb = 2.0  # Tight on <12GB systems
        
        usable_ram_gb = max(0, available_ram_gb - os_buffer_gb)
        
        return {
            "total_ram_gb": ram_gb,
            "available_ram_gb": available_ram_gb,
            "usable_ram_gb": usable_ram_gb,
            "os_buffer_gb": os_buffer_gb,
            "cpu_cores": cpu_count,
            "cpu_freq_mhz": cpu_freq,
            "system": system,
            "machine": machine,
            "is_old_mac": is_old_mac,
            "mac_year_estimate": mac_year_estimate,
            "platform": f"{system} {machine}"
        }
    
    @staticmethod
    def get_compatible_models(system_info: Dict) -> List[Dict]:
        """Get models that will work on this system"""
        
        usable_ram = system_info["usable_ram_gb"]
        
        compatible = []
        for model in ModelSelector.MODELS:
            if model["ram_required_gb"] <= usable_ram:
                compatible.append(model)
        
        # Sort by quality score (best first)
        compatible.sort(key=lambda m: m["quality_score"], reverse=True)
        
        return compatible
    
    @staticmethod
    def select_best_model(prefer_instruct: bool = True) -> Tuple[str, Dict]:
        """
        Automatically select the best model for this system
        
        Args:
            prefer_instruct: If True, prefer instruction-tuned models over causal
            
        Returns:
            Tuple of (model_name, model_info)
        """
        system_info = ModelSelector.get_system_info()
        compatible = ModelSelector.get_compatible_models(system_info)
        
        if not compatible:
            # Absolute emergency fallback
            print("⚠️  WARNING: Very limited RAM detected")
            print("   Using smallest possible model (distilgpt2)")
            return "distilgpt2", ModelSelector.MODELS[-1]
        
        # Print system detection
        print("\n🖥️  SYSTEM DETECTION")
        print(f"   Platform: {system_info['platform']}")
        print(f"   Total RAM: {system_info['total_ram_gb']:.1f} GB")
        print(f"   Available RAM: {system_info['available_ram_gb']:.1f} GB")
        print(f"   OS Buffer: {system_info['os_buffer_gb']:.1f} GB")
        print(f"   Usable for models: {system_info['usable_ram_gb']:.1f} GB")
        print(f"   CPU cores: {system_info['cpu_cores']}")
        
        if system_info.get('mac_year_estimate'):
            print(f"   Mac Era: ~{system_info['mac_year_estimate']}")
        
        if system_info['is_old_mac']:
            print(f"   ⚠️  Older Mac detected - will validate model choice")
        
        print(f"\n📊 COMPATIBLE MODELS: {len(compatible)}")
        
        # Show top 3 compatible models
        for i, model in enumerate(compatible[:3], 1):
            print(f"   {i}. {model['name']}")
            print(f"      Quality: {model['quality_score']}/100 | RAM: {model['ram_required_gb']}GB | Size: {model['size_gb']}GB")
        
        # Select best model with preference logic
        best_model = None
        
        if prefer_instruct:
            # Try to find best instruct model first
            instruct_models = [m for m in compatible if m["type"] == "instruct"]
            if instruct_models:
                best_model = instruct_models[0]
                print(f"\n✅ SELECTED: {best_model['name']} (instruct model)")
            else:
                # Fall back to best causal model
                best_model = compatible[0]
                print(f"\n✅ SELECTED: {best_model['name']} (best available causal model)")
        else:
            # Just use highest quality compatible model
            best_model = compatible[0]
            print(f"\n✅ SELECTED: {best_model['name']}")
        
        print(f"   Quality Score: {best_model['quality_score']}/100")
        print(f"   Description: {best_model['description']}")
        print(f"   Strengths: {', '.join(best_model['strengths'])}")
        print(f"   RAM Required: {best_model['ram_required_gb']} GB (You have {system_info['usable_ram_gb']:.1f} GB)")
        
        # Smarter safety check for old Macs - only override if RAM is tight
        safety_margin = system_info['usable_ram_gb'] - best_model['ram_required_gb']
        
        if system_info['is_old_mac'] and safety_margin < 0.5:
            # Very tight on RAM - use smaller model
            print(f"\n⚠️  SAFETY OVERRIDE: Only {safety_margin:.1f}GB safety margin on older Mac")
            # Find a model with at least 1GB safety margin
            safe_models = [m for m in compatible 
                          if (system_info['usable_ram_gb'] - m['ram_required_gb']) >= 1.0]
            if safe_models:
                best_model = safe_models[0]
                print(f"   Using safer model: {best_model['name']} ({best_model['ram_required_gb']}GB)")
        
        return best_model["name"], best_model
    
    @staticmethod
    def get_fallback_chain(primary_model: str) -> List[str]:
        """
        Get fallback models in order if primary fails
        
        Args:
            primary_model: The model that failed
            
        Returns:
            List of model names to try in order
        """
        system_info = ModelSelector.get_system_info()
        compatible = ModelSelector.get_compatible_models(system_info)
        
        # Remove the failed model
        compatible = [m for m in compatible if m["name"] != primary_model]
        
        # Return names in quality order
        return [m["name"] for m in compatible]
    
    @staticmethod
    def print_recommendation_report():
        """Print detailed hardware analysis and model recommendations"""
        
        system_info = ModelSelector.get_system_info()
        compatible = ModelSelector.get_compatible_models(system_info)
        
        print("\n" + "=" * 70)
        print("🎯 MODEL RECOMMENDATION REPORT")
        print("=" * 70)
        
        print(f"\n📋 SYSTEM SPECIFICATIONS:")
        print(f"   Total RAM: {system_info['total_ram_gb']:.1f} GB")
        print(f"   Available RAM: {system_info['available_ram_gb']:.1f} GB")
        print(f"   Usable for AI: {system_info['usable_ram_gb']:.1f} GB (after OS overhead)")
        print(f"   CPU Cores: {system_info['cpu_cores']}")
        print(f"   Platform: {system_info['platform']}")
        
        if system_info['is_old_mac']:
            print(f"   ⚠️  Older Mac detected - recommend conservative settings")
        
        print(f"\n✅ MODELS YOU CAN USE: {len(compatible)}/{len(ModelSelector.MODELS)}")
        print("\nRanked by quality:")
        
        for i, model in enumerate(compatible, 1):
            print(f"\n{i}. {model['name']}")
            print(f"   Quality: {'█' * (model['quality_score'] // 10)} {model['quality_score']}/100")
            print(f"   Size: {model['size_gb']} GB")
            print(f"   RAM needed: {model['ram_required_gb']} GB")
            print(f"   Type: {model['type']}")
            print(f"   Best for: {', '.join(model['strengths'])}")
        
        if len(compatible) < len(ModelSelector.MODELS):
            incompatible = [m for m in ModelSelector.MODELS if m not in compatible]
            print(f"\n❌ MODELS TOO LARGE FOR YOUR SYSTEM: {len(incompatible)}")
            for model in incompatible:
                print(f"   • {model['name']} (needs {model['ram_required_gb']} GB, you have {system_info['usable_ram_gb']:.1f} GB)")
        
        print("\n" + "=" * 70)
        print("💡 RECOMMENDATION:")
        best_name, best_model = ModelSelector.select_best_model()
        print(f"   Use: {best_name}")
        print(f"   This provides the best quality your system can handle.")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    # Test the selector
    ModelSelector.print_recommendation_report()
