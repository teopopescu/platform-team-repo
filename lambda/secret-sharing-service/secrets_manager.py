import logging

from pgp import secret_manager, env, product_name, decrypt_secret
from typing import Optional


def upsert_partner_public_key(partner_id: str, public_key: str) -> None:
    partner_public_key_secret_name = f"merc-{env}-{product_name}-module-secretsharing-partner-{partner_id}-public-key"

    try:
        secret_manager.get_secret_value(SecretId=partner_public_key_secret_name)
    except secret_manager.exceptions.ResourceNotFoundException:
        secret_manager.create_secret(
            Name=partner_public_key_secret_name,
            SecretString=public_key,
            Description=f"PGP Public Key from partner: {partner_id} for product: {product_name}",
            Tags=[{"Key": "env", "Value": env}, {"Key": "product_name", "Value": product_name}, {"Key": "partner_id", "Value": partner_id}],
        )
    else:
        secret_manager.put_secret_value(
            SecretId=partner_public_key_secret_name,
            SecretString=public_key,
        )

def upsert_secret(partner_id: str, secret_name: str, encrypted_secret: str) -> bool:
    """
    Upsert a secret into AWS Secrets Manager.

    Args:
        partner_id: The ID of the partner.
        secret_name: The name of the secret.
        encrypted_secret: The encrypted secret.
    
    Returns:
        A boolean indicating whether the secret was successfully upserted.
    """
    secret_name = f"merc-{env}-{product_name}-module-secretsharing-partner-{partner_id}-secret-{secret_name}"

    # decrypt the secret
    
    # TODO: Testing code, remove
    print("\n\n ENCRYPTED SECRET")
    print(encrypted_secret)
    
    decrypted_secret = decrypt_secret(encrypted_secret)
    if not decrypted_secret:
        logging.error(f"Failed to decrypt secret for partner: {partner_id}")
        return False

    try:
        secret_manager.get_secret_value(SecretId=secret_name)
    except secret_manager.exceptions.ResourceNotFoundException:
        secret_manager.create_secret(
            Name=secret_name,
            SecretString=decrypted_secret,
            Description=f"Secret for product: {product_name} from partner: {partner_id}",
            Tags=[
                {"Key": "env", "Value": env},
                {"Key": "product_name", "Value": product_name},
                {"Key": "partner_id", "Value": partner_id},
            ],
        )
    else:
        secret_manager.put_secret_value(
            SecretId=secret_name,
            SecretString=decrypted_secret,
        )

    return True


def get_partner_public_key(partner_id: str) -> Optional[str]:
    """
    Get a partner's public key by partner_id.
    
    Args:
        partner_id: The ID of the partner
        
    Returns:
        The partner's public key or None if not found
    """
    secret_name = f"merc-{env}-{product_name}-module-secretsharing-partner-{partner_id}-public-key"
    
    try:
        response = secret_manager.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except secret_manager.exceptions.ResourceNotFoundException:
        return None


def get_secret(partner_id: str, secret_name: str) -> Optional[str]:
    """Retrieve a secret from AWS Secrets Manager."""
    try:
        response = secret_manager.get_secret_value(SecretId=secret_name)
        return response.get('SecretString')
    except secret_manager.exceptions.ResourceNotFoundException:
        return None
    except Exception as e:
        logging.error(f"Error getting secret: {str(e)}")
        raise