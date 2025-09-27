# Generated Scripts Module Documentation

This module provides a comprehensive script management interface for AI-generated video scripts with multiple view modes, filtering, pagination, and status tracking.

## 📁 Folder Structure

```
app/generated-scripts/
├── page.js                 # Main page component
├── components/             # Reusable UI components
│   ├── index.js           # Component exports
│   ├── ScriptCard.js      # Grid view script card
│   ├── ScriptListItem.js  # List view script item
│   ├── KanbanCard.js      # Kanban view script card
│   ├── Pagination.js     # Pagination component
│   ├── Controls.js        # Search, filter, and view controls
│   └── EmptyState.js      # Empty state with onboarding
├── views/                 # View layout components
│   ├── index.js          # View exports
│   └── ViewComponents.js # Grid, List, and Kanban views
├── hooks/                 # Custom React hooks
│   ├── index.js          # Hook exports
│   └── useScripts.js     # Script management hooks
├── utils/                 # Utility functions
│   ├── index.js          # Utility exports
│   ├── api.js            # API functions
│   ├── helpers.js        # Helper functions
│   └── mockData.js       # Mock data generator
└── config/               # Configuration and constants
    ├── index.js          # Config exports
    └── constants.js      # App constants and configs
```

## 🔧 Core Components

### 1. **Main Page Component** (`page.js`)
- **Purpose**: Main entry point that orchestrates all functionality
- **Features**: Authentication, routing, state management
- **Dependencies**: All child components, hooks, and utilities

### 2. **Component Library** (`components/`)

#### **ScriptCard.js**
- Grid view component for script cards
- Shows script details, status, progress indicators, and actions
- Responsive design with hover effects

#### **ScriptListItem.js** 
- List view component for compact script display
- Horizontal layout optimized for scanning
- Shows essential script information inline

#### **KanbanCard.js**
- Kanban column component for workflow visualization
- Minimal design for status-based organization
- Quick action buttons

#### **Controls.js**
- Search, filter, sort, and view mode controls
- Active filter display with clear options
- Responsive layout adaptation

#### **Pagination.js**
- Smart pagination with ellipsis support
- Configurable page limits
- Page info display

#### **EmptyState.js**
- Onboarding experience for new users
- Filtered results empty state
- Getting started guides and tips

### 3. **View Components** (`views/`)

#### **GridView**
- Card-based layout (1-4 columns responsive)
- Rich visual information display
- Best for browsing and discovery

#### **ListView**
- Compact horizontal layout
- Information-dense display
- Best for quick scanning

#### **KanbanView**
- Status-based column organization
- Workflow visualization
- Best for progress tracking

### 4. **Custom Hooks** (`hooks/`)

#### **useScripts**
- Manages script data with filters and pagination
- Provides search, sort, filter state management
- Auto-refresh and error handling

#### **useViewMode**
- Persists view mode selection in localStorage
- Provides view mode switching logic

#### **useBulkSelection**
- Manages multiple script selection
- Provides bulk action capabilities

#### **useScriptActions**
- Handles script action execution
- Loading states and error handling

### 5. **Utilities** (`utils/`)

#### **api.js**
- API functions for script CRUD operations
- Mock data handling (replace with real API)
- Error handling and response processing

#### **helpers.js**
- Script action handlers
- Data formatting functions
- Export/import utilities
- Validation functions

#### **mockData.js**
- Generates realistic mock script data
- Configurable data sets for testing
- Consistent data structure

### 6. **Configuration** (`config/`)

#### **constants.js**
- Status configurations with colors and icons
- API endpoints and configuration
- View modes, sort options, filter options
- Pagination settings

## 🚀 Key Features

### **Multi-View Support**
- **Grid View**: Visual card layout with rich information
- **List View**: Compact table-like display
- **Kanban View**: Workflow-based column organization

### **Advanced Filtering & Search**
- Real-time search across title and description
- Status-based filtering
- Multiple sorting options (date, title, status, duration)
- Active filter display with individual clear options

### **Status Tracking System**
```
📝 Draft → ✅ Script Ready → 📱 Social Media → 🎤 Voiceover → 🎬 Video → 🎉 Complete
```

### **Smart Pagination**
- Configurable items per page
- Ellipsis for large page counts
- Page info display
- Keyboard navigation support

### **Theme Integration**
- Dark/light mode support via useTheme hook
- Consistent color schemes
- Smooth theme transitions

### **Progressive Enhancement**
- Empty states with onboarding
- Loading states with proper feedback
- Error handling with user-friendly messages
- Responsive design for all screen sizes

## 🎯 Usage Examples

### **Basic Import and Usage**
```javascript
// Import main page
import GeneratedScriptsPage from './generated-scripts/page';

// Import individual components
import { ScriptCard, Controls } from './generated-scripts/components';

// Import hooks
import { useScripts, useViewMode } from './generated-scripts/hooks';

// Import utilities
import { handleScriptAction, generateMockScripts } from './generated-scripts/utils';
```

### **Custom Hook Usage**
```javascript
const {
  scripts,
  loading,
  updateSearch,
  updateFilter,
  updateSort
} = useScripts({
  currentPage: 1,
  sortBy: 'recent',
  filterBy: 'all'
});
```

### **API Integration**
Replace mock functions in `utils/api.js` with actual API calls:

```javascript
// Replace this mock implementation
const fetchScripts = async (filters) => {
  const mockScripts = generateMockScripts();
  // ... mock logic
};

// With actual API call
const fetchScripts = async (filters) => {
  const response = await fetch('/api/scripts', {
    method: 'POST',
    body: JSON.stringify(filters)
  });
  return await response.json();
};
```

## 🔄 Data Flow

1. **Main Page** renders and initializes hooks
2. **useScripts Hook** manages state and triggers API calls
3. **API Utils** fetch and process data
4. **View Components** render data in selected format
5. **User Interactions** trigger state updates via hook functions
6. **State Changes** automatically trigger re-renders and data fetches

## 🎨 Design Principles

### **Modularity**
Each component has a single responsibility and clear interfaces

### **Reusability** 
Components are designed to be reused across different contexts

### **Maintainability**
Clear separation of concerns makes code easy to understand and modify

### **Performance**
Efficient state management and conditional rendering for optimal performance

### **Accessibility**
Semantic HTML, keyboard navigation, and screen reader support

## 🔮 Future Enhancements

- **Bulk Actions**: Select multiple scripts for batch operations
- **Advanced Filters**: Date ranges, tags, categories
- **Export/Import**: CSV/JSON export functionality
- **Real-time Updates**: WebSocket integration for live updates
- **Keyboard Shortcuts**: Power user navigation
- **Script Templates**: Predefined script structures
- **Collaboration**: Multi-user editing and comments

## 📝 Contributing

When adding new features:

1. Follow the established folder structure
2. Create corresponding components, hooks, or utilities
3. Update the index files for exports
4. Add proper TypeScript types (if migrating to TS)
5. Update this documentation

## 🐛 Troubleshooting

### **Common Issues**

1. **Import Errors**: Check index.js files for proper exports
2. **Hook Dependencies**: Ensure hooks are called in correct order
3. **API Integration**: Verify API endpoints match configuration
4. **Theme Issues**: Confirm ThemeProvider is properly configured

### **Debug Mode**
Enable console logging in development:
```javascript
const DEBUG = process.env.NODE_ENV === 'development';
if (DEBUG) console.log('Script data:', scripts);
```
