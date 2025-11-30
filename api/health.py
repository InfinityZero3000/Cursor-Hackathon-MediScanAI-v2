from http.server import BaseHTTPRequestHandler
import json
from api.utils import get_drug_database

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        drug_db = get_drug_database()
        
        response = {
            'status': 'ok',
            'message': 'Backend API is running',
            'drugs_loaded': len(drug_db) if drug_db is not None and not drug_db.empty else 0
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

