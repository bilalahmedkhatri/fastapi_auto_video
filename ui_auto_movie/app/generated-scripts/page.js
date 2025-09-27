'use client';

import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/components/ThemeProvider';
import { useRouter } from 'next/navigation';

// Import separated components
import Controls from './components/Controls';
import Pagination from './components/Pagination';
import EmptyState from './components/EmptyState';
import { GridView, ListView, KanbanView } from './views/ViewComponents';

// Import hooks and utilities
import { useScripts, useViewMode } from './hooks/useScripts';
import { handleScriptAction } from './utils/helpers';
import { VIEW_MODES, FILTER_OPTIONS, SORT_OPTIONS } from './config/constants';

const GeneratedScriptsPage = () => {
	const { isAuthenticated, isLoading, user } = useAuth();
	const { theme } = useTheme();
	const router = useRouter();

	// Use custom hooks for state management
	const {
		scripts,
		loading,
		totalPages,
		totalItems,
		currentPage,
		sortBy,
		filterBy,
		searchQuery,
		updateSort,
		updateFilter,
		updateSearch,
		updatePage,
		clearFilters,
		refresh
	} = useScripts();

	// Debug logging (can be removed in production)
	console.log('Generated Scripts Page - Scripts loaded:', scripts.length);

	const [viewMode, setViewMode] = useViewMode('grid');

	// Protect the route - for now, allow access without authentication
	useEffect(() => {
		// Note: Temporarily allowing access without authentication for testing
		// In production, uncomment the authentication check below:
		/*
		if (!isLoading && !isAuthenticated) {
			toast.error('Please login to access Generated Scripts');
			router.push('/login');
		}
		*/
	}, [isAuthenticated, isLoading, router]);

	// Handle script actions
	const onScriptAction = async (scriptId, action) => {
		const success = await handleScriptAction(scriptId, action, router);
		if (success) {
			// Optionally refresh the scripts list
			refresh();
		}
	};

	// Handle new script creation
	const handleNewScript = () => {
		console.log('🆕 New Script button clicked - starting fresh process');
		
		// Clear all localStorage items immediately
		try {
			localStorage.removeItem('video-builder-storage');
			localStorage.removeItem('generatedVoiceoverData');
			localStorage.removeItem('videoBuilderState');
			localStorage.removeItem('projectData');
			
			// Clear process states
			const processStateKey = 'video_builder_process_states';
			localStorage.removeItem(processStateKey);
			
			console.log('✅ All localStorage cleared');
		} catch (error) {
			console.error('❌ Error clearing localStorage:', error);
		}
		
		// Navigate with fresh flag
		router.push('/video-builder?fresh=true');
	};

	// Show loading spinner while checking authentication
	if (isLoading) {
		return (
			<div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
				<div className="text-center">
					<LoadingSpinner />
					<p className="mt-4 text-gray-600 dark:text-gray-400">Checking authentication...</p>
				</div>
			</div>
		);
	}

	// Allow access without authentication for now
	// In production, uncomment this check:
	/*
	if (!isAuthenticated) {
		return null;
	}
	*/

	// Check if we have active filters
	const hasActiveFilters = searchQuery || filterBy !== FILTER_OPTIONS.ALL || sortBy !== SORT_OPTIONS.RECENT;

	return (
		<div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				{/* Header */}
				<div className="mb-8">
					<h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
						📚 Generated Scripts
					</h1>
					<p className="text-gray-600 dark:text-gray-400">
						Manage your AI-generated video scripts and track their production progress
					</p>
				</div>

				{/* Controls */}
				<Controls
					searchQuery={searchQuery}
					onSearchChange={updateSearch}
					filterBy={filterBy}
					onFilterChange={updateFilter}
					sortBy={sortBy}
					onSortChange={updateSort}
					viewMode={viewMode}
					onViewModeChange={setViewMode}
					onNewScript={handleNewScript}
					totalItems={totalItems}
				/>

				{/* Content */}
				{loading ? (
					<div className="flex justify-center py-12">
						<LoadingSpinner message="Loading scripts..." />
					</div>
				) : scripts.length === 0 ? (
					<EmptyState
						hasFilters={hasActiveFilters}
						searchQuery={searchQuery}
						filterBy={filterBy}
						onNewScript={handleNewScript}
						onClearFilters={clearFilters}
					/>
				) : (
					<>
						{/* Results Info */}
						<div className="mb-6">
							<p className="text-sm text-gray-600 dark:text-gray-400">
								Showing {scripts.length} of {totalItems} scripts
								{searchQuery && ` matching "${searchQuery}"`}
							</p>
						</div>

						{/* Different Views */}
						{viewMode === VIEW_MODES.GRID && (
							<GridView scripts={scripts} onAction={onScriptAction} />
						)}
						{viewMode === VIEW_MODES.LIST && (
							<ListView scripts={scripts} onAction={onScriptAction} />
						)}
						{viewMode === VIEW_MODES.KANBAN && (
							<KanbanView scripts={scripts} onAction={onScriptAction} />
						)}

						{/* Pagination */}
						<Pagination
							currentPage={currentPage}
							totalPages={totalPages}
							onPageChange={updatePage}
						/>
					</>
				)}
			</div>
		</div>
	);
};

export default GeneratedScriptsPage;
