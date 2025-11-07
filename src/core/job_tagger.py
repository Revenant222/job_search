"""
Job tagging module for marking jobs to apply for.
"""
import json
import os
from typing import Set, Dict, List, Any
from datetime import datetime
from src.utils.logger import app_logger


# Predefined tags that users can assign to jobs
PREDEFINED_TAGS = [
    "High Interest",
    "Mid Interest",
    "Low Interest",
    "Applied",
    "Closed",
    "NEW"
]


class JobTagger:
    """
    Handles tagging and tracking jobs for application.
    """
    
    def __init__(self, tags_file: str = "data/job_tags.json"):
        """
        Initialize JobTagger.
        
        Args:
            tags_file: Path to JSON file storing tagged jobs
        """
        # Ensure absolute path
        if not os.path.isabs(tags_file):
            # Use project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.tags_file = os.path.join(project_root, tags_file)
        else:
            self.tags_file = tags_file
        
        self.logger = app_logger
        self._load_tags()
    
    def _load_tags(self) -> None:
        """Load tags from file or create new structure."""
        if os.path.exists(self.tags_file):
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tagged_job_ids = set(data.get('tagged_jobs', []))
                    # job_tags is now a dict: {job_id: [list of tags]}
                    self.job_tags = data.get('job_tags', {})
                    self.tag_notes = data.get('tag_notes', {})  # Optional notes per job
                    self.tag_dates = data.get('tag_dates', {})  # When jobs were tagged
            except Exception as e:
                self.logger.error(f"Error loading tags file: {e}")
                self.tagged_job_ids = set()
                self.job_tags = {}
                self.tag_notes = {}
                self.tag_dates = {}
        else:
            self.tagged_job_ids = set()
            self.job_tags = {}
            self.tag_notes = {}
            self.tag_dates = {}
    
    def _save_tags(self) -> bool:
        """Save tags to file."""
        try:
            data = {
                'tagged_jobs': list(self.tagged_job_ids),
                'job_tags': self.job_tags,  # {job_id: [list of tags]}
                'tag_notes': self.tag_notes,
                'tag_dates': self.tag_dates,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving tags file: {e}")
            return False
    
    def tag_job(self, job_id: str, note: str = None) -> bool:
        """
        Tag a job for application.
        
        Args:
            job_id: Unique job ID
            note: Optional note about why this job is tagged
            
        Returns:
            True if successful
        """
        if not job_id:
            return False
        
        self.tagged_job_ids.add(job_id)
        if note:
            self.tag_notes[job_id] = note
        self.tag_dates[job_id] = datetime.now().isoformat()
        
        result = self._save_tags()
        if result:
            self.logger.info(f"Tagged job: {job_id}")
        return result
    
    def untag_job(self, job_id: str) -> bool:
        """
        Remove tag from a job.
        
        Args:
            job_id: Unique job ID
            
        Returns:
            True if successful
        """
        if job_id in self.tagged_job_ids:
            self.tagged_job_ids.remove(job_id)
            if job_id in self.tag_notes:
                del self.tag_notes[job_id]
            if job_id in self.tag_dates:
                del self.tag_dates[job_id]
            
            result = self._save_tags()
            if result:
                self.logger.info(f"Untagged job: {job_id}")
            return result
        return True
    
    def is_tagged(self, job_id: str) -> bool:
        """
        Check if a job is tagged.
        
        Args:
            job_id: Unique job ID
            
        Returns:
            True if job is tagged
        """
        return job_id in self.tagged_job_ids
    
    def get_tagged_count(self) -> int:
        """Get total number of tagged jobs."""
        return len(self.tagged_job_ids)
    
    def get_tagged_job_ids(self) -> Set[str]:
        """Get set of all tagged job IDs."""
        return self.tagged_job_ids.copy()
    
    def get_tag_note(self, job_id: str) -> str:
        """Get note for a tagged job."""
        return self.tag_notes.get(job_id, "")
    
    def set_tag_note(self, job_id: str, note: str) -> bool:
        """Set note for a tagged job."""
        if job_id in self.tagged_job_ids:
            self.tag_notes[job_id] = note
            return self._save_tags()
        return False
    
    def clear_all_tags(self) -> bool:
        """Clear all tags (use with caution)."""
        self.tagged_job_ids.clear()
        self.job_tags.clear()
        self.tag_notes.clear()
        self.tag_dates.clear()
        return self._save_tags()
    
    def add_tag(self, job_id: str, tag: str) -> bool:
        """
        Add a specific tag to a job (e.g., "NEW", "HIGH_PRIORITY").
        
        Args:
            job_id: Unique job ID
            tag: Tag name to add
            
        Returns:
            True if successful
        """
        if not job_id or not tag:
            return False
        
        # Ensure job is in tagged set
        self.tagged_job_ids.add(job_id)
        
        # Add tag to job's tag list
        if job_id not in self.job_tags:
            self.job_tags[job_id] = []
        
        if tag not in self.job_tags[job_id]:
            self.job_tags[job_id].append(tag)
            self.logger.info(f"Added tag '{tag}' to job: {job_id}")
        
        # Update tag date
        self.tag_dates[job_id] = datetime.now().isoformat()
        
        return self._save_tags()
    
    def remove_tag(self, job_id: str, tag: str) -> bool:
        """
        Remove a specific tag from a job.
        
        Args:
            job_id: Unique job ID
            tag: Tag name to remove
            
        Returns:
            True if successful
        """
        if job_id in self.job_tags and tag in self.job_tags[job_id]:
            self.job_tags[job_id].remove(tag)
            
            # If no tags left, remove from tagged set
            if not self.job_tags[job_id]:
                self.tagged_job_ids.discard(job_id)
                if job_id in self.tag_notes:
                    del self.tag_notes[job_id]
                if job_id in self.tag_dates:
                    del self.tag_dates[job_id]
            
            self.logger.info(f"Removed tag '{tag}' from job: {job_id}")
            return self._save_tags()
        
        return True
    
    def has_tag(self, job_id: str, tag: str) -> bool:
        """
        Check if a job has a specific tag.
        
        Args:
            job_id: Unique job ID
            tag: Tag name to check
            
        Returns:
            True if job has the tag
        """
        return job_id in self.job_tags and tag in self.job_tags[job_id]
    
    def get_job_tags(self, job_id: str) -> List[str]:
        """
        Get all tags for a specific job.
        
        Args:
            job_id: Unique job ID
            
        Returns:
            List of tag names
        """
        return self.job_tags.get(job_id, [])
    
    def get_jobs_with_tag(self, tag: str) -> Set[str]:
        """
        Get all job IDs that have a specific tag.
        
        Args:
            tag: Tag name to search for
            
        Returns:
            Set of job IDs with the tag
        """
        job_ids = set()
        for job_id, tags in self.job_tags.items():
            if tag in tags:
                job_ids.add(job_id)
        return job_ids


