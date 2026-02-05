#!/usr/bin/env python3
"""
Standalone test of Skolverket knowledge base content
"""

def create_skolverket_knowledge_base():
    """Create comprehensive Skolverket knowledge base for Engelska 5"""
    
    knowledge_items = [
        # Engelska - Ämnets syfte (exakt från Skolverket)
        {
            "content": "Engelska - Ämnets syfte: Det engelska språket omger oss i vardagen och används inom skilda områden som kultur, politik, utbildning och ekonomi. Kunskaper i engelska ökar individens möjligheter att ingå i olika sociala och kulturella sammanhang och att delta i ett globaliserat studie- och arbetsliv. Kunskaper i engelska kan dessutom ge nya perspektiv på omvärlden, ökade möjligheter till kontakter och större förståelse för olika sätt att leva. Undervisningen i ämnet engelska ska syfta till att eleverna utvecklar språk- och omvärldskunskaper så att de kan, vill och vågar använda engelska i olika situationer och för skilda syften.",
            "type": "amnes_syfte",
            "subject": "engelska",
            "level": "all",
            "criteria": "språk- och omvärldskunskaper, globaliserat liv, sociala sammanhang, kulturella sammanhang"
        },
        
        # Engelska - Kommunikativ förmåga
        {
            "content": "Engelska - Kommunikativ förmåga: Eleverna ska ges möjlighet att, genom språkanvändning i funktionella och meningsfulla sammanhang, utveckla en allsidig kommunikativ förmåga. Denna förmåga innefattar dels reception, som innebär att förstå talat språk och texter, dels produktion och interaktion, som innebär att formulera sig och samspela med andra i tal och skrift samt att anpassa sitt språk till olika situationer, syften och mottagare. Genom undervisningen ska eleverna även ges möjlighet att utveckla språklig säkerhet i tal och skrift samt förmåga att uttrycka sig med variation och komplexitet.",
            "type": "amnes_syfte",
            "subject": "engelska",
            "level": "all",
            "criteria": "kommunikativ förmåga, reception, produktion, interaktion, språklig säkerhet, variation, komplexitet"
        },
        
        # Betygskriterier - Betyget E (exakt från Skolverket)
        {
            "content": "Betyget E - Engelska 5: Eleven lyssnar samt förstår och tolkar huvudsakligt innehåll och tydliga detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar huvudsakligt innehåll och tydliga detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant sätt det valda materialet i sin egen produktion och interaktion.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "E-nivå, lyssnande, läsning, källkritik, muntlig produktion, skriftlig produktion, interaktion, diskussion"
        },
        
        # Betygskriterier - Betyget C (exakt från Skolverket)
        {
            "content": "Betyget C - Engelska 5: Eleven lyssnar samt förstår och tolkar på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant och effektivt sätt det valda materialet i sin egen produktion och interaktion.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "C-nivå, välgrundat, väsentliga detaljer, effektivt, strukturerat, flyt, utvecklat"
        },
        
        # Betygskriterier - Betyget A (exakt från Skolverket)
        {
            "content": "Betyget A - Engelska 5: Eleven lyssnar samt förstår och tolkar på ett välgrundat och nyanserat sätt såväl helhet som detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar på ett välgrundat och nyanserat sätt såväl helhet som detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant, effektivt och problematiserande sätt det valda materialet i sin egen produktion och interaktion.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "A-nivå, välgrundat, nyanserat, helhet, detaljer, problematiserande, kritiskt tänkande"
        }
    ]
    
    return knowledge_items

def test_knowledge_base():
    """Test the knowledge base content"""
    
    items = create_skolverket_knowledge_base()
    
    print(f"✅ Created {len(items)} knowledge items")
    print()
    
    # Show all items
    print("📚 Knowledge items:")
    for i, item in enumerate(items, 1):
        print(f"{i}. Type: {item['type']}")
        print(f"   Subject: {item['subject']}, Level: {item['level']}")
        print(f"   Content: {item['content'][:150]}...")
        print()
    
    # Show all types
    types = set(item['type'] for item in items)
    print(f"🎯 Knowledge types: {sorted(types)}")
    print()
    
    print("🎉 Knowledge base test completed successfully!")

if __name__ == "__main__":
    test_knowledge_base()

