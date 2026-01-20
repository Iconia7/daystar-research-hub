"""
SDG (Sustainable Development Goals) Classifier

Automatically detects and tags publications with relevant UN Sustainable Development Goals
based on keywords found in abstracts, titles, and metadata.

Uses keyword matching approach for lightweight, production-ready classification.
"""
import re
from typing import Set, List, Dict
from research_graph.models import SDGChoices


class SDGClassifier:
    """
    Keyword-based classifier for UN Sustainable Development Goals (SDGs 1-17).
    
    Provides methods to automatically tag publications, theses, and research projects
    with relevant SDGs based on textual analysis.
    """
    
    # SDG Keywords Dictionary
    # Each SDG mapped to relevant keywords that indicate alignment
    SDG_KEYWORDS = {
        SDGChoices.SDG_1: [
            'poverty', 'poor', 'low-income', 'vulnerable', 'disadvantaged',
            'economic inequality', 'welfare', 'subsistence', 'destitution',
            'extreme poverty', 'absolute poverty', 'poverty alleviation',
            'impoverished', 'impoverishment', 'deprivation', 'inequitable',
            'income inequality', 'wealth gap', 'economic disparity'
        ],
        SDGChoices.SDG_2: [
            'hunger', 'food security', 'malnutrition', 'famine', 'starvation',
            'agriculture', 'crop', 'farming', 'livestock', 'nutrition',
            'food production', 'agricultural productivity', 'food supply',
            'subsistence farming', 'food insecurity', 'dietary', 'nutritional'
        ],
        SDGChoices.SDG_3: [
            'health', 'disease', 'medical', 'healthcare', 'illness', 'wellness',
            'hospital', 'clinic', 'physician', 'medicine', 'treatment', 'vaccine',
            'mortality', 'morbidity', 'epidemiology', 'pandemic', 'epidemic',
            'mental health', 'well-being', 'healthy', 'sanitation', 'hygiene'
        ],
        SDGChoices.SDG_4: [
            'education', 'learning', 'school', 'university', 'student',
            'teacher', 'curriculum', 'academic', 'literacy', 'training',
            'skill development', 'educational', 'pedagogical', 'didactic',
            'higher education', 'primary education', 'secondary education',
            'quality education', 'equal education'
        ],
        SDGChoices.SDG_5: [
            'gender equality', 'gender', 'women', 'female', 'woman',
            'feminism', 'feminist', 'discrimination', 'bias', 'equity',
            'women\'s rights', 'gender-based violence', 'sexual harassment',
            'empowerment', 'gender parity', 'male-female', 'gender gap'
        ],
        SDGChoices.SDG_6: [
            'water', 'sanitation', 'hygiene', 'clean water', 'drinking water',
            'water supply', 'water treatment', 'wastewater', 'sewage',
            'water quality', 'water scarcity', 'water pollution', 'aquatic',
            'hydration', 'water security', 'water resources'
        ],
        SDGChoices.SDG_7: [
            'energy', 'renewable', 'solar', 'wind', 'hydroelectric', 'geothermal',
            'fossil fuel', 'electricity', 'power', 'clean energy', 'sustainable energy',
            'energy efficiency', 'energy access', 'energy security', 'biofuel',
            'nuclear energy', 'energy transition'
        ],
        SDGChoices.SDG_8: [
            'employment', 'jobs', 'work', 'labor', 'labour', 'wage', 'workplace',
            'economic growth', 'economic development', 'productivity', 'entrepreneurship',
            'business', 'decent work', 'working conditions', 'unemployment',
            'formal employment', 'informal economy'
        ],
        SDGChoices.SDG_9: [
            'infrastructure', 'industry', 'innovation', 'technology', 'industrial',
            'manufacturing', 'construct', 'bridge', 'road', 'transport',
            'innovation', 'research', 'development', 'industrial development',
            'resilient infrastructure', 'sustainable industry', 'ict'
        ],
        SDGChoices.SDG_10: [
            'inequality', 'inequitable', 'inequity', 'discrimination', 'marginalize',
            'disadvantaged', 'vulnerable', 'disparity', 'gap', 'unequal',
            'social inclusion', 'social cohesion', 'redistribution', 'equity'
        ],
        SDGChoices.SDG_11: [
            'city', 'urban', 'community', 'settlement', 'housing', 'slum',
            'sustainable city', 'sustainable community', 'livable', 'resilient',
            'disaster reduction', 'infrastructure', 'pollution', 'green space',
            'public transport', 'municipal'
        ],
        SDGChoices.SDG_12: [
            'consumption', 'production', 'waste', 'recycle', 'circular economy',
            'sustainable consumption', 'responsible consumption', 'resource',
            'material', 'pollution', 'sustainable management', 'reduce',
            'reuse', 'repurpose', 'lifecycle', 'footprint'
        ],
        SDGChoices.SDG_13: [
            'climate', 'global warming', 'greenhouse gas', 'carbon', 'emissions',
            'temperature', 'weather', 'climate change', 'mitigation', 'adaptation',
            'climate action', 'climate variability', 'extreme weather', 'gdp',
            'carbon dioxide', 'methane', 'environmental'
        ],
        SDGChoices.SDG_14: [
            'ocean', 'marine', 'sea', 'aquatic', 'fish', 'fishing', 'coral',
            'marine ecosystem', 'biodiversity', 'ocean acidification', 'pollution',
            'overfishing', 'sustainable fisheries', 'coastal', 'blue economy',
            'maritime', 'water body'
        ],
        SDGChoices.SDG_15: [
            'forest', 'woodland', 'terrestrial', 'ecosystem', 'biodiversity',
            'species', 'wildlife', 'conservation', 'endangered', 'habitat',
            'deforestation', 'land degradation', 'desertification', 'wetland',
            'vegetation', 'fauna', 'flora'
        ],
        SDGChoices.SDG_16: [
            'peace', 'justice', 'institution', 'governance', 'corruption',
            'violence', 'conflict', 'law enforcement', 'legal', 'rule of law',
            'human rights', 'discrimination', 'accountability', 'transparency',
            'democratic', 'inclusive'
        ],
        SDGChoices.SDG_17: [
            'partnership', 'collaboration', 'cooperation', 'stakeholder', 'multi-stakeholder',
            'network', 'alliance', 'development', 'finance', 'investment',
            'technology transfer', 'capacity building', 'global partnership',
            'sustainable development'
        ],
    }
    
    @classmethod
    def classify_text(cls, text: str, threshold: float = 0.3) -> List[str]:
        """
        Classify text and return list of detected SDG tags.
        
        Algorithm:
        1. Normalize and tokenize text
        2. Count keyword matches for each SDG
        3. Calculate match ratio (matches / unique_keywords)
        4. Return SDGs exceeding threshold
        
        Args:
            text: Text to classify (abstract, title, description)
            threshold: Minimum match ratio (0-1) to include SDG (default: 0.3 = 30%)
                      Adjust based on specificity needs:
                      - 0.1 = very permissive (many false positives)
                      - 0.3 = balanced (recommended)
                      - 0.5 = conservative (only strong matches)
            
        Returns:
            List of SDG choice values (e.g., ['SDG_1', 'SDG_3', 'SDG_13'])
            
        Example:
            >>> text = "This study analyzes climate change impacts on ocean ecosystems"
            >>> sdgs = SDGClassifier.classify_text(text)
            >>> print(sdgs)
            ['SDG_13', 'SDG_14']  # Climate Action, Life Below Water
        """
        if not text or not text.strip():
            return []
        
        # Normalize text
        normalized_text = cls._normalize_text(text)
        tokens = cls._tokenize(normalized_text)
        
        detected_sdgs = []
        
        # Check each SDG
        for sdg_choice, keywords in cls.SDG_KEYWORDS.items():
            # Count matches
            matches = cls._count_keyword_matches(tokens, keywords)
            
            if not matches:
                continue
            
            # Calculate match ratio
            # ratio = matches / number of unique keywords in list
            match_ratio = matches / len(keywords)
            
            # Include if exceeds threshold
            if match_ratio >= threshold:
                detected_sdgs.append(sdg_choice)
        
        return detected_sdgs
    
    @classmethod
    def classify_publication(cls, title: str = "", abstract: str = "", 
                            threshold: float = 0.3) -> List[str]:
        """
        Classify a publication based on title and abstract.
        
        Combines classification results from both title and abstract,
        giving more weight to abstract since it contains more detail.
        
        Args:
            title: Publication title
            abstract: Publication abstract
            threshold: Match threshold
            
        Returns:
            List of detected SDG tags
            
        Example:
            >>> title = "Climate Resilience in Urban Communities"
            >>> abstract = "This study examines adaptation strategies..."
            >>> sdgs = SDGClassifier.classify_publication(title, abstract)
        """
        sdgs_detected = set()
        
        # Classify title (lower weight)
        if title:
            title_sdgs = cls.classify_text(title, threshold=threshold + 0.1)
            sdgs_detected.update(title_sdgs)
        
        # Classify abstract (higher weight)
        if abstract:
            abstract_sdgs = cls.classify_text(abstract, threshold=threshold)
            sdgs_detected.update(abstract_sdgs)
        
        return sorted(list(sdgs_detected))
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for keyword matching.
        
        - Convert to lowercase
        - Remove special characters
        - Normalize whitespace
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but preserve word boundaries
        text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Split text into tokens (words)."""
        return set(text.split())
    
    @staticmethod
    def _count_keyword_matches(tokens: Set[str], keywords: List[str]) -> int:
        """
        Count how many keywords appear in token set.
        
        Performs both exact and partial matching:
        - Exact: "energy" matches token "energy"
        - Partial: "fuel" in "fossil fuel" matches token "fossil"
        """
        count = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_tokens = keyword_lower.split()
            
            # Check for exact phrase match
            # Build phrase from consecutive tokens
            if all(token in tokens for token in keyword_tokens):
                count += 1
            # Check for individual keyword tokens
            elif any(token in tokens for token in keyword_tokens):
                count += 0.5  # Partial match = half credit
        
        return int(count)
    
    @classmethod
    def get_sdg_description(cls, sdg_choice: str) -> str:
        """
        Get human-readable description for an SDG.
        
        Args:
            sdg_choice: SDG choice value (e.g., 'SDG_1')
            
        Returns:
            Human-readable label (e.g., 'No Poverty')
        """
        try:
            # Get the choice object
            for choice_value, choice_label in SDGChoices.choices:
                if choice_value == sdg_choice:
                    return choice_label
            return sdg_choice
        except:
            return sdg_choice
    
    @classmethod
    def get_keywords_for_sdg(cls, sdg_choice: str) -> List[str]:
        """
        Get list of keywords for a specific SDG.
        
        Useful for documentation and tuning thresholds.
        
        Args:
            sdg_choice: SDG choice value (e.g., 'SDG_3')
            
        Returns:
            List of keywords that trigger this SDG
        """
        return cls.SDG_KEYWORDS.get(sdg_choice, [])
    
    @classmethod
    def print_classifier_info(cls):
        """Print information about classifier for debugging."""
        print("\nSDG Classifier Information")
        print("=" * 70)
        print(f"Total SDGs: {len(cls.SDG_KEYWORDS)}")
        print(f"Total keywords: {sum(len(v) for v in cls.SDG_KEYWORDS.values())}")
        print()
        
        for sdg_choice, keywords in cls.SDG_KEYWORDS.items():
            label = cls.get_sdg_description(sdg_choice)
            print(f"{sdg_choice}: {label}")
            print(f"  Keywords ({len(keywords)}): {', '.join(keywords[:5])}...")
            print()


# Testing utilities
def test_sdg_classifier():
    """Run basic tests on SDG classifier."""
    print("\n" + "=" * 70)
    print("SDG CLASSIFIER TEST")
    print("=" * 70 + "\n")
    
    test_cases = [
        {
            'title': 'Climate Change and Ocean Acidification',
            'abstract': 'This study examines the effects of global warming on marine ecosystems, '
                       'coral reefs, and ocean pH levels in response to greenhouse gas emissions.',
            'expected_sdgs': ['SDG_13', 'SDG_14'],  # Climate Action, Life Below Water
        },
        {
            'title': 'Educational Innovation in Rural Communities',
            'abstract': 'We evaluate quality education programs designed to reduce educational '
                       'inequality and improve literacy rates in disadvantaged communities.',
            'expected_sdgs': ['SDG_4', 'SDG_10'],  # Quality Education, Reduced Inequalities
        },
        {
            'title': 'Renewable Energy for Sustainable Development',
            'abstract': 'Analysis of solar and wind energy technologies for affordable, clean energy '
                       'access in developing nations, focusing on energy efficiency and sustainability.',
            'expected_sdgs': ['SDG_7', 'SDG_17'],  # Affordable Clean Energy, Partnerships
        },
    ]
    
    classifier = SDGClassifier()
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['title']}")
        print(f"Expected: {test['expected_sdgs']}")
        
        detected = classifier.classify_publication(
            title=test['title'],
            abstract=test['abstract']
        )
        print(f"Detected: {detected}")
        
        # Show match details
        for sdg in detected:
            label = classifier.get_sdg_description(sdg)
            print(f"  ✓ {sdg}: {label}")
        
        print()
