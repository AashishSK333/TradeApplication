# Create project workspace
mkdir -p zero-trust-aws-poc/{frontend/{js,css},backend,terraform}
cd zero-trust-aws-poc

# Set up Python virtual environment for backend development
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install boto3 pyjwt cryptography