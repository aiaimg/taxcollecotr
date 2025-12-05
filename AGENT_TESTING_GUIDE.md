# Agent System Testing Guide

## 🎯 Test Agents Created

### Agent Partenaire (2 agents)
**Agent Partenaire 1:**
- Username: `agent_partenaire1`
- Password: `agentpartenaire123`
- Agent ID: `AP19270`
- Location: Antananarivo - Analakely
- Commission Rate: 2.50%
- Login URL: `/administration/agent-partenaire/login/`

**Agent Partenaire 2:**
- Username: `agent_partenaire2`
- Password: `agentpartenaire123`
- Agent ID: `AP25286`
- Location: Antananarivo - Ivandry
- Commission Rate: 3.00%
- Login URL: `/administration/agent-partenaire/login/`

### Agent Gouvernement (2 agents)
**Agent Gouvernement 1:**
- Username: `agent_government1`
- Password: `agentgov123`
- Badge Number: `AG2337`
- Zone: Antananarivo Centre
- Login URL: `/administration/agent-government/login/`

**Agent Gouvernement 2:**
- Username: `agent_government2`
- Password: `agentgov123`
- Badge Number: `AG7552`
- Zone: Antananarivo - Atsimondrano
- Login URL: `/administration/agent-government/login/`

## 🧪 Testing Scenarios

### 1. Agent Partenaire Login Test

**Steps:**
1. Navigate to: `http://localhost:8000/administration/agent-partenaire/login/`
2. Enter credentials:
   - Username: `agent_partenaire1`
   - Password: `agentpartenaire123`
3. Click "Se connecter"
4. **Expected Result:** 
   - Successfully logged in
   - Redirected to cash session management or dashboard
   - Can see agent partenaire features

**Test with wrong credentials:**
1. Try logging in with incorrect password
2. **Expected Result:** Error message displayed

**Test with non-agent user:**
1. Try logging in with a regular user account
2. **Expected Result:** Access denied message

### 2. Agent Gouvernement Login Test

**Steps:**
1. Navigate to: `http://localhost:8000/administration/agent-government/login/`
2. Enter credentials:
   - Username: `agent_government1`
   - Password: `agentgov123`
3. Click "Se connecter"
4. **Expected Result:**
   - Successfully logged in
   - Redirected to QR verification dashboard
   - Can see verification statistics and recent verifications

**Test with wrong credentials:**
1. Try logging in with incorrect password
2. **Expected Result:** Error message displayed

### 3. QR Code Verification Test

**Prerequisites:**
- Need a valid QR code token from the system
- Agent Gouvernement must be logged in

**Steps:**
1. Login as `agent_government1`
2. Navigate to QR verification dashboard
3. Enter a QR code token manually or scan a QR code
4. **Expected Result:**
   - QR code verified
   - Verification logged
   - Vehicle and payment information displayed
   - Status shown (valid/invalid/expired)

**Test with invalid token:**
1. Enter an invalid/non-existent token
2. **Expected Result:** Error message "QR Code invalide ou introuvable"

### 4. API Endpoint Tests

#### Agent Partenaire API

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-partenaire/profile/ \
  -H "Authorization: Bearer <token>"
```

**Get Sessions:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-partenaire/my_sessions/ \
  -H "Authorization: Bearer <token>"
```

**Get Statistics:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-partenaire/statistics/ \
  -H "Authorization: Bearer <token>"
```

#### Agent Gouvernement API

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-government/profile/ \
  -H "Authorization: Bearer <token>"
```

**Verify QR Code:**
```bash
curl -X POST http://localhost:8000/api/v1/agent-government/verify_qr_code/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "qr_code_token_here",
    "gps_location": {"lat": -18.9, "lng": 47.5},
    "notes": "Test verification"
  }'
```

**Get Verifications:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-government/my_verifications/ \
  -H "Authorization: Bearer <token>"
```

**Get Statistics:**
```bash
curl -X GET http://localhost:8000/api/v1/agent-government/statistics/ \
  -H "Authorization: Bearer <token>"
