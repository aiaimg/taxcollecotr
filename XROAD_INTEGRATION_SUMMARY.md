# X-Road Integration - Quick Summary

## What Needs to Be Done

### 1. Infrastructure Setup
- [ ] Install X-Road Security Server (Ubuntu/RHEL)
- [ ] Register organization with X-Road ecosystem
- [ ] Obtain SSL certificates from trusted CA
- [ ] Configure network and firewall rules
- [ ] Set up monitoring and logging

### 2. Service Agreements
- [ ] Establish agreements with service providers:
  - National ID Verification Service
  - Vehicle Registry Service
- [ ] Obtain service descriptions (OpenAPI 3.0)
- [ ] Configure access rights in Security Server

### 3. Code Integration
- [ ] Install X-Road client library (`pyxroad` or custom implementation)
- [ ] Create X-Road client service (`core/services/xroad_client.py`)
- [ ] Update Identity Verification Service to use X-Road
- [ ] Update Vehicle Registration Verification Service to use X-Road
- [ ] Add X-Road configuration to `settings.py`
- [ ] Update environment variables

### 4. Testing
- [ ] Unit tests for X-Road client
- [ ] Integration tests with test Security Server
- [ ] End-to-end testing
- [ ] Security testing

### 5. Production Deployment
- [ ] Configure production Security Server
- [ ] Install production certificates
- [ ] Set up monitoring and alerts
- [ ] Train operations team

## Key Changes Required

### Files to Create
1. `core/services/xroad_client.py` - X-Road client service
2. `core/tests/test_xroad_client.py` - Unit tests
3. `XROAD_INTEGRATION_GUIDE.md` - Full documentation

### Files to Update
1. `core/services/identity_verification.py` - Use X-Road client
2. `vehicles/services/registration_verification.py` - Use X-Road client
3. `settings.py` - Add X-Road configuration
4. `requirements.txt` - Add X-Road dependencies
5. `.env` - Add X-Road environment variables

### Configuration to Add

```python
# settings.py
XROAD_ENABLED = env.bool('XROAD_ENABLED', default=False)
XROAD_SECURITY_SERVER_URL = env('XROAD_SECURITY_SERVER_URL', default='')
XROAD_CLIENT_MEMBER_CLASS = env('XROAD_CLIENT_MEMBER_CLASS', default='GOV')
XROAD_CLIENT_MEMBER_CODE = env('XROAD_CLIENT_MEMBER_CODE', default='')
XROAD_CLIENT_SUBSYSTEM_CODE = env('XROAD_CLIENT_SUBSYSTEM_CODE', default='TAXCOLLECTOR')
XROAD_CLIENT_CERT_PATH = env('XROAD_CLIENT_CERT_PATH', default='')
XROAD_CLIENT_KEY_PATH = env('XROAD_CLIENT_KEY_PATH', default='')
```

## Service Identifiers

### Current Services (to be migrated)
- **National ID Verification**: Currently uses `NATIONAL_ID_VERIFICATION_API_URL`
- **Vehicle Registry**: Currently uses `VEHICLE_REGISTRY_API_URL`

### X-Road Service Identifiers Format
```
INSTANCE/MEMBER_CLASS/MEMBER_CODE/SUBSYSTEM_CODE/SERVICE_CODE/VERSION
```

Example:
```
GOV/GOV/GOV-001/IDENTITY/VERIFY-NATIONAL-ID/v1
```

## Timeline

- **Week 1-2**: Infrastructure setup and registration
- **Week 2-3**: Service agreements and service discovery
- **Week 3-4**: Code integration
- **Week 4-5**: Testing
- **Week 5-6**: Production deployment

## Dependencies

```txt
# requirements.txt
pyxroad>=1.0.0
# OR
requests>=2.31.0
cryptography>=41.0.0
```

## Security Considerations

1. **Certificates**: Store securely, rotate regularly
2. **Network**: Use HTTPS only, verify SSL certificates
3. **Access Control**: Least privilege, monitor access
4. **Logging**: Log all requests, maintain audit trail

## Resources

- **Full Guide**: See `XROAD_INTEGRATION_GUIDE.md`
- **X-Road Docs**: https://docs.x-road.global/
- **X-Road GitHub**: https://github.com/nordic-institute/X-Road

## Next Steps

1. Review the full integration guide
2. Plan infrastructure requirements
3. Contact X-Road operator for registration
4. Obtain service agreements from providers
5. Begin implementation

---

**Last Updated**: January 2025

