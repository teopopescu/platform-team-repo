import json
import os
import re
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import AWS Secrets Manager client
import boto3
secret_manager = boto3.client('secretsmanager')

from pgp import generate_pgp_key, get_public_key, encrypt_with_public_key
from secrets_manager import upsert_partner_public_key, upsert_secret, get_secret

tmp = os.getenv("ACCEPTED_PARTNER_IDS")
if not tmp:
    raise ValueError("Environment variable 'ACCEPTED_PARTNER_IDS' is not set")
ACCEPTED_PARTNER_IDS = json.loads(tmp)


def reply_with_json(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
        "isBase64Encoded": False,
    }


def handle_get_pgp_key() -> Dict[str, Any]:
    public_key = get_public_key()
    if public_key is None:
        generate_pgp_key()
        public_key = get_public_key()

    return {
        "statusCode": 200,
        "body": public_key,
        "isBase64Encoded": False,
    }


def import_partner(event: Dict[str, Any]) -> Dict[str, Any]:
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method != "POST":
        return reply_with_json(405, {"message": "Only POST is allowed"})

    data = {}
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return reply_with_json(400, {"message": "Invalid JSON body"})

    required = {"partner_id", "public_key"}
    missing = sorted(required - set(data))
    if missing:
        return reply_with_json(400, {"message": f"Missing fields: {missing}"})

    valid_partner_ids = [partner["id"] for partner in ACCEPTED_PARTNER_IDS]
    if data["partner_id"] not in valid_partner_ids:
        return reply_with_json(403, {"message": "Unauthorized partner_id"})

    upsert_partner_public_key(data["partner_id"], data["public_key"])

    return reply_with_json(
        202, {"message": "partner public key processed successfully"}
    )


def import_secret(event: Dict[str, Any]) -> Dict[str, Any]:
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method != "POST":
        return reply_with_json(405, {"message": "Only POST is allowed"})

    data = {}
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return reply_with_json(400, {"message": "Invalid JSON body"})

    required = {"partner_id", "secret_name", "secret"}
    missing = sorted(required - set(data))
    if missing:
        return reply_with_json(400, {"message": f"Missing fields: {missing}"})

    valid_partner_ids = [partner["id"] for partner in ACCEPTED_PARTNER_IDS]
    if data["partner_id"] not in valid_partner_ids:
        return reply_with_json(403, {"message": "Unauthorized partner_id"})

    secret_name = data["secret_name"].replace("_", "")
    if not re.match("^[a-zA-Z0-9-]+$", secret_name):
        return reply_with_json(400, {"message": "Invalid secret format"})

    # If all checks pass, process the secret
    ret = upsert_secret(data["partner_id"], secret_name, data["secret"])

    if ret:
        return reply_with_json(202, {"message": "secret processed successfully"})
    return reply_with_json(500, {"message": "Failed to process secret"})

def export_secret(event: Dict[str, Any]) -> Dict[str, Any]:
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method != "GET":
        return reply_with_json(405, {"message": "Only GET is allowed"})

    # Extract query parameters
    query_params = json.loads(event.get("body") or "{}")
    partner_id = query_params.get("partner_id")
    secret_name = query_params.get("secret_name")

    if not partner_id or not secret_name:
        return reply_with_json(400, {
            "message": "Missing required query parameters: partner_id and secret_name"
        })

    # Validate partner and get their public key
    partner = next((p for p in ACCEPTED_PARTNER_IDS if p["id"] == partner_id), None)
    if not partner:
        return reply_with_json(403, {"message": "Unauthorized partner_id"})
    
    if not partner.get("public_key"):
        return reply_with_json(403, {
            "message": f"Unauthorized partner: No public key found for partner {partner_id}"
        })

    try:
        # Get the secret from AWS Secrets Manager
        secret_value = get_secret(partner_id, secret_name)
        if not secret_value:
            return reply_with_json(404, {"message": "Secret not found"})

        # Encrypt the secret with partner's public key
        encrypted_secret = encrypt_secret(secret_value, partner["public_key"])
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/pgp-encrypted"},
            "body": encrypted_secret,
            "isBase64Encoded": False,
        }

    except Exception as e:
        logging.error(f"Error exporting secret: {str(e)}")
        return reply_with_json(500, {"message": "Failed to export secret"})

def encrypt_secret(secret: str, public_key: str) -> str:
    """Encrypt a secret using a PGP public key."""
    try:
        return encrypt_with_public_key(public_key, secret)
    except Exception as e:
        logging.error(f"Error encrypting secret: {str(e)}")
        raise

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    route = event.get("rawPath")  # HTTP API v2
    if route == "/.well-known/pgp-key":
        return handle_get_pgp_key()

    if route == "/partners/import":
        return import_partner(event)
    
    # if route == "/partners/export/mTLS":
    #     return export_partner_mtls(event)
        
    if route == "/secrets/export":
        return export_secret(event)

    if route == "/secrets/import":
        return import_secret(event)

    return reply_with_json(404, {"message": "Not Found"})
