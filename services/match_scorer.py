"""
Match Score Calculator
Calculates CV-to-job description match percentage
"""

import re
from typing import Dict, List, Set
from collections import Counter


class MatchScorer:
    """Calculate CV-to-job description match score"""

    # Common stop words to exclude
    STOP_WORDS = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
        'was', 'one', 'our', 'out', 'has', 'have', 'with', 'this', 'that',
        'from', 'they', 'been', 'will', 'their', 'would', 'about', 'which',
        'when', 'make', 'like', 'into', 'year', 'your', 'some', 'could',
        'them', 'than', 'then', 'what', 'there', 'other', 'more', 'these',
        'such', 'also', 'over', 'most', 'only', 'just', 'very', 'should',
        'being', 'through', 'where', 'much', 'before', 'those', 'same',
        'each', 'under', 'within', 'must', 'need', 'well', 'while', 'using',
        'used', 'work', 'working', 'experience', 'ability', 'able', 'skills',
        'including', 'required', 'requirements', 'preferred', 'etc', 'role',
        'position', 'candidate', 'candidates', 'looking', 'join', 'team'
    }

    # Important skill categories for weighting
    SKILL_PATTERNS = {
        'programming': r'\b(python|java|javascript|typescript|c\+\+|ruby|php|swift|kotlin|golang|rust|scala)\b',
        'frameworks': r'\b(react|angular|vue|django|flask|spring|node|express|fastapi|nextjs|rails)\b',
        'databases': r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|dynamodb|oracle|sqlite)\b',
        'cloud': r'\b(aws|azure|gcp|docker|kubernetes|terraform|jenkins|ci\/cd|devops)\b',
        'data': r'\b(machine learning|ml|ai|data science|analytics|tableau|power bi|pandas|numpy|tensorflow|pytorch)\b',
        'soft_skills': r'\b(leadership|communication|teamwork|problem.solving|analytical|management|agile|scrum)\b'
    }

    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        """
        Extract meaningful keywords from text

        Args:
            text: Input text

        Returns:
            Set of extracted keywords
        """
        text = text.lower()
        # Extract words (3+ characters)
        words = re.findall(r'\b[a-z]{3,}\b', text)

        # Filter out stop words
        keywords = {word for word in words if word not in MatchScorer.STOP_WORDS}

        return keywords

    @staticmethod
    def extract_skill_keywords(text: str) -> Dict[str, List[str]]:
        """
        Extract categorized skill keywords

        Args:
            text: Input text

        Returns:
            Dict of category -> list of found skills
        """
        text = text.lower()
        found_skills = {}

        for category, pattern in MatchScorer.SKILL_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_skills[category] = list(set(matches))

        return found_skills

    @classmethod
    def calculate_score(cls, cv_text: str, job_description: str) -> Dict:
        """
        Calculate comprehensive match score

        Args:
            cv_text: CV content
            job_description: Job description content

        Returns:
            Dict with score and detailed analysis
        """
        # Extract general keywords
        cv_keywords = cls.extract_keywords(cv_text)
        job_keywords = cls.extract_keywords(job_description)

        # Extract skill-specific keywords
        cv_skills = cls.extract_skill_keywords(cv_text)
        job_skills = cls.extract_skill_keywords(job_description)

        # Calculate keyword overlap
        matching_keywords = cv_keywords.intersection(job_keywords)
        missing_keywords = job_keywords - cv_keywords

        # Calculate skill matches
        skill_matches = {}
        skill_missing = {}
        total_skill_score = 0
        skill_count = 0

        for category in cls.SKILL_PATTERNS.keys():
            job_category_skills = set(job_skills.get(category, []))
            cv_category_skills = set(cv_skills.get(category, []))

            if job_category_skills:
                matched = job_category_skills.intersection(cv_category_skills)
                missed = job_category_skills - cv_category_skills

                if matched:
                    skill_matches[category] = list(matched)
                if missed:
                    skill_missing[category] = list(missed)

                # Calculate category score
                category_score = len(matched) / len(job_category_skills) * 100
                total_skill_score += category_score
                skill_count += 1

        # Calculate base keyword score
        if len(job_keywords) > 0:
            keyword_score = (len(matching_keywords) / len(job_keywords)) * 100
        else:
            keyword_score = 0

        # Calculate skill score
        if skill_count > 0:
            avg_skill_score = total_skill_score / skill_count
        else:
            avg_skill_score = keyword_score  # Fallback to keyword score

        # Combined score (weighted: 60% skills, 40% keywords)
        if skill_count > 0:
            final_score = (avg_skill_score * 0.6) + (keyword_score * 0.4)
        else:
            final_score = keyword_score

        # Get top missing keywords (prioritize shorter, more specific ones)
        sorted_missing = sorted(missing_keywords, key=lambda x: (len(x), x))[:15]

        return {
            "score": min(round(final_score, 1), 100),
            "keyword_score": round(keyword_score, 1),
            "skill_score": round(avg_skill_score, 1) if skill_count > 0 else None,
            "matching_keywords": sorted(list(matching_keywords))[:20],
            "missing_keywords": sorted_missing,
            "skill_matches": skill_matches,
            "skill_missing": skill_missing,
            "total_job_keywords": len(job_keywords),
            "total_cv_keywords": len(cv_keywords),
            "match_count": len(matching_keywords)
        }

    @staticmethod
    def get_score_interpretation(score: float, language: str = "English") -> Dict[str, str]:
        """
        Get interpretation of the match score

        Args:
            score: Match score percentage
            language: Language for labels

        Returns:
            Dict with label, color, and description
        """
        from translations import get_text

        if score >= 80:
            return {
                "label": get_text("excellent_match", language),
                "color": "#10b981",  # Green
                "description": get_text("excellent_desc", language)
            }
        elif score >= 60:
            return {
                "label": get_text("good_match", language),
                "color": "#06b6d4",  # Cyan
                "description": get_text("good_desc", language)
            }
        elif score >= 40:
            return {
                "label": get_text("moderate_match", language),
                "color": "#f59e0b",  # Amber
                "description": get_text("moderate_desc", language)
            }
        else:
            return {
                "label": get_text("needs_improvement", language),
                "color": "#ef4444",  # Red
                "description": get_text("needs_improvement_desc", language)
            }
