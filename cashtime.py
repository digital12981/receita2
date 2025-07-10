import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CashtimeAPI:
    """
    API wrapper for Cashtime PIX payment integration
    """
    API_URL = "https://api.cashtime.com.br/v1"
    
    def __init__(self, secret_key: str, public_key: Optional[str] = None):
        self.secret_key = secret_key
        self.public_key = public_key
    
    def _get_headers(self) -> Dict[str, str]:
        """Create authentication headers for Cashtime API"""
        headers = {
            'Content-Type': 'application/json',
            'x-authorization-key': self.secret_key,
        }
        
        if self.public_key:
            headers['x-store-key'] = self.public_key
        
        return headers
    
    def _generate_txid(self) -> str:
        """Generate unique transaction ID"""
        return f"CASHTIME{int(datetime.now().timestamp())}{os.urandom(4).hex().upper()}"
    
    def create_pix_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a PIX payment request using Cashtime API"""
        try:
            logger.info("Iniciando criação de PIX via Cashtime...")
            
            # Validar dados obrigatórios
            required_fields = ['amount', 'description']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Campo obrigatório ausente: {field}")
            
            # Gerar transaction ID único
            txid = self._generate_txid()
            expiration_minutes = data.get('expirationMinutes', 60)
            expires_at = datetime.now() + timedelta(minutes=expiration_minutes)
            
            # Converter valor para centavos
            amount_cents = int(float(data['amount']) * 100)
            
            # Preparar payload para Cashtime
            cashtime_payload = {
                "paymentMethod": "pix",
                "customer": {
                    "name": data.get('name', 'Cliente'),
                    "email": data.get('email', 'cliente@dominio.com.br'),
                    "phone": data.get('phone', '11999999999'),
                    "document": {
                        "number": data.get('cpf', '').replace('.', '').replace('-', ''),
                        "type": "cpf"
                    }
                },
                "items": [
                    {
                        "title": "Regularização de Débitos",
                        "description": data['description'],
                        "unitPrice": amount_cents,
                        "quantity": 1,
                        "tangible": False  # Produto digital
                    }
                ],
                "isInfoProducts": True,  # Produto digital - sem necessidade de endereço
                "installments": 1,
                "installmentFee": 0,
                "postbackUrl": "https://webhook.site/unique-uuid-4-testing",
                "ip": "127.0.0.1",
                "amount": amount_cents
            }
            
            logger.info(f"Payload Cashtime: {json.dumps(cashtime_payload, indent=2)}")
            
            # Fazer requisição para API
            headers = self._get_headers()
            response = requests.post(
                f"{self.API_URL}/transactions",
                headers=headers,
                json=cashtime_payload,
                timeout=30
            )
            
            logger.info(f"Status da resposta Cashtime: {response.status_code}")
            
            if not response.ok:
                error_text = response.text
                logger.error(f"Erro na API Cashtime: {error_text}")
                
                if response.status_code == 403:
                    raise Exception("Erro de autenticação. Verifique sua secret key da Cashtime")
                elif response.status_code == 400:
                    raise Exception("Dados inválidos enviados para a API")
                else:
                    raise Exception(f"Erro na API Cashtime: {response.status_code}")
            
            cashtime_result = response.json()
            logger.info(f"Resposta Cashtime: {json.dumps(cashtime_result, indent=2)}")
            
            # Extrair dados do PIX
            pix_data = cashtime_result.get('pix', {})
            pix_code = pix_data.get('payload', '')
            qr_code_image = pix_data.get('encodedImage', '')
            
            # Formatar resposta padronizada
            result = {
                'success': True,
                'txid': txid,
                'cashtime_id': cashtime_result.get('id', ''),
                'amount': data['amount'],
                'currency': 'BRL',
                'description': data['description'],
                'status': cashtime_result.get('status', 'pending'),
                'pix_code': pix_code,
                'qr_code_image': qr_code_image,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now().isoformat(),
                'payer': {
                    'name': data.get('name'),
                    'cpf': data.get('cpf'),
                    'email': data.get('email'),
                },
                'cashtime_response': cashtime_result
            }
            
            logger.info("PIX criado com sucesso via Cashtime!")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com Cashtime: {str(e)}")
            raise Exception(f"Erro de conexão com a API: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao criar PIX: {str(e)}")
            raise Exception(f"Erro ao processar pagamento: {str(e)}")
    
    def check_payment_status(self, txid: str) -> Dict[str, Any]:
        """Check payment status by transaction ID"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.API_URL}/transactions/{txid}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 404:
                return {'success': False, 'error': 'Transação não encontrada'}
            
            if not response.ok:
                return {'success': False, 'error': f'Erro na API: {response.status_code}'}
            
            result = response.json()
            orders = result.get('orders', {})
            
            return {
                'success': True,
                'txid': txid,
                'status': orders.get('status', 'unknown'),
                'amount': orders.get('total', 0) / 100 if orders.get('total') else 0,
                'payment_method': orders.get('paymentMethod'),
                'created_at': orders.get('createdAt'),
                'updated_at': orders.get('updatedAt'),
                'cashtime_response': result
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return {'success': False, 'error': str(e)}


def create_cashtime_api(secret_key: Optional[str] = None, public_key: Optional[str] = None) -> CashtimeAPI:
    """Factory function to create CashtimeAPI instance"""
    if not secret_key:
        secret_key = os.environ.get('CASHTIME_SECRET_KEY')
        if not secret_key:
            raise ValueError("CASHTIME_SECRET_KEY não encontrada nas variáveis de ambiente")
    
    if not public_key:
        public_key = os.environ.get('CASHTIME_PUBLIC_KEY')
    
    return CashtimeAPI(secret_key=secret_key, public_key=public_key)