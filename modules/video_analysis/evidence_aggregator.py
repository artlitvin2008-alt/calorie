"""
Evidence aggregator - combines data from all frames and audio
"""

import logging
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class EvidenceAggregator:
    """Aggregates evidence from multiple frames and audio hypothesis"""
    
    async def aggregate(
        self, 
        audio_hypothesis: Dict[str, Any], 
        visual_evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combine all sources of information into single analysis
        
        Algorithm:
        1. For each component (dish) collect "votes" from all frames
        2. Consider confidence of each "vote"
        3. Consider audio hypothesis as additional vote with certain weight
        4. Make decision based on consensus
        5. If conflicts exist - mark as "low confidence"
        
        Args:
            audio_hypothesis: Hypothesis from audio
            visual_evidence_list: List of analysis results from frames
        
        Returns:
            Final aggregated analysis
        """
        if not visual_evidence_list:
            logger.warning("No visual evidence to aggregate")
            return self._empty_analysis()
        
        # 1. Collect all unique components from all frames
        all_components = self._collect_all_components(visual_evidence_list)
        
        # 2. For each component, conduct "voting"
        aggregated_components = []
        for component_name in all_components:
            votes = self._get_votes_for_component(component_name, visual_evidence_list)
            
            # If component mentioned in audio - increase its weight
            audio_bonus = 0.0
            if self._mentioned_in_audio(component_name, audio_hypothesis):
                audio_bonus = 0.3  # Trust user's words
                logger.info(f"Component '{component_name}' mentioned in audio, adding bonus")
            
            # Make decision: include component in final analysis?
            decision = self._make_decision(votes, audio_bonus)
            
            if decision['include']:
                # Calculate averaged values (weight, calories)
                aggregated_component = self._calculate_averages(
                    component_name, 
                    votes, 
                    decision['confidence']
                )
                aggregated_components.append(aggregated_component)
        
        # 3. Build final analysis
        final_analysis = self._build_final_analysis(
            aggregated_components,
            audio_hypothesis,
            visual_evidence_list
        )
        
        # 4. Add meta-information about process
        final_analysis['aggregation_metadata'] = {
            'frames_analyzed': len(visual_evidence_list),
            'conflicts_resolved': len(self._find_conflicts(visual_evidence_list)),
            'audio_hypothesis_used': bool(audio_hypothesis.get('transcription')),
            'final_confidence': self._calculate_overall_confidence(final_analysis)
        }
        
        return final_analysis
    
    def _collect_all_components(self, evidence_list: List[Dict[str, Any]]) -> set:
        """Collect all unique component names from all frames"""
        components = set()
        for evidence in evidence_list:
            if 'components' in evidence:
                for comp in evidence['components']:
                    components.add(comp.get('name', '').lower())
        return components
    
    def _get_votes_for_component(
        self, 
        component_name: str, 
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get all "votes" for a component from different frames
        
        Returns:
        {
            'positive': 3,  # Number of frames that detected this component
            'total': 5,     # Total frames analyzed
            'values': [     # All detected values
                {'weight_g': 200, 'calories': 150, 'confidence': 0.8},
                {'weight_g': 220, 'calories': 160, 'confidence': 0.7},
                ...
            ]
        }
        """
        votes = {
            'positive': 0,
            'total': len(evidence_list),
            'values': []
        }
        
        for evidence in evidence_list:
            if 'components' not in evidence:
                continue
            
            for comp in evidence['components']:
                if comp.get('name', '').lower() == component_name:
                    votes['positive'] += 1
                    votes['values'].append({
                        'weight_g': comp.get('weight_g', 0),
                        'calories': comp.get('calories', 0),
                        'protein_g': comp.get('protein_g', 0),
                        'fat_g': comp.get('fat_g', 0),
                        'carbs_g': comp.get('carbs_g', 0),
                        'confidence': comp.get('confidence', 0.5)
                    })
        
        return votes
    
    def _mentioned_in_audio(self, component_name: str, hypothesis: Dict[str, Any]) -> bool:
        """Check if component was mentioned in audio"""
        hyp = hypothesis.get('hypothesis', {})
        
        # Check primary dish
        primary = hyp.get('primary_dish')
        if primary and primary.get('name', '').lower() == component_name:
            return True
        
        # Check secondary items
        for item in hyp.get('secondary_items', []):
            if item.get('name', '').lower() == component_name:
                return True
        
        # Check mentioned items
        for item in hyp.get('mentioned_items', []):
            if item.lower() == component_name:
                return True
        
        return False
    
    def _make_decision(self, votes: Dict[str, Any], audio_bonus: float) -> Dict[str, Any]:
        """
        Make decision based on voting
        
        Logic:
        - If >=60% frames show component → include
        - If 40-60% → include with low confidence
        - If <40% → exclude (likely recognition error)
        - Audio bonus shifts boundaries
        
        Args:
            votes: Voting results
            audio_bonus: Bonus from audio mention (0-0.3)
        
        Returns:
            {'include': bool, 'confidence': str}
        """
        if votes['total'] == 0:
            return {'include': False, 'confidence': 'none'}
        
        vote_ratio = votes['positive'] / votes['total']
        adjusted_ratio = vote_ratio + audio_bonus
        
        if adjusted_ratio >= 0.6:
            return {'include': True, 'confidence': 'high'}
        elif adjusted_ratio >= 0.4:
            return {'include': True, 'confidence': 'medium'}
        else:
            return {'include': False, 'confidence': 'low'}
    
    def _calculate_averages(
        self, 
        component_name: str, 
        votes: Dict[str, Any], 
        confidence: str
    ) -> Dict[str, Any]:
        """Calculate averaged values for component"""
        if not votes['values']:
            return {
                'name': component_name,
                'weight_g': 0,
                'calories': 0,
                'protein_g': 0,
                'fat_g': 0,
                'carbs_g': 0,
                'confidence': 0.5
            }
        
        # Weighted average by confidence
        total_weight = sum(v['confidence'] for v in votes['values'])
        
        avg_weight_g = sum(v['weight_g'] * v['confidence'] for v in votes['values']) / total_weight
        avg_calories = sum(v['calories'] * v['confidence'] for v in votes['values']) / total_weight
        avg_protein = sum(v['protein_g'] * v['confidence'] for v in votes['values']) / total_weight
        avg_fat = sum(v['fat_g'] * v['confidence'] for v in votes['values']) / total_weight
        avg_carbs = sum(v['carbs_g'] * v['confidence'] for v in votes['values']) / total_weight
        avg_confidence = sum(v['confidence'] for v in votes['values']) / len(votes['values'])
        
        # Adjust confidence based on decision
        confidence_multiplier = {'high': 1.0, 'medium': 0.8, 'low': 0.6}.get(confidence, 0.5)
        final_confidence = avg_confidence * confidence_multiplier
        
        return {
            'name': component_name.title(),
            'weight_g': int(avg_weight_g),
            'calories': int(avg_calories),
            'protein_g': round(avg_protein, 1),
            'fat_g': round(avg_fat, 1),
            'carbs_g': round(avg_carbs, 1),
            'confidence': round(final_confidence, 2)
        }
    
    def _build_final_analysis(
        self,
        components: List[Dict[str, Any]],
        audio_hypothesis: Dict[str, Any],
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build final analysis structure"""
        # Calculate totals
        total_weight = sum(c['weight_g'] for c in components)
        total_calories = sum(c['calories'] for c in components)
        total_protein = sum(c['protein_g'] for c in components)
        total_fat = sum(c['fat_g'] for c in components)
        total_carbs = sum(c['carbs_g'] for c in components)
        
        # Determine dish name
        if components:
            dish_name = components[0]['name']
            if len(components) > 1:
                dish_name += f" с {components[1]['name'].lower()}"
        else:
            dish_name = "Неизвестное блюдо"
        
        # Calculate health score (simple heuristic)
        health_score = 5
        if total_protein > 20:
            health_score += 1
        if total_fat < 20:
            health_score += 1
        if total_carbs < 50:
            health_score += 1
        health_score = min(health_score, 10)
        
        # Generate warnings
        warnings = []
        if total_calories > 800:
            warnings.append("Высокая калорийность")
        if total_carbs > 100:
            warnings.append("Много углеводов")
        if total_protein < 15:
            warnings.append("Мало белка")
        
        return {
            'dish_name': dish_name,
            'components': components,
            'weight_grams': total_weight,
            'calories_total': total_calories,
            'calories_per_100g': int(total_calories / total_weight * 100) if total_weight > 0 else 0,
            'protein_g': round(total_protein, 1),
            'fat_g': round(total_fat, 1),
            'carbs_g': round(total_carbs, 1),
            'health_score': health_score,
            'warnings': warnings,
            'source': 'video_note',
            'audio_transcription': audio_hypothesis.get('transcription', ''),
            'transcription_used': bool(audio_hypothesis.get('transcription'))
        }
    
    def _find_conflicts(self, evidence_list: List[Dict[str, Any]]) -> List[str]:
        """Find conflicts between frames"""
        conflicts = []
        
        # Check if different frames identified different primary dishes
        primary_dishes = set()
        for evidence in evidence_list:
            if 'actual_dish' in evidence:
                primary_dishes.add(evidence['actual_dish'])
        
        if len(primary_dishes) > 1:
            conflicts.append(f"Different dishes identified: {', '.join(primary_dishes)}")
        
        return conflicts
    
    def _calculate_overall_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence of analysis"""
        if not analysis.get('components'):
            return 0.0
        
        # Average confidence of all components
        confidences = [c.get('confidence', 0.5) for c in analysis['components']]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Reduce if there are warnings
        if analysis.get('warnings'):
            avg_confidence *= 0.9
        
        return round(avg_confidence, 2)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'dish_name': 'Не удалось распознать',
            'components': [],
            'weight_grams': 0,
            'calories_total': 0,
            'calories_per_100g': 0,
            'protein_g': 0,
            'fat_g': 0,
            'carbs_g': 0,
            'health_score': 0,
            'warnings': ['Не удалось проанализировать видео'],
            'source': 'video_note',
            'audio_transcription': '',
            'transcription_used': False
        }
