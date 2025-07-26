#!/usr/bin/env python3
"""
Test du parser ville/code postal
"""

from utac_scraper import UTACScraper

def test_ville_parser():
    scraper = UTACScraper()
    
    # Cas de test
    test_cases = [
        ("METZ 57000", "METZ", "57000"),
        ("ST SEBASTIEN SUR LOIRE 44230", "ST SEBASTIEN SUR LOIRE", "44230"),
        ("PARIS 16EME ARRONDISSEMENT 75016", "PARIS 16EME ARRONDISSEMENT", "75016"),
        ("AIX EN PROVENCE 13090", "AIX EN PROVENCE", "13090"),
        ("BARCELONNETTE 04400", "BARCELONNETTE", "04400"),
        ("LA GARDE 83130", "LA GARDE", "83130"),
        ("SAINT-DENIS 93200", "SAINT-DENIS", "93200"),
        ("VILLEURBANNE 69100", "VILLEURBANNE", "69100"),
        ("FORT DE FRANCE 97200", "FORT DE FRANCE", "97200"),
        ("NOUMEA 98800", "NOUMEA", "98800"),
        ("", "", ""),  # Cas vide
        ("VILLE SANS CODE", "VILLE SANS CODE", ""),  # Pas de code postal
    ]
    
    print("=== Test du parser ville/code postal ===")
    print()
    
    all_success = True
    
    for i, (input_val, expected_ville, expected_cp) in enumerate(test_cases, 1):
        ville, code_postal = scraper._parse_ville_code_postal(input_val)
        
        success = (ville == expected_ville and code_postal == expected_cp)
        status = "✅" if success else "❌"
        
        print(f"Test {i:2d}: {status}")
        print(f"  Input:    '{input_val}'")
        print(f"  Expected: ville='{expected_ville}', cp='{expected_cp}'")
        print(f"  Got:      ville='{ville}', cp='{code_postal}'")
        
        if not success:
            all_success = False
            print(f"  ERROR: Résultat inattendu!")
        
        print()
    
    print("=== Résultat ===")
    if all_success:
        print("✅ Tous les tests réussis!")
    else:
        print("❌ Certains tests ont échoué!")
    
    return all_success

if __name__ == "__main__":
    test_ville_parser()