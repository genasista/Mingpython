#!/usr/bin/env python3
"""
Load Skolverket Knowledge Base for RAG System
Creates a comprehensive knowledge base with Gy25 criteria for Engelska 5
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.servies.vector_service import vector_db

logger = logging.getLogger("skolverket_knowledge")

def create_skolverket_knowledge_base() -> List[Dict[str, Any]]:
    """Create comprehensive Skolverket knowledge base for Engelska 5 (Gy25)"""
    
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
        
        # Engelska - Strategier och språkmedvetenhet
        {
            "content": "Engelska - Strategier och språkmedvetenhet: Eleverna ska ges möjlighet att utveckla förmåga att använda olika strategier för att underlätta kommunikationen när språkkunskaperna inte räcker till. Eleverna ska ges möjlighet att utveckla förståelse av livsvillkor, samhällsfrågor och kulturella förhållanden i olika sammanhang och områden där engelska används. Undervisningen ska stimulera elevernas nyfikenhet på språk och kultur samt ge dem förutsättningar att utveckla sin flerspråkighet där kunskaper i olika språk samverkar och stödjer varandra.",
            "type": "amnes_syfte",
            "subject": "engelska",
            "level": "all",
            "criteria": "strategier, kommunikation, livsvillkor, samhällsfrågor, kulturella förhållanden, flerspråkighet"
        },
        
        # Engelska - Undervisningsprinciper
        {
            "content": "Engelska - Undervisningsprinciper: Undervisningen ska i allt väsentligt bedrivas på engelska. I undervisningen ska eleverna få möta talad och skriven engelska av olika slag samt få sätta innehållet i relation till egna erfarenheter och kunskaper. Eleverna ska ges möjlighet att interagera i tal och skrift samt producera talat språk och olika texter, på egen hand och tillsammans med andra, och med stöd av olika hjälpmedel och medier.",
            "type": "amnes_syfte",
            "subject": "engelska",
            "level": "all",
            "criteria": "undervisning på engelska, talad och skriven engelska, erfarenheter, interaktion, hjälpmedel"
        },
        
        # Engelska - Utvecklingsmål
        {
            "content": "Engelska - Utvecklingsmål: Undervisningen i ämnet engelska ska ge eleverna förutsättningar att utveckla följande: Förståelse av engelska i tal och skrift. Förmåga att formulera sig och kommunicera på engelska i tal och skrift. Förmåga att anpassa språket efter olika syften, mottagare och sammanhang. Förståelse av kulturella och sociala förhållanden i olika sammanhang och områden där engelska används.",
            "type": "amnes_syfte",
            "subject": "engelska",
            "level": "all",
            "criteria": "förståelse, kommunikation, anpassning, kulturella förhållanden, sociala förhållanden"
        },
        
        # LGY11 - Skolans värdegrund och grundläggande värden
        {
            "content": "LGY11 - Skolans värdegrund: Skolväsendet vilar på demokratins grund. Utbildningen ska främja elevers utveckling och lärande samt en livslång lust att lära. Utbildningen ska förmedla och förankra respekt för de mänskliga rättigheterna och de grundläggande demokratiska värderingar som det svenska samhället vilar på. Undervisningen ska vila på vetenskaplig grund och beprövad erfarenhet. Människolivets okränkbarhet, individens frihet och integritet, alla människors lika värde, jämställdhet mellan kvinnor och män samt solidaritet mellan människor är de värden som utbildningen ska gestalta och förmedla.",
            "type": "lgy11_vardegrund",
            "subject": "allmän",
            "level": "all",
            "criteria": "demokrati, mänskliga rättigheter, jämställdhet, solidaritet, vetenskaplig grund"
        },
        
        # LGY11 - Förståelse och medmänsklighet
        {
            "content": "LGY11 - Förståelse och medmänsklighet: Skolan ska främja förståelse för andra människor och förmåga till inlevelse. Utbildningen ska präglas av öppenhet och respekt för människors olikheter. Ingen ska i skolan utsättas för diskriminering. Alla tendenser till diskriminering eller kränkande behandling ska aktivt motverkas. Skolan är en social och kulturell mötesplats som ska stärka förmågan att leva med och inse de värden som ligger i en kulturell mångfald.",
            "type": "lgy11_vardegrund",
            "subject": "allmän",
            "level": "all",
            "criteria": "förståelse, medmänsklighet, respekt, olikheter, diskriminering, kulturell mångfald"
        },
        
        # LGY11 - Saklighet och allsidighet
        {
            "content": "LGY11 - Saklighet och allsidighet: Skolan ska vara öppen för skilda uppfattningar och uppmuntra att de förs fram. Den ska framhålla betydelsen av personliga ställningstaganden och ge möjligheter till sådana. Undervisningen ska vara saklig och allsidig. När värderingar redovisas, ska det alltid klart framgå vem det är som står för dem.",
            "type": "lgy11_vardegrund",
            "subject": "allmän",
            "level": "all",
            "criteria": "saklighet, allsidighet, ställningstaganden, värderingar, öppenhet"
        },
        
        # LGY11 - Likvärdig utbildning
        {
            "content": "LGY11 - Likvärdig utbildning: Undervisningen ska anpassas till varje elevs förutsättningar och behov. Utbildningen inom varje skolform ska vara likvärdig, oavsett var i landet den anordnas. En likvärdig utbildning innebär inte att undervisningen ska utformas på samma sätt överallt, men hänsyn ska tas till elevernas olika förutsättningar, behov och kunskapsnivå. Skolan ska aktivt och medvetet främja elevernas lika rättigheter och möjligheter oberoende av könstillhörighet.",
            "type": "lgy11_vardegrund",
            "subject": "allmän",
            "level": "all",
            "criteria": "likvärdig utbildning, anpassning, förutsättningar, behov, jämställdhet"
        },
        
        # LGY11 - Gymnasieskolans uppdrag
        {
            "content": "LGY11 - Gymnasieskolans uppdrag: Huvuduppgiften för gymnasieskolan är att förmedla kunskaper och skapa förutsättningar för att eleverna ska tillägna sig och utveckla kunskaper. Utbildningen ska främja elevernas utveckling till ansvarskännande människor, som aktivt deltar i och utvecklar yrkes- och samhällslivet. Eleverna ska träna sig att tänka kritiskt, att granska information och förhållanden och att inse konsekvenserna av olika alternativ. På så vis närmar sig eleverna ett vetenskapligt sätt att tänka och arbeta.",
            "type": "lgy11_uppdrag",
            "subject": "allmän",
            "level": "all",
            "criteria": "kunskaper, ansvarskännande, kritiskt tänkande, vetenskapligt sätt, samhällsliv"
        },
        
        # LGY11 - Kunskaper och lärande
        {
            "content": "LGY11 - Kunskaper och lärande: Kunskap kommer till uttryck i olika former - såsom fakta, förståelse, färdighet och förtrogenhet - som förutsätter och samspelar med varandra. Elevernas kunskapsutveckling är beroende av om de får möjlighet att se samband. Skolan ska ge eleverna möjligheter att få överblick och sammanhang. Eleverna ska få möjlighet att reflektera över sina erfarenheter och tillämpa sina kunskaper.",
            "type": "lgy11_kunskap",
            "subject": "allmän",
            "level": "all",
            "criteria": "kunskap, fakta, förståelse, färdighet, förtrogenhet, samband, reflektion"
        },
        
        # LGY11 - Bedömning och betyg
        {
            "content": "LGY11 - Bedömning och betyg: Betyget uttrycker i vilken utsträckning den enskilda eleven har uppfyllt de nationella betygskriterier som finns för varje kurs. Läraren ska göra en allsidig bedömning av elevens kunskaper i förhållande till de nationella betygskriterier som finns för respektive kurs, och beakta även sådana kunskaper som en elev har tillägnat sig på annat sätt än genom den aktuella undervisningen. Läraren ska fortlöpande ge varje elev information om framgångar och utvecklingsbehov i studierna.",
            "type": "lgy11_bedomning",
            "subject": "allmän",
            "level": "all",
            "criteria": "betyg, nationella kriterier, allsidig bedömning, framgångar, utvecklingsbehov"
        },
        
        # LGY11 - Digital kompetens
        {
            "content": "LGY11 - Digital kompetens: I ett allt mer digitaliserat samhälle ska skolan bidra till att utveckla elevernas digitala kompetens. Skolan ska bidra till att eleverna utvecklar förståelse av hur digitaliseringen påverkar individen och samhällets utveckling. Alla elever ska ges möjlighet att utveckla sin förmåga att använda digital teknik. De ska också ges möjlighet att utveckla ett kritiskt och ansvarsfullt förhållningssätt till digital teknik, för att kunna se möjligheter och förstå risker samt för att kunna värdera information.",
            "type": "lgy11_digital",
            "subject": "allmän",
            "level": "all",
            "criteria": "digital kompetens, digital teknik, kritiskt förhållningssätt, information, värdering"
        },
        
        # LGY11 - Internationellt perspektiv
        {
            "content": "LGY11 - Internationellt perspektiv: Ett internationellt perspektiv är viktigt för att kunna se den egna verkligheten i ett globalt sammanhang och för att skapa internationell solidaritet. Undervisningen i olika ämnen ska ge eleverna kunskaper om Europeiska unionen och dess betydelse för Sverige samt förbereda eleverna för ett samhälle med allt tätare kontakter över nations- och kulturgränser. Det internationella perspektivet ska också bidra till att utveckla elevernas förståelse för den kulturella mångfalden inom landet.",
            "type": "lgy11_internationellt",
            "subject": "allmän",
            "level": "all",
            "criteria": "internationellt perspektiv, globalt sammanhang, solidaritet, kulturell mångfald, EU"
        },
        
        # LGY11 - Hållbar utveckling
        {
            "content": "LGY11 - Hållbar utveckling: Miljöperspektivet i undervisningen ska ge eleverna insikter så att de kan dels själva medverka till att hindra skadlig miljöpåverkan, dels skaffa sig ett personligt förhållningssätt till de övergripande och globala miljöfrågorna. Undervisningen ska belysa hur samhällets funktioner och vårt sätt att leva och arbeta kan anpassas för att skapa hållbar utveckling. Eleverna ska kunna observera och analysera människans samspel med sin omvärld utifrån perspektivet hållbar utveckling.",
            "type": "lgy11_hallbar",
            "subject": "allmän",
            "level": "all",
            "criteria": "hållbar utveckling, miljöperspektiv, miljöpåverkan, globala frågor, samspel"
        },
        
        # Engelska 5 - Ämnets syfte och centralt innehåll
        {
            "content": "Engelska 5 - Ämnets syfte: Kursen engelska 5 omfattar punkterna 1–4 under rubriken Ämnets syfte. Centralt innehåll: Kommunikationens innehåll - Aktuella och bekanta ämnesområden, även med anknytning till samhälls- och arbetsliv och till elevernas utbildning. Händelser och händelseförlopp. Åsikter, tankar och erfarenheter samt relationer och etiska frågor. Innehåll och form i olika typer av fiktion. Aktuella händelser, sociala och kulturella företeelser och förhållanden samt värderingar i olika sammanhang och områden där engelska används, även i jämförelse med egna erfarenheter och kunskaper. Engelska språkets ställning i världen.",
            "type": "centralt_innehall",
            "subject": "engelska",
            "level": "5",
            "criteria": "kommunikation, ämnesområden, händelser, åsikter, fiktion, kulturella företeelser"
        },
        
        # Reception - Läsning och lyssnande
        {
            "content": "Engelska 5 - Reception: Talad engelska i varierande tempo, även med inslag av sociolektal och dialektal variation, och texter, från olika medier. Talad engelska och texter som är berättande, förklarande, diskuterande, argumenterande och rapporterande – varje slag för sig eller i olika kombinationer. Till exempel intervjuer, reportage, manualer och enklare populärvetenskapliga texter. Skönlitteratur och annan fiktion. Sånger och dikter. Strategier för att uppfatta detaljer och dra slutsatser om innehåll och budskap, till exempel genom att visualisera, associera, återberätta, förutse innehåll och ställa sig frågor.",
            "type": "centralt_innehall",
            "subject": "engelska",
            "level": "5",
            "criteria": "reception, lyssnande, läsning, texter, strategier, förståelse"
        },
        
        # Källkritik och språklig variation
        {
            "content": "Engelska 5 - Källkritik och språklig variation: Sökning av innehåll i muntliga och skriftliga källor av olika slag och utifrån olika syften. Värdering av källornas relevans och trovärdighet. Hur variation och anpassning skapas genom meningsbyggnad, ord och fraser, till exempel kollokationer. Hur struktur och sammanhang skapas genom ord och fraser som markerar till exempel orsakssammanhang, talarens inställning, tidsaspekt och avslutning.",
            "type": "centralt_innehall",
            "subject": "engelska",
            "level": "5",
            "criteria": "källkritik, källor, relevans, trovärdighet, språklig variation, meningsbyggnad"
        },
        
        # Produktion och interaktion
        {
            "content": "Engelska 5 - Produktion och interaktion: Muntlig och skriftlig produktion och interaktion av olika slag, även i mer formella sammanhang, där eleverna berättar, återger, förklarar, motiverar sina åsikter, värderar och diskuterar. Strategier för att bidra till och aktivt medverka i diskussioner och skriftlig interaktion, även digital, med anknytning till samhälls- och arbetslivet, till exempel genom att ställa följdfrågor, formulera om, förklara och bidra med nya infallsvinklar.",
            "type": "centralt_innehall",
            "subject": "engelska",
            "level": "5",
            "criteria": "produktion, interaktion, muntlig, skriftlig, formella sammanhang, strategier"
        },
        
        # Språkliga företeelser och bearbetning
        {
            "content": "Engelska 5 - Språkliga företeelser och bearbetning: Språkliga företeelser, däribland uttal, vokabulär, grammatiska strukturer och meningsbyggnad, stavning, textbindning, inre och yttre struktur samt anpassning, i elevernas egen produktion och interaktion. Bearbetning av egna muntliga och skriftliga framställningar för att förtydliga, variera och precisera samt för att skapa struktur och anpassa kommunikationen efter syfte, mottagare och sammanhang.",
            "type": "centralt_innehall",
            "subject": "engelska",
            "level": "5",
            "criteria": "språkliga företeelser, uttal, vokabulär, grammatik, stavning, textbindning, bearbetning"
        },
        
        # Betygskriterier - Betyget E (exakt från Skolverket)
        {
            "content": "Betyget E - Engelska 5: Eleven lyssnar samt förstår och tolkar huvudsakligt innehåll och tydliga detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar huvudsakligt innehåll och tydliga detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant sätt det valda materialet i sin egen produktion och interaktion. I muntliga framställningar av olika slag formulerar sig eleven med viss variation, relativt tydligt och relativt sammanhängande. Eleven formulerar sig även med visst flyt och i någon mån anpassat till syfte, mottagare och situation. I skriftliga framställningar av olika slag formulerar sig eleven med viss variation, relativt tydligt och relativt sammanhängande. Eleven formulerar sig även med visst flyt och i någon mån anpassat till syfte, mottagare och situation. I interaktion i olika sammanhang, även mer formella, uttrycker sig eleven relativt tydligt och med visst flyt samt i någon mån anpassat till syfte, mottagare och situation. Dessutom använder eleven strategier som i viss utsträckning underlättar och förbättrar interaktionen. Eleven diskuterar översiktligt, på engelska, förhållanden i olika sammanhang och områden där språket används, även utifrån egna erfarenheter eller kunskaper.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "E-nivå, lyssnande, läsning, källkritik, muntlig produktion, skriftlig produktion, interaktion, diskussion"
        },
        
        # Betygskriterier - Betyget D
        {
            "content": "Betyget D - Engelska 5: Elevens kunskaper bedöms sammantaget vara mellan C och E.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "D-nivå, mellan C och E"
        },
        
        # Betygskriterier - Betyget C (exakt från Skolverket)
        {
            "content": "Betyget C - Engelska 5: Eleven lyssnar samt förstår och tolkar på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant och effektivt sätt det valda materialet i sin egen produktion och interaktion. I muntliga framställningar av olika slag formulerar sig eleven med viss variation, tydligt, sammanhängande och relativt strukturerat. Eleven formulerar sig även med flyt och viss anpassning till syfte, mottagare och situation. I skriftliga framställningar av olika slag formulerar sig eleven med viss variation, tydligt, sammanhängande och relativt strukturerat. Eleven formulerar sig även med flyt och viss anpassning till syfte, mottagare och situation. I interaktion i olika sammanhang, även mer formella, uttrycker sig eleven tydligt och med flyt samt med viss anpassning till syfte, mottagare och situation. Dessutom använder eleven strategier som underlättar och förbättrar interaktionen. Eleven diskuterar utvecklat, på engelska, förhållanden i olika sammanhang och områden där språket används, även utifrån egna erfarenheter eller kunskaper.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "C-nivå, välgrundat, väsentliga detaljer, effektivt, strukturerat, flyt, utvecklat"
        },
        
        # Betygskriterier - Betyget B
        {
            "content": "Betyget B - Engelska 5: Elevens kunskaper bedöms sammantaget vara mellan A och C.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "B-nivå, mellan A och C"
        },
        
        # Betygskriterier - Betyget A (exakt från Skolverket)
        {
            "content": "Betyget A - Engelska 5: Eleven lyssnar samt förstår och tolkar på ett välgrundat och nyanserat sätt såväl helhet som detaljer i talat språk i varierande tempo och i olika sammanhang. Eleven läser samt förstår och tolkar på ett välgrundat och nyanserat sätt såväl helhet som detaljer i tydligt formulerade texter av olika slag. Eleven väljer med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag och använder på ett relevant, effektivt och problematiserande sätt det valda materialet i sin egen produktion och interaktion. I muntliga framställningar av olika slag formulerar sig eleven varierat, tydligt, sammanhängande och strukturerat. Eleven formulerar sig även relativt ledigt och med viss anpassning till syfte, mottagare och situation. I skriftliga framställningar av olika slag formulerar sig eleven varierat, tydligt, sammanhängande och strukturerat. Eleven formulerar sig även relativt ledigt och med viss anpassning till syfte, mottagare och situation. I interaktion i olika sammanhang, även mer formella, uttrycker sig eleven tydligt, relativt ledigt och med viss anpassning till syfte, mottagare och situation. Dessutom använder eleven strategier som underlättar och förbättrar interaktionen och för den framåt på ett konstruktivt sätt. Eleven diskuterar välutvecklat, på engelska, förhållanden i olika sammanhang och områden där språket används, även utifrån egna erfarenheter eller kunskaper.",
            "type": "betygskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "A-nivå, välgrundat, nyanserat, helhet, detaljer, problematiserande, varierat, ledigt, konstruktivt, välutvecklat"
        },
        
        # Skriftlig kommunikation - E-nivå
        {
            "content": "Skriftlig kommunikation E-nivå: Eleven kan skriva enkla texter på engelska med tydlig struktur. Texterna innehåller grundläggande information och följer enkla mönster. Eleven använder grundläggande språkstrukturer och har en begränsad men funktionell ordförråd.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "skriftlig, E-nivå, enkel struktur, grundläggande information"
        },
        
        # Skriftlig kommunikation - C-nivå
        {
            "content": "Skriftlig kommunikation C-nivå: Eleven kan skriva strukturerade texter på engelska med tydlig disposition och logisk uppbyggnad. Texterna innehåller relevant information och följer etablerade genrer. Eleven använder språket med variation och har ett utvecklat ordförråd som gör det möjligt att uttrycka sig tydligt.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "skriftlig, C-nivå, strukturerad, logisk uppbyggnad"
        },
        
        # Skriftlig kommunikation - A-nivå
        {
            "content": "Skriftlig kommunikation A-nivå: Eleven kan skriva välstrukturerade texter på engelska med sofistikerad disposition och genomtänkt uppbyggnad. Texterna innehåller relevant och välutvecklad information och följer genrer med stilistisk medvetenhet. Eleven använder språket med stor variation och har ett rikt ordförråd som gör det möjligt att uttrycka sig nyanserat.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "skriftlig, A-nivå, välstrukturerad, sofistikerad disposition"
        },
        
        # Textanalys - E-nivå
        {
            "content": "Textanalys E-nivå: Eleven kan identifiera grundläggande textdrag som ämne, syfte och mottagare i enkla texter på engelska. Eleven kan förklara textens huvudsakliga budskap och identifiera enkla språkliga drag som ordval och meningar.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "textanalys, E-nivå, grundläggande textdrag, huvudsakligt budskap"
        },
        
        # Textanalys - C-nivå
        {
            "content": "Textanalys C-nivå: Eleven kan analysera textdrag som ämne, syfte, mottagare och genre i olika typer av texter på engelska. Eleven kan förklara textens budskap och hur det förmedlas, samt analysera språkliga drag som ordval, meningsbyggnad och stilistiska val.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "textanalys, C-nivå, analysera textdrag, språkliga drag"
        },
        
        # Textanalys - A-nivå
        {
            "content": "Textanalys A-nivå: Eleven kan göra djupgående analyser av textdrag som ämne, syfte, mottagare, genre och kontext i komplexa texter på engelska. Eleven kan förklara textens budskap och hur det förmedlas, samt göra sofistikerade analyser av språkliga drag och stilistiska val med hänsyn till textens funktion och effekt.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "textanalys, A-nivå, djupgående analyser, sofistikerade analyser"
        },
        
        # Muntlig kommunikation - E-nivå
        {
            "content": "Muntlig kommunikation E-nivå: Eleven kan förstå och delta i enkla samtal på engelska om vardagliga ämnen. Eleven kan uttrycka sig med grundläggande språkstrukturer och har en begränsad men funktionell ordförråd som gör det möjligt att kommunicera i enkla situationer.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "muntlig, E-nivå, enkla samtal, vardagliga ämnen"
        },
        
        # Muntlig kommunikation - C-nivå
        {
            "content": "Muntlig kommunikation C-nivå: Eleven kan förstå och delta i samtal på engelska om olika ämnen. Eleven kan uttrycka sig med variation och har ett utvecklat ordförråd som gör det möjligt att kommunicera tydligt i olika situationer.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "muntlig, C-nivå, olika ämnen, variation"
        },
        
        # Muntlig kommunikation - A-nivå
        {
            "content": "Muntlig kommunikation A-nivå: Eleven kan förstå och delta i samtal på engelska om komplexa ämnen. Eleven kan uttrycka sig med precision och variation och har ett rikt ordförråd som gör det möjligt att kommunicera nyanserat i olika situationer.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "muntlig, A-nivå, komplexa ämnen, precision och variation"
        },
        
        # Språklig korrekthet - E-nivå
        {
            "content": "Språklig korrekthet E-nivå: Eleven använder grundläggande språkstrukturer med viss korrekthet. Stavning och uttal är i huvudsak korrekt i enkla sammanhang. Eleven har en begränsad men funktionell ordförråd som täcker grundläggande behov.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "språklig korrekthet, E-nivå, grundläggande strukturer, begränsad ordförråd"
        },
        
        # Språklig korrekthet - C-nivå
        {
            "content": "Språklig korrekthet C-nivå: Eleven använder språkstrukturer med god korrekthet. Stavning och uttal är i huvudsak korrekt. Eleven har ett utvecklat ordförråd som täcker olika behov och gör det möjligt att uttrycka sig tydligt.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "språklig korrekthet, C-nivå, god korrekthet, utvecklat ordförråd"
        },
        
        # Språklig korrekthet - A-nivå
        {
            "content": "Språklig korrekthet A-nivå: Eleven använder språkstrukturer med hög korrekthet. Stavning och uttal är korrekt. Eleven har ett rikt ordförråd som täcker olika behov och gör det möjligt att uttrycka sig nyanserat och med stilistisk medvetenhet.",
            "type": "bedomningskriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "språklig korrekthet, A-nivå, hög korrekthet, rikt ordförråd"
        },
        
        # Specifika kriterier för lyssnande och förståelse
        {
            "content": "Lyssnande och förståelse - Engelska 5: Eleven ska förstå och tolka talat språk i varierande tempo och i olika sammanhang. För E-nivå: huvudsakligt innehåll och tydliga detaljer. För C-nivå: på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer. För A-nivå: på ett välgrundat och nyanserat sätt såväl helhet som detaljer.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "lyssnande, förståelse, tempo, sammanhang, huvudsakligt innehåll, detaljer, helhet"
        },
        
        # Specifika kriterier för läsning och tolkning
        {
            "content": "Läsning och tolkning - Engelska 5: Eleven ska förstå och tolka texter av olika slag. För E-nivå: huvudsakligt innehåll och tydliga detaljer i tydligt formulerade texter. För C-nivå: på ett välgrundat sätt huvudsakligt innehåll och väsentliga detaljer i tydligt formulerade texter. För A-nivå: på ett välgrundat och nyanserat sätt såväl helhet som detaljer i tydligt formulerade texter.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "läsning, tolkning, texter, formulerade, innehåll, detaljer, helhet"
        },
        
        # Specifika kriterier för källkritik och materialanvändning
        {
            "content": "Källkritik och materialanvändning - Engelska 5: Eleven ska välja med källkritisk medvetenhet innehåll från muntliga och skriftliga källor av olika slag. För E-nivå: använder på ett relevant sätt det valda materialet. För C-nivå: använder på ett relevant och effektivt sätt det valda materialet. För A-nivå: använder på ett relevant, effektivt och problematiserande sätt det valda materialet.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "källkritik, medvetenhet, källor, relevant, effektivt, problematiserande"
        },
        
        # Specifika kriterier för muntlig produktion
        {
            "content": "Muntlig produktion - Engelska 5: Eleven ska formulera sig i muntliga framställningar av olika slag. För E-nivå: med viss variation, relativt tydligt och relativt sammanhängande, med visst flyt och i någon mån anpassat till syfte, mottagare och situation. För C-nivå: med viss variation, tydligt, sammanhängande och relativt strukturerat, med flyt och viss anpassning till syfte, mottagare och situation. För A-nivå: varierat, tydligt, sammanhängande och strukturerat, relativt ledigt och med viss anpassning till syfte, mottagare och situation.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "muntlig produktion, variation, tydligt, sammanhängande, strukturerat, flyt, ledigt, anpassning"
        },
        
        # Specifika kriterier för skriftlig produktion
        {
            "content": "Skriftlig produktion - Engelska 5: Eleven ska formulera sig i skriftliga framställningar av olika slag. För E-nivå: med viss variation, relativt tydligt och relativt sammanhängande, med visst flyt och i någon mån anpassat till syfte, mottagare och situation. För C-nivå: med viss variation, tydligt, sammanhängande och relativt strukturerat, med flyt och viss anpassning till syfte, mottagare och situation. För A-nivå: varierat, tydligt, sammanhängande och strukturerat, relativt ledigt och med viss anpassning till syfte, mottagare och situation.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "skriftlig produktion, variation, tydligt, sammanhängande, strukturerat, flyt, ledigt, anpassning"
        },
        
        # Specifika kriterier för interaktion
        {
            "content": "Interaktion - Engelska 5: Eleven ska uttrycka sig i interaktion i olika sammanhang, även mer formella. För E-nivå: relativt tydligt och med visst flyt samt i någon mån anpassat till syfte, mottagare och situation, använder strategier som i viss utsträckning underlättar och förbättrar interaktionen. För C-nivå: tydligt och med flyt samt med viss anpassning till syfte, mottagare och situation, använder strategier som underlättar och förbättrar interaktionen. För A-nivå: tydligt, relativt ledigt och med viss anpassning till syfte, mottagare och situation, använder strategier som underlättar och förbättrar interaktionen och för den framåt på ett konstruktivt sätt.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "interaktion, sammanhang, formella, tydligt, flyt, ledigt, strategier, konstruktivt"
        },
        
        # Specifika kriterier för diskussion
        {
            "content": "Diskussion - Engelska 5: Eleven ska diskutera förhållanden i olika sammanhang och områden där språket används, även utifrån egna erfarenheter eller kunskaper. För E-nivå: diskuterar översiktligt. För C-nivå: diskuterar utvecklat. För A-nivå: diskuterar välutvecklat.",
            "type": "specifika_kriterier",
            "subject": "engelska",
            "level": "5",
            "criteria": "diskussion, sammanhang, områden, erfarenheter, kunskaper, översiktligt, utvecklat, välutvecklat"
        },
        
        # Feedback och utveckling - E till C
        {
            "content": "Utveckling från E till C: För att nå C-nivå ska eleven utveckla sin förmåga att strukturera texter logiskt, använda mer varierade språkstrukturer och utöka sitt ordförråd. Eleven bör träna på att analysera texter mer systematiskt och uttrycka sig tydligare.",
            "type": "utvecklingsstod",
            "subject": "engelska",
            "level": "5",
            "criteria": "E till C, struktur, variation, ordförråd, analys"
        },
        
        # Feedback och utveckling - C till A
        {
            "content": "Utveckling från C till A: För att nå A-nivå ska eleven utveckla sin förmåga att göra djupgående analyser av texter, använda språket med större variation och precision, samt utveckla ett rikt ordförråd. Eleven bör träna på stilistisk medvetenhet och sofistikerad textproduktion.",
            "type": "utvecklingsstod",
            "subject": "engelska",
            "level": "5",
            "criteria": "C till A, djupgående analyser, variation, precision, stilistisk medvetenhet"
        },
        
        # Genomgående bedömningsaspekter
        {
            "content": "Genomgående bedömningsaspekter Engelska 5: Bedömningen ska fokusera på elevens förmåga att förstå, tolka och producera texter på engelska. Viktiga aspekter inkluderar språklig korrekthet, kommunikativ förmåga, textanalytisk förmåga och språklig variation. Bedömningen ska vara formativ och stödja elevens fortsatta utveckling.",
            "type": "bedomningsaspekter",
            "subject": "engelska",
            "level": "5",
            "criteria": "genomgående, bedömning, formativ, utveckling, språklig korrekthet"
        }
    ]
    
    return knowledge_items

async def load_knowledge_base():
    """Load the Skolverket knowledge base into the vector database"""
    try:
        # Create knowledge items
        knowledge_items = create_skolverket_knowledge_base()
        
        print(f"Created {len(knowledge_items)} knowledge base items")
        
        # Load into vector database
        success = vector_db.add_knowledge_base(knowledge_items)
        
        if success:
            print("✅ Successfully loaded Skolverket knowledge base")
            
            # Get stats
            stats = vector_db.get_collection_stats()
            print(f"📊 Database stats: {stats}")
            
        else:
            print("❌ Failed to load knowledge base")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading knowledge base: {e}")
        return False

async def test_knowledge_search():
    """Test the knowledge base search functionality"""
    try:
        print("\n🔍 Testing knowledge base search...")
        
        # Test queries
        test_queries = [
            "What are the requirements for grade A in English 5?",
            "How should I give feedback to students at E level?",
            "What are the criteria for written communication?",
            "How can students improve from C to A level?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = vector_db.search_knowledge(
                query=query,
                subject="engelska",
                level="5",
                n_results=2
            )
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['content'][:100]}... (Score: {result['relevance_score']:.3f})")
        
        print("\n✅ Knowledge base search test completed")
        
    except Exception as e:
        print(f"❌ Knowledge base search test failed: {e}")

async def main():
    """Main function to load and test the knowledge base"""
    print("🚀 Loading Skolverket Knowledge Base for RAG System")
    print("=" * 60)
    
    # Load knowledge base
    success = await load_knowledge_base()
    
    if success:
        # Test search functionality
        await test_knowledge_search()
        
        print("\n🎉 Knowledge base setup completed successfully!")
        print("\nNext steps:")
        print("1. Start your FastAPI service")
        print("2. Test the RAG endpoints")
        print("3. Upload documents and analyze student submissions")
    
    else:
        print("\n❌ Knowledge base setup failed")

if __name__ == "__main__":
    asyncio.run(main())
