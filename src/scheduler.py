"""
Scheduler module for Schedule DB query
Handles scheduled execution of snapshot tasks
"""
import logging
import time
import schedule
from datetime import datetime
from typing import Callable
from config.settings import settings

logger = logging.getLogger(__name__)


class SnapshotScheduler:
    """Manages scheduled execution of snapshot tasks"""
    
    def __init__(self, task_function: Callable):
        """
        Initialize scheduler
        
        Args:
            task_function: Function to execute on schedule
        """
        self.task_function = task_function
        self.schedule_times = settings.SCHEDULE_TIME if isinstance(settings.SCHEDULE_TIME, list) else [settings.SCHEDULE_TIME]
        self.schedule_days = [day.strip().upper() for day in settings.SCHEDULE_DAYS]
        self.is_running = False
        self.task_executing = False  # Flag to prevent concurrent execution
        self.last_execution_minute = None  # Track the last execution minute to prevent duplicates
    
    def _create_task_wrapper(self, schedule_time: str):
        """
        Create a wrapper function that logs the schedule time
        
        Args:
            schedule_time: The scheduled time (HH:MM format)
        
        Returns:
            Wrapper function that executes the task with context
        """
        def wrapper():
            from datetime import datetime
            
            # Get current time rounded to the minute
            now = datetime.now()
            current_minute = now.strftime('%Y-%m-%d %H:%M')
            
            # Prevent duplicate execution within the same minute
            if self.last_execution_minute == current_minute:
                logger.warning(f"Skipping duplicate execution for {schedule_time} - already executed at {current_minute}")
                return
            
            # Prevent concurrent execution
            if self.task_executing:
                logger.warning(f"Skipping execution for {schedule_time} - task already running")
                return
            
            try:
                self.task_executing = True
                self.last_execution_minute = current_minute
                logger.info("=" * 80)
                logger.info(f"⏰ Scheduled execution triggered at {schedule_time}")
                logger.info("=" * 80)
                return self.task_function()
            finally:
                self.task_executing = False
        return wrapper
    
    def setup_schedule(self):
        """Configure the schedule based on settings"""
        from datetime import datetime
        try:
            logger.info("Setting up schedule...")
            logger.info(f"Schedule times: {', '.join(self.schedule_times)}")
            logger.info(f"Schedule days: {', '.join(self.schedule_days)}")
            
            # Clear any existing schedules
            schedule.clear()
            
            # Define valid day names for schedule library
            valid_days = {'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'}
            schedule_days_set = set(day.upper() for day in self.schedule_days if day.upper() in valid_days)
            
            # Get current day of week
            current_day = datetime.now().strftime('%a').upper()[:3]  # MON, TUE, WED, etc.
            
            # Map day abbreviations to schedule methods
            day_map = {
                'MON': schedule.every().monday,
                'TUE': schedule.every().tuesday,
                'WED': schedule.every().wednesday,
                'THU': schedule.every().thursday,
                'FRI': schedule.every().friday,
                'SAT': schedule.every().saturday,
                'SUN': schedule.every().sunday,
            }
            
            # Track scheduled times to prevent duplicates at the same time
            scheduled_times = set()
            
            # Schedule for each time
            for schedule_time in self.schedule_times:
                # If all days are specified, use daily schedule
                if len(schedule_days_set) == 7 or 'EVERYDAY' in self.schedule_days:
                    # Create a wrapper function for this specific schedule time
                    task_wrapper = self._create_task_wrapper(schedule_time)
                    job = schedule.every().day.at(schedule_time).do(task_wrapper)
                    logger.debug(f"Scheduled daily at {schedule_time} (next run: {job.next_run})")
                    scheduled_times.add(schedule_time)
                else:
                    # Add day-specific jobs for all configured days
                    # Use a set to track which day+time combinations we've already scheduled
                    for day in schedule_days_set:
                        if day in day_map:
                            # Create a unique key for this day+time combination
                            schedule_key = f"{day}_{schedule_time}"
                            if schedule_key not in scheduled_times:
                                # Create a unique wrapper for each day+time combination
                                task_wrapper = self._create_task_wrapper(schedule_time)
                                job = day_map[day].at(schedule_time).do(task_wrapper)
                                logger.debug(f"Scheduled {day} at {schedule_time} (next run: {job.next_run})")
                                scheduled_times.add(schedule_key)
                            else:
                                logger.debug(f"Skipping duplicate schedule for {day} at {schedule_time}")
            
            # Log all scheduled jobs for debugging
            all_jobs = schedule.get_jobs()
            logger.info(f"Schedule setup completed - Total jobs created: {len(all_jobs)}")
            for idx, job in enumerate(all_jobs, 1):
                logger.debug(f"Job {idx}: next_run={job.next_run}, interval={job.interval}, unit={job.unit}")
            
        except Exception as e:
            logger.error(f"Error setting up schedule: {str(e)}")
            raise
    
    def run(self):
        """Start the scheduler loop"""
        try:
            self.setup_schedule()
            self.is_running = True
            
            # Clean up any jobs with past next_run times immediately after setup
            self._cleanup_past_jobs()
            
            logger.info("Scheduler started. Waiting for scheduled tasks...")
            logger.info("Press Ctrl+C to stop")
            
            # Show all scheduled jobs and their next run times
            self._display_next_runs()
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.stop()
            raise
    
    def _cleanup_past_jobs(self):
        """Remove jobs with next_run times that have already passed"""
        from datetime import datetime
        
        now = datetime.now()
        jobs = schedule.get_jobs()
        removed_count = 0
        
        for job in jobs[:]:  # Create a copy of the list to iterate safely
            if job.next_run and job.next_run <= now:
                logger.debug(f"Removing job with past next_run: {job.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                schedule.cancel_job(job)
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} job(s) with past execution times")
    
    def _display_next_runs(self):
        """Display upcoming scheduled runs"""
        from datetime import datetime, timedelta
        
        jobs = schedule.get_jobs()
        if not jobs:
            logger.warning("No scheduled jobs found")
            return
        
        # Get all job run times that are in the future
        now = datetime.now()
        job_times = []
        
        for job in jobs:
            next_run = job.next_run
            # Only include jobs with future next_run times
            if next_run and next_run > now:
                job_times.append(next_run)
        
        if not job_times:
            logger.warning("No upcoming runs scheduled")
            return
        
        # Sort by time
        job_times.sort()
        
        # DEBUG: Log current time and all scheduled times
        logger.debug(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.debug(f"Future scheduled times: {[t.strftime('%Y-%m-%d %H:%M:%S') for t in job_times[:5]]}")  # Show first 5
        
        # Get the earliest future run
        next_run = job_times[0]
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show today's remaining runs (unique times only)
        today = now.date()
        today_runs = [t for t in job_times if t.date() == today]
        
        if today_runs:
            # Remove duplicates and sort
            unique_times = sorted(set(t.strftime('%H:%M') for t in today_runs))
            times_str = ", ".join(unique_times)
            logger.info(f"Remaining runs today: {times_str}")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def run_once(self):
        """Execute the task once immediately"""
        logger.info("Running task once (no scheduling)")
        try:
            self.task_function()
        except Exception as e:
            logger.error(f"Error running task: {str(e)}")
            raise


def create_scheduler(task_function: Callable) -> SnapshotScheduler:
    """
    Create and configure a scheduler
    
    Args:
        task_function: Function to execute on schedule
        
    Returns:
        Configured SnapshotScheduler instance
    """
    return SnapshotScheduler(task_function)
