#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from utac_scraper import UTACScraper

app = Flask(__name__)
CORS(app)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instance globale du scraper
scraper = UTACScraper()

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil avec documentation de l'API"""
    return jsonify({
        'message': 'API UTAC-OTC - Recherche de centres de contrôle technique',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Documentation de l\'API',
            'GET /health': 'Vérification de l\'état de l\'API',
            'GET /agreement/<agreement_number>': 'Recherche par numéro d\'agrément',
            'POST /agreement': 'Recherche par numéro d\'agrément (JSON body)',
            'GET /department/<department_code>': 'Recherche tous les centres d\'un département',
            'POST /department': 'Recherche par département (JSON body)',
            'GET /all-centers': 'Récupère TOUS les centres de France (long processus)'
        },
        'example_usage': {
            'agreement_search': {
                'url': '/agreement/S044C203',
                'response_format': {
                    'success': True,
                    'data': {
                        'agreement_number': 'S044C203',
                        'raison_sociale': 'CONTROLE TECHNIQUE SAINT SEB',
                        'enseigne': 'AUTO SECURITE',
                        'adresse': '329 ROUTE DE CLISSON ZAC DES GRIPOTS',
                        'ville': 'ST SEBASTIEN SUR LOIRE',
                        'code_postal': '44230',
                        'telephone': '02 40 80 06 00',
                        'option': 'GAZ*',
                        'site_internet': '',
                        'url': 'Page de résultats'
                    }
                }
            },
            'department_search': {
                'url': '/department/04',
                'response_format': {
                    'success': True,
                    'data': {
                        'department_code': '04',
                        'total_centers': 25,
                        'centers': [
                            {
                                'raison_sociale': 'BA CONTROLE',
                                'agreement_number': 'S004S062',
                                'enseigne': 'BA CONTROLE',
                                'adresse': '3 AVENUE EMILE AUBERT',
                                'ville': 'BARCELONNETTE',
                                'code_postal': '04400',
                                'telephone': '04 92 81 15 89',
                                'option': '',
                                'site_internet': ''
                            }
                        ]
                    }
                }
            }
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'service': 'UTAC-OTC API',
        'version': '1.0.0'
    })

@app.route('/agreement/<string:agreement_number>', methods=['GET'])
def get_agreement_info_get(agreement_number):
    """
    Récupère les informations d'un centre de contrôle technique par numéro d'agrément (GET)
    
    Args:
        agreement_number (str): Le numéro d'agrément du centre
        
    Returns:
        JSON: Informations du centre ou erreur
    """
    return _process_agreement_request(agreement_number)

@app.route('/agreement', methods=['POST'])
def get_agreement_info_post():
    """
    Récupère les informations d'un centre de contrôle technique par numéro d'agrément (POST)
    
    Body JSON attendu:
        {
            "agreement_number": "S044C203"
        }
        
    Returns:
        JSON: Informations du centre ou erreur
    """
    try:
        data = request.get_json()
        if not data or 'agreement_number' not in data:
            return jsonify({
                'success': False,
                'error': 'Paramètre agreement_number requis dans le body JSON',
                'example': {'agreement_number': 'S044C203'}
            }), 400
        
        agreement_number = data['agreement_number']
        return _process_agreement_request(agreement_number)
        
    except Exception as e:
        logger.error(f"Erreur lors du parsing JSON: {e}")
        return jsonify({
            'success': False,
            'error': 'Format JSON invalide',
            'details': str(e)
        }), 400

@app.route('/department/<string:department_code>', methods=['GET'])
def get_department_centers_get(department_code):
    """
    Récupère tous les centres de contrôle technique d'un département (GET)
    
    Args:
        department_code (str): Le code du département (ex: "04", "75", "971")
        
    Returns:
        JSON: Liste des centres du département ou erreur
    """
    return _process_department_request(department_code)

@app.route('/department', methods=['POST'])
def get_department_centers_post():
    """
    Récupère tous les centres de contrôle technique d'un département (POST)
    
    Body JSON attendu:
        {
            "department_code": "04"
        }
        
    Returns:
        JSON: Liste des centres du département ou erreur
    """
    try:
        data = request.get_json()
        if not data or 'department_code' not in data:
            return jsonify({
                'success': False,
                'error': 'Paramètre department_code requis dans le body JSON',
                'example': {'department_code': '04'}
            }), 400
        
        department_code = data['department_code']
        return _process_department_request(department_code)
        
    except Exception as e:
        logger.error(f"Erreur lors du parsing JSON: {e}")
        return jsonify({
            'success': False,
            'error': 'Format JSON invalide',
            'details': str(e)
        }), 400

