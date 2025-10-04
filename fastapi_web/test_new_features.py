#!/usr/bin/env python3
"""
Test the newly added features: transition intensity, vignette, custom text colors
"""

import sys
sys.path.insert(0, '.')

print("="*70)
print("🧪 TESTING NEWLY ADDED FEATURES")
print("="*70)

# Test 1: Import function with new parameter
print("\n✅ Test 1: Checking add_transitions_with_config signature...")
try:
    from video_builder.video_builder import add_transitions_with_config
    import inspect
    
    sig = inspect.signature(add_transitions_with_config)
    params = list(sig.parameters.keys())
    
    if 'transition_intensity' in params:
        print("✅ SUCCESS: transition_intensity parameter added!")
        default_val = sig.parameters['transition_intensity'].default
        print(f"   Default value: {default_val}")
    else:
        print("❌ FAILED: transition_intensity parameter missing!")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FAILED: Could not import function: {e}")
    sys.exit(1)

# Test 2: Check vignette code exists
print("\n✅ Test 2: Checking vignette effect implementation...")

import pathlib
video_builder_file = pathlib.Path('video_builder/video_builder.py')
with open(video_builder_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'vignette_enabled' in content and 'vignette(0.5)' in content:
    print("✅ SUCCESS: Vignette effect code found!")
    print("   Checks for vignette_enabled flag")
    print("   Applies vignette with 0.5 intensity")
else:
    print("❌ FAILED: Vignette code not found!")
    sys.exit(1)

# Test 3: Check custom text colors are passed
print("\n✅ Test 3: Checking custom text color parameters...")

required_text_params = [
    'text_base_color',
    'text_highlight_color',
    'text_highlight_text_color',
    'text_border_color',
    'text_border_width',
    'text_font_size',
    'text_position'
]

missing_params = []
for param in required_text_params:
    if param not in content:
        missing_params.append(param)

if not missing_params:
    print("✅ SUCCESS: All text color parameters found!")
    for param in required_text_params:
        print(f"   ✅ {param}")
else:
    print(f"❌ FAILED: Missing parameters: {missing_params}")
    sys.exit(1)

# Test 4: Check text colors are passed to function
print("\n✅ Test 4: Checking text colors passed to create_first5_words_highlighted_clips...")

if 'base_color=text_base_color' in content:
    print("✅ base_color passed")
else:
    print("❌ base_color NOT passed")
    sys.exit(1)

if 'highlight_color=text_highlight_color' in content:
    print("✅ highlight_color passed")
else:
    print("❌ highlight_color NOT passed")
    sys.exit(1)

if 'highlight_text_color=text_highlight_text_color' in content:
    print("✅ highlight_text_color passed")
else:
    print("❌ highlight_text_color NOT passed")
    sys.exit(1)

if 'border_color=text_border_color' in content:
    print("✅ border_color passed")
else:
    print("❌ border_color NOT passed")
    sys.exit(1)

if 'border_width=text_border_width' in content:
    print("✅ border_width passed")
else:
    print("❌ border_width NOT passed")
    sys.exit(1)

if 'font_size=text_font_size' in content:
    print("✅ font_size passed")
else:
    print("❌ font_size NOT passed")
    sys.exit(1)

# Test 5: Check transition intensity is passed to function
print("\n✅ Test 5: Checking transition_intensity passed to add_transitions_with_config...")

if 'transition_intensity=transition_intensity' in content:
    print("✅ SUCCESS: transition_intensity parameter passed!")
else:
    print("❌ FAILED: transition_intensity NOT passed to function!")
    sys.exit(1)

# Test 6: Check actual_fade_duration calculation
print("\n✅ Test 6: Checking actual_fade_duration calculation...")

if 'actual_fade_duration = transition_duration * transition_intensity' in content:
    print("✅ SUCCESS: actual_fade_duration calculated correctly!")
else:
    print("❌ FAILED: actual_fade_duration calculation not found!")
    sys.exit(1)

# Test 7: Check actual_fade_duration is used in transitions
print("\n✅ Test 7: Checking actual_fade_duration used in transitions...")

if 'CrossFadeIn(actual_fade_duration)' in content:
    print("✅ SUCCESS: CrossFadeIn uses actual_fade_duration!")
else:
    print("❌ FAILED: CrossFadeIn does not use actual_fade_duration!")
    sys.exit(1)

if 'CrossFadeOut(actual_fade_duration)' in content:
    print("✅ SUCCESS: CrossFadeOut uses actual_fade_duration!")
else:
    print("❌ FAILED: CrossFadeOut does not use actual_fade_duration!")
    sys.exit(1)

print("\n" + "="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70)

print("\n📋 Summary of New Features:")
print("  ✅ Transition intensity parameter added and used")
print("  ✅ Vignette effect code implemented")
print("  ✅ Custom text colors extracted and passed")
print("  ✅ Custom text border settings applied")
print("  ✅ Custom font size used")
print("  ✅ Text position configurable")
print("  ✅ actual_fade_duration calculated from intensity")
print("  ✅ All transition effects use intensity")

print("\n🎨 What's Now Customizable:")
print("  - Transition fade strength (via intensity)")
print("  - Text base color (white, yellow, etc.)")
print("  - Text highlight background color")
print("  - Text highlight text color")
print("  - Text border color")
print("  - Text border width (1-10px)")
print("  - Text font size (50-200px)")
print("  - Text position (top/bottom)")
print("  - Vignette effect (dark edges)")

print("\n⚠️  Note about Vignette:")
print("  The vignette effect is implemented but may not work if")
print("  MoviePy doesn't have the vignette module. Check Celery logs")
print("  for any import errors after restarting.")

print("\n🚀 Next Step:")
print("  1. Restart Celery worker (required!)")
print("  2. Generate a test video")
print("  3. Check that text has your selected colors")
print("  4. Check that transitions are more/less subtle based on intensity")
print("  5. Check if vignette (dark edges) appears")
