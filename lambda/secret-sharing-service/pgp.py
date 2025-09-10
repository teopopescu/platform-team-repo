import logging
import os
from datetime import timedelta
from typing import Optional, Tuple

import boto3

# import gnupg
import pgpy
from pgpy.constants import (
    PubKeyAlgorithm,
    KeyFlags,
    HashAlgorithm,
    SymmetricKeyAlgorithm,
    CompressionAlgorithm,
)

secret_manager = boto3.client("secretsmanager")
kms = boto3.client("kms")


product_name = os.getenv("PRODUCT_NAME")
if not product_name:
    raise ValueError("Environment variable 'PRODUCT_NAME' is not set")
product_name = product_name.lower().replace("_", "")

env = os.getenv("ENV")
if not env:
    raise ValueError("Environment variable 'ENV' is not set")

contact_email = os.getenv("CONTACT_EMAIL")
if not contact_email:
    raise ValueError("Environment variable 'CONTACT_EMAIL' is not set")

contact_name = os.getenv("CONTACT_NAME")
if not contact_name:
    raise ValueError("Environment variable 'CONTACT_NAME' is not set")

public_key_secret_name = (
    f"M2_PLATFORM_PUBLIC_KEY"
)
private_key_secret_name = (
    f"M2_PLATFORM_PRIVATE_KEY"
)

def decrypt_secret(encrypted_secret: str) -> Optional[str]:
    logging.info(f"Decrypting secret...")
    private_key = get_private_key()
    
    key, _ = pgpy.PGPKey.from_blob(private_key)
    if key is None:
        logging.error(f"Failed to parse private key.")
        return None

    # Decrypt the secret using the private key
    try:
        message_from_blob = pgpy.PGPMessage.from_blob(encrypted_secret)
        decrypted_secret = key.decrypt(message_from_blob).message
        return decrypted_secret.decode("utf-8")
    except Exception as e:
        logging.error(f"Error decrypting secret: {e}")
        return None

def _get_key(secret: str) -> Optional[str]:
    logging.info(f"Trying to retrieve secret: {secret}")
    try:
        secret = secret_manager.get_secret_value(SecretId=secret)
        if "SecretString" in secret:
            secret_string = secret["SecretString"]
        else:
            secret_string = secret["SecretBinary"].decode("utf-8")
        # Assuming the secret string contains the PGP public key
        return secret_string
    except Exception as e:
        logging.error(f"Error retrieving key: {secret} -> {e}")
        return None


def get_public_key() -> Optional[str]:
    return _get_key(public_key_secret_name)


def get_private_key() -> Optional[str]:
    return _get_key(private_key_secret_name)


def encrypt_with_public_key(public_key_str: str, data: str) -> str:
    """Encrypt data using a PGP public key.
    
    Args:
        public_key_str: The PGP public key in string format
        data: The data to encrypt
        
    Returns:
        The encrypted data as an ASCII-armored string
    """
    try:
        # Load the public key
        key = pgpy.PGPKey()
        key.parse(public_key_str)
        
        # Create a message and encrypt it
        message = pgpy.PGPMessage.new(data)
        encrypted_message = key.pubkey.encrypt(message)
        
        return str(encrypted_message)
    except Exception as e:
        logging.error(f"Error encrypting with public key: {e}")
        raise


def generate_pgp_key(passphrase: str = "password") -> Tuple[str, str]:
    logging.info("generating new key...")
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    uid = pgpy.PGPUID.new(
        contact_name, comment=f"PGP Key for British Airways Mercury Platform, product: {product_name}", email=contact_email
    )
    key.add_uid(
        uid,
        usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
        hashes=[
            HashAlgorithm.SHA256,
            HashAlgorithm.SHA384,
            HashAlgorithm.SHA512,
            HashAlgorithm.SHA224,
        ],
        ciphers=[
            SymmetricKeyAlgorithm.AES256,
            SymmetricKeyAlgorithm.AES192,
            SymmetricKeyAlgorithm.AES128,
        ],
        compression=[
            CompressionAlgorithm.ZLIB,
            CompressionAlgorithm.BZ2,
            CompressionAlgorithm.ZIP,
            CompressionAlgorithm.Uncompressed,
        ],
        key_expiration=timedelta(days=90),
    )

    ascii_armored_public_keys = str(key.pubkey)
    ascii_armored_private_keys = str(key)

    tags = [
        {"Key": "env", "Value": env},
        {"Key": "product_name", "Value": product_name},
    ]
    
    # Store the public key in AWS Secrets Manager
    secret_manager.create_secret(
        Name=public_key_secret_name,
        SecretString=ascii_armored_public_keys,
        Description=f"PGP Public Key for product: {product_name}",
        Tags=tags,
    )

    # Store the private key in AWS Secrets Manager
    secret_manager.create_secret(
        Name=private_key_secret_name,
        SecretString=ascii_armored_private_keys,
        Description=f"PGP Private Key for product: {product_name}",
        Tags=tags,
    )

    logging.error(f"keys generated and stored in AWS Secrets Manager")

    return ascii_armored_public_keys, ascii_armored_private_keys


if __name__ == "__main__":
    # public_key = get_public_key()
    # if public_key is None:
    # print("Public key not found, generating a new one...")
    public_key, private_key = generate_pgp_key()
    # else:
    # print("Public key retrieved successfully.")
    # print(public_key)
