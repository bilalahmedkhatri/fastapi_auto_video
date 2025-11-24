"""
Test startup tasks
"""
from server_starting_apps.startup_tasks import should_run_voice_sample_check

should_run, reason = should_run_voice_sample_check()
print(f"\n{'='*70}")
print(f"🔍 Voice Sample Startup Check Test")
print(f"{'='*70}")
print(f"Should run: {should_run}")
print(f"Reason: {reason}")
print(f"{'='*70}\n")
