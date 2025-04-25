from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pandas as pd
import asyncio
import uuid
import logging
from scraper.revenueScraper import get_company_revenue_from_growjo
from scraper.websiteNameScraper import find_company_website
from scraper.apollo_scraper import enrich_single_company
from scraper.linkedinScraper.scraping.scraper import scrape_linkedin
from scraper.linkedinScraper.scraping.login import login_to_linkedin
from scraper.linkedinScraper.utils.chromeUtils import get_chrome_driver
from scraper.linkedinScraper.main import run_batches
from scraper.growjoScraper import GrowjoScraper
from security import generate_token, token_required, VALID_USERS


app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Load environment variables
load_dotenv()

# Ensure upload directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Ensure required directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('log', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    logger.info(f"Incoming request headers: {request.headers}")
    logger.info(f"Request origin: {request.headers.get('Origin')}")
    if request.method == 'OPTIONS':
        response = jsonify({"message": "Preflight check passed"})
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    try:
        data = request.get_json()
        if not data:
            logger.error("Missing request body")
            return jsonify({"error": "Missing request body"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            logger.error("Missing email or password")
            return jsonify({"error": "Missing credentials"}), 400

        if VALID_USERS.get(email) != password:
            logger.warning(f"Invalid login attempt for email: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_token(email)
        response = jsonify({
            "message": "Login successful",
            "token": token,
            "email": email
        })
        response.set_cookie('token', token, httponly=True, secure=True, samesite='None')
        return response, 200
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login"}), 500

# Protected Test Endpoint
@app.route('/api/protected-test', methods=['GET'])
@token_required
def protected_test():
    return jsonify({"message": "This is a protected route"}), 200

@app.route("/api/find-website", methods=["GET"])
@token_required
def get_website():
    company = request.args.get("company")
    if not company:
        return jsonify({"error": "Missing company parameter"}), 400

    website = find_company_website(company)
    print(website)
    if website:
        return jsonify({"company": company, "website": website})
    else:
        return jsonify({"error": "Website not found"}), 404

@app.route("/api/get-revenue", methods=["GET"])
@token_required
def get_revenue():
    company = request.args.get("company")
    if not company:
        return jsonify({"error": "Missing company parameter"}), 400

    data = get_company_revenue_from_growjo(company)
    return jsonify(data)

@app.route("/api/apollo-info", methods=["POST"])
@token_required
def get_apollo_info_batch():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        if isinstance(data, dict):
            data = [data]

        results = []
        for company in data:
            domain = company.get("domain")
            if domain:
                enriched = enrich_single_company(domain)
                results.append(enriched)
            else:
                results.append({"error": "Missing domain"})

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/linkedin-info-batch", methods=["POST"])
@token_required
def get_linkedin_info_batch():
    try:
        load_dotenv()
        data_list = request.get_json()

        if not isinstance(data_list, list):
            return jsonify({"error": "Expected a list of objects"}), 400

        # Convert and normalize DataFrame
        df = pd.DataFrame(data_list)
        df.rename(columns=lambda col: col.capitalize(), inplace=True)

        if df.empty or "Company" not in df.columns:
            return jsonify({"error": "Missing or empty 'Company' column"}), 400

        client_id = f"api_{uuid.uuid4().hex[:8]}"
        results = run_batches(df, client_id=client_id)

        return jsonify(results), 200

    except Exception as e:
        logging.error(f":fire: API Fatal error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/growjo", methods=["POST"])
def scrape():
    data = request.get_json()
    if not data or "company" not in data:
        return jsonify({"error": "Missing 'company' in request JSON"}), 400

    company = data["company"]
    headless = data.get("headless", True)

    scraper = GrowjoScraper(headless=headless)
    try:
        results = scraper.scrape_company(company)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        scraper.close()

@app.after_request
def after_request(response):
    # Don't modify CORS headers for static files
    if not request.path.startswith('/static/'):
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:3000':
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Vary'] = 'Origin'
    return response

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
@token_required
def upload_file():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        # Log request details
        logger.info(f'Received file upload request. Headers: {dict(request.headers)}')
        
        if 'file' not in request.files:
            logger.error('No file part in request')
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400
            
        if not file.filename.endswith('.csv'):
            logger.error('Invalid file type')
            return jsonify({'error': 'Only CSV files are allowed'}), 400

        # Save the file
        filename = str(uuid.uuid4()) + '.csv'
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Read and process the CSV file
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                os.remove(filepath)
                return jsonify({'error': 'The uploaded file is empty'}), 400

            # Normalize column names
            df.columns = df.columns.str.strip().str.title()
            if 'Company' not in df.columns and 'Company Name' in df.columns:
                df = df.rename(columns={'Company Name': 'Company'})

            required_columns = ['Company']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                os.remove(filepath)
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }), 400

            # Process the data with enrichment
            results = []
            total_rows = len(df)
            
            for index, row in df.iterrows():
                company_name = str(row['Company']).strip()
                if not company_name:
                    continue

                company_data = {'company': company_name}
                logger.info(f'Processing {company_name} ({index + 1}/{total_rows})')
                
                try:
                    # Find company website
                    website = find_company_website(company_name)
                    if website:
                        company_data['website'] = website
                        logger.info(f'Found website for {company_name}: {website}')
                        
                        # Get revenue data from Growjo
                        revenue_data = get_company_revenue_from_growjo(company_name)
                        if 'error' not in revenue_data:
                            company_data.update(revenue_data)
                            logger.info(f'Found revenue data for {company_name}')
                        
                        # Get Apollo data
                        apollo_data = enrich_single_company(website)
                        if apollo_data and 'error' not in apollo_data:
                            company_data.update(apollo_data)
                            logger.info(f'Found Apollo data for {company_name}')
                    else:
                        company_data['error'] = 'Could not find company website'
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f'Error enriching {company_name}: {error_msg}')
                    company_data['error'] = error_msg
                
                results.append(company_data)

            if not results:
                os.remove(filepath)
                return jsonify({'error': 'No valid data could be processed'}), 400

            # Save processed results
            output_filename = f'processed_{filename}'
            output_path = os.path.join('output', output_filename)
            
            # Convert results to DataFrame and save
            result_df = pd.DataFrame(results)
            result_df.to_csv(output_path, index=False)

            # Clean up the original file
            os.remove(filepath)

            return jsonify({
                'message': 'File processed successfully',
                'filename': output_filename,
                'total_processed': len(results),
                'results': results
            })

        except pd.errors.EmptyDataError:
            os.remove(filepath)
            return jsonify({'error': 'The uploaded file is empty'}), 400
        except Exception as e:
            error_msg = str(e)
            logger.error(f'Error processing file: {error_msg}')
            os.remove(filepath)
            return jsonify({'error': f'Error processing file: {error_msg}'}), 500

    except Exception as e:
        error_msg = str(e)
        logger.error(f'Upload error: {error_msg}')
        return jsonify({'error': f'Upload error: {error_msg}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
