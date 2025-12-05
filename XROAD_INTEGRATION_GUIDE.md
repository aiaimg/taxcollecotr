# X-Road Integration Guide
## Tax Collection Platform - Data Exchange Through X-Road

**Version:** 1.0  
**Date:** January 2025  
**Status:** Implementation Guide

---

## Table of Contents

1. [Overview](#overview)
2. [What is X-Road?](#what-is-x-road)
3. [Why X-Road for This Project?](#why-x-road-for-this-project)
4. [X-Road Architecture](#x-road-architecture)
5. [Prerequisites](#prerequisites)
6. [Infrastructure Requirements](#infrastructure-requirements)
7. [Implementation Steps](#implementation-steps)
8. [Code Integration](#code-integration)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [Security Considerations](#security-considerations)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This document outlines the steps required to integrate X-Road data exchange layer into the Tax Collection Platform. X-Road will enable secure, standardized communication with government services such as:

- **National ID Verification Service** - Verify citizen identity cards
- **Vehicle Registry Service** - Verify vehicle registration and ownership
- **Payment Gateway Services** - Potentially integrate payment services through X-Road
- **Government Reporting Services** - Submit tax collection reports to government systems

---

## What is X-Road?

X-Road is an open-source data exchange layer solution that enables secure and standardized information sharing between organizations over the Internet. It provides:

- **Secure Communication**: Mutual TLS (mTLS) encryption for all data exchanges
- **Digital Signatures**: Ensures message integrity and non-repudiation
- **Access Control**: Fine-grained access rights management
- **Audit Logging**: Complete audit trail of all data exchanges
- **Interoperability**: Standardized protocols for SOAP and REST APIs
- **No Intermediaries**: Direct communication between service consumers and providers

### Key Components

1. **Security Server**: Gateway for each organization to connect to X-Road
2. **Central Server**: Manages the X-Road ecosystem and service discovery
3. **Configuration Proxy**: Distributes configuration to Security Servers
4. **Service Provider**: Organization offering services through X-Road
5. **Service Consumer**: Organization consuming services through X-Road

---

## Why X-Road for This Project?

### Current State

The project currently has placeholder configurations for external API integrations:

```python
# Current approach (direct API calls)
NATIONAL_ID_VERIFICATION_API_URL = env('NATIONAL_ID_API_URL', default='')
NATIONAL_ID_API_TOKEN = env('NATIONAL_ID_API_TOKEN', default='')

VEHICLE_REGISTRY_API_URL = env('VEHICLE_REGISTRY_API_URL', default='')
VEHICLE_REGISTRY_API_TOKEN = env('VEHICLE_REGISTRY_API_TOKEN', default='')
```

### Benefits of X-Road Integration

1. **Security**: Enhanced security through mTLS and digital signatures
2. **Standardization**: Standardized way to communicate with government services
3. **Compliance**: Meets government requirements for secure data exchange
4. **Auditability**: Complete audit trail for compliance and troubleshooting
5. **Scalability**: Easy to add new services without changing infrastructure
6. **Reliability**: Built-in error handling and retry mechanisms

---

## X-Road Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tax Collection Platform                      │
│                      (Service Consumer)                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTPS (mTLS)
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│              X-Road Security Server (Consumer)                  │
│  • Message signing                                              │
│  • Access control                                               │
│  • Logging                                                      │
│  • Routing                                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ X-Road Protocol
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    X-Road Central Server                        │
│  • Service registry                                             │
│  • Configuration management                                     │
│  • Certificate management                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ X-Road Protocol
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│           X-Road Security Server (Provider)                     │
│         Government Services Security Server                     │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTPS (mTLS)
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│              Government Services                                │
│  • National ID Verification Service                            │
│  • Vehicle Registry Service                                    │
│  • Payment Gateway Services                                    │
│  • Reporting Services                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Service Identifiers

X-Road uses a hierarchical service identifier format:

```
INSTANCE/MEMBER_CLASS/MEMBER_CODE/SUBSYSTEM_CODE/SERVICE_CODE/VERSION
```

Example:
```
GOV/MEMBER/GOV-001/TAXCOLLECTOR/IDENTITY-VERIFICATION/v1
```

---

## Prerequisites

### 1. Organizational Requirements

- [ ] Organization must be a legal entity
- [ ] Organization must be approved by X-Road Operator
- [ ] Organization must obtain certificates from trusted CA
- [ ] Organization must have technical infrastructure

### 2. Technical Requirements

- [ ] X-Road Security Server installation
- [ ] Network access to X-Road Central Server
- [ ] SSL/TLS certificates for Security Server
- [ ] Service agreements with service providers
- [ ] Python 3.8+ for client library
- [ ] Django 4.2+ (already installed)

### 3. Service Provider Agreements

- [ ] Agreement with National ID Verification Service provider
- [ ] Agreement with Vehicle Registry Service provider
- [ ] Service descriptions (OpenAPI 3.0 for REST services)
- [ ] Access rights configuration

---

## Infrastructure Requirements

### 1. X-Road Security Server

#### Minimum Requirements

- **OS**: Ubuntu 20.04 LTS or later / RHEL 8 or later
- **CPU**: 2 cores minimum, 4 cores recommended
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 100 GB minimum for logs and data
- **Network**: Static IP address, open ports 80, 443, 5500, 5577, 5588
- **Certificates**: SSL certificates from trusted CA

#### Installation Steps

1. **Download X-Road Security Server**
   ```bash
   # For Ubuntu
   wget https://artifactory.niis.org/xroad-release-deb/pool/main/x/xroad-securityserver/xroad-securityserver_7.0.0-1.jammy_amd64.deb
   
   # Install dependencies
   sudo apt-get update
   sudo apt-get install -y postgresql postgresql-contrib
   
   # Install Security Server
   sudo dpkg -i xroad-securityserver_7.0.0-1.jammy_amd64.deb
   sudo apt-get install -f
   ```

2. **Configure Security Server**
   - Access admin UI: `https://your-security-server:4000`
   - Register with Central Server
   - Configure member information
   - Install certificates
   - Configure services

3. **Network Configuration**
   - Configure firewall rules
   - Set up reverse proxy (optional)
   - Configure SSL certificates

### 2. Python X-Road Client Library

#### Option 1: Use pyxroad Library (Recommended)

```bash
pip install pyxroad
```

#### Option 2: Use requests with X-Road Headers

Custom implementation using `requests` library with X-Road-specific headers.

---

## Implementation Steps

### Phase 1: Infrastructure Setup (Week 1-2)

1. **Install X-Road Security Server**
   - [ ] Set up Ubuntu/RHEL server
   - [ ] Install X-Road Security Server
   - [ ] Configure network and firewall
   - [ ] Install SSL certificates

2. **Register with X-Road Ecosystem**
   - [ ] Submit membership application
   - [ ] Obtain organization certificates
   - [ ] Register member in Central Server
   - [ ] Configure member information

3. **Configure Security Server**
   - [ ] Set up client certificates
   - [ ] Configure service consumers
   - [ ] Test connectivity to Central Server
   - [ ] Verify certificate chain

### Phase 2: Service Discovery and Agreements (Week 2-3)

1. **Discover Available Services**
   - [ ] Access X-Road service catalog
   - [ ] Identify required services
   - [ ] Review service descriptions
   - [ ] Understand service requirements

2. **Establish Service Agreements**
   - [ ] Contact service providers
   - [ ] Request access rights
   - [ ] Sign service agreements
   - [ ] Configure access rights in Security Server

3. **Obtain Service Descriptions**
   - [ ] Download OpenAPI 3.0 specifications (for REST)
   - [ ] Download WSDL files (for SOAP)
   - [ ] Review API documentation
   - [ ] Understand request/response formats

### Phase 3: Code Integration (Week 3-4)

1. **Install X-Road Client Library**
   ```bash
   pip install pyxroad
   # OR
   pip install requests cryptography
   ```

2. **Create X-Road Client Service**
   - [ ] Create `core/services/xroad_client.py`
   - [ ] Implement X-Road request builder
   - [ ] Handle X-Road headers
   - [ ] Implement error handling

3. **Update Existing Services**
   - [ ] Update `IdentityVerificationService`
   - [ ] Update `VehicleRegistrationVerificationService`
   - [ ] Add X-Road service identifiers
   - [ ] Update error handling

4. **Update Configuration**
   - [ ] Add X-Road settings to `settings.py`
   - [ ] Add service identifiers
   - [ ] Configure Security Server URL
   - [ ] Add certificate paths

### Phase 4: Testing (Week 4-5)

1. **Unit Testing**
   - [ ] Test X-Road client service
   - [ ] Test service integrations
   - [ ] Test error handling
   - [ ] Test certificate handling

2. **Integration Testing**
   - [ ] Test with test Security Server
   - [ ] Test service calls
   - [ ] Verify responses
   - [ ] Test error scenarios

3. **End-to-End Testing**
   - [ ] Test complete workflows
   - [ ] Test with production-like environment
   - [ ] Performance testing
   - [ ] Security testing

### Phase 5: Production Deployment (Week 5-6)

1. **Production Configuration**
   - [ ] Configure production Security Server
   - [ ] Install production certificates
   - [ ] Update service identifiers
   - [ ] Configure monitoring

2. **Monitoring and Logging**
   - [ ] Set up X-Road monitoring
   - [ ] Configure log aggregation
   - [ ] Set up alerts
   - [ ] Configure audit logging

3. **Documentation**
   - [ ] Document service integrations
   - [ ] Document configuration
   - [ ] Create runbooks
   - [ ] Train operations team

---

## Code Integration

### 1. Install Dependencies

Add to `requirements.txt`:

```txt
# X-Road integration
pyxroad>=1.0.0
# OR use requests with custom implementation
requests>=2.31.0
cryptography>=41.0.0
```

### 2. Create X-Road Client Service

Create `core/services/xroad_client.py`:

```python
"""
X-Road Client Service for secure data exchange
"""
import logging
import requests
from typing import Dict, Optional, Any
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

logger = logging.getLogger(__name__)


class XRoadClient:
    """
    X-Road client for making secure requests to X-Road services
    """
    
    def __init__(
        self,
        security_server_url: str,
        client_member_class: str,
        client_member_code: str,
        client_subsystem_code: str,
        instance: str = "GOV"
    ):
        """
        Initialize X-Road client
        
        Args:
            security_server_url: URL of the X-Road Security Server
            client_member_class: Member class of the client (e.g., "GOV")
            client_member_code: Member code of the client
            client_subsystem_code: Subsystem code of the client
            instance: X-Road instance identifier
        """
        self.security_server_url = security_server_url.rstrip('/')
        self.client_member_class = client_member_class
        self.client_member_code = client_member_code
        self.client_subsystem_code = client_subsystem_code
        self.instance = instance
        
        # Load client certificate
        self.cert_path = getattr(settings, 'XROAD_CLIENT_CERT_PATH', None)
        self.cert_key_path = getattr(settings, 'XROAD_CLIENT_KEY_PATH', None)
        self.cert_password = getattr(settings, 'XROAD_CLIENT_CERT_PASSWORD', None)
        
    def _build_xroad_headers(
        self,
        service_member_class: str,
        service_member_code: str,
        service_subsystem_code: str,
        service_code: str,
        service_version: str = "v1"
    ) -> Dict[str, str]:
        """
        Build X-Road specific headers
        
        Args:
            service_member_class: Member class of the service provider
            service_member_code: Member code of the service provider
            service_subsystem_code: Subsystem code of the service provider
            service_code: Service code
            service_version: Service version
            
        Returns:
            Dictionary of X-Road headers
        """
        # Build service identifier
        service_id = (
            f"{self.instance}/"
            f"{service_member_class}/"
            f"{service_member_code}/"
            f"{service_subsystem_code}/"
            f"{service_code}/"
            f"{service_version}"
        )
        
        # Build client identifier
        client_id = (
            f"{self.instance}/"
            f"{self.client_member_class}/"
            f"{self.client_member_code}/"
            f"{self.client_subsystem_code}"
        )
        
        headers = {
            'X-Road-Client': client_id,
            'X-Road-Service': service_id,
            'Content-Type': 'application/json',
        }
        
        return headers
    
    def _get_cert_tuple(self) -> Optional[tuple]:
        """
        Get certificate tuple for mTLS authentication
        
        Returns:
            Tuple of (cert_path, key_path) or None
        """
        if self.cert_path and self.cert_key_path:
            return (self.cert_path, self.cert_key_path)
        return None
    
    def request(
        self,
        method: str,
        service_path: str,
        service_member_class: str,
        service_member_code: str,
        service_subsystem_code: str,
        service_code: str,
        service_version: str = "v1",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """
        Make a request to an X-Road service
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            service_path: Path to the service endpoint
            service_member_class: Member class of the service provider
            service_member_code: Member code of the service provider
            service_subsystem_code: Subsystem code of the service provider
            service_code: Service code
            service_version: Service version
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response object
        """
        # Build URL
        url = f"{self.security_server_url}/r1/{service_path}"
        
        # Build headers
        headers = self._build_xroad_headers(
            service_member_class=service_member_class,
            service_member_code=service_member_code,
            service_subsystem_code=service_subsystem_code,
            service_code=service_code,
            service_version=service_version
        )
        
        # Get certificates
        cert = self._get_cert_tuple()
        
        # Verify SSL (should be True in production)
        verify = getattr(settings, 'XROAD_VERIFY_SSL', True)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                cert=cert,
                verify=verify,
                timeout=timeout
            )
            
            # Log request
            logger.info(
                f"X-Road request: {method} {url} - "
                f"Status: {response.status_code}"
            )
            
            return response
            
        except requests.RequestException as e:
            logger.error(f"X-Road request failed: {e}")
            raise
    
    def get(
        self,
        service_path: str,
        service_member_class: str,
        service_member_code: str,
        service_subsystem_code: str,
        service_code: str,
        service_version: str = "v1",
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make a GET request"""
        return self.request(
            method='GET',
            service_path=service_path,
            service_member_class=service_member_class,
            service_member_code=service_member_code,
            service_subsystem_code=service_subsystem_code,
            service_code=service_code,
            service_version=service_version,
            params=params,
            timeout=timeout
        )
    
    def post(
        self,
        service_path: str,
        service_member_class: str,
        service_member_code: str,
        service_subsystem_code: str,
        service_code: str,
        service_version: str = "v1",
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make a POST request"""
        return self.request(
            method='POST',
            service_path=service_path,
            service_member_class=service_member_class,
            service_member_code=service_member_code,
            service_subsystem_code=service_subsystem_code,
            service_code=service_code,
            service_version=service_version,
            data=data,
            timeout=timeout
        )
```

### 3. Update Identity Verification Service

Update `core/services/identity_verification.py`:

```python
"""
Identity Verification Service with X-Road integration
"""
import logging
from typing import Dict, Optional
from django.conf import settings
from core.services.xroad_client import XRoadClient

logger = logging.getLogger(__name__)


class IdentityVerificationService:
    """Service de vérification des cartes d'identité nationales via X-Road"""
    
    def __init__(self):
        """Initialize X-Road client"""
        self.xroad_client = XRoadClient(
            security_server_url=getattr(settings, 'XROAD_SECURITY_SERVER_URL', ''),
            client_member_class=getattr(settings, 'XROAD_CLIENT_MEMBER_CLASS', 'GOV'),
            client_member_code=getattr(settings, 'XROAD_CLIENT_MEMBER_CODE', ''),
            client_subsystem_code=getattr(settings, 'XROAD_CLIENT_SUBSYSTEM_CODE', 'TAXCOLLECTOR'),
            instance=getattr(settings, 'XROAD_INSTANCE', 'GOV')
        )
        
        # Service provider identifiers
        self.service_member_class = getattr(settings, 'XROAD_IDENTITY_SERVICE_MEMBER_CLASS', 'GOV')
        self.service_member_code = getattr(settings, 'XROAD_IDENTITY_SERVICE_MEMBER_CODE', 'GOV-001')
        self.service_subsystem_code = getattr(settings, 'XROAD_IDENTITY_SERVICE_SUBSYSTEM_CODE', 'IDENTITY')
        self.service_code = getattr(settings, 'XROAD_IDENTITY_SERVICE_CODE', 'VERIFY-NATIONAL-ID')
        self.service_version = getattr(settings, 'XROAD_IDENTITY_SERVICE_VERSION', 'v1')
    
    def verify_national_id(
        self,
        national_id_number: str,
        user_profile
    ) -> Dict[str, any]:
        """
        Vérifie un numéro de CIN avec les bases de données officielles via X-Road
        
        Args:
            national_id_number: Numéro de carte d'identité nationale
            user_profile: User profile object
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Prepare request data
            request_data = {
                'national_id': national_id_number,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name
            }
            
            # Make X-Road request
            response = self.xroad_client.post(
                service_path='verify-national-id',
                service_member_class=self.service_member_class,
                service_member_code=self.service_member_code,
                service_subsystem_code=self.service_subsystem_code,
                service_code=self.service_code,
                service_version=self.service_version,
                data=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': data.get('valid', False),
                    'details': data.get('details', {}),
                    'message': data.get('message', ''),
                    'verified_via': 'xroad'
                }
            else:
                logger.error(f"X-Road identity verification failed: {response.status_code} - {response.text}")
                return {
                    'valid': False,
                    'error': f'X-Road API Error: {response.status_code}',
                    'message': 'Erreur de vérification',
                    'verified_via': 'xroad'
                }
                
        except Exception as e:
            logger.error(f"Identity verification error: {e}")
            return {
                'valid': False,
                'error': str(e),
                'message': 'Service de vérification indisponible',
                'verified_via': 'xroad'
            }
    
    def extract_data_from_id_scan(self, image_url: str) -> Dict[str, any]:
        """
        Extraction OCR des données depuis le scan de CIN via X-Road
        
        Args:
            image_url: URL of the ID card scan image
            
        Returns:
            Dictionary with extracted data
        """
        try:
            request_data = {
                'image_url': image_url
            }
            
            response = self.xroad_client.post(
                service_path='extract-id-data',
                service_member_class=self.service_member_class,
                service_member_code=self.service_member_code,
                service_subsystem_code=self.service_subsystem_code,
                service_code='EXTRACT-ID-DATA',
                service_version=self.service_version,
                data=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"X-Road OCR extraction failed: {response.status_code}")
                return {
                    'error': f'X-Road API Error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                'error': str(e)
            }
```

### 4. Update Vehicle Registration Verification Service

Update `vehicles/services/registration_verification.py`:

```python
"""
Vehicle Registration Verification Service with X-Road integration
"""
import logging
from typing import Dict, Optional
from django.conf import settings
from core.services.xroad_client import XRoadClient

logger = logging.getLogger(__name__)


class VehicleRegistrationVerificationService:
    """Service de vérification des immatriculations via X-Road"""
    
    def __init__(self):
        """Initialize X-Road client"""
        self.xroad_client = XRoadClient(
            security_server_url=getattr(settings, 'XROAD_SECURITY_SERVER_URL', ''),
            client_member_class=getattr(settings, 'XROAD_CLIENT_MEMBER_CLASS', 'GOV'),
            client_member_code=getattr(settings, 'XROAD_CLIENT_MEMBER_CODE', ''),
            client_subsystem_code=getattr(settings, 'XROAD_CLIENT_SUBSYSTEM_CODE', 'TAXCOLLECTOR'),
            instance=getattr(settings, 'XROAD_INSTANCE', 'GOV')
        )
        
        # Service provider identifiers
        self.service_member_class = getattr(settings, 'XROAD_VEHICLE_SERVICE_MEMBER_CLASS', 'GOV')
        self.service_member_code = getattr(settings, 'XROAD_VEHICLE_SERVICE_MEMBER_CODE', 'GOV-002')
        self.service_subsystem_code = getattr(settings, 'XROAD_VEHICLE_SERVICE_SUBSYSTEM_CODE', 'VEHICLE-REGISTRY')
        self.service_code = getattr(settings, 'XROAD_VEHICLE_SERVICE_CODE', 'VERIFY-PLATE')
        self.service_version = getattr(settings, 'XROAD_VEHICLE_SERVICE_VERSION', 'v1')
    
    def verify_license_plate(self, plate_number: str) -> Dict[str, any]:
        """
        Vérifie l'existence et la validité d'une plaque d'immatriculation via X-Road
        
        Args:
            plate_number: Plaque d'immatriculation
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Make X-Road request
            response = self.xroad_client.get(
                service_path=f'verify/{plate_number}',
                service_member_class=self.service_member_class,
                service_member_code=self.service_member_code,
                service_subsystem_code=self.service_subsystem_code,
                service_code=self.service_code,
                service_version=self.service_version,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exists': data.get('exists', False),
                    'valid': data.get('valid', False),
                    'details': data.get('vehicle_details', {}),
                    'owner_info': data.get('owner_info', {}),
                    'status': data.get('status', 'unknown'),
                    'verified_via': 'xroad'
                }
            else:
                logger.error(f"X-Road vehicle verification failed: {response.status_code} - {response.text}")
                return {
                    'exists': False,
                    'valid': False,
                    'error': f'X-Road API Error: {response.status_code}',
                    'verified_via': 'xroad'
                }
                
        except Exception as e:
            logger.error(f"Vehicle verification error: {e}")
            return {
                'exists': None,
                'valid': None,
                'error': str(e),
                'verified_via': 'xroad'
            }
    
    def get_vehicle_history(self, plate_number: str) -> Dict[str, any]:
        """
        Récupère l'historique d'un véhicule via X-Road
        
        Args:
            plate_number: Plaque d'immatriculation
            
        Returns:
            Dictionary with vehicle history
        """
        try:
            response = self.xroad_client.get(
                service_path=f'history/{plate_number}',
                service_member_class=self.service_member_class,
                service_member_code=self.service_member_code,
                service_subsystem_code=self.service_subsystem_code,
                service_code='VEHICLE-HISTORY',
                service_version=self.service_version,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"X-Road vehicle history failed: {response.status_code}")
                return {
                    'error': f'X-Road API Error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Vehicle history error: {e}")
            return {
                'error': str(e)
            }
```

---

## Configuration

### 1. Update settings.py

Add X-Road configuration to `settings.py`:

```python
# X-Road Configuration
XROAD_ENABLED = env.bool('XROAD_ENABLED', default=False)
XROAD_INSTANCE = env('XROAD_INSTANCE', default='GOV')
XROAD_SECURITY_SERVER_URL = env('XROAD_SECURITY_SERVER_URL', default='https://xroad-security-server.gov.mg')

# Client (Tax Collector) identifiers
XROAD_CLIENT_MEMBER_CLASS = env('XROAD_CLIENT_MEMBER_CLASS', default='GOV')
XROAD_CLIENT_MEMBER_CODE = env('XROAD_CLIENT_MEMBER_CODE', default='')
XROAD_CLIENT_SUBSYSTEM_CODE = env('XROAD_CLIENT_SUBSYSTEM_CODE', default='TAXCOLLECTOR')

# Client certificates
XROAD_CLIENT_CERT_PATH = env('XROAD_CLIENT_CERT_PATH', default='')
XROAD_CLIENT_KEY_PATH = env('XROAD_CLIENT_KEY_PATH', default='')
XROAD_CLIENT_CERT_PASSWORD = env('XROAD_CLIENT_CERT_PASSWORD', default='')
XROAD_VERIFY_SSL = env.bool('XROAD_VERIFY_SSL', default=True)

# Identity Verification Service
XROAD_IDENTITY_SERVICE_MEMBER_CLASS = env('XROAD_IDENTITY_SERVICE_MEMBER_CLASS', default='GOV')
XROAD_IDENTITY_SERVICE_MEMBER_CODE = env('XROAD_IDENTITY_SERVICE_MEMBER_CODE', default='GOV-001')
XROAD_IDENTITY_SERVICE_SUBSYSTEM_CODE = env('XROAD_IDENTITY_SERVICE_SUBSYSTEM_CODE', default='IDENTITY')
XROAD_IDENTITY_SERVICE_CODE = env('XROAD_IDENTITY_SERVICE_CODE', default='VERIFY-NATIONAL-ID')
XROAD_IDENTITY_SERVICE_VERSION = env('XROAD_IDENTITY_SERVICE_VERSION', default='v1')

# Vehicle Registry Service
XROAD_VEHICLE_SERVICE_MEMBER_CLASS = env('XROAD_VEHICLE_SERVICE_MEMBER_CLASS', default='GOV')
XROAD_VEHICLE_SERVICE_MEMBER_CODE = env('XROAD_VEHICLE_SERVICE_MEMBER_CODE', default='GOV-002')
XROAD_VEHICLE_SERVICE_SUBSYSTEM_CODE = env('XROAD_VEHICLE_SERVICE_SUBSYSTEM_CODE', default='VEHICLE-REGISTRY')
XROAD_VEHICLE_SERVICE_CODE = env('XROAD_VEHICLE_SERVICE_CODE', default='VERIFY-PLATE')
XROAD_VEHICLE_SERVICE_VERSION = env('XROAD_VEHICLE_SERVICE_VERSION', default='v1')

# Fallback to direct API if X-Road is disabled
if not XROAD_ENABLED:
    # Keep existing direct API configurations
    NATIONAL_ID_VERIFICATION_API_URL = env('NATIONAL_ID_API_URL', default='')
    NATIONAL_ID_API_TOKEN = env('NATIONAL_ID_API_TOKEN', default='')
    VEHICLE_REGISTRY_API_URL = env('VEHICLE_REGISTRY_API_URL', default='')
    VEHICLE_REGISTRY_API_TOKEN = env('VEHICLE_REGISTRY_API_TOKEN', default='')
```

### 2. Update .env file

Add X-Road environment variables:

```bash
# X-Road Configuration
XROAD_ENABLED=true
XROAD_INSTANCE=GOV
XROAD_SECURITY_SERVER_URL=https://xroad-security-server.gov.mg

# Client identifiers
XROAD_CLIENT_MEMBER_CLASS=GOV
XROAD_CLIENT_MEMBER_CODE=TAXCOLLECTOR-001
XROAD_CLIENT_SUBSYSTEM_CODE=TAXCOLLECTOR

# Client certificates
XROAD_CLIENT_CERT_PATH=/etc/ssl/xroad/client.crt
XROAD_CLIENT_KEY_PATH=/etc/ssl/xroad/client.key
XROAD_CLIENT_CERT_PASSWORD=
XROAD_VERIFY_SSL=true

# Identity Service
XROAD_IDENTITY_SERVICE_MEMBER_CLASS=GOV
XROAD_IDENTITY_SERVICE_MEMBER_CODE=GOV-001
XROAD_IDENTITY_SERVICE_SUBSYSTEM_CODE=IDENTITY
XROAD_IDENTITY_SERVICE_CODE=VERIFY-NATIONAL-ID
XROAD_IDENTITY_SERVICE_VERSION=v1

# Vehicle Registry Service
XROAD_VEHICLE_SERVICE_MEMBER_CLASS=GOV
XROAD_VEHICLE_SERVICE_MEMBER_CODE=GOV-002
XROAD_VEHICLE_SERVICE_SUBSYSTEM_CODE=VEHICLE-REGISTRY
XROAD_VEHICLE_SERVICE_CODE=VERIFY-PLATE
XROAD_VEHICLE_SERVICE_VERSION=v1
```

### 3. Update Service Initialization

Update services to use X-Road when enabled:

```python
# core/services/identity_verification.py
from django.conf import settings

if getattr(settings, 'XROAD_ENABLED', False):
    from core.services.identity_verification_xroad import IdentityVerificationService
else:
    from core.services.identity_verification_direct import IdentityVerificationService
```

---

## Testing

### 1. Unit Tests

Create `core/tests/test_xroad_client.py`:

```python
"""
Unit tests for X-Road client
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from core.services.xroad_client import XRoadClient


class XRoadClientTestCase(TestCase):
    """Test cases for X-Road client"""
    
    def setUp(self):
        """Set up test client"""
        self.client = XRoadClient(
            security_server_url='https://test-xroad.gov.mg',
            client_member_class='GOV',
            client_member_code='TEST-001',
            client_subsystem_code='TEST'
        )
    
    @patch('core.services.xroad_client.requests.request')
    def test_get_request(self, mock_request):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'valid': True}
        mock_request.return_value = mock_response
        
        response = self.client.get(
            service_path='test/service',
            service_member_class='GOV',
            service_member_code='GOV-001',
            service_subsystem_code='SERVICE',
            service_code='TEST-SERVICE'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['valid'], True)
    
    @patch('core.services.xroad_client.requests.request')
    def test_post_request(self, mock_request):
        """Test POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_request.return_value = mock_response
        
        response = self.client.post(
            service_path='test/service',
            service_member_class='GOV',
            service_member_code='GOV-001',
            service_subsystem_code='SERVICE',
            service_code='TEST-SERVICE',
            data={'test': 'data'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
```

### 2. Integration Tests

Create test scenarios:

1. **Test Identity Verification**
   - Test with valid national ID
   - Test with invalid national ID
   - Test with service unavailable
   - Test with timeout

2. **Test Vehicle Verification**
   - Test with valid plate
   - Test with invalid plate
   - Test with service unavailable
   - Test with timeout

3. **Test Error Handling**
   - Test certificate errors
   - Test network errors
   - Test service errors
   - Test timeout errors

### 3. Test X-Road Security Server

Use test Security Server for integration testing:

```bash
# Set up test environment
XROAD_ENABLED=true
XROAD_SECURITY_SERVER_URL=https://test-xroad.gov.mg
XROAD_CLIENT_CERT_PATH=/path/to/test/cert.crt
XROAD_CLIENT_KEY_PATH=/path/to/test/cert.key
```

---

## Security Considerations

### 1. Certificate Management

- **Store certificates securely**: Use secure storage for client certificates
- **Rotate certificates regularly**: Implement certificate rotation process
- **Protect private keys**: Never expose private keys in code or logs
- **Use strong passwords**: Protect certificate files with strong passwords

### 2. Network Security

- **Use HTTPS only**: Always use HTTPS for Security Server communication
- **Verify SSL certificates**: Enable SSL verification in production
- **Firewall rules**: Configure firewall to allow only necessary ports
- **Network isolation**: Isolate Security Server in separate network segment

### 3. Access Control

- **Least privilege**: Grant minimum necessary access rights
- **Monitor access**: Monitor and audit all X-Road service calls
- **Review access rights**: Regularly review and update access rights
- **Implement rate limiting**: Prevent abuse of X-Road services

### 4. Logging and Monitoring

- **Log all requests**: Log all X-Road requests and responses
- **Monitor errors**: Set up alerts for X-Road errors
- **Audit trail**: Maintain audit trail for compliance
- **Performance monitoring**: Monitor X-Road service performance

---

## Troubleshooting

### Common Issues

#### 1. Certificate Errors

**Problem**: SSL certificate validation errors

**Solution**:
- Verify certificate paths are correct
- Check certificate expiration dates
- Verify certificate chain is complete
- Ensure private key matches certificate

#### 2. Connection Errors

**Problem**: Cannot connect to Security Server

**Solution**:
- Verify Security Server URL is correct
- Check network connectivity
- Verify firewall rules
- Check Security Server status

#### 3. Service Not Found

**Problem**: Service identifier not found

**Solution**:
- Verify service identifiers are correct
- Check service is registered in Central Server
- Verify access rights are configured
- Check service is available

#### 4. Access Denied

**Problem**: Access denied to service

**Solution**:
- Verify access rights are configured
- Check service agreement is active
- Verify client identifiers are correct
- Contact service provider

### Debugging

Enable debug logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core.services.xroad_client': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Monitoring

Monitor X-Road services:

1. **Security Server Monitoring**: Monitor Security Server logs and metrics
2. **Service Monitoring**: Monitor service availability and performance
3. **Error Monitoring**: Set up alerts for X-Road errors
4. **Performance Monitoring**: Monitor response times and throughput

---

## Additional Resources

### Official Documentation

- [X-Road Documentation](https://docs.x-road.global/)
- [X-Road Architecture](https://docs.x-road.global/Architecture/arc-g_x-road_arhitecture.html)
- [X-Road REST API](https://docs.x-road.global/Protocols/pr-rest_x-road_message_protocol_for_rest.html)
- [X-Road Security Server](https://docs.x-road.global/UG-SS/ug-ss_x-road_6_security_server_user_guide.html)

### Python Libraries

- [pyxroad](https://pypi.org/project/pyxroad/) - Python X-Road client library
- [requests](https://requests.readthedocs.io/) - HTTP library for Python
- [cryptography](https://cryptography.io/) - Cryptographic library for Python

### Community Resources

- [X-Road GitHub](https://github.com/nordic-institute/X-Road)
- [X-Road Forum](https://forum.x-road.global/)
- [X-Road Slack](https://xroad-global.slack.com/)

---

## Conclusion

This guide provides a comprehensive overview of integrating X-Road into the Tax Collection Platform. The integration will enable secure, standardized data exchange with government services while maintaining compliance with security and audit requirements.

### Next Steps

1. **Review and approve**: Review this guide with stakeholders
2. **Plan infrastructure**: Plan Security Server infrastructure
3. **Obtain certificates**: Obtain required certificates from CA
4. **Register with X-Road**: Register organization with X-Road ecosystem
5. **Implement code**: Implement X-Road client and service updates
6. **Test thoroughly**: Test integration in test environment
7. **Deploy to production**: Deploy to production with monitoring

### Support

For questions or issues, contact:
- **Technical Team**: tech@taxcollection.gov.mg
- **X-Road Operator**: xroad-operator@gov.mg
- **Service Providers**: Contact respective service providers

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Maintained By**: Technical Team

