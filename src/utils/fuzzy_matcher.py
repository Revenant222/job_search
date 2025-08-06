"""
Fuzzy matching utilities for job filtering.
"""
from typing import List, Tuple, Optional
from fuzzywuzzy import fuzz, process
import re


def clean_text(text: str) -> str:
    """
    Clean text for better fuzzy matching.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def fuzzy_match(input_str: str, candidates: List[str], threshold: int = 80) -> List[Tuple[str, int]]:
    """
    Perform fuzzy matching between input string and candidate list.
    
    Args:
        input_str: Input string to match
        candidates: List of candidate strings
        threshold: Minimum similarity threshold (0-100)
        
    Returns:
        List of tuples (candidate, score) for matches above threshold
    """
    if not input_str or not candidates:
        return []
    
    # Clean input string
    cleaned_input = clean_text(input_str)
    if not cleaned_input:
        return []
    
    # Clean candidates
    cleaned_candidates = [clean_text(candidate) for candidate in candidates]
    
    # Perform fuzzy matching
    matches = []
    for i, candidate in enumerate(candidates):
        cleaned_candidate = cleaned_candidates[i]
        if cleaned_candidate:
            # Use token sort ratio for better matching of word order
            score = fuzz.token_sort_ratio(cleaned_input, cleaned_candidate)
            if score >= threshold:
                matches.append((candidate, score))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches


def fuzzy_match_keywords(text: str, keywords: List[str], threshold: int = 70) -> List[Tuple[str, int]]:
    """
    Match keywords within text using fuzzy matching.
    
    Args:
        text: Text to search in
        keywords: List of keywords to find
        threshold: Minimum similarity threshold (0-100)
        
    Returns:
        List of tuples (keyword, score) for matches above threshold
    """
    if not text or not keywords:
        return []
    
    # Clean text and keywords
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return []
    
    matches = []
    for keyword in keywords:
        cleaned_keyword = clean_text(keyword)
        if cleaned_keyword:
            # Use partial ratio for substring matching
            score = fuzz.partial_ratio(cleaned_keyword, cleaned_text)
            if score >= threshold:
                matches.append((keyword, score))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches


def extract_skills_from_text(text: str, skill_keywords: List[str], threshold: int = 70) -> List[str]:
    """
    Extract skills from text using fuzzy matching.
    
    Args:
        text: Text to extract skills from
        skill_keywords: List of skill keywords to look for
        threshold: Minimum similarity threshold (0-100)
        
    Returns:
        List of matched skills
    """
    matches = fuzzy_match_keywords(text, skill_keywords, threshold)
    return [match[0] for match in matches]


def calculate_title_similarity(title1: str, title2: str) -> int:
    """
    Calculate similarity between two job titles.
    
    Args:
        title1: First job title
        title2: Second job title
        
    Returns:
        Similarity score (0-100)
    """
    if not title1 or not title2:
        return 0
    
    cleaned_title1 = clean_text(title1)
    cleaned_title2 = clean_text(title2)
    
    if not cleaned_title1 or not cleaned_title2:
        return 0
    
    # Use token sort ratio for job title comparison
    return fuzz.token_sort_ratio(cleaned_title1, cleaned_title2)


def calculate_location_similarity(location1: str, location2: str) -> int:
    """
    Calculate similarity between two locations.
    
    Args:
        location1: First location
        location2: Second location
        
    Returns:
        Similarity score (0-100)
    """
    if not location1 or not location2:
        return 0
    
    cleaned_location1 = clean_text(location1)
    cleaned_location2 = clean_text(location2)
    
    if not cleaned_location1 or not cleaned_location2:
        return 0
    
    # Use simple ratio for location comparison
    return fuzz.ratio(cleaned_location1, cleaned_location2)


def get_best_match(input_str: str, candidates: List[str], threshold: int = 80) -> Optional[Tuple[str, int]]:
    """
    Get the best match from a list of candidates.
    
    Args:
        input_str: Input string to match
        candidates: List of candidate strings
        threshold: Minimum similarity threshold (0-100)
        
    Returns:
        Tuple of (best_match, score) or None if no match above threshold
    """
    matches = fuzzy_match(input_str, candidates, threshold)
    return matches[0] if matches else None 