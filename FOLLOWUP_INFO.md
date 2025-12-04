# Informations sur les Messages de Suivi (Follow-ups)

## Quand sont envoyés les messages de suivi ?

### Timing
- **Délai initial**: Les messages de suivi sont programmés **7 jours** après l'envoi du message de connexion initial
- **Vérification**: Le système vérifie toutes les **heures** s'il y a des messages de suivi à envoyer
- **Programmation automatique**: Les suivis sont automatiquement programmés pour toutes les nouvelles connexions acceptées

### Processus
1. **Connexion acceptée** → Un message initial est envoyé avec la demande de connexion
2. **7 jours plus tard** → Un message de suivi est automatiquement programmé
3. **Vérification horaire** → Le système vérifie chaque heure s'il y a des suivis à envoyer
4. **Envoi automatique** → Les messages de suivi sont envoyés automatiquement si la connexion est toujours active

## Exemples de Messages

### Message de Connexion Initial (Exemple)

**Profil:**
- Nom: Coline LAURENT
- Titre: Responsable communication
- Entreprise: Rejoué

**Message généré:**
```
Bonjour Coline, j'ai remarqué votre travail chez Rejoué dans l'économie circulaire et je trouve votre approche très inspirante. J'aimerais beaucoup nous connecter pour échanger sur nos expériences communes !
```

### Message de Suivi (Exemple)

**Contexte:** 7 jours après le message initial

**Message généré:**
```
Bonjour Coline, je souhaitais faire un suivi sur ma demande de connexion. J'aimerais beaucoup échanger sur vos initiatives en économie circulaire chez Rejoué. Avez-vous un moment pour discuter ?
```

## Configuration

- **Délai de suivi**: 7 jours (configurable via `FOLLOWUP_DAYS`)
- **Limite de débit**: 5 secondes entre chaque action (configurable via `RATE_LIMIT_DELAY`)
- **Langue**: Tous les messages sont générés en français

## Notes Importantes

- Les messages sont générés par IA (Mistral) et personnalisés selon le profil
- Les messages de suivi ne sont envoyés que si la connexion a été acceptée
- Si une connexion échoue, le suivi est automatiquement annulé
- Vous pouvez également envoyer des suivis manuellement depuis l'interface

