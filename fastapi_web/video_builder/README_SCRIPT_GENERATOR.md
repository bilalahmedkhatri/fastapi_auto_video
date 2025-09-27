# Multi-Script Video Generator

A comprehensive solution for generating multiple video script variations with user selection, editing, and merging capabilities.

## Features

### ✅ Core Features Implemented

1. **Multi-Script Generation**
   - Generate 3+ different script variations from a single prompt
   - Support for different script types: Short, Medium, Long, Educational, Storytelling, Entertaining
   - Each script optimized for different durations and styles

2. **Script Selection Interface**
   - Interactive web interface to view and compare scripts
   - Preview scripts with metadata (duration, word count, tags)
   - Easy selection process

3. **Regeneration Capability**
   - Option to regenerate if user doesn't like initial scripts
   - Uses alternative prompting for varied results
   - Maintains script type preferences

4. **Script Editing**
   - Edit selected scripts with natural language instructions
   - Maintains script structure while applying changes
   - Real-time preview of edited content

5. **Script Merging**
   - Combine multiple scripts into one cohesive script
   - Intelligent merging with optional user instructions
   - Maintains flow and coherence

### 🎬 Script Types Available

| Type | Duration | Word Count | Description |
|------|----------|------------|-------------|
| **Short** | 30-45 seconds | 75-115 words | Quick, punchy, attention-grabbing |
| **Medium** | 1-2 minutes | 150-300 words | Balanced information with examples |
| **Long** | 3-5 minutes | 450-750 words | In-depth exploration and analysis |
| **Educational** | 2-4 minutes | 300-600 words | Clear teaching approach with structure |
| **Storytelling** | 2-3 minutes | 300-450 words | Narrative with emotional engagement |
| **Entertaining** | 1-2 minutes | 150-300 words | Fun, engaging, humorous content |

## File Structure

```
fastapi_web/
├── video_builder/
│   ├── script_generator.py          # Core script generation logic
│   ├── script_api.py               # FastAPI endpoints
│   ├── enhanced_video_builder.py   # Integration with existing video system
│   └── generated_scripts/          # Saved scripts directory
├── script_generator_demo.html      # Web interface demo
└── main.py                        # Updated main FastAPI app
```

## API Endpoints

### POST /script-generator/generate
Generate multiple script variations from a prompt.

**Request:**
```json
{
  "user_prompt": "AI in Education",
  "script_types": ["short", "medium", "long"],
  "voiceover_language": "English",
  "category": "Technology",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully generated 3 script variations.",
  "scripts": [...],
  "total_scripts": 3
}
```

### POST /script-generator/regenerate
Regenerate scripts with alternative approach.

### POST /script-generator/edit/{script_index}
Edit a specific script with instructions.

**Request:**
```json
{
  "script_index": 0,
  "edit_instructions": "Make it more casual and friendly",
  "user_id": "user123"
}
```

### POST /script-generator/merge
Merge multiple scripts into one.

**Request:**
```json
{
  "script_indices": [0, 2],
  "merge_instructions": "Combine the introduction from script 1 with the conclusion from script 2",
  "user_id": "user123"
}
```

### POST /script-generator/select/{script_index}
Select a script for video generation.

### GET /script-generator/current/{user_id}
Get current scripts for a user.

### GET /script-generator/script-types
Get available script types and descriptions.

## Usage Examples

### 1. Command Line Interface

```python
from video_builder.script_generator import ScriptGenerator, ScriptType

generator = ScriptGenerator()

# Generate multiple scripts
scripts = generator.generate_multiple_scripts(
    user_prompt="The Future of Electric Vehicles",
    script_types=[ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.EDUCATIONAL],
    voiceover_language="English",
    category="Technology"
)

# Display options
for i, script in enumerate(scripts, 1):
    print(f"Script {i}: {script.title}")
    print(f"Type: {script.script_type.value}")
    print(f"Duration: {script.duration_estimate}")
    print(f"Preview: {script.voiceover_script[:100]}...")
    print("-" * 50)

# Edit a script
edited_script = generator.edit_script(
    script_option=scripts[0],
    edit_instructions="Make it more technical and add statistics"
)

# Merge scripts
merged_script = generator.merge_scripts(
    script_options=[scripts[0], scripts[2]],
    merge_instructions="Create a balanced version combining both approaches"
)
```

