#!/usr/bin/env python3

import sys
from utac_scraper import search_agreement

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_agreement.py NUMERO_AGREMENT")
        print("Exemple: python test_agreement.py 12345")
        sys.exit(1)
    
    agreement_number = sys.argv[1]
    search_agreement(agreement_number)

if __name__ == "__main__":
    main()