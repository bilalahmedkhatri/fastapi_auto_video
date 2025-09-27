# Script Generator Components

This directory contains reusable components extracted from the video-builder page, organized by functionality.

## Components Overview

### 1. InputForm.js
**Purpose**: Initial form for script generation input
**Props**:
- `formData`: Object containing userPrompt, category, language, scriptTypes
- `scriptTypeConfigs`: Configuration object for different script types
- `onInputChange`: Handler for form input changes
- `onToggleScriptType`: Handler for script type selection
- `onGenerateScripts`: Handler for script generation
- `loading`: Boolean indicating loading state

### 2. LoadingState.js
**Purpose**: Loading indicator with time-based messages
**Props**:
- `loadingElapsed`: Number of seconds elapsed during loading

### 3. ScriptsGrid.js
**Purpose**: Display generated scripts in a grid layout with actions
**Props**:
- `scripts`: Array of generated script objects
- `selectedScriptIndex`: Index of currently selected script
- `generationDuration`: Time taken to generate scripts
- `loading`: Boolean indicating loading state
- `onSelectScript`: Handler for script selection
- `onDirectEdit`: Handler for direct script editing
- `onAIEdit`: Handler for AI-assisted editing
- `onSocialMedia`: Handler for social media generation
- `onRegenerateScripts`: Handler for regenerating scripts
- `onEditSelected`: Handler for editing mode
- `onMergeScripts`: Handler for merging mode
- `onGenerateSocialMedia`: Handler for social media generation
- `onSelectScriptForVideo`: Handler for video creation
- `onBackToInput`: Handler for returning to input form

### 4. ScriptEditor.js
**Purpose**: Interface for editing scripts (direct or AI-assisted)
**Props**:
- `selectedScript`: Script object being edited
- `selectedScriptIndex`: Index of selected script
- `editMode`: String indicating edit mode ('direct' or 'instructions')
- `editedScriptContent`: Current edited content
- `editInstructions`: AI edit instructions
- `loading`: Boolean indicating loading state
- `onEditModeChange`: Handler for changing edit mode
- `onEditedContentChange`: Handler for content changes
- `onEditInstructionsChange`: Handler for instruction changes
- `onSaveDirectEdit`: Handler for saving direct edits
- `onApplyAIEdit`: Handler for applying AI edits
- `onCancel`: Handler for canceling edit

### 5. ScriptMerger.js
**Purpose**: Interface for merging multiple scripts
**Props**:
- `scripts`: Array of all scripts
- `selectedForMerge`: Array of indices selected for merging
- `mergeInstructions`: Instructions for merge process
- `loading`: Boolean indicating loading state
- `onToggleScriptSelection`: Handler for script selection
- `onMergeInstructionsChange`: Handler for instruction changes
- `onMergeScripts`: Handler for executing merge
- `onCancel`: Handler for canceling merge

### 6. SocialMediaContent.js
**Purpose**: Display and manage social media content generation
**Props**:
- `socialMediaContent`: Object containing platform-specific content
- `loading`: Boolean indicating loading state
- `onRegenerateSocialMedia`: Handler for regenerating content
- `onBackToScripts`: Handler for returning to scripts view

## Features
- **Dark Mode Support**: All components include dark mode styling
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Accessibility**: Proper labeling and keyboard navigation
- **Error Handling**: Graceful handling of missing data
- **Copy to Clipboard**: Easy sharing of generated content
- **Loading States**: Visual feedback during operations

## Usage
```javascript
import {
  InputForm,
  LoadingState,
  ScriptsGrid,
  ScriptEditor,
  ScriptMerger,
  SocialMediaContent
} from '@/components/ScriptGenerator';
```

## Benefits of Component Extraction
1. **Reusability**: Components can be used in other parts of the application
2. **Maintainability**: Easier to update and debug individual components
3. **Testing**: Each component can be unit tested independently
4. **Code Organization**: Cleaner separation of concerns
5. **Performance**: Smaller bundle sizes and potential for lazy loading
6. **Team Collaboration**: Multiple developers can work on different components