### 2. Interactive CLI

```bash
cd fastapi_web/video_builder
python script_generator.py
```

This launches an interactive command-line interface where you can:
- Generate multiple scripts
- View and compare options
- Edit scripts with natural language instructions
- Merge multiple scripts
- Regenerate if not satisfied

### 3. Web Interface

1. Start the FastAPI server:
```bash
cd fastapi_web
fastapi dev main.py
```

2. Open `script_generator_demo.html` in your browser
3. Enter your video topic and select script types
4. Generate, edit, merge, and select scripts interactively

### 4. Enhanced Video Builder

```python
from video_builder.enhanced_video_builder import EnhancedVideoBuilder

builder = EnhancedVideoBuilder()

# Generate script options
scripts = builder.generate_script_options(
    user_prompt="Climate Change Solutions",
    script_types=[ScriptType.EDUCATIONAL, ScriptType.STORYTELLING]
)

# Interactive selection (command line)
selected_script = builder.get_user_script_selection(scripts)

# Create video from selected script
video_path = builder.create_video_from_script(
    selected_script=selected_script,
    voice="am_puck"
)
```

## Integration with Existing Video Builder

The system integrates seamlessly with the existing `video_builder.py`:

1. **Script Selection**: Choose from multiple generated scripts
2. **Format Compatibility**: Scripts are formatted to work with existing AI data structure
3. **Video Generation**: Selected script feeds into existing video creation pipeline
4. **Metadata Preservation**: Tags, categories, and descriptions maintained throughout

## Configuration

### Environment Variables
Ensure these are set in your `.env` file:
- `QWEN_3_KEY_OPENROUTER`: For AI text generation
- `GOOGLE_CUSTOM_SEARCH_API_KEY`: For image search
- `GOOGLE_SEARCH_ENGINE`: For image search

### Script Types Customization
Add new script types by extending the `ScriptType` enum in `script_generator.py`:

```python
class ScriptType(Enum):
    # Existing types...
    TUTORIAL = "tutorial"
    NEWS = "news"
    REVIEW = "review"
```

## Error Handling

The system includes comprehensive error handling:
- AI generation failures with fallback options
- Invalid input validation
- Network error recovery
- Graceful degradation when services are unavailable

## Logging

All operations are logged with appropriate levels:
- Info: Normal operations and successful generations
- Warning: Non-critical issues (missing API keys, etc.)
- Error: Failed operations with detailed error messages

## Future Enhancements

Potential improvements for the system:

1. **Advanced Script Analytics**
   - Readability scores
   - Engagement prediction
   - SEO optimization scores

2. **Template System**
   - Pre-defined script templates
   - Industry-specific formats
   - Brand voice customization

3. **Collaborative Features**
   - Multi-user script editing
   - Version control for scripts
   - Team review and approval workflows

4. **Performance Optimization**
   - Caching for similar prompts
   - Batch script generation
   - Background processing

5. **Integration Enhancements**
   - Direct video generation from selected script
   - Automated A/B testing of script variations
   - Analytics on script performance

## Troubleshooting

### Common Issues

1. **Scripts not generating**
   - Check API keys in environment variables
   - Verify network connectivity
   - Check logs for specific error messages

2. **Web interface not loading scripts**
   - Ensure FastAPI server is running on port 8000
   - Check browser console for JavaScript errors
   - Verify CORS settings in main.py

3. **Edit/Merge operations failing**
   - Ensure user has generated scripts first
   - Check script indices are valid
   - Verify edit instructions are clear and specific

### Debug Mode

Enable debug logging by setting log level to DEBUG:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues or questions:
1. Check the logs directory for error details
2. Verify all dependencies are installed
3. Ensure environment variables are properly set
4. Review the API response format matches expectations

The system is designed to be robust and user-friendly, providing multiple pathways for script generation and customization to meet diverse video creation needs.
