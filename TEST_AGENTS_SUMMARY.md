# Test Agents Summary

## ✅ All Available Test Agents

### Agent Partenaire (2 agents)

#### Agent Partenaire 1
- **Username:** `agent_partenaire1`
- **Password:** `agentpartenaire123`
- **Agent ID:** `AP19270`
- **Full Name:** Agent Partenaire Test 1
- **Location:** Antananarivo - Analakely
- **Commission Rate:** 2.50%
- **Status:** Active ✅
- **Login URL:** `/administration/agent-partenaire/login/`

#### Agent Partenaire 2
- **Username:** `agent_partenaire2`
- **Password:** `agentpartenaire123`
- **Agent ID:** `AP25286`
- **Full Name:** Agent Partenaire Test 2
- **Location:** Antananarivo - Ivandry
- **Commission Rate:** 3.00%
- **Status:** Active ✅
- **Login URL:** `/administration/agent-partenaire/login/`

### Agent Gouvernement (3 agents)

#### Agent Gouvernement 1
- **Username:** `agent_government1`
- **Password:** `agentgov123`
- **Badge Number:** `AG2337`
- **Zone:** Antananarivo Centre
- **Status:** Active ✅
- **Login URL:** `/administration/agent-government/login/`

#### Agent Gouvernement 2
- **Username:** `agent_government2`
- **Password:** `agentgov123`
- **Badge Number:** `AG7552`
- **Zone:** Antananarivo - Atsimondrano
- **Status:** Active ✅
- **Login URL:** `/administration/agent-government/login/`

#### Agent 1 (Existing - from previous setup)
- **Username:** `agent1`
- **Password:** (check your password)
- **Badge Number:** `AGENT1126`
- **Zone:** (check profile)
- **Status:** Active ✅
- **Login URL:** `/administration/agent-government/login/`

## 🚀 Quick Start Testing

### Test Agent Partenaire
```bash
# Login at:
http://localhost:8000/administration/agent-partenaire/login/

# Use credentials:
Username: agent_partenaire1
Password: agentpartenaire123
```

### Test Agent Gouvernement
```bash
# Login at:
http://localhost:8000/administration/agent-government/login/

# Use credentials:
Username: agent_government1
Password: agentgov123
```

## 📋 Management Commands

### Create/Recreate Test Agents
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

### Clean and Recreate
```bash
python manage.py create_test_agents --clean
```

## 🔑 Key Features to Test

### Agent Partenaire
- ✅ Cash session management
- ✅ Payment collection
- ✅ Commission tracking
- ✅ Statistics dashboard
- ✅ API endpoints

### Agent Gouvernement
- ✅ QR code verification
- ✅ Verification logging
- ✅ Statistics dashboard
- ✅ Verification history
- ✅ API endpoints

## 📝 Notes

- All agents are **active** and ready for testing
- Passwords are simple for testing purposes
- Agent IDs and Badge Numbers are auto-generated
- All agents have proper user profiles
- All agents can access their respective features

## 🎯 Testing Scenarios

1. **Login Test** - Test both agent types can log in
2. **Permission Test** - Test agents cannot access each other's features
3. **QR Verification Test** - Test QR code verification works
4. **API Test** - Test API endpoints with authentication
5. **Dashboard Test** - Test dashboards display correctly
6. **Statistics Test** - Test statistics are calculated correctly

See `AGENT_TESTING_GUIDE.md` for detailed testing instructions!

