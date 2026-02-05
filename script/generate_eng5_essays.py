#!/usr/bin/env python3
"""
SCRUM-23: Synthetic Essay Library Generator
Skapar 200 syntetiska ENG5-uppsatser med Skolverkets kriterier och feedback-system.
"""
 
import argparse
import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

# Skolverkets kriterier för Engelska 5 (Gy11)
SKOLVERKET_CRITERIA = {
    "E": {
        "description": "Eleven uppnår inte kunskapskraven för kursen",
        "requirements": [
            "Begränsad förståelse av texter",
            "Stora brister i språklig korrekthet",
            "Svårigheter att uttrycka sig skriftligt",
            "Begränsad ordförråd och grammatik"
        ]
    },
    "C": {
        "description": "Eleven uppnår kunskapskraven för kursen",
        "requirements": [
            "God förståelse av texter på olika nivåer",
            "Språklig korrekthet i huvudsak",
            "Kan uttrycka sig skriftligt med viss säkerhet",
            "Adequat ordförråd och grammatik"
        ]
    },
    "A": {
        "description": "Eleven uppnår kunskapskraven för kursen med säkerhet",
        "requirements": [
            "Utmärkt förståelse av komplexa texter",
            "Hög språklig korrekthet",
            "Kan uttrycka sig skriftligt med stor säkerhet",
            "Rikt ordförråd och avancerad grammatik"
        ]
    }
}

@dataclass
class EssayMetadata:
    id: str
    title: str
    student_id: str
    word_count: int
    gold_level: str  # E, C, or A
    topics: List[str]
    difficulty: str
    created_at: str

