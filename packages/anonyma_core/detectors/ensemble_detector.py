"""
Ensemble PII Detector - Combining Multiple Detection Methods.

Combines:
- Presidio (rule-based + NER)
- Flair NER (deep learning)
- Custom patterns (regex)
- spaCy NER (optional)

With intelligent confidence voting and entity resolution.
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
import re

from .base import BaseDetector
from .pii_detector import PIIDetector
from .flair_detector import FlairDetector
from .custom_detector import CustomPatternDetector
from ..logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DetectionVote:
    """Vote from a single detector"""
    detector_name: str
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float


@dataclass
class EnsembleResult:
    """Ensemble detection result with voting"""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float
    votes: int
    detectors: List[str]  # Which detectors agreed


class EnsembleDetector(BaseDetector):
    """
    Ensemble detector combining multiple detection methods.

    Features:
    - Multi-detector voting
    - Confidence aggregation
    - Entity resolution (overlapping spans)
    - Customizable voting strategies

    Voting Strategies:
    - unanimous: All detectors must agree
    - majority: Majority of detectors must agree
    - any: At least one detector (most permissive)
    - weighted: Weighted by confidence scores
    """

    def __init__(
        self,
        use_presidio: bool = True,
        use_flair: bool = False,
        use_custom: bool = False,
        custom_patterns: Optional[CustomPatternDetector] = None,
        voting_strategy: str = "weighted",
        min_confidence: float = 0.5,
        min_votes: int = 1,
    ):
        """
        Initialize ensemble detector.

        Args:
            use_presidio: Use Presidio detector
            use_flair: Use Flair NER detector
            use_custom: Use custom pattern detector
            custom_patterns: Custom pattern detector instance
            voting_strategy: Voting strategy (unanimous/majority/any/weighted)
            min_confidence: Minimum confidence threshold
            min_votes: Minimum number of detector votes required
        """
        super().__init__()
        self.name = "EnsembleDetector"

        # Initialize detectors
        self.detectors: List[BaseDetector] = []
        self.detector_weights: Dict[str, float] = {}

        if use_presidio:
            try:
                self.detectors.append(PIIDetector())
                self.detector_weights["PIIDetector"] = 1.0
                logger.info("Presidio detector initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Presidio: {e}")

        if use_flair:
            try:
                self.detectors.append(FlairDetector())
                self.detector_weights["FlairDetector"] = 1.2  # Higher weight for ML
                logger.info("Flair detector initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Flair: {e}")

        if use_custom and custom_patterns:
            self.detectors.append(custom_patterns)
            self.detector_weights[custom_patterns.name] = 0.8
            logger.info("Custom pattern detector initialized")

        if not self.detectors:
            raise ValueError("At least one detector must be initialized")

        self.voting_strategy = voting_strategy
        self.min_confidence = min_confidence
        self.min_votes = min_votes

        logger.info(
            f"Ensemble detector initialized",
            extra={
                "extra_fields": {
                    "detectors": len(self.detectors),
                    "strategy": voting_strategy,
                    "min_confidence": min_confidence
                }
            }
        )

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII using ensemble of detectors.

        Args:
            text: Text to analyze

        Returns:
            List of detection results with voting information
        """
        logger.debug(f"Running ensemble detection on text ({len(text)} chars)")

        # Collect votes from all detectors
        all_votes: List[DetectionVote] = []

        for detector in self.detectors:
            try:
                detections = detector.detect(text)

                for detection in detections:
                    vote = DetectionVote(
                        detector_name=detector.name,
                        text=detection["text"],
                        entity_type=detection["entity_type"],
                        start=detection["start"],
                        end=detection["end"],
                        confidence=detection.get("confidence", 0.9)
                    )
                    all_votes.append(vote)

            except Exception as e:
                logger.error(f"Detector {detector.name} failed: {e}", exc_info=True)

        logger.debug(f"Collected {len(all_votes)} votes from {len(self.detectors)} detectors")

        # Resolve overlapping detections and vote
        ensemble_results = self._resolve_and_vote(all_votes)

        # Convert to standard detection format
        final_detections = []
        for result in ensemble_results:
            final_detections.append({
                "text": result.text,
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "confidence": result.confidence,
                "votes": result.votes,
                "detectors": result.detectors,
            })

        logger.info(
            f"Ensemble detection completed",
            extra={
                "extra_fields": {
                    "total_votes": len(all_votes),
                    "final_detections": len(final_detections)
                }
            }
        )

        return final_detections

    def _resolve_and_vote(self, votes: List[DetectionVote]) -> List[EnsembleResult]:
        """
        Resolve overlapping detections and aggregate votes.

        Args:
            votes: All detection votes

        Returns:
            List of ensemble results
        """
        if not votes:
            return []

        # Group overlapping votes
        groups = self._group_overlapping_votes(votes)

        # Aggregate each group
        results = []
        for group in groups:
            result = self._aggregate_votes(group)
            if result:
                results.append(result)

        return results

    def _group_overlapping_votes(self, votes: List[DetectionVote]) -> List[List[DetectionVote]]:
        """
        Group votes that overlap in text span.

        Args:
            votes: All votes

        Returns:
            List of vote groups
        """
        if not votes:
            return []

        # Sort by start position
        sorted_votes = sorted(votes, key=lambda v: (v.start, v.end))

        groups = []
        current_group = [sorted_votes[0]]

        for vote in sorted_votes[1:]:
            # Check if overlaps with current group
            group_start = min(v.start for v in current_group)
            group_end = max(v.end for v in current_group)

            if self._spans_overlap(vote.start, vote.end, group_start, group_end):
                current_group.append(vote)
            else:
                groups.append(current_group)
                current_group = [vote]

        groups.append(current_group)
        return groups

    def _spans_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two spans overlap"""
        return not (end1 <= start2 or end2 <= start1)

    def _aggregate_votes(self, votes: List[DetectionVote]) -> Optional[EnsembleResult]:
        """
        Aggregate votes for overlapping detections.

        Args:
            votes: Overlapping votes to aggregate

        Returns:
            Ensemble result or None if doesn't meet criteria
        """
        if not votes:
            return None

        # Count votes by entity type
        entity_votes = defaultdict(list)
        for vote in votes:
            entity_votes[vote.entity_type].append(vote)

        # Find consensus entity type (most votes)
        consensus_type = max(entity_votes.keys(), key=lambda k: len(entity_votes[k]))
        consensus_votes = entity_votes[consensus_type]

        # Check minimum votes
        if len(consensus_votes) < self.min_votes:
            return None

        # Apply voting strategy
        if not self._meets_voting_criteria(consensus_votes):
            return None

        # Aggregate confidence
        confidence = self._aggregate_confidence(consensus_votes)

        # Check minimum confidence
        if confidence < self.min_confidence:
            return None

        # Determine text span (use the longest span from votes)
        start = min(v.start for v in consensus_votes)
        end = max(v.end for v in consensus_votes)
        text = consensus_votes[0].text  # Use first vote's text as representative

        return EnsembleResult(
            text=text,
            entity_type=consensus_type,
            start=start,
            end=end,
            confidence=confidence,
            votes=len(consensus_votes),
            detectors=[v.detector_name for v in consensus_votes]
        )

    def _meets_voting_criteria(self, votes: List[DetectionVote]) -> bool:
        """
        Check if votes meet voting strategy criteria.

        Args:
            votes: Votes for same entity

        Returns:
            True if criteria met
        """
        num_votes = len(votes)
        num_detectors = len(self.detectors)

        if self.voting_strategy == "unanimous":
            return num_votes == num_detectors

        elif self.voting_strategy == "majority":
            return num_votes > num_detectors / 2

        elif self.voting_strategy == "any":
            return num_votes >= 1

        elif self.voting_strategy == "weighted":
            # Always true for weighted, confidence handles threshold
            return True

        else:
            logger.warning(f"Unknown voting strategy: {self.voting_strategy}")
            return True

    def _aggregate_confidence(self, votes: List[DetectionVote]) -> float:
        """
        Aggregate confidence scores from votes.

        Args:
            votes: Votes to aggregate

        Returns:
            Aggregated confidence score
        """
        if not votes:
            return 0.0

        if self.voting_strategy == "weighted":
            # Weighted average by detector weights
            total_weight = 0.0
            weighted_sum = 0.0

            for vote in votes:
                weight = self.detector_weights.get(vote.detector_name, 1.0)
                weighted_sum += vote.confidence * weight
                total_weight += weight

            return weighted_sum / total_weight if total_weight > 0 else 0.0

        else:
            # Simple average
            return sum(v.confidence for v in votes) / len(votes)

    def set_detector_weight(self, detector_name: str, weight: float):
        """
        Set weight for a specific detector.

        Args:
            detector_name: Name of detector
            weight: Weight value (higher = more important)
        """
        self.detector_weights[detector_name] = weight
        logger.info(f"Set weight for {detector_name}: {weight}")

    def get_detector_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about detector performance.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with detector statistics
        """
        stats = {
            "detectors": [],
            "total_detections": 0
        }

        for detector in self.detectors:
            try:
                detections = detector.detect(text)
                stats["detectors"].append({
                    "name": detector.name,
                    "detections": len(detections),
                    "weight": self.detector_weights.get(detector.name, 1.0)
                })
                stats["total_detections"] += len(detections)
            except Exception as e:
                logger.error(f"Failed to get stats for {detector.name}: {e}")

        return stats


