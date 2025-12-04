# Configuration du Contexte Entreprise

## Vue d'ensemble

L'application peut maintenant :
1. **Scraper les profils LinkedIn complets** pour obtenir plus d'informations (headline, about, expérience)
2. **Utiliser le contexte de votre entreprise** pour personnaliser les messages

## Configuration des Variables d'Environnement

Ajoutez ces variables dans Railway pour personnaliser vos messages :

### Variables à configurer

```bash
COMPANY_NAME="Votre Nom d'Entreprise"
COMPANY_DESCRIPTION="Description de ce que fait votre entreprise"
VALUE_PROPOSITION="Votre proposition de valeur unique"
```

### Exemple de configuration

```bash
COMPANY_NAME="Chyll.ai"
COMPANY_DESCRIPTION="Nous développons des solutions d'IA pour automatiser la prospection commerciale et améliorer l'engagement client sur LinkedIn."
VALUE_PROPOSITION="Nous aidons les entreprises à automatiser leur prospection LinkedIn tout en maintenant une approche personnalisée et respectueuse, augmentant ainsi leur taux de réponse de 300%."
```

## Comment configurer sur Railway

```bash
cd backend
railway variables --set "COMPANY_NAME=Votre Nom d'Entreprise"
railway variables --set "COMPANY_DESCRIPTION=Votre description"
railway variables --set "VALUE_PROPOSITION=Votre proposition de valeur"
```

## Comment ça fonctionne

### 1. Scraping des profils LinkedIn

Quand vous démarrez une connexion, l'application :
- Visite automatiquement le profil LinkedIn complet
- Extrait : headline, section "À propos", expérience actuelle, localisation
- Met à jour le profil dans la base de données avec ces informations

### 2. Personnalisation des messages

Les messages sont générés avec :
- **Informations du profil** : nom, titre, entreprise, about
- **Contexte de votre entreprise** : nom, description, proposition de valeur
- **IA (Mistral)** qui crée un message personnalisé en français

## Exemples de Messages Personnalisés

### Sans contexte entreprise (ancien)

```
Bonjour Coline, j'ai remarqué votre travail chez Rejoué et je pense que nous pourrions avoir des intérêts communs. J'aimerais beaucoup nous connecter !
```

### Avec contexte entreprise (nouveau)

**Configuration:**
- COMPANY_NAME: "Chyll.ai"
- COMPANY_DESCRIPTION: "Solutions d'IA pour automatiser la prospection LinkedIn"
- VALUE_PROPOSITION: "Automatisation personnalisée qui augmente le taux de réponse de 300%"

**Message généré:**
```
Bonjour Coline, j'ai remarqué votre engagement dans l'économie circulaire chez Rejoué. Chez Chyll.ai, nous développons des solutions d'IA pour automatiser la prospection tout en gardant une approche personnalisée. Je pense que cela pourrait vous intéresser. Connectons-nous ?
```

## Avantages

1. **Messages plus pertinents** : L'IA utilise le contexte de votre entreprise pour créer des liens naturels
2. **Meilleure personnalisation** : Les profils sont enrichis avec les données LinkedIn complètes
3. **Taux de réponse amélioré** : Les messages sont plus engageants et pertinents

## Notes Importantes

- Le scraping des profils ajoute ~3 secondes par profil (en plus du délai de 5s)
- Les informations scrapées sont sauvegardées dans la base de données
- Si le scraping échoue, l'application utilise les données existantes du profil

