#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UTACScraper:
    def __init__(self):
        self.base_url = "https://www.utac-otc.com"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération de la page: {e}")
            return None
    
    def scrape_ct_search_page(self):
        url = "https://www.utac-otc.com/vehicule_leger/Pages/Retrouver_un_CT.aspx"
        soup = self.get_page(url)
        
        if not soup:
            return None
        
        result = {
            'page_title': soup.title.text.strip() if soup.title else '',
            'forms': [],
            'input_fields': [],
            'tables': [],
            'links': []
        }
        
        # Chercher les formulaires
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                'id': form.get('id', ''),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                input_data = {
                    'name': inp.get('name', ''),
                    'type': inp.get('type', ''),
                    'id': inp.get('id', ''),
                    'placeholder': inp.get('placeholder', ''),
                    'value': inp.get('value', '')
                }
                form_data['inputs'].append(input_data)
            
            result['forms'].append(form_data)
        
        # Chercher tous les champs input
        inputs = soup.find_all(['input', 'select', 'textarea'])
        for inp in inputs:
            input_data = {
                'name': inp.get('name', ''),
                'type': inp.get('type', ''),
                'id': inp.get('id', ''),
                'placeholder': inp.get('placeholder', ''),
                'value': inp.get('value', '')
            }
            result['input_fields'].append(input_data)
        
        # Chercher les tableaux
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header row
                row = [td.get_text().strip() for td in tr.find_all('td')]
                if row:
                    rows.append(row)
            
            result['tables'].append({
                'index': i,
                'headers': headers,
                'rows': rows[:5]  # Limit to first 5 rows
            })
        
        # Chercher les liens importants
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href and not href.startswith('#'):
                full_url = urljoin(url, href)
                result['links'].append({
                    'text': link.get_text().strip()[:100],
                    'href': full_url
                })
        
        return result
    
    def search_by_agreement_number(self, agreement_number):
        """
        Recherche un centre de contrôle technique par numéro d'agrément
        """
        url = "https://www.utac-otc.com/vehicule_leger/Pages/Retrouver_un_CT.aspx"
        soup = self.get_page(url)
        
        if not soup:
            return None
        
        # Trouver le formulaire principal
        form = soup.find('form', {'id': 'aspnetForm'})
        if not form:
            print("Formulaire principal non trouvé")
            return None
        
        # Récupérer tous les champs cachés nécessaires pour ASP.NET
        form_data = {}
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        for inp in hidden_inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value
        
        # Trouver le champ de critère et le dropdown
        criteria_field = None
        dropdown_field = None
        
        # Rechercher tous les inputs et selects
        all_inputs = form.find_all(['input', 'select'])
        for inp in all_inputs:
            inp_name = inp.get('name', '')
            
            # Chercher le champ critère (input text qui contient "critereValueInput")
            if inp.name == 'input' and inp.get('type') == 'text' and 'critereValueInput' in inp_name:
                criteria_field = inp_name
            
            # Chercher le dropdown qui contient "ddlCritereField"
            if inp.name == 'select' and 'ddlCritereField' in inp_name:
                dropdown_field = inp_name
                # Sélectionner l'option "Agrement"
                form_data[dropdown_field] = 'Agrement'
        
        if not criteria_field or not dropdown_field:
            print("Champs de recherche non trouvés")
            return self._debug_form_fields(form)
        
        # Remplir le formulaire
        form_data[criteria_field] = agreement_number
        
        # Trouver et ajouter le bouton de recherche
        search_button = form.find('input', {'type': 'submit', 'value': 'Rechercher'})
        if search_button:
            button_name = search_button.get('name')
            if button_name:
                form_data[button_name] = search_button.get('value', 'Rechercher')
        
        # Ajouter les données de soumission ASP.NET
        form_data['__EVENTTARGET'] = ''
        form_data['__EVENTARGUMENT'] = ''
        
        # Envoyer la requête POST
        try:
            response = self.session.post(url, data=form_data, timeout=10)
            response.raise_for_status()
            
            # Parser la réponse
            result_soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_search_results(result_soup, agreement_number)
            
        except requests.RequestException as e:
            print(f"Erreur lors de la recherche: {e}")
            return None
    
    def _debug_form_fields(self, form):
        """Fonction de debug pour afficher tous les champs du formulaire"""
        print("=== DEBUG: Champs du formulaire ===")
        all_inputs = form.find_all(['input', 'select', 'textarea'])
        for inp in all_inputs:
            print(f"Tag: {inp.name}, Name: {inp.get('name', 'N/A')}, ID: {inp.get('id', 'N/A')}, Type: {inp.get('type', 'N/A')}")
            if inp.name == 'select':
                options = inp.find_all('option')
                for opt in options:
                    print(f"  Option: {opt.get('value', 'N/A')} - {opt.get_text().strip()}")
        return {"debug": "Champs du formulaire affichés"}
    
    def _parse_search_results(self, soup, agreement_number):
        """Parse les résultats de recherche et trouve les informations"""
        
        # D'abord, regarder si on a des informations directement dans les résultats
        result_info = self._extract_info_from_results_page(soup, agreement_number)
        if result_info and any(result_info[key] for key in ['raison_sociale', 'enseigne', 'adresse', 'ville', 'telephone']):
            return result_info
        
        # Chercher le tableau de résultats et les liens JavaScript
        tables = soup.find_all('table')
        detail_link = None
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    # Chercher le lien "Voir le détail"
                    link = cell.find('a', string=lambda text: text and 'détail' in text.lower())
                    if link:
                        href = link.get('href')
                        if href and href.startswith('javascript:'):
                            # Extraire les paramètres du JavaScript
                            detail_link = self._handle_javascript_link(href, soup)
                        else:
                            detail_link = href
                        break
                if detail_link:
                    break
            if detail_link:
                break
        
        if not detail_link:
            print("Lien 'Voir le détail' non trouvé")
            # Afficher plus d'info de debug
            tables_info = []
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                if rows:
                    tables_info.append(f"Table {i}: {len(rows)} rows")
                    for j, row in enumerate(rows[:2]):  # First 2 rows
                        cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                        tables_info.append(f"  Row {j}: {cells}")
            
            return {"error": "Lien détail non trouvé", "debug_tables": tables_info}
        
        # Construire l'URL complète du lien détail
        if detail_link.startswith('http'):
            detail_url = detail_link
        else:
            detail_url = urljoin("https://www.utac-otc.com/vehicule_leger/Pages/", detail_link)
        
        # Récupérer la page de détail
        return self._get_agreement_details(detail_url, agreement_number)
    
    def _extract_info_from_results_page(self, soup, agreement_number):
        """Essaie d'extraire les informations directement de la page de résultats"""
        details = {
            'agreement_number': agreement_number,
            'raison_sociale': '',
            'enseigne': '',
            'adresse': '',
            'ville': '',
            'telephone': '',
            'option': '',
            'site_internet': '',
            'url': 'Page de résultats'
        }
        
        # Chercher dans tous les tableaux
        tables = soup.find_all('table')
        for table in tables:
            # D'abord, analyser les en-têtes pour comprendre la structure
            headers = table.find_all('th')
            header_mapping = {}
            
            if headers:
                for i, th in enumerate(headers):
                    header_text = th.get_text().strip().lower()
                    if 'raison sociale' in header_text:
                        header_mapping['raison_sociale'] = i
                    elif 'agrement' in header_text:
                        header_mapping['agreement_number'] = i
                    elif 'enseigne' in header_text:
                        header_mapping['enseigne'] = i
                    elif 'adresse' in header_text:
                        header_mapping['adresse'] = i
                    elif 'ville' in header_text:
                        header_mapping['ville'] = i
                    elif 'tél' in header_text:
                        header_mapping['telephone'] = i
                    elif 'option' in header_text:
                        header_mapping['option'] = i
                    elif 'site internet' in header_text:
                        header_mapping['site_internet'] = i
            
            # Chercher la ligne avec le numéro d'agrément
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_text = ' '.join([cell.get_text().strip() for cell in cells])
                
                # Si la ligne contient le numéro d'agrément, extraire toutes les informations
                if agreement_number in row_text:
                    # Mapping basé sur la structure connue du tableau UTAC-OTC:
                    # [0] Raison sociale, [1] Agrément, [2] Enseigne (hidden), [3] Adresse
                    # [4] Ville, [5] Tél (hidden), [6] Option, [7] Site internet (hidden), [8] Détails
                    
                    if len(cells) >= 8:
                        details['raison_sociale'] = cells[0].get_text().strip()
                        details['agreement_number'] = cells[1].get_text().strip()
                        details['enseigne'] = cells[2].get_text().strip()  # Colonne cachée
                        details['adresse'] = cells[3].get_text().strip()
                        details['ville'] = cells[4].get_text().strip()
                        details['telephone'] = cells[5].get_text().strip()  # Colonne cachée
                        details['option'] = cells[6].get_text().strip()
                        details['site_internet'] = cells[7].get_text().strip()  # Colonne cachée
                    
                    # Alternative : utiliser le mapping des en-têtes si disponible
                    elif header_mapping:
                        for field, index in header_mapping.items():
                            if index < len(cells):
                                details[field] = cells[index].get_text().strip()
                    
                    break  # On a trouvé la ligne, pas besoin de continuer
        
        return details
    
    def _handle_javascript_link(self, js_link, soup):
        """Gère les liens JavaScript ASP.NET"""
        # Pour les liens JavaScript ASP.NET, nous devons simuler le postback
        # Pour l'instant, retournons None pour éviter l'erreur
        print(f"Lien JavaScript détecté: {js_link}")
        return None
    
    def _get_agreement_details(self, detail_url, agreement_number):
        """Récupère les détails du centre d'agrément"""
        
        detail_soup = self.get_page(detail_url)
        if not detail_soup:
            return {"error": "Impossible de récupérer la page de détail"}
        
        details = {
            'agreement_number': agreement_number,
            'enseigne': '',
            'adresse': '',
            'ville': '',
            'telephone': '',
            'url': detail_url
        }
        
        # Rechercher les informations dans le contenu de la page
        text_content = detail_soup.get_text()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        # Chercher les informations spécifiques
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if 'enseigne' in line_lower and ':' in line:
                details['enseigne'] = line.split(':', 1)[1].strip()
            elif 'adresse' in line_lower and ':' in line:
                details['adresse'] = line.split(':', 1)[1].strip()
            elif 'ville' in line_lower and ':' in line:
                details['ville'] = line.split(':', 1)[1].strip()
            elif 'tél' in line_lower and ':' in line:
                details['telephone'] = line.split(':', 1)[1].strip()
        
        # Méthode alternative: chercher dans les éléments structurés
        if not any(details[key] for key in ['enseigne', 'adresse', 'ville', 'telephone']):
            # Chercher dans les éléments avec des labels
            labels = detail_soup.find_all(['label', 'span', 'div', 'td'])
            for label in labels:
                text = label.get_text().strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'enseigne' in key:
                        details['enseigne'] = value
                    elif 'adresse' in key:
                        details['adresse'] = value
                    elif 'ville' in key:
                        details['ville'] = value
                    elif 'tél' in key:
                        details['telephone'] = value
        
        return details
    
    def search_by_department(self, department_code):
        """
        Recherche tous les centres de contrôle technique d'un département
        
        Args:
            department_code (str): Code du département (ex: "04", "75", "971")
            
        Returns:
            list: Liste des centres trouvés avec toutes leurs informations
        """
        # Valider le format du département
        if not self._validate_department_code(department_code):
            return {"error": f"Code département invalide: {department_code}"}
        
        url = "https://www.utac-otc.com/vehicule_leger/Pages/Retrouver_un_CT.aspx"
        soup = self.get_page(url)
        
        if not soup:
            return {"error": "Impossible de récupérer la page de recherche"}
        
        # Trouver le formulaire principal
        form = soup.find('form', {'id': 'aspnetForm'})
        if not form:
            return {"error": "Formulaire principal non trouvé"}
        
        # Préparer les données du formulaire
        form_data = {}
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        for inp in hidden_inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value
        
        # Trouver les champs de recherche
        criteria_field = None
        dropdown_field = None
        
        all_inputs = form.find_all(['input', 'select'])
        for inp in all_inputs:
            inp_name = inp.get('name', '')
            
            if inp.name == 'input' and inp.get('type') == 'text' and 'critereValueInput' in inp_name:
                criteria_field = inp_name
            
            if inp.name == 'select' and 'ddlCritereField' in inp_name:
                dropdown_field = inp_name
        
        if not criteria_field or not dropdown_field:
            return {"error": "Champs de recherche non trouvés"}
        
        # Remplir le formulaire pour recherche par département
        form_data[criteria_field] = department_code
        form_data[dropdown_field] = 'Departement'
        
        # Ajouter le bouton de recherche
        search_button = form.find('input', {'type': 'submit', 'value': 'Rechercher'})
        if search_button:
            button_name = search_button.get('name')
            if button_name:
                form_data[button_name] = search_button.get('value', 'Rechercher')
        
        form_data['__EVENTTARGET'] = ''
        form_data['__EVENTARGUMENT'] = ''
        
        # Effectuer la recherche initiale
        try:
            response = self.session.post(url, data=form_data, timeout=10)
            response.raise_for_status()
            
            result_soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire tous les résultats avec pagination
            all_centers = []
            page_number = 1
            
            while True:
                print(f"Traitement de la page {page_number}...")
                
                # Extraire les centres de la page actuelle
                page_centers = self._extract_all_centers_from_page(result_soup, department_code)
                all_centers.extend(page_centers)
                
                # Chercher le lien vers la page suivante
                next_page_link = self._find_next_page_link(result_soup)
                
                if not next_page_link:
                    print(f"Pas de page suivante trouvée. Total: {len(all_centers)} centres")
                    break
                
                # Naviguer vers la page suivante
                result_soup = self._navigate_to_next_page(result_soup, next_page_link)
                if not result_soup:
                    print("Erreur lors de la navigation vers la page suivante")
                    break
                
                page_number += 1
                
                # Sécurité : éviter les boucles infinies
                if page_number > 50:
                    print("Limite de 50 pages atteinte, arrêt de la pagination")
                    break
            
            return {
                "department_code": department_code,
                "total_centers": len(all_centers),
                "centers": all_centers
            }
            
        except requests.RequestException as e:
            return {"error": f"Erreur lors de la recherche: {e}"}
    
    def _validate_department_code(self, code):
        """Valide le format du code département"""
        if not code or not isinstance(code, str):
            return False
        
        # Supprimer les espaces
        code = code.strip()
        
        # Vérifier le format
        if code.isdigit():
            num = int(code)
            # Départements 01-95 ou DOM-TOM 971-989
            return (1 <= num <= 95) or (971 <= num <= 989)
        
        return False
    
    def _extract_all_centers_from_page(self, soup, department_code):
        """Extrait tous les centres de la page actuelle"""
        centers = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 8:  # Ligne complète de données
                    row_text = ' '.join([cell.get_text().strip() for cell in cells])
                    
                    # Vérifier si cette ligne appartient au département recherché
                    if self._is_department_row(row_text, department_code):
                        center_info = self._extract_center_from_row(cells)
                        if center_info:
                            centers.append(center_info)
        
        return centers
    
    def _is_department_row(self, row_text, department_code):
        """Vérifie si une ligne appartient au département recherché"""
        # Chercher les codes postaux correspondant au département
        dept_num = int(department_code)
        
        if dept_num <= 95:
            # Départements métropolitains : codes postaux commencent par le numéro du département
            dept_formatted = f"{dept_num:02d}"  # Format 01, 02, etc.
            postal_codes = [f"{dept_formatted}{i:03d}" for i in range(1000)]  # 01000-01999, etc.
            return any(postal in row_text for postal in [dept_formatted + '0', dept_formatted + '1', dept_formatted + '2', dept_formatted + '3', dept_formatted + '4', dept_formatted + '5', dept_formatted + '6', dept_formatted + '7', dept_formatted + '8', dept_formatted + '9'])
        else:
            # DOM-TOM : codes postaux = numéro département
            return department_code in row_text
    
    def _extract_center_from_row(self, cells):
        """Extrait les informations d'un centre depuis une ligne de tableau"""
        if len(cells) < 8:
            return None
        
        return {
            'raison_sociale': cells[0].get_text().strip(),
            'agreement_number': cells[1].get_text().strip(),
            'enseigne': cells[2].get_text().strip(),
            'adresse': cells[3].get_text().strip(),
            'ville': cells[4].get_text().strip(),
            'telephone': cells[5].get_text().strip(),
            'option': cells[6].get_text().strip(),
            'site_internet': cells[7].get_text().strip() if len(cells) > 7 else ''
        }
    
    def _find_next_page_link(self, soup):
        """Trouve le lien vers la page suivante"""
        # Chercher les liens de pagination
        pagination_links = soup.find_all('a', href=lambda href: href and '__doPostBack' in href and 'Page$' in href)
        
        if not pagination_links:
            return None
        
        # Trouver le numéro de page actuelle
        current_page = 1
        page_spans = soup.find_all('span')
        for span in page_spans:
            text = span.get_text().strip()
            if text.isdigit():
                # Vérifier si c'est la page courante (pas un lien)
                parent = span.parent
                if parent and parent.name != 'a':
                    current_page = int(text)
                    break
        
        # Chercher le lien vers la page suivante
        next_page = current_page + 1
        for link in pagination_links:
            href = link.get('href', '')
            if f'Page${next_page}' in href:
                return link
        
        return None
    
    def _navigate_to_next_page(self, current_soup, next_link):
        """Navigue vers la page suivante en simulant le postback ASP.NET"""
        href = next_link.get('href', '')
        
        # Extraire les paramètres du JavaScript __doPostBack
        if '__doPostBack' not in href:
            return None
        
        # Parser le JavaScript pour extraire les paramètres
        # Format: javascript:__doPostBack('target','argument')
        import re
        match = re.search(r"__doPostBack\('([^']+)','([^']+)'\)", href)
        if not match:
            return None
        
        event_target = match.group(1)
        event_argument = match.group(2)
        
        # Préparer les données du formulaire pour le postback
        form = current_soup.find('form', {'id': 'aspnetForm'})
        if not form:
            return None
        
        form_data = {}
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        for inp in hidden_inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value
        
        # Ajouter les paramètres du postback
        form_data['__EVENTTARGET'] = event_target
        form_data['__EVENTARGUMENT'] = event_argument
        
        # Effectuer la requête POST
        try:
            url = "https://www.utac-otc.com/vehicule_leger/Pages/Retrouver_un_CT.aspx"
            response = self.session.post(url, data=form_data, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        
        except requests.RequestException as e:
            print(f"Erreur lors de la navigation: {e}")
            return None
    
    def get_all_french_centers(self, output_dir="/tmp/utac_departments"):
        """
        Récupère tous les centres de contrôle technique de France
        Sauvegarde incrémentale par département pour éviter les pertes
        
        Args:
            output_dir (str): Répertoire pour les fichiers temporaires
            
        Returns:
            dict: Résultats complets avec statistiques
        """
        import os
        import json
        import time
        
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Liste complète des départements français
        departments = []
        
        # Départements métropolitains (01-95)
        for i in range(1, 96):
            departments.append(f"{i:02d}")
        
        # Départements d'outre-mer (971-989)
        for i in range(971, 990):
            departments.append(str(i))
        
        print(f"=== RÉCUPÉRATION DE TOUS LES CENTRES DE FRANCE ===")
        print(f"Départements à traiter: {len(departments)}")
        print(f"Estimation: ~6700 centres en ~8-10 minutes")
        print(f"Sauvegarde incrémentale dans: {output_dir}")
        
        all_centers = []
        department_stats = {}
        total_centers = 0
        errors = []
        start_time = time.time()
        
        for i, dept in enumerate(departments, 1):
            dept_start_time = time.time()
            print(f"\n[{i:3d}/{len(departments)}] Traitement département {dept}...")
            
            try:
                result = self.search_by_department(dept)
                
                if result and 'error' not in result:
                    centers = result.get('centers', [])
                    dept_total = len(centers)
                    total_centers += dept_total
                    
                    # Ajouter le code département à chaque centre
                    for center in centers:
                        center['department'] = dept
                    
                    all_centers.extend(centers)
                    
                    # Statistiques du département
                    dept_duration = time.time() - dept_start_time
                    department_stats[dept] = {
                        'centers_count': dept_total,
                        'duration_seconds': round(dept_duration, 2),
                        'status': 'success'
                    }
                    
                    # Sauvegarde incrémentale
                    dept_file = os.path.join(output_dir, f"dept_{dept}.json")
                    with open(dept_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'department_code': dept,
                            'total_centers': dept_total,
                            'centers': centers,
                            'timestamp': time.time()
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"    ✅ {dept_total} centres récupérés en {dept_duration:.1f}s")
                    
                else:
                    error_msg = result.get('error', 'Erreur inconnue') if result else 'Pas de résultat'
                    errors.append(f"Département {dept}: {error_msg}")
                    department_stats[dept] = {
                        'centers_count': 0,
                        'duration_seconds': round(time.time() - dept_start_time, 2),
                        'status': 'error',
                        'error': error_msg
                    }
                    print(f"    ❌ Erreur: {error_msg}")
                
            except Exception as e:
                error_msg = str(e)
                errors.append(f"Département {dept}: Exception - {error_msg}")
                department_stats[dept] = {
                    'centers_count': 0,
                    'duration_seconds': round(time.time() - dept_start_time, 2),
                    'status': 'exception',
                    'error': error_msg
                }
                print(f"    💥 Exception: {error_msg}")
            
            # Affichage du progrès
            elapsed = time.time() - start_time
            if i > 0:
                avg_time_per_dept = elapsed / i
                remaining_time = avg_time_per_dept * (len(departments) - i)
                print(f"    📊 Total: {total_centers} centres | Temps écoulé: {elapsed/60:.1f}min | Restant: {remaining_time/60:.1f}min")
        
        total_duration = time.time() - start_time
        
        # Sauvegarde du résultat final
        final_result = {
            'success': True,
            'timestamp': time.time(),
            'total_duration_seconds': round(total_duration, 2),
            'total_duration_minutes': round(total_duration / 60, 2),
            'summary': {
                'total_centers': total_centers,
                'total_departments': len(departments),
                'successful_departments': len([d for d in department_stats.values() if d['status'] == 'success']),
                'failed_departments': len([d for d in department_stats.values() if d['status'] != 'success']),
                'average_centers_per_department': round(total_centers / len(departments), 1) if departments else 0,
                'processing_rate_centers_per_second': round(total_centers / total_duration, 1) if total_duration > 0 else 0
            },
            'department_statistics': department_stats,
            'errors': errors,
            'data': {
                'total_centers': total_centers,
                'centers': all_centers
            }
        }
        
        # Sauvegarder le résultat complet
        final_file = os.path.join(output_dir, "all_french_centers.json")
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== RÉCUPÉRATION TERMINÉE ===")
        print(f"✅ {total_centers} centres récupérés")
        print(f"⏱️  Durée totale: {total_duration/60:.1f} minutes")
        print(f"📁 Fichier final: {final_file}")
        print(f"📂 Fichiers par département: {output_dir}/dept_*.json")
        
        if errors:
            print(f"⚠️  {len(errors)} erreurs rencontrées:")
            for error in errors[:5]:  # Afficher les 5 premières erreurs
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... et {len(errors)-5} autres erreurs")
        
        return final_result

def main():
    scraper = UTACScraper()
    
    # Test de recherche par numéro d'agrément
    print("=== Test de recherche par numéro d'agrément ===")
    
    # D'abord, analyser la structure du formulaire
    print("\n1. Analyse de la structure du formulaire:")
    result = scraper.scrape_ct_search_page()
    
    if result and result['forms']:
        form = result['forms'][0]
        print(f"Formulaire trouvé: {form['id']}")
        print("Champs disponibles:")
        for inp in form['inputs']:
            if inp['name'] and inp['type'] in ['text', 'select']:
                print(f"  - {inp['name']} ({inp['type']})")
    
    # Test avec un numéro d'agrément d'exemple (vous devrez fournir un vrai numéro)
    print("\n2. Pour tester la recherche, utilisez:")
    print("scraper.search_by_agreement_number('NUMERO_AGREMENT')")
    print("\nExemple d'utilisation:")
    print("python3 -c \"")
    print("from utac_scraper import UTACScraper")
    print("scraper = UTACScraper()")
    print("result = scraper.search_by_agreement_number('12345')")
    print("print(result)")
    print("\"")

def search_agreement(agreement_number):
    """Fonction utilitaire pour rechercher un numéro d'agrément"""
    scraper = UTACScraper()
    
    print(f"=== Recherche du numéro d'agrément: {agreement_number} ===")
    result = scraper.search_by_agreement_number(agreement_number)
    
    if result:
        if 'error' in result:
            print(f"Erreur: {result['error']}")
            if 'debug' in result:
                print("Mode debug activé")
        else:
            print("=== Informations trouvées ===")
            print(f"Numéro d'agrément: {result.get('agreement_number', 'N/A')}")
            print(f"Raison sociale: {result.get('raison_sociale', 'N/A')}")
            print(f"Enseigne: {result.get('enseigne', 'N/A')}")
            print(f"Adresse: {result.get('adresse', 'N/A')}")
            print(f"Ville: {result.get('ville', 'N/A')}")
            print(f"Téléphone: {result.get('telephone', 'N/A')}")
            print(f"Option: {result.get('option', 'N/A')}")
            print(f"Site internet: {result.get('site_internet', 'N/A')}")
            print(f"URL détail: {result.get('url', 'N/A')}")
    else:
        print("Aucun résultat trouvé")

if __name__ == "__main__":
    main()