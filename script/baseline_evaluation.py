#!/usr/bin/env python3
"""
SCRUM-23: Baseline Evaluation Utility
Jämför AI-förslag vs gold standard för ENG5 essays.
"""

import argparse
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import pandas as pd

class BaselineEvaluator:
    def __init__(self, essay_library_path: str):
        self.essay_library = self._load_essay_library(essay_library_path)
        self.gold_labels = self._extract_gold_labels()
    
    def _load_essay_library(self, path: str) -> List[Dict[str, Any]]:
        """Laddar essay-biblioteket"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_gold_labels(self) -> List[str]:
        """Extraherar gold labels från biblioteket"""
        return [essay['metadata']['gold_level'] for essay in self.essay_library]
    
    def predict_level_heuristic(self, essay_content: str) -> str:
        """Enkel heuristik-baserad prediktion"""
        word_count = len(essay_content.split())
        sentences = essay_content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Enkla regler baserat på Skolverkets kriterier
        if word_count < 200 or avg_sentence_length < 8:
            return "E"
        elif word_count < 400 or avg_sentence_length < 15:
            return "C"
        else:
            return "A"
    
    def predict_level_advanced(self, essay_content: str) -> str:
        """Mer avancerad prediktion baserat på flera faktorer"""
        word_count = len(essay_content.split())
        sentences = essay_content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Räkna avancerade språkliga indikatorer
        complex_words = sum(1 for word in essay_content.split() if len(word) > 6)
        complex_ratio = complex_words / word_count if word_count > 0 else 0
        
        # Räkna transition words och avancerade uttryck
        transition_words = ['however', 'furthermore', 'moreover', 'nevertheless', 'consequently', 
                           'therefore', 'additionally', 'similarly', 'conversely', 'meanwhile']
        transition_count = sum(1 for word in essay_content.lower().split() if word in transition_words)
        
        # Räkna subjektiva uttryck (indikerar mindre avancerat språk)
        subjective_words = ['i think', 'i believe', 'i feel', 'i think that', 'in my opinion']
        subjective_count = sum(1 for phrase in subjective_words if phrase in essay_content.lower())
        
        # Kombinera faktorer för prediktion
        score = 0
        
        # Ordantal (40% vikt)
        if word_count >= 500:
            score += 4
        elif word_count >= 300:
            score += 2
        elif word_count >= 200:
            score += 1
        
        # Meninglängd (30% vikt)
        if avg_sentence_length >= 20:
            score += 3
        elif avg_sentence_length >= 15:
            score += 2
        elif avg_sentence_length >= 10:
            score += 1
        
        # Komplexa ord (20% vikt)
        if complex_ratio >= 0.3:
            score += 2
        elif complex_ratio >= 0.2:
            score += 1
        
        # Transition words (10% vikt)
        if transition_count >= 3:
            score += 1
        
        # Subjektiva uttryck (negativ vikt)
        if subjective_count > 2:
            score -= 1
        
        # Konvertera score till nivå
        if score >= 7:
            return "A"
        elif score >= 4:
            return "C"
        else:
            return "E"
    
    def evaluate_baseline(self, method: str = "heuristic") -> Dict[str, Any]:
        """Utvärderar baseline-metod mot gold standard"""
        predictions = []
        
        for essay in self.essay_library:
            content = essay['content']
            
            if method == "heuristic":
                pred = self.predict_level_heuristic(content)
            elif method == "advanced":
                pred = self.predict_level_advanced(content)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            predictions.append(pred)
        
        # Beräkna metrics
        accuracy = accuracy_score(self.gold_labels, predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            self.gold_labels, predictions, average=None, labels=['E', 'C', 'A']
        )
        
        # Confusion matrix
        cm = confusion_matrix(self.gold_labels, predictions, labels=['E', 'C', 'A'])
        
        # Per-level metrics
        per_level_metrics = {}
        for i, level in enumerate(['E', 'C', 'A']):
            per_level_metrics[level] = {
                'precision': precision[i],
                'recall': recall[i],
                'f1_score': f1[i],
                'support': int(support[i])
            }
        
        return {
            'method': method,
            'overall_accuracy': accuracy,
            'per_level_metrics': per_level_metrics,
            'confusion_matrix': cm.tolist(),
            'total_essays': len(self.essay_library),
            'gold_distribution': dict(zip(*np.unique(self.gold_labels, return_counts=True))),
            'predicted_distribution': dict(zip(*np.unique(predictions, return_counts=True)))
        }
    
    def generate_detailed_report(self, method: str = "heuristic") -> List[Dict[str, Any]]:
        """Genererar detaljerad rapport per essay"""
        detailed_results = []
        
        for i, essay in enumerate(self.essay_library):
            content = essay['content']
            gold_level = essay['metadata']['gold_level']
            
            if method == "heuristic":
                predicted_level = self.predict_level_heuristic(content)
            else:
                predicted_level = self.predict_level_advanced(content)
            
            # Analysera faktorer
            word_count = len(content.split())
            sentences = content.split('.')
            avg_sentence_length = word_count / len(sentences) if sentences else 0
            
            detailed_results.append({
                'essay_id': essay['metadata']['id'],
                'student_id': essay['metadata']['student_id'],
                'title': essay['metadata']['title'],
                'gold_level': gold_level,
                'predicted_level': predicted_level,
                'correct': gold_level == predicted_level,
                'word_count': word_count,
                'avg_sentence_length': avg_sentence_length,
                'content_preview': content[:200] + "..." if len(content) > 200 else content
            })
        
        return detailed_results

def main():
    parser = argparse.ArgumentParser(description="Baseline Evaluation for ENG5 Essays")
    parser.add_argument("--essay-library", type=str, default="script/output/essays/essay_library.json")
    parser.add_argument("--method", choices=["heuristic", "advanced"], default="heuristic")
    parser.add_argument("--output", type=str, default="script/output/evaluation")
    parser.add_argument("--detailed", action="store_true", help="Generate detailed per-essay report")
    
    args = parser.parse_args()
    
    print(f"Loading essay library from {args.essay_library}...")
    evaluator = BaselineEvaluator(args.essay_library)
    
    print(f"Evaluating baseline method: {args.method}")
    results = evaluator.evaluate_baseline(args.method)
    
    # Skapa output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Spara huvudrapport
    report_file = output_dir / f"baseline_report_{args.method}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Spara CSV för enkel analys
    csv_file = output_dir / f"baseline_metrics_{args.method}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Level', 'Precision', 'Recall', 'F1-Score', 'Support'])
        for level in ['E', 'C', 'A']:
            metrics = results['per_level_metrics'][level]
            writer.writerow([
                level, 
                f"{metrics['precision']:.3f}",
                f"{metrics['recall']:.3f}",
                f"{metrics['f1_score']:.3f}",
                metrics['support']
            ])
    
    # Generera detaljerad rapport om begärt
    if args.detailed:
        print("Generating detailed per-essay report...")
        detailed_results = evaluator.generate_detailed_report(args.method)
        
        detailed_file = output_dir / f"detailed_report_{args.method}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
        
        # CSV för detaljerad analys
        detailed_csv = output_dir / f"detailed_results_{args.method}.csv"
        with open(detailed_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'essay_id', 'student_id', 'title', 'gold_level', 'predicted_level', 
                'correct', 'word_count', 'avg_sentence_length', 'content_preview'
            ])
            writer.writeheader()
            writer.writerows(detailed_results)
    
    # Skriv ut sammanfattning
    print(f"\n📊 Baseline Evaluation Results ({args.method})")
    print(f"Overall Accuracy: {results['overall_accuracy']:.3f}")
    print(f"Total Essays: {results['total_essays']}")
    print(f"\nPer-Level Metrics:")
    for level in ['E', 'C', 'A']:
        metrics = results['per_level_metrics'][level]
        print(f"  {level}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1_score']:.3f}")
    
    print(f"\n📁 Reports saved to {output_dir}")
    print(f"   - baseline_report_{args.method}.json")
    print(f"   - baseline_metrics_{args.method}.csv")
    if args.detailed:
        print(f"   - detailed_report_{args.method}.json")
        print(f"   - detailed_results_{args.method}.csv")

if __name__ == "__main__":
    import numpy as np
    main()
