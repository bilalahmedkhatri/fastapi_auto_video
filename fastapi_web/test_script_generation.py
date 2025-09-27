 #!/usr/bin/env python3

"""
Test the script generation directly
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from video_builder.script_generator import ScriptGenerator, ScriptType

load_dotenv()

def test_script_generation():
    """Test script generation directly"""
    print("Testing script generation...")
    
    try:
        generator = ScriptGenerator()
        print("✅ ScriptGenerator initialized")
        
        # Test with simple prompt
        scripts = generator.generate_multiple_scripts(
            user_prompt="Benefits of renewable energy",
            script_types=[ScriptType.SHORT],
            voiceover_language="English",
            category="Education",
            user="test_user"
        )
        
        print(f"✅ Generated {len(scripts)} scripts")
        
        if scripts:
            script = scripts[0]
            print(f"📝 Sample script title: {script.title}")
            print(f"📝 Sample script content (first 100 chars): {script.voiceover_script[:100]}...")
        else:
            print("❌ No scripts were generated")
            
        return len(scripts) > 0
        
    except Exception as e:
        print(f"❌ Error during script generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_script_generation()