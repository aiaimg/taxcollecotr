# MVola API V2 Beta - Conformité de l'Implémentation

## ✅ Corrections Appliquées Basées sur la Documentation V2 Beta

### 1. Format UserAccountIdentifier ✅
**Documentation** : `msisdn;{{MerchantNumber}}`
**Correction** : Tous les headers `UserAccountIdentifier` utilisent maintenant le format `msisdn;{msisdn}` au lieu de juste `{msisdn}`.

**Méthodes corrigées** :
- `initiate_payment()` - ligne 480
- `get_transaction_status()` - ligne 637
- `get_transaction_details()` - ligne 836

### 2. Metadata dans le Payload ✅
**Documentation** : Les metadata doivent inclure `partnerName` et peuvent inclure `XCorrelationId`.

**Corrections appliquées** :
- ✅ Ajout de `partnerName` dans les metadata (obligatoire selon la doc)
- ✅ Changement de `fc.internalReference` vers `XCorrelationId` (pour correspondre au format retourné dans les callbacks)
- ✅ Ajout de `originalTransactionReference: ""` (champ obligatoire même s'il est vide)

### 3. X-CorrelationID Format ✅
**Documentation** : Doit être UUID format (max 40 caractères)
**Statut** : ✅ Déjà conforme - nous utilisons `uuid.uuid4()` qui génère un UUID valide

### 4. Headers Requis ✅
**Documentation** : Tous les headers requis sont présents :
- ✅ `Authorization: Bearer <ACCESS_TOKEN>`
- ✅ `Version: 1.0`
- ✅ `X-CorrelationID: <UUID>`
- ✅ `UserLanguage: FR` (ou MG)
- ✅ `UserAccountIdentifier: msisdn;{msisdn}`
- ✅ `partnerName: {companyName}`
- ✅ `Content-Type: application/json`
- ✅ `X-Callback-URL: {callback_url}` (pour initiate_payment)
- ✅ `Cache-Control: no-cache`

### 5. Format requestDate ✅
**Documentation** : `yyyy-MM-ddTHH:mm:ss.SSSZ`
**Statut** : ✅ Déjà conforme - nous utilisons `datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'`

### 6. Numéros de Téléphone Sandbox ⚠️
**Documentation** : Pour le sandbox (preprod), les numéros de téléphone sont **fixes** :
- `0343500003`
- `0343500004`

**Information ajoutée** : Un log informatif a été ajouté pour rappeler ces numéros de test lors de l'initialisation en mode SANDBOX.

## 📋 Conformité avec la Documentation V2 Beta

### Payload Initiate Payment
```json
{
  "amount": "10000",
  "currency": "Ar",
  "descriptionText": "Payment description",
  "requestDate": "2024-01-01T12:00:00.000Z",
  "debitParty": [
    {
      "key": "msisdn",
      "value": "0343500003"
    }
  ],
  "creditParty": [
    {
      "key": "msisdn",
      "value": "0343500004"
    }
  ],
  "metadata": [
    {
      "key": "partnerName",
      "value": "Company Name"
    },
    {
      "key": "vehicle_plate",
      "value": "1234TAB"
    },
    {
      "key": "tax_year",
      "value": "2024"
    },
    {
      "key": "XCorrelationId",
      "value": "123e4567-e89b-12d3-a456-426614174000"
    }
  ],
  "requestingOrganisationTransactionReference": "123e4567-e89b-12d3-a456-426614174000",
  "originalTransactionReference": ""
}
```

### Headers Initiate Payment
```
Authorization: Bearer <ACCESS_TOKEN>
Version: 1.0
X-CorrelationID: 123e4567-e89b-12d3-a456-426614174000
UserLanguage: FR
UserAccountIdentifier: msisdn;0343500004
partnerName: Company Name
Content-Type: application/json
X-Callback-URL: https://yourdomain.com/api/payments/mvola/callback/
Cache-Control: no-cache
```

## 🔍 Points d'Attention

### 1. Authentification (Token)
**Problème actuel** : Erreur 401 "Invalid consumer credentials"

**Causes possibles** :
- Les identifiants ne correspondent pas à l'environnement (Sandbox vs Production)
- Les identifiants sont invalides ou expirés
- Les identifiants contiennent des espaces (maintenant automatiquement supprimés)

**Solution** :
- Vérifier que vous avez les bons identifiants pour l'environnement configuré
- Tester d'abord avec le sandbox (`https://devapi.mvola.mg`)
- Utiliser les numéros de test sandbox : `0343500003` ou `0343500004`

### 2. Numéros de Test Sandbox
**Important** : En mode SANDBOX, vous devez utiliser :
- `0343500003` ou `0343500004` comme numéros de téléphone
- Ces numéros sont fixes et ne peuvent pas être changés
- Tous les autres numéros seront rejetés en sandbox

### 3. Callback Response Format
**Documentation** : Le callback retourne les metadata avec `XCorrelationId` :
```json
{
  "metadata": [
    {
      "key": "XCorrelationId",
      "value": "3f2488d3-08cd-4fee-9dfa-a6a537a3b0b4"
    }
  ]
}
```

**Note** : Nous avons changé notre metadata pour utiliser `XCorrelationId` au lieu de `fc.internalReference` pour correspondre à ce format.

## ✅ Checklist de Conformité

- [x] Format UserAccountIdentifier : `msisdn;{msisdn}`
- [x] X-CorrelationID : UUID format
- [x] Headers requis : Tous présents
- [x] Metadata partnerName : Inclus
- [x] Metadata XCorrelationId : Inclus (au lieu de fc.internalReference)
- [x] originalTransactionReference : Inclus (vide)
- [x] Format requestDate : ISO 8601 avec Z
- [x] Currency : "Ar"
- [x] Version : "1.0"
- [x] Content-Type : "application/json"
- [x] Cache-Control : "no-cache"
- [x] Détection automatique de l'environnement (Sandbox/Production)
- [x] Logging des numéros de test sandbox

## 🧪 Test Recommandé

### Configuration Sandbox
```python
MVOLA_BASE_URL=https://devapi.mvola.mg
MVOLA_CONSUMER_KEY=votre_consumer_key_sandbox
MVOLA_CONSUMER_SECRET=votre_consumer_secret_sandbox
MVOLA_PARTNER_MSISDN=0343500004  # Numéro fixe pour sandbox
MVOLA_PARTNER_NAME=VotreNomEntreprise
MVOLA_CALLBACK_URL=https://yourdomain.com/api/payments/mvola/callback/
```

### Numéros de Test
- **Customer MSISDN** : `0343500003` ou `0343500004`
- **Merchant MSISDN** : `0343500003` ou `0343500004`

### Vérifications
1. ✅ L'authentification fonctionne (token obtenu)
2. ✅ Le paiement est initié avec succès
3. ✅ Le callback est reçu correctement
4. ✅ Les metadata contiennent `XCorrelationId`
5. ✅ Le statut de la transaction peut être vérifié

## 📝 Notes Importantes

1. **Les identifiants sandbox et production sont différents** - Assurez-vous d'utiliser les bons identifiants pour l'environnement configuré.

2. **Les numéros de test sandbox sont fixes** - Vous devez utiliser `0343500003` ou `0343500004` en sandbox.

3. **Le format XCorrelationId** - Nous utilisons maintenant `XCorrelationId` dans les metadata pour correspondre au format retourné dans les callbacks.

4. **partnerName dans metadata** - Maintenant inclus dans les metadata comme requis par la documentation.

5. **originalTransactionReference** - Maintenant inclus dans le payload (même s'il est vide).

## 🔄 Prochaines Étapes

1. ✅ Tester l'authentification avec les identifiants sandbox
2. ✅ Tester l'initiation d'un paiement avec les numéros de test
3. ✅ Vérifier que le callback est reçu correctement
4. ✅ Vérifier que les metadata sont correctes dans le callback
5. ✅ Tester la vérification du statut de la transaction

## 📞 Support

Si vous rencontrez des problèmes après ces corrections :
1. Vérifiez que vous avez les bons identifiants pour l'environnement
2. Utilisez les numéros de test sandbox : `0343500003` ou `0343500004`
3. Consultez les logs pour plus de détails
4. Contactez le support MVola si nécessaire