class ENG5EssayGenerator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.essay_templates = self._load_essay_templates()
        self.topics = [
            "Climate Change and Environmental Issues",
            "Social Media and Its Impact on Society", 
            "The Role of Technology in Education",
            "Cultural Diversity in Modern Society",
            "The Importance of Mental Health",
            "Sustainable Living and Consumerism",
            "The Future of Work and Automation",
            "Globalization and Its Effects",
            "The Power of Literature and Storytelling",
            "Youth Activism and Social Change"
        ]
        
    def _load_essay_templates(self) -> Dict[str, List[str]]:
        """Laddar essay-mallar baserat på Skolverkets kriterier"""
        return {
            "E": [
                "I think {topic} is very important. Many people say it is good. I agree with this. It is very important for us. We should do more about this. I think everyone should care about this topic. It affects many people. We need to work together. This is my opinion about {topic}.",
                "In my opinion, {topic} is something we need to think about. Many people talk about this. I think it is important. We should do something. Everyone has different ideas. I think we should listen to each other. This is what I think about {topic}.",
                "I want to write about {topic}. This is very important topic. Many people are talking about this. I think we need to do something. It is not easy but we should try. I hope everyone will help. This is my view on {topic}."
            ],
            "C": [
                "The topic of {topic} has become increasingly relevant in today's society. While some argue that it presents significant challenges, others believe it offers opportunities for positive change. In this essay, I will explore both perspectives and provide my own analysis of this complex issue.",
                "When discussing {topic}, it is important to consider various viewpoints and their implications. This subject affects people from different backgrounds and requires careful examination. Through this essay, I aim to present a balanced discussion of the key aspects involved.",
                "The debate surrounding {topic} continues to evolve as new information becomes available. Understanding this topic requires looking at both historical context and current developments. In my analysis, I will examine the main arguments and their potential consequences."
            ],
            "A": [
                "The multifaceted nature of {topic} demands a comprehensive analysis that transcends simplistic binary thinking. This complex phenomenon intersects with numerous social, economic, and cultural factors, requiring nuanced examination of its implications for contemporary society. Through critical engagement with diverse scholarly perspectives, this essay will demonstrate how {topic} represents both a challenge and an opportunity for meaningful social transformation.",
                "Contemporary discourse on {topic} reveals a fascinating interplay between traditional paradigms and emerging frameworks of understanding. The complexity of this issue necessitates sophisticated analytical approaches that acknowledge both its historical roots and its dynamic present manifestations. This essay will argue that a holistic understanding of {topic} requires interdisciplinary thinking and careful consideration of multiple stakeholder perspectives.",
                "The evolving landscape of {topic} presents unprecedented challenges that demand innovative solutions grounded in both empirical evidence and theoretical sophistication. This essay will demonstrate how current approaches to {topic} must be reimagined through the lens of contemporary social theory, while maintaining critical awareness of the limitations inherent in any single analytical framework."
            ]
        }
    
    def _generate_essay_content(self, level: str, topic: str, target_words: int) -> str:
        """Genererar essay-innehåll baserat på nivå och ämne"""
        templates = self.essay_templates[level]
        base_template = self.rng.choice(templates)
        
        # Anpassa längd baserat på nivå
        if level == "E":
            # Korta, enkla meningar
            content = base_template.format(topic=topic)
            while len(content.split()) < target_words:
                content += " " + self.rng.choice([
                    "This is important.", "I think so.", "We should care.", 
                    "It matters a lot.", "Everyone knows this."
                ])
        elif level == "C":
            # Medellånga, strukturerade paragraf
            content = base_template.format(topic=topic)
            # Lägg till fler paragraf
            additional_paragraphs = [
                f"Furthermore, the implications of {topic} extend beyond immediate concerns. This requires careful consideration of long-term effects and potential solutions.",
                f"Another important aspect to consider is how {topic} affects different groups in society. This diversity of impact necessitates inclusive approaches to addressing the issue.",
                f"Looking forward, the future of {topic} will likely depend on our current actions and decisions. This makes it crucial to engage thoughtfully with the topic now."
            ]
            while len(content.split()) < target_words:
                content += " " + self.rng.choice(additional_paragraphs)
        else:  # A level
            # Långa, komplexa analyser
            content = base_template.format(topic=topic)
            # Lägg till avancerade analyser
            advanced_paragraphs = [
                f"Moreover, the theoretical underpinnings of {topic} reveal intricate connections to broader social phenomena. This complexity necessitates sophisticated analytical frameworks that can accommodate the multifaceted nature of the issue.",
                f"From a methodological perspective, studying {topic} requires interdisciplinary approaches that draw from various academic traditions. This methodological diversity enriches our understanding while also presenting challenges in terms of synthesis and coherence.",
                f"The epistemological implications of {topic} extend beyond mere empirical observation, touching upon fundamental questions about knowledge production and social understanding. This philosophical dimension adds depth to practical considerations."
            ]
            while len(content.split()) < target_words:
                content += " " + self.rng.choice(advanced_paragraphs)
        
        return content.strip()
    
    def _generate_feedback(self, level: str, word_count: int) -> str:
        """Genererar feedback baserat på Skolverkets kriterier"""
        criteria = SKOLVERKET_CRITERIA[level]
        
        if level == "E":
            feedback = f"Denna uppsats når E-nivå eftersom den visar begränsad förståelse av ämnet. "
            feedback += f"För att nå C-nivå behöver eleven: utveckla sina argument mer detaljerat, "
            feedback += f"använda ett bredare ordförråd, och strukturera texten tydligare. "
            feedback += f"Fokusera på att förklara dina tankar mer utförligt och använda exempel för att stödja dina påståenden."
        
        elif level == "C":
            feedback = f"Denna uppsats når C-nivå och visar god förståelse av ämnet. "
            feedback += f"För att nå A-nivå behöver eleven: utveckla mer sofistikerade analyser, "
            feedback += f"använda mer avancerat språk och ordförråd, och visa djupare kritiskt tänkande. "
            feedback += f"Fortsätt att bygga på dina starka sidor medan du arbetar med att fördjupa dina analyser."
        
        else:  # A level
            feedback = f"Denna uppsats når A-nivå och visar utmärkt förståelse av ämnet. "
            feedback += f"Eleven demonstrerar avancerat språkbruk, sofistikerad analys och djup förståelse. "
            feedback += f"Fortsätt att utveckla dina analytiska färdigheter och experimentera med olika skrivtekniker."
        
        return feedback
    
    def generate_essay(self, essay_id: str, student_id: str) -> Dict[str, Any]:
        """Genererar en enskild essay med metadata"""
        # Välj nivå (40% E, 40% C, 20% A för realistisk fördelning)
        level_weights = {"E": 0.4, "C": 0.4, "A": 0.2}
        level = self.rng.choices(list(level_weights.keys()), weights=list(level_weights.values()))[0]
        
        # Välj ämne
        topic = self.rng.choice(self.topics)
        
        # Generera titel
        title_templates = [
            f"My Thoughts on {topic}",
            f"Understanding {topic} in Today's World",
            f"The Importance of {topic}",
            f"Reflections on {topic}",
            f"{topic}: A Personal Perspective"
        ]
        title = self.rng.choice(title_templates)
        
        # Bestäm ordantal baserat på nivå
        word_counts = {"E": (150, 300), "C": (300, 500), "A": (500, 800)}
        min_words, max_words = word_counts[level]
        word_count = self.rng.randint(min_words, max_words)
        
        # Generera innehåll
        content = self._generate_essay_content(level, topic, word_count)
        
        # Generera feedback
        feedback = self._generate_feedback(level, word_count)
        
        # Skapa metadata
        metadata = EssayMetadata(
            id=essay_id,
            title=title,
            student_id=student_id,
            word_count=word_count,
            gold_level=level,
            topics=[topic],
            difficulty=level,
            created_at="2024-01-15T10:00:00Z"
        )
        
        return {
            "metadata": metadata.__dict__,
            "content": content,
            "feedback": feedback,
            "skolverket_criteria": criteria
        }
    
    def generate_essay_library(self, num_essays: int = 200) -> List[Dict[str, Any]]:
        """Genererar hela essay-biblioteket"""
        essays = []
        
        for i in range(1, num_essays + 1):
            essay_id = f"ENG5_ESSAY_{i:03d}"
            student_id = f"STUDENT_{self.rng.randint(1, 200):03d}"
            
            essay = self.generate_essay(essay_id, student_id)
            essays.append(essay)
        
        return essays

