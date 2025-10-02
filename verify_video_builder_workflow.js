// Video Builder Workflow Verification Script
// Copy and paste this in your browser console after using the video builder

console.log('🔍 Video Builder Workflow Verification\n');

// 1. Check if workflow exists
const workflowData = localStorage.getItem('videoBuilderWorkflow');
if (!workflowData) {
  console.error('❌ No videoBuilderWorkflow found in localStorage');
  console.log('💡 Start using the video builder to create workflow data.');
} else {
  console.log('✅ videoBuilderWorkflow found in localStorage\n');
  
  try {
    const workflows = JSON.parse(workflowData);
    console.log(`📊 Total workflow records: ${workflows.length}\n`);
    
    if (workflows.length === 0) {
      console.warn('⚠️ videoBuilderWorkflow exists but is empty');
    } else {
      // Display all workflows
      workflows.forEach((workflow, index) => {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`📁 Workflow ${index + 1}`);
        console.log(`${'='.repeat(60)}`);
        console.log('Workflow ID:', workflow.id);
        console.log('User ID:', workflow.userId);
        console.log('Status:', workflow.status);
        console.log('Current Step:', workflow.currentStep);
        console.log('Current Step Name:', workflow.currentStepName);
        console.log('Created At:', workflow.createdAt);
        console.log('Updated At:', workflow.updatedAt);
        
        console.log('\n📋 Steps Progress:');
        console.log('-'.repeat(60));
        
        // Show step details in table format
        const stepData = [];
        for (let i = 1; i <= 6; i++) {
          const step = workflow.steps[i.toString()];
          if (step) {
            stepData.push({
              'Step #': i,
              'Name': step.name,
              'Status': step.status,
              'Has Data': Object.keys(step.data || {}).length > 0 ? '✅' : '❌',
              'Data Fields': Object.keys(step.data || {}).join(', ') || 'none'
            });
          } else {
            stepData.push({
              'Step #': i,
              'Name': 'Not Started',
              'Status': 'N/A',
              'Has Data': '❌',
              'Data Fields': 'none'
            });
          }
        }
        console.table(stepData);
        
        // Show detailed data for each step
        console.log('\n📦 Detailed Step Data:');
        console.log('-'.repeat(60));
        Object.keys(workflow.steps).sort().forEach(stepNum => {
          const step = workflow.steps[stepNum];
          console.log(`\nStep ${stepNum}: ${step.name}`);
          console.log(`  Status: ${step.status}`);
          if (step.completedAt) {
            console.log(`  Completed: ${step.completedAt}`);
          }
          console.log(`  Data:`, step.data);
        });
      });
      
      // Validation checks
      console.log(`\n\n${'='.repeat(60)}`);
      console.log('🔍 VALIDATION CHECKS');
      console.log(`${'='.repeat(60)}`);
      
      const latestWorkflow = workflows[workflows.length - 1];
      const issues = [];
      const successes = [];
      
      // Check structure
      if (latestWorkflow.userId && latestWorkflow.userId.startsWith('user_')) {
        successes.push('✅ User ID format correct');
      } else {
        issues.push('❌ User ID format incorrect');
      }
      
      if (latestWorkflow.currentStep >= 1 && latestWorkflow.currentStep <= 6) {
        successes.push('✅ Current step is valid (1-6)');
      } else {
        issues.push('❌ Current step is invalid');
      }
      
      if (latestWorkflow.currentStepName) {
        successes.push('✅ Current step name exists');
      } else {
        issues.push('❌ Current step name is missing');
      }
      
      if (['in_progress', 'completed'].includes(latestWorkflow.status)) {
        successes.push('✅ Workflow status is valid');
      } else {
        issues.push('❌ Workflow status is invalid');
      }
      
      // Check timestamp format
      try {
        new Date(latestWorkflow.createdAt);
        new Date(latestWorkflow.updatedAt);
        successes.push('✅ Timestamps are valid ISO format');
      } catch {
        issues.push('❌ Invalid timestamp format');
      }
      
      // Check step data structure
      const stepNumbers = Object.keys(latestWorkflow.steps);
      if (stepNumbers.length > 0) {
        successes.push(`✅ Has ${stepNumbers.length} step(s) recorded`);
      } else {
        issues.push('❌ No steps recorded');
      }
      
      // Check if step numbers match
      stepNumbers.forEach(num => {
        const step = latestWorkflow.steps[num];
        if (step.name && step.status && step.data !== undefined) {
          successes.push(`✅ Step ${num} has complete structure`);
        } else {
          issues.push(`❌ Step ${num} missing required fields`);
        }
      });
      
      // Display results
      console.log('\n✅ Successes:');
      successes.forEach(s => console.log(`  ${s}`));
      
      if (issues.length > 0) {
        console.log('\n❌ Issues Found:');
        issues.forEach(i => console.log(`  ${i}`));
      } else {
        console.log('\n🎉 No issues found! Workflow structure is perfect!');
      }
      
      // Summary
      console.log(`\n\n${'='.repeat(60)}`);
      console.log('📈 SUMMARY');
      console.log(`${'='.repeat(60)}`);
      console.log(`Total Workflows: ${workflows.length}`);
      console.log(`Latest Workflow Status: ${latestWorkflow.status}`);
      console.log(`Current Step: ${latestWorkflow.currentStep} - ${latestWorkflow.currentStepName}`);
      console.log(`Steps Completed: ${Object.values(latestWorkflow.steps).filter(s => s.status === 'completed').length}/6`);
      console.log(`Steps In Progress: ${Object.values(latestWorkflow.steps).filter(s => s.status === 'in_progress').length}`);
      console.log(`Steps Pending: ${6 - Object.keys(latestWorkflow.steps).length}`);
    }
    
  } catch (error) {
    console.error('❌ Error parsing workflow data:', error);
  }
}

// 2. Provide helpful commands
console.log(`\n\n${'='.repeat(60)}`);
console.log('📋 USEFUL COMMANDS');
console.log(`${'='.repeat(60)}`);
console.log('\nView raw workflow data:');
console.log('  JSON.parse(localStorage.getItem("videoBuilderWorkflow"))');
console.log('\nClear workflow data:');
console.log('  localStorage.removeItem("videoBuilderWorkflow")');
console.log('\nGet specific step data:');
console.log('  const workflow = JSON.parse(localStorage.getItem("videoBuilderWorkflow"))[0];');
console.log('  console.log(workflow.steps["2"].data); // Step 2 data');
console.log('\nCheck if step completed:');
console.log('  const workflow = JSON.parse(localStorage.getItem("videoBuilderWorkflow"))[0];');
console.log('  workflow.steps["2"].status === "completed"');

console.log('\n✅ Verification complete!\n');