@app.route('/all-centers', methods=['GET'])
def get_all_french_centers():
    """
    Récupère TOUS les centres de contrôle technique de France
    
    ATTENTION: Cette opération prend 8-10 minutes et traite ~6700 centres
    
    Returns:
        JSON: Tous les centres de France avec statistiques complètes
    """
    try:
        logger.info("Début de la récupération de tous les centres de France")
        
        # Utiliser le scraper pour récupérer tous les centres
        result = scraper.get_all_french_centers()
        
        if not result or not result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la récupération des centres'
            }), 500
        
        # Réorganiser les données pour l'API
        api_response = {
            'success': True,
            'timestamp': result.get('timestamp'),
            'processing_time': {
                'total_seconds': result.get('total_duration_seconds'),
                'total_minutes': result.get('total_duration_minutes')
            },
            'summary': result.get('summary'),
            'data': {
                'total_centers': result['data']['total_centers'],
                'centers': result['data']['centers']
            },
            'department_statistics': result.get('department_statistics'),
            'errors': result.get('errors', [])
        }
        
        logger.info(f"Récupération terminée: {result['data']['total_centers']} centres en {result.get('total_duration_minutes', 0):.1f} minutes")
        
        return jsonify(api_response)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération complète: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur lors de la récupération complète',
            'details': str(e)
        }), 500

def _process_department_request(department_code):
    """
    Traite une requête de recherche par département
    
    Args:
        department_code (str): Le code du département
        
    Returns:
        JSON response
    """
    if not department_code or not department_code.strip():
        return jsonify({
            'success': False,
            'error': 'Code département vide ou invalide'
        }), 400
    
    try:
        logger.info(f"Recherche du département: {department_code}")
        
        # Utiliser le scraper pour récupérer les informations
        result = scraper.search_by_department(department_code.strip())
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Aucun résultat trouvé pour ce département',
                'department_code': department_code
            }), 404
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error'],
                'department_code': department_code
            }), 400
        
        # Vérifier que nous avons des centres
        if not result.get('centers') or len(result['centers']) == 0:
            return jsonify({
                'success': False,
                'error': 'Aucun centre trouvé pour ce département',
                'department_code': department_code
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'department_code': result.get('department_code', department_code),
                'total_centers': result.get('total_centers', 0),
                'centers': result.get('centers', [])
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': str(e)
        }), 500

def _process_agreement_request(agreement_number):
    """
    Traite une requête de recherche d'agrément
    
    Args:
        agreement_number (str): Le numéro d'agrément
        
    Returns:
        JSON response
    """
    if not agreement_number or not agreement_number.strip():
        return jsonify({
            'success': False,
            'error': 'Numéro d\'agrément vide ou invalide'
        }), 400
    
    try:
        logger.info(f"Recherche du numéro d'agrément: {agreement_number}")
        
        # Utiliser le scraper pour récupérer les informations
        result = scraper.search_by_agreement_number(agreement_number.strip())
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Aucun résultat trouvé pour ce numéro d\'agrément',
                'agreement_number': agreement_number
            }), 404
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error'],
                'agreement_number': agreement_number,
                'debug_info': result.get('debug_tables', [])
            }), 404
        
        # Vérifier que nous avons au moins une information utile
        required_fields = ['raison_sociale', 'enseigne', 'adresse', 'ville', 'telephone']
        if not any(result.get(field, '').strip() for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Aucune information détaillée trouvée pour ce numéro d\'agrément',
                'agreement_number': agreement_number
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'agreement_number': result.get('agreement_number', agreement_number),
                'raison_sociale': result.get('raison_sociale', ''),
                'enseigne': result.get('enseigne', ''),
                'adresse': result.get('adresse', ''),
                'ville': result.get('ville', ''),
                'code_postal': result.get('code_postal', ''),
                'telephone': result.get('telephone', ''),
                'option': result.get('option', ''),
                'site_internet': result.get('site_internet', ''),
                'url': result.get('url', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404"""
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé',
        'available_endpoints': [
            '/',
            '/health',
            '/agreement/<agreement_number>',
            '/agreement (POST)',
            '/department/<department_code>',
            '/department (POST)',
            '/all-centers'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500"""
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur'
    }), 500

if __name__ == '__main__':
    import os
    
    # Port dynamique pour Railway, Heroku, etc.
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Démarrage de l'API UTAC-OTC...")
    print(f"📖 Documentation disponible sur: http://localhost:{port}/")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print("🔍 Exemples:")
    print(f"   - Recherche par agrément: http://localhost:{port}/agreement/S044C203")
    print(f"   - Recherche par département: http://localhost:{port}/department/04")
    
    # En production, utiliser Gunicorn au lieu du serveur de dev Flask
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)