```

### 5. Permission Tests

**Test Agent Partenaire accessing Government features:**
1. Login as `agent_partenaire1`
2. Try to access `/administration/agent-government/login/` or QR verification
3. **Expected Result:** Access denied or redirected

**Test Agent Gouvernement accessing Partenaire features:**
1. Login as `agent_government1`
2. Try to access cash session management
3. **Expected Result:** Access denied or redirected

**Test Regular User accessing Agent features:**
1. Login as a regular user (not an agent)
2. Try to access agent login pages
3. **Expected Result:** Access denied

### 6. Dashboard Tests

#### Agent Partenaire Dashboard
1. Login as `agent_partenaire1`
2. Check dashboard displays:
   - Today's transactions
   - Total collected
   - Commission earned
   - Active session status
   - Recent transactions

#### Agent Gouvernement Dashboard
1. Login as `agent_government1`
2. Check dashboard displays:
   - Today's verifications count
   - Week's verifications count
   - Status breakdown (valid/invalid/expired)
   - Recent verifications list
   - Agent information (badge, zone)

## 🔍 Quick Test Checklist

### Agent Partenaire
- [ ] Can log in with correct credentials
- [ ] Cannot log in with wrong credentials
- [ ] Redirected to correct dashboard after login
- [ ] Can access cash session management
- [ ] Can view statistics
- [ ] API endpoints work with authentication
- [ ] Cannot access government agent features

### Agent Gouvernement
- [ ] Can log in with correct credentials
- [ ] Cannot log in with wrong credentials
- [ ] Redirected to QR verification dashboard after login
- [ ] Can verify QR codes
- [ ] Verifications are logged correctly
- [ ] Can view verification history
- [ ] Statistics are displayed correctly
- [ ] API endpoints work with authentication
- [ ] Cannot access partenaire agent features

### QR Code Verification
- [ ] Valid QR codes are verified correctly
- [ ] Invalid QR codes show error message
- [ ] Expired QR codes are marked as expired
- [ ] Verification is logged with agent information
- [ ] Scan count is incremented
- [ ] Payment information is displayed (if available)

### API Endpoints
- [ ] All endpoints require authentication
- [ ] Permission classes work correctly
- [ ] Agent Partenaire can only access partenaire endpoints
- [ ] Agent Gouvernement can only access government endpoints
- [ ] Error handling works correctly
- [ ] Responses are in correct format

## 🛠️ Management Commands

### Create Test Agents
```bash
python manage.py create_test_agents
```

### Create Only Agent Partenaire
```bash
python manage.py create_test_agents --partenaire
```

### Create Only Agent Gouvernement
```bash
python manage.py create_test_agents --government
```

### Clean and Recreate Agents
```bash
python manage.py create_test_agents --clean
```

## 📝 Notes

1. **Passwords:** All test agents have simple passwords for testing. Change them in production!
2. **Agent IDs/Badges:** These are auto-generated and will be different each time you run the command
3. **Active Status:** All created agents are active by default
4. **Commission Rates:** Agent Partenaire 1 has 2.50%, Agent Partenaire 2 has 3.00%
5. **Zones:** Different zones are assigned to test zone-based features

## 🐛 Troubleshooting

### Agent cannot log in
- Check if agent profile exists: `python manage.py shell -c "from payments.models import AgentPartenaireProfile; print(AgentPartenaireProfile.objects.all())"`
- Check if agent is active: `agent.is_active` or `agent.est_actif`
- Check user is active: `user.is_active`

### QR Code verification not working
- Check if QR code exists: `python manage.py shell -c "from payments.models import QRCode; print(QRCode.objects.all())"`
- Check if token is correct (not code)
- Check if agent is logged in and has verification profile

### API endpoints returning 403
- Check authentication token is valid
- Check user has correct agent profile
- Check agent is active
- Check permission classes are correctly configured

## ✅ Success Criteria

The agent system is working correctly if:
1. ✅ Agents can log in with their credentials
2. ✅ Agents are redirected to correct dashboards
3. ✅ QR codes can be verified by government agents
4. ✅ Verifications are logged correctly
5. ✅ API endpoints work with proper authentication
6. ✅ Permission checks prevent unauthorized access
7. ✅ Statistics are displayed correctly
8. ✅ Different agent types cannot access each other's features

## 🎉 Ready to Test!

All test agents are created and ready. Use the credentials above to test the agent system!

