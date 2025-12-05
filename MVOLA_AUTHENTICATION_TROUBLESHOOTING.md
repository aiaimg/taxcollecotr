# MVola Authentication Troubleshooting Guide

## Problème : Erreur 401 "Invalid consumer credentials"

### Analyse du problème

L'erreur 401 indique que les identifiants fournis ne sont pas reconnus par l'API MVola. Voici les points importants à vérifier :

## ⚠️ Important : La documentation ne contient PAS d'identifiants

La documentation fournie par MVola **ne contient pas d'identifiants sandbox ou production**. Elle montre uniquement :
- Les URLs (Sandbox: `https://devapi.mvola.mg`, Production: `https://api.mvola.mg`)
- Le format des requêtes
- Les headers requis
- Mais **PAS les Consumer Key/Secret**

## 🔑 Comment obtenir les identifiants

### Pour l'environnement SANDBOX (Test)
1. Contactez le support technique MVola
2. Demandez l'accès au portail développeur
3. Obtenez vos identifiants sandbox :
   - Consumer Key
   - Consumer Secret
   - Partner MSISDN (numéro de téléphone du marchand)
   - Partner Name (nom de votre entreprise)

### Pour l'environnement PRODUCTION
1. Faites une demande d'accès production auprès de MVola
2. Complétez le processus d'onboarding
3. Obtenez vos identifiants production (différents des identifiants sandbox)

## ✅ Vérifications à effectuer

### 1. Vérifier l'environnement
- **SANDBOX** : URL doit être `https://devapi.mvola.mg`
- **PRODUCTION** : URL doit être `https://api.mvola.mg`
- ⚠️ **Les identifiants sandbox ne fonctionnent PAS en production et vice versa**

### 2. Vérifier les identifiants
- Consumer Key et Consumer Secret sont **corrects**
- Les identifiants **correspondent à l'environnement** configuré
- Les identifiants **n'ont pas expiré**
- Pas d'espaces en début/fin (sera automatiquement corrigé maintenant)

### 3. Vérifier le format
- Consumer Key : Chaîne de caractères (pas d'espaces)
- Consumer Secret : Chaîne de caractères (pas d'espaces)
- Partner MSISDN : Format `0340000000` (10 chiffres)
- Partner Name : Nom de l'entreprise (max 50 caractères)

## 🔧 Améliorations apportées au code

### 1. Détection automatique des espaces
Le code détecte maintenant automatiquement et supprime les espaces en début/fin des identifiants :
```python
consumer_key = self.consumer_key.strip() if self.consumer_key else ""
consumer_secret = self.consumer_secret.strip() if self.consumer_secret else ""
```

### 2. Validation améliorée
- Vérification que les identifiants ne sont pas vides
- Détection des espaces dans les identifiants
- Messages d'erreur plus détaillés

### 3. Logging amélioré
- Détection automatique de l'environnement (SANDBOX/PRODUCTION)
- Logs détaillés sans exposer les secrets
- Messages d'erreur plus informatifs

### 4. Correction du format UserAccountIdentifier
- Correction du header `UserAccountIdentifier` : maintenant `msisdn;{msisdn}` au lieu de juste `{msisdn}`
- Appliqué à toutes les méthodes API (initiate_payment, get_transaction_status, get_transaction_details)

## 📋 Checklist de diagnostic

- [ ] Les identifiants sont corrects
- [ ] Les identifiants correspondent à l'environnement (Sandbox vs Production)
- [ ] L'URL de base correspond à l'environnement
- [ ] Pas d'espaces dans les identifiants
- [ ] Les identifiants n'ont pas expiré
- [ ] Le Partner MSISDN est correct
- [ ] Le Partner Name est correct
- [ ] Le Callback URL est configuré

## 🧪 Test recommandé

### 1. Tester d'abord avec SANDBOX
```python
# Configuration Sandbox
MVOLA_BASE_URL=https://devapi.mvola.mg
MVOLA_CONSUMER_KEY=votre_consumer_key_sandbox
MVOLA_CONSUMER_SECRET=votre_consumer_secret_sandbox
MVOLA_PARTNER_MSISDN=0340000000
MVOLA_PARTNER_NAME=VotreNomEntreprise
```

### 2. Vérifier les logs
Les logs montrent maintenant :
- L'environnement détecté (SANDBOX/PRODUCTION)
- Si des espaces ont été détectés dans les identifiants
- La longueur des identifiants (sans les exposer)

### 3. Si ça fonctionne en Sandbox
- Vos identifiants sandbox sont corrects
- Le problème vient peut-être des identifiants production

### 4. Si ça ne fonctionne pas en Sandbox
- Vérifiez que vous avez bien les identifiants sandbox
- Contactez le support MVola pour obtenir les identifiants

## 📞 Support MVola

Si le problème persiste après avoir vérifié tous les points ci-dessus :
1. Contactez le support technique MVola
2. Fournissez les informations suivantes :
   - L'environnement utilisé (Sandbox/Production)
   - L'URL de base utilisée
   - Le code d'erreur reçu (401)
   - Le message d'erreur complet
   - Les logs (sans les identifiants complets)

## 🔒 Sécurité

⚠️ **Ne jamais commiter les identifiants dans le code**
- Utilisez des variables d'environnement
- Utilisez un fichier `.env` (non versionné)
- Utilisez un gestionnaire de secrets pour la production

## 📝 Notes importantes

1. **Les identifiants sandbox et production sont différents**
2. **Les identifiants peuvent expirer** - contactez MVola si nécessaire
3. **Le format UserAccountIdentifier est maintenant corrigé** : `msisdn;{msisdn}`
4. **Les espaces dans les identifiants sont automatiquement supprimés**

## 🔄 Prochaines étapes

1. Vérifiez que vous avez les bons identifiants pour l'environnement configuré
2. Testez avec le sandbox d'abord (`https://devapi.mvola.mg`)
3. Si ça fonctionne en sandbox, vérifiez vos identifiants production
4. Contactez le support MVola si nécessaire

