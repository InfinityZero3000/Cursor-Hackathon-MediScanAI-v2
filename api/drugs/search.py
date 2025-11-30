from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from api.utils import get_drug_database

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            query = query_params.get('q', [''])[0]
            
            if not query:
                self.send_error(400, 'Query parameter required')
                return
            
            drug_db = get_drug_database()
            
            if drug_db is None or drug_db.empty:
                response = {'drugs': []}
            else:
                # Search
                query_lower = query.lower()
                results = drug_db[drug_db['DrugName'].str.lower().str.contains(query_lower, na=False)]
                
                # Limit results
                results = results.head(20)
                
                response = {
                    'drugs': results.to_dict('records')
                }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'error': 'Internal server error',
                'message': str(e)
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

