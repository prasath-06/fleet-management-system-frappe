import frappe
from frappe.model.document import Document
import requests
import base64
import json
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class BankAccountIntegration(Document):
    pass

def decrypt_response(enc_message, private_key_path):
    with open(private_key_path, "r") as key_file:
        private_key_pem = key_file.read()
    payload = json.loads(base64.b64decode(enc_message).decode())
    enc_key = base64.b64decode(payload["key"])
    iv = base64.b64decode(payload["iv"])
    ciphertext = base64.b64decode(payload["data"])

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None, backend=default_backend()
    )

    aes_key = private_key.decrypt(
        enc_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    message = json.loads(data.decode())
    return message

@frappe.whitelist()
def account_integration(account_name, phone, address, email, account_type, public_key="/home/prasath/public_key.pem", private_key_path="/home/prasath/private_key.pem"):
    with open(public_key, "r") as key_file:
        public_key = key_file.read()
    url = "http://192.168.1.38:8000/api/method/bank_service.api.create_bank_account"
    data = {
        "account_name": account_name,
        "phone": phone,
        "address": address,
        "email": email,
        "account_type": account_type,
        "client_public_key_file": public_key
    }
    res = requests.post(url, json=data)

    if res.status_code == 200:
        enc_message = res.json().get("message", "")
        print("Raw Encrypted Response:", enc_message)
        enc_data = enc_message.get("encrypted_response") if isinstance(enc_message, dict) else None

        if enc_data:           
            response_data = decrypt_response(enc_data, private_key_path)
            print("Decrypted Response Data:", response_data)
            doc = frappe.new_doc("Bank Account Integration")
            doc.account_name = response_data.get("account_name")
            doc.account_number = response_data.get("account_number")
            doc.account_type = response_data.get("account_type")
            doc.public_key = response_data.get("bank_public_key")
            doc.insert()
            print(response_data)

            bank_credentials = response_data.get("bank_name")
            if bank_credentials:
                bank_name = bank_credentials.split("-")[-1].strip()
                if not frappe.db.exists("Bank", bank_name):
                    bank_doc = frappe.new_doc("Bank")
                    bank_doc.bank_name = bank_name
                    bank_doc.insert()

                bank_account_doc = frappe.new_doc("Bank Account")
                bank_account_doc.bank = bank_name
                bank_account_doc.account_name = response_data.get("account_name")
                bank_account_doc.bank_account_no = response_data.get("account_number")
                bank_account_doc.account_type = response_data.get("account_type")
                bank_account_doc.is_company_account = 1
                # bank_account_doc.company = frappe.db.get_value("Company", {"company_name": response_data.get("company_name")})
                bank_account_doc.company = frappe.db.get_value("Company", {}, "name", order_by="creation desc")
                bank_account_doc.insert()

                doc=frappe.new_doc("Account")
                doc.account_name = account_name
                doc.account_number = response_data.get("account_number")
                company_doc = frappe.db.get_value("Company", {}, "name", order_by="creation desc")
                doc.company = company_doc.name           
                doc.parent_account = "Bank Accounts - " + company_doc.com
            
            return {
                "message": "Details sent to bank successfully!",
            }
        else:
            return {"message": "No encrypted data found in response."}
        
    else:
        return {"message": f"Failed: {res.status_code} {res.text}"}