class AdaptiveEnsembleDetector(EnsembleDetector):
    """
    Adaptive ensemble that learns from feedback.

    Features:
    - Dynamic weight adjustment
    - Confidence threshold tuning
    - False positive tracking
    """

    def __init__(self, *args, **kwargs):
        """Initialize adaptive ensemble"""
        super().__init__(*args, **kwargs)

        # Track detector performance
        self._detector_hits = defaultdict(int)
        self._detector_misses = defaultdict(int)

    def report_feedback(self, detection: Dict[str, Any], is_correct: bool):
        """
        Report feedback on detection quality.

        Args:
            detection: Detection result
            is_correct: Whether detection was correct
        """
        detectors = detection.get("detectors", [])

        for detector_name in detectors:
            if is_correct:
                self._detector_hits[detector_name] += 1
            else:
                self._detector_misses[detector_name] += 1

        # Adjust weights based on performance
        self._adjust_weights()

    def _adjust_weights(self):
        """Adjust detector weights based on performance"""
        for detector_name in self._detector_hits.keys():
            hits = self._detector_hits[detector_name]
            misses = self._detector_misses[detector_name]
            total = hits + misses

            if total > 10:  # Require minimum feedback
                accuracy = hits / total
                # Adjust weight: higher accuracy = higher weight
                new_weight = 0.5 + (accuracy * 1.5)
                self.detector_weights[detector_name] = new_weight

                logger.info(
                    f"Adjusted weight for {detector_name}",
                    extra={
                        "extra_fields": {
                            "accuracy": accuracy,
                            "new_weight": new_weight,
                            "total_feedback": total
                        }
                    }
                )

    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance statistics for each detector.

        Returns:
            Dictionary with detector performance stats
        """
        stats = {}

        for detector_name in set(list(self._detector_hits.keys()) + list(self._detector_misses.keys())):
            hits = self._detector_hits[detector_name]
            misses = self._detector_misses[detector_name]
            total = hits + misses

            stats[detector_name] = {
                "hits": hits,
                "misses": misses,
                "total": total,
                "accuracy": hits / total if total > 0 else 0.0,
                "weight": self.detector_weights.get(detector_name, 1.0)
            }

        return stats
