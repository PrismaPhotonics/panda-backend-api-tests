"""
Bug Deduplication Service
==========================

This module provides automatic bug deduplication by checking if similar bugs
already exist in Jira before creating new ones.

Features:
- Search for existing bugs by summary, description, and keywords
- Compare test failures to existing bugs
- Prevent duplicate bug creation
- Cache existing bugs for performance

Author: QA Automation Architect
Date: 2025-11-08
Version: 1.0.0
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from external.jira.jira_client import JiraClient
try:
    from jira.exceptions import JIRAError
except ImportError:
    # Fallback if jira library not available
    class JIRAError(Exception):
        pass

logger = logging.getLogger(__name__)


class BugDeduplicationService:
    """
    Service for deduplicating bugs before creation.
    
    This service checks if similar bugs already exist in Jira by:
    1. Searching for bugs with similar summaries
    2. Searching for bugs with similar descriptions
    3. Searching for bugs with matching keywords
    4. Comparing test failure patterns
    
    Example:
        ```python
        from external.jira.bug_deduplication import BugDeduplicationService
        
        service = BugDeduplicationService()
        
        # Check if bug already exists
        existing_bug = service.find_similar_bug(
            summary="MongoDB connection failure",
            description="Pod restarts due to MongoDB connection error",
            keywords=["mongodb", "connection", "restart"]
        )
        
        if existing_bug:
            print(f"Similar bug already exists: {existing_bug['key']}")
        else:
            # Create new bug
            ...
        ```
    """
    
    def __init__(
        self,
        jira_client: Optional[JiraClient] = None,
        project_key: Optional[str] = None,
        similarity_threshold: float = 0.7,
        cache_duration_hours: int = 24
    ):
        """
        Initialize Bug Deduplication Service.
        
        Args:
            jira_client: JiraClient instance (creates new if not provided)
            project_key: Project key to search in (defaults to client config)
            similarity_threshold: Minimum similarity score (0.0-1.0) to consider bugs similar
            cache_duration_hours: How long to cache existing bugs (default: 24 hours)
        """
        self.jira_client = jira_client or JiraClient()
        self.project_key = project_key or self.jira_client.project_key
        self.similarity_threshold = similarity_threshold
        self.cache_duration_hours = cache_duration_hours
        
        # Cache for existing bugs
        self._bug_cache: Dict[str, Tuple[datetime, List[Dict]]] = {}
        
        logger.info(
            f"BugDeduplicationService initialized for project: {self.project_key} "
            f"(similarity threshold: {similarity_threshold})"
        )
    
    def find_similar_bug(
        self,
        summary: str,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        error_message: Optional[str] = None,
        test_name: Optional[str] = None,
        max_results: int = 10
    ) -> Optional[Dict[str, any]]:
        """
        Find similar bugs that already exist in Jira.
        
        Args:
            summary: Bug summary/title
            description: Bug description
            keywords: List of keywords to search for
            error_message: Error message from test failure
            test_name: Name of the test that failed
            max_results: Maximum number of results to check
            
        Returns:
            Dictionary of the most similar bug if found, None otherwise
        """
        if not summary:
            logger.warning("Cannot search for similar bugs without summary")
            return None
        
        logger.info(f"Searching for similar bugs: '{summary[:50]}...'")
        
        # Build search queries
        search_queries = self._build_search_queries(
            summary, description, keywords, error_message, test_name
        )
        
        # Search for existing bugs
        all_candidates = []
        for query in search_queries:
            try:
                candidates = self._search_bugs(query, max_results)
                all_candidates.extend(candidates)
            except Exception as e:
                logger.warning(f"Search query failed: {query} - {e}")
                continue
        
        # Remove duplicates (by key)
        seen_keys = set()
        unique_candidates = []
        for candidate in all_candidates:
            if candidate['key'] not in seen_keys:
                seen_keys.add(candidate['key'])
                unique_candidates.append(candidate)
        
        if not unique_candidates:
            logger.info("No similar bugs found")
            return None
        
        # Calculate similarity scores
        scored_candidates = []
        for candidate in unique_candidates:
            score = self._calculate_similarity(
                summary, description, keywords, error_message,
                candidate['summary'], candidate.get('description', ''),
                candidate.get('labels', [])
            )
            scored_candidates.append((score, candidate))
        
        # Sort by similarity score (highest first)
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Get the most similar bug
        best_score, best_bug = scored_candidates[0]
        
        if best_score >= self.similarity_threshold:
            logger.info(
                f"Found similar bug: {best_bug['key']} "
                f"(similarity: {best_score:.2f})"
            )
            return best_bug
        else:
            logger.info(
                f"Most similar bug: {best_bug['key']} "
                f"(similarity: {best_score:.2f} < threshold {self.similarity_threshold})"
            )
            return None
    
    def _build_search_queries(
        self,
        summary: str,
        description: Optional[str],
        keywords: Optional[List[str]],
        error_message: Optional[str],
        test_name: Optional[str]
    ) -> List[str]:
        """
        Build JQL search queries for finding similar bugs.
        
        Args:
            summary: Bug summary
            description: Bug description
            keywords: List of keywords
            error_message: Error message
            test_name: Test name
            
        Returns:
            List of JQL query strings
        """
        queries = []
        project = self.project_key
        
        # Extract key terms from summary
        summary_terms = self._extract_key_terms(summary)
        
        # Query 1: Search by summary keywords
        if summary_terms:
            # Use first 2-3 most important terms
            important_terms = summary_terms[:3]
            summary_query = ' AND '.join([f'summary ~ "{term}"' for term in important_terms])
            queries.append(
                f'project = {project} AND issuetype = Bug AND status != Done AND ({summary_query})'
            )
        
        # Query 2: Search by keywords
        if keywords:
            keyword_query = ' OR '.join([f'summary ~ "{kw}" OR description ~ "{kw}"' for kw in keywords[:5]])
            queries.append(
                f'project = {project} AND issuetype = Bug AND status != Done AND ({keyword_query})'
            )
        
        # Query 3: Search by error message keywords
        if error_message:
            error_terms = self._extract_key_terms(error_message)
            if error_terms:
                error_query = ' OR '.join([f'description ~ "{term}"' for term in error_terms[:3]])
                queries.append(
                    f'project = {project} AND issuetype = Bug AND status != Done AND ({error_query})'
                )
        
        # Query 4: Search by test name
        if test_name:
            # Extract test class/method name
            test_parts = test_name.split('.')
            if len(test_parts) >= 2:
                test_class = test_parts[-2]
                queries.append(
                    f'project = {project} AND issuetype = Bug AND status != Done AND '
                    f'(summary ~ "{test_class}" OR description ~ "{test_class}")'
                )
        
        # Query 5: Search by "Found by" = "QA Cycle" (recent bugs)
        queries.append(
            f'project = {project} AND issuetype = Bug AND status != Done AND '
            f'found by = "QA Cycle" AND created >= -30d ORDER BY created DESC'
        )
        
        return queries
    
    def _search_bugs(self, jql: str, max_results: int) -> List[Dict]:
        """
        Search for bugs using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
            
        Returns:
            List of bug dictionaries
        """
        # Check cache first
        cache_key = f"{jql}_{max_results}"
        if cache_key in self._bug_cache:
            cached_time, cached_bugs = self._bug_cache[cache_key]
            if datetime.now() - cached_time < timedelta(hours=self.cache_duration_hours):
                logger.debug(f"Using cached results for query: {jql[:50]}...")
                return cached_bugs
        
        # Search Jira
        try:
            bugs = self.jira_client.search_issues(jql, max_results=max_results)
            
            # Cache results
            self._bug_cache[cache_key] = (datetime.now(), bugs)
            
            return bugs
        except Exception as e:
            logger.warning(f"JQL search failed: {jql} - {e}")
            return []
    
    def _extract_key_terms(self, text: str, min_length: int = 4) -> List[str]:
        """
        Extract key terms from text for searching.
        
        Args:
            text: Text to extract terms from
            min_length: Minimum term length
            
        Returns:
            List of key terms (sorted by importance)
        """
        if not text:
            return []
        
        # Convert to lowercase
        text_lower = text.lower()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Filter by length and stop words
        terms = [w for w in words if len(w) >= min_length and w not in stop_words]
        
        # Count frequency
        term_freq = {}
        for term in terms:
            term_freq[term] = term_freq.get(term, 0) + 1
        
        # Sort by frequency (most common first)
        sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [term for term, freq in sorted_terms]
    
    def _calculate_similarity(
        self,
        summary1: str,
        description1: Optional[str],
        keywords1: Optional[List[str]],
        error1: Optional[str],
        summary2: str,
        description2: str,
        labels2: List[str]
    ) -> float:
        """
        Calculate similarity score between two bugs.
        
        Args:
            summary1: First bug summary
            description1: First bug description
            keywords1: First bug keywords
            error1: First bug error message
            summary2: Second bug summary
            description2: Second bug description
            labels2: Second bug labels
            
        Returns:
            Similarity score (0.0-1.0)
        """
        scores = []
        
        # Compare summaries
        summary_score = SequenceMatcher(None, summary1.lower(), summary2.lower()).ratio()
        scores.append(('summary', summary_score, 0.4))  # 40% weight
        
        # Compare descriptions
        if description1 and description2:
            desc_score = SequenceMatcher(None, description1.lower(), description2.lower()).ratio()
            scores.append(('description', desc_score, 0.3))  # 30% weight
        else:
            scores.append(('description', 0.0, 0.3))
        
        # Compare keywords
        if keywords1:
            keywords1_lower = [kw.lower() for kw in keywords1]
            labels2_lower = [l.lower() for l in labels2]
            
            # Count matching keywords
            matches = sum(1 for kw in keywords1_lower if any(kw in label or label in kw for label in labels2_lower))
            keyword_score = matches / len(keywords1_lower) if keywords1_lower else 0.0
            scores.append(('keywords', keyword_score, 0.2))  # 20% weight
        else:
            scores.append(('keywords', 0.0, 0.2))
        
        # Compare error messages (if available)
        if error1 and description2:
            # Check if error message appears in description
            error_terms = self._extract_key_terms(error1)
            desc2_lower = description2.lower()
            matches = sum(1 for term in error_terms if term in desc2_lower)
            error_score = matches / len(error_terms) if error_terms else 0.0
            scores.append(('error', error_score, 0.1))  # 10% weight
        else:
            scores.append(('error', 0.0, 0.1))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        return total_score
    
    def clear_cache(self):
        """Clear the bug cache."""
        self._bug_cache.clear()
        logger.info("Bug cache cleared")
    
    def close(self):
        """Close the service and clean up resources."""
        self.clear_cache()
        if hasattr(self, 'jira_client') and self.jira_client:
            self.jira_client.close()

