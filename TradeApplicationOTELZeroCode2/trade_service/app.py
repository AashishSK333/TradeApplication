import os
import logging
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_cors import CORS
from models import db, Trade
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure X-Ray
xray_recorder.configure(
    service='trade-service',
    daemon_address='xray-daemon:2000',
    sampling=False,  # Don't sample - trace everything
    context_missing='LOG_ERROR'
)
patch_all()

# Custom X-Ray middleware with trace ID extraction
class TraceAwareXRayMiddleware(XRayMiddleware):
    def __call__(self, environ, start_response):
        # Get trace id from incoming request
        trace_header = environ.get('HTTP_X_AMZN_TRACE_ID', '')
        
        if trace_header and 'Root=' in trace_header:
            # Extract trace ID from header format "Root=1-abcdef-12345"
            trace_id = trace_header.split('Root=')[1].strip()
            logger.info(f"Using trace ID from header: {trace_id}")
            
            # Create a segment with the extracted trace ID
            segment = xray_recorder.begin_segment('trade-service', trace_id=trace_id)
        else:
            # Create a new segment
            segment = xray_recorder.begin_segment('trade-service')
            logger.info(f"Created new segment: {segment.trace_id}")
        
        def wrapped_start_response(status, headers, exc_info=None):
            return start_response(status, headers, exc_info)
        
        try:
            return self.app(environ, wrapped_start_response)
        finally:
            xray_recorder.end_segment()

# Apply custom middleware
TraceAwareXRayMiddleware(app, xray_recorder)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/trades'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
api = Api(app)
CORS(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

# Routes
@app.route('/trades', methods=['POST'])
def create_trade():
    try:
        trade_data = request.json
        logger.info(f"Processing trade: {trade_data}")
        
        # Create trade
        new_trade = Trade(
            asset_name=trade_data['asset_name'],
            quantity=float(trade_data['quantity']),
            price=float(trade_data['price']),
            trade_time=trade_data['trade_time'],
            trader_id=int(trade_data['trader_id'])
        )
        
        db.session.add(new_trade)
        db.session.commit()
        
        logger.info(f"Trade created successfully: {new_trade.id}")
        
        return jsonify({
            "id": new_trade.id,
            "message": "Trade created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating trade: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)