def save_essays_to_files(essays: List[Dict[str, Any]], output_dir: Path):
    """Sparar essays i olika format"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Metadata CSV
    metadata_file = output_dir / "essay_metadata.csv"
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'title', 'student_id', 'word_count', 'gold_level', 
            'topics', 'difficulty', 'created_at'
        ])
        writer.writeheader()
        for essay in essays:
            row = essay['metadata'].copy()
            row['topics'] = '|'.join(row['topics'])  # Convert list to pipe-separated
            writer.writerow(row)
    
    # 2. Gold tags CSV
    gold_file = output_dir / "gold_tags.csv"
    with open(gold_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'gold_level', 'criteria_description'])
        writer.writeheader()
        for essay in essays:
            writer.writerow({
                'id': essay['metadata']['id'],
                'gold_level': essay['metadata']['gold_level'],
                'criteria_description': SKOLVERKET_CRITERIA[essay['metadata']['gold_level']]['description']
            })
    
    # 3. Full JSON library
    json_file = output_dir / "essay_library.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(essays, f, indent=2, ensure_ascii=False)
    
    # 4. Individual essay files
    essays_dir = output_dir / "essays"
    essays_dir.mkdir(exist_ok=True)
    
    for essay in essays:
        essay_file = essays_dir / f"{essay['metadata']['id']}.txt"
        with open(essay_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {essay['metadata']['title']}\n")
            f.write(f"Student: {essay['metadata']['student_id']}\n")
            f.write(f"Level: {essay['metadata']['gold_level']}\n")
            f.write(f"Word Count: {essay['metadata']['word_count']}\n")
            f.write(f"Topics: {', '.join(essay['metadata']['topics'])}\n")
            f.write("-" * 50 + "\n\n")
            f.write(essay['content'])
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("FEEDBACK:\n")
            f.write(essay['feedback'])

def main():
    parser = argparse.ArgumentParser(description="Generate ENG5 Essay Library")
    parser.add_argument("--num-essays", type=int, default=200, help="Number of essays to generate")
    parser.add_argument("--output", type=str, default="script/output/essays", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    print(f"Generating {args.num_essays} ENG5 essays...")
    
    generator = ENG5EssayGenerator(seed=args.seed)
    essays = generator.generate_essay_library(args.num_essays)
    
    output_dir = Path(args.output)
    save_essays_to_files(essays, output_dir)
    
    # Statistik
    level_counts = {}
    for essay in essays:
        level = essay['metadata']['gold_level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print(f"✅ Generated {len(essays)} essays in {output_dir}")
    print(f"📊 Level distribution: {level_counts}")
    print(f"📁 Files created:")
    print(f"   - essay_metadata.csv")
    print(f"   - gold_tags.csv") 
    print(f"   - essay_library.json")
    print(f"   - essays/ (individual files)")

if __name__ == "__main__":
    main()
