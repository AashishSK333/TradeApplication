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
    service='portfolio-service',
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
            segment = xray_recorder.begin_segment('portfolio-service', trace_id=trace_id)
        else:
            # Create a new segment
            segment = xray_recorder.begin_segment('portfolio-service')
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
@app.route('/portfolio/<int:trader_id>', methods=['GET'])
def get_portfolio(trader_id):
    try:
        logger.info(f"Portfolio requested for trader_id: {trader_id}")
        
        # Get current segment for debugging
        segment = xray_recorder.current_segment()
        if segment:
            logger.info(f"Current segment ID: {segment.id}, trace ID: {segment.trace_id}")
        
        # Query all trades for this trader from the database
        trades = Trade.query.filter_by(trader_id=trader_id).all()
        logger.info(f"Found {len(trades)} trades")
        
        # Process trades to calculate portfolio positions
        positions = {}
        total_value = 0.0
        
        for trade in trades:
            symbol = trade.asset_name
            
            if symbol not in positions:
                positions[symbol] = {
                    "symbol": symbol,
                    "quantity": 0,
                    "total_cost": 0.0
                }
            
            # Update position with this trade
            positions[symbol]["quantity"] += trade.quantity
            positions[symbol]["total_cost"] += trade.quantity * trade.price
            
            # Update total portfolio value
            total_value += trade.quantity * trade.price
        
        # Calculate average price for each position
        position_list = []
        
        for symbol, position in positions.items():
            position["average_price"] = position["total_cost"] / position["quantity"]
            del position["total_cost"]
            position_list.append(position)
        
        logger.info(f"Calculated positions: {position_list}")
        logger.info(f"Total value: {total_value}")
        
        # Return portfolio data
        return jsonify({
            "trader_id": trader_id,
            "positions": position_list,
            "total_value": total_value
        })
        
    except Exception as e:
        logger.error(f"Error calculating portfolio: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)