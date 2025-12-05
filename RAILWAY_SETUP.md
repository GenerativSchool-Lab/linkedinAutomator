# Configuration des Variables Railway

Ce guide explique comment configurer les variables d'environnement Railway pour le LinkedIn Prospection Agent.

## Configuration Automatique

Utilisez le script fourni pour configurer automatiquement toutes les variables :

```bash
cd backend
./set_railway_variables.sh
```

## Configuration Manuelle

Vous pouvez aussi configurer les variables manuellement avec la CLI Railway :

```bash
# Naviguer vers le dossier backend
cd backend

# Variables de rate limiting
railway variables set RATE_LIMIT_DELAY=30
railway variables set MAX_CONNECTIONS_PER_DAY=20
railway variables set RETRY_DELAY_BASE=60
railway variables set MAX_RETRIES=3

# Variables de suivi
railway variables set FOLLOWUP_DAYS=7

# Vérifier les variables configurées
railway variables
```

## Variables Disponibles

### Rate Limiting

- **`RATE_LIMIT_DELAY`** (défaut: 30)
  - Délai en secondes entre chaque action LinkedIn
  - Recommandation LinkedIn: 20-30 secondes minimum
  - Augmentez si vous recevez des erreurs de rate limiting

- **`MAX_CONNECTIONS_PER_DAY`** (défaut: 20)
  - Nombre maximum de demandes de connexion par jour
  - LinkedIn limite généralement à 20-30 par jour pour les comptes personnels
  - Réduisez si votre compte est restreint

- **`RETRY_DELAY_BASE`** (défaut: 60)
  - Délai de base en secondes pour les tentatives de retry
  - Utilisé pour le backoff exponentiel en cas d'erreur

- **`MAX_RETRIES`** (défaut: 3)
  - Nombre maximum de tentatives en cas d'échec
  - Après ce nombre, la connexion sera marquée comme FAILED

### Suivi

- **`FOLLOWUP_DAYS`** (défaut: 7)
  - Nombre de jours à attendre avant d'envoyer un message de suivi
  - Après qu'une connexion soit acceptée (status CONNECTED)

## Statuts de Connexion

L'application différencie maintenant :

- **`PENDING`** : Demande de connexion envoyée, en attente d'acceptation
- **`CONNECTED`** : Connexion acceptée, vous pouvez envoyer des messages
- **`FAILED`** : Échec de la demande de connexion
- **`CONNECTING`** : En cours de traitement

## Relancer les Connexions

Utilisez l'endpoint `/api/connections/retry` pour relancer les connexions échouées :

```bash
# Relancer toutes les connexions échouées
curl -X POST https://backend-production-433a.up.railway.app/api/connections/retry

# Relancer des connexions spécifiques
curl -X POST https://backend-production-433a.up.railway.app/api/connections/retry \
  -H "Content-Type: application/json" \
  -d '{"connection_ids": [1, 2, 3]}'
```

## Recommandations

1. **Démarrez conservateur** : Utilisez `RATE_LIMIT_DELAY=30` et `MAX_CONNECTIONS_PER_DAY=15` au début
2. **Surveillez les erreurs** : Si vous voyez beaucoup d'erreurs "rate limit" ou "ERR_ABORTED", augmentez les délais
3. **Respectez les limites** : LinkedIn peut restreindre ou bannir les comptes qui dépassent les limites
4. **Testez progressivement** : Augmentez progressivement le nombre de connexions par jour

## Vérification

Après avoir configuré les variables, redéployez l'application :

```bash
cd backend
railway up
```

Les nouvelles variables seront prises en compte au prochain démarrage.
