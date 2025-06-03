from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class HeaderDisplayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send a successful HTTP response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Capture and display all headers
        headers = {key: value for key, value in self.headers.items()}
        
        # Response body with captured headers
        response = {
            'message': 'Headers captured successfully',
            'headers': headers  # Add the captured headers here
        }

        # Send the response to the client
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    print("Starting server on http://localhost:8080")
    server_address = ('', 8080)  # Use port 8080 (or another available port)
    httpd = HTTPServer(server_address, HeaderDisplayHandler)
    httpd.serve_forever()
