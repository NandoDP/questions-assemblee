# Configuration des Secrets GitHub

## 📋 Secrets Nécessaires

### Pour le workflow `cron_etl.yml` (ETL automatique)

| Secret | Valeur | Obligatoire |
|--------|--------|-------------|
| `DATABASE_URL` | URL de connexion PostgreSQL depuis Render | ✅ Oui |
| `API_TOKEN` | Token API Assemblée Nationale (si nécessaire) | ⚠️ Optionnel |

### Pour le workflow `build_and_push.yml` (Build Docker)

✅ **Aucun secret à configurer !** Le workflow utilise automatiquement `GITHUB_TOKEN` fourni par GitHub Actions.

---

## 🔧 Comment Configurer les Secrets

### Étape 1 : Accéder aux Settings du Repository

1. Allez sur votre repository GitHub : https://github.com/NandoDP/questions-assemblee
2. Cliquez sur **Settings** (⚙️)
3. Dans le menu latéral gauche, cliquez sur **Secrets and variables** > **Actions**

### Étape 2 : Ajouter `DATABASE_URL`

1. Cliquez sur **New repository secret**
2. Name: `DATABASE_URL`
3. Secret: Récupérez l'URL depuis Render

#### 🔍 Où trouver DATABASE_URL sur Render ?

1. Allez sur votre dashboard Render : https://dashboard.render.com
2. Cliquez sur votre base de données PostgreSQL : `questions-assemblee-db`
3. Dans l'onglet **Info**, copiez la valeur de **Internal Database URL**
4. Format : `postgresql://user:password@hostname:5432/dbname`

**Exemple :**
```
postgresql://questions_assemblee_user:abcd1234xyz@dpg-xxxxx-a.oregon-postgres.render.com:5432/questions_assemblee
```

5. Collez cette URL dans le champ **Secret** sur GitHub
6. Cliquez sur **Add secret**

### Étape 3 : Ajouter `API_TOKEN` (Optionnel)

Si votre code utilise un token pour l'API de l'Assemblée Nationale :

1. Cliquez sur **New repository secret**
2. Name: `API_TOKEN`
3. Secret: Votre token API (ou laissez vide si pas nécessaire)
4. Cliquez sur **Add secret**

> ⚠️ **Note :** Si vous n'utilisez pas de token API, vous pouvez ignorer cette étape. Le workflow a une valeur par défaut vide.

---

## ✅ Vérifier la Configuration

### Test 1 : Vérifier que les secrets sont configurés

1. Allez dans **Settings** > **Secrets and variables** > **Actions**
2. Vous devriez voir :
   - ✅ `DATABASE_URL` (Updated X seconds/minutes ago)
   - ⚠️ `API_TOKEN` (optionnel)

### Test 2 : Déclencher manuellement le workflow ETL

1. Allez dans l'onglet **Actions** de votre repository
2. Cliquez sur le workflow **Scheduled ETL Pipeline**
3. Cliquez sur **Run workflow** > **Run workflow**
4. Attendez l'exécution (2-3 minutes)
5. Vérifiez que le workflow se termine en vert ✅

### Test 3 : Vérifier les logs

Cliquez sur l'exécution du workflow et vérifiez :
- ✅ Install dependencies
- ✅ Download spaCy model
- ✅ Download CamemBERT model from HuggingFace
- ✅ Run ETL Pipeline

---

## 🔒 Sécurité des Secrets

### ✅ Bonnes Pratiques

- Les secrets GitHub sont **chiffrés** et ne sont jamais affichés dans les logs
- Utilisez **Internal Database URL** de Render (pas l'External URL) pour plus de sécurité
- Ne commitez **jamais** les secrets dans le code
- Utilisez `.env.local` pour le développement local (ignoré par Git)

### ⚠️ Que Faire si un Secret est Compromis ?

1. **Régénérer la DATABASE_URL sur Render :**
   - Render Dashboard > Database > Settings > Reset Database Password
   - Mettre à jour le secret sur GitHub

2. **Révoquer l'API_TOKEN :**
   - Générer un nouveau token
   - Mettre à jour le secret sur GitHub

---

## 🐛 Dépannage

### Erreur : `Error: Username and password required`

**Cause :** Le workflow `build_and_push.yml` utilisait `GHCR_TOKEN` au lieu de `GITHUB_TOKEN`.

**Solution :** ✅ Déjà corrigé ! Le workflow utilise maintenant `secrets.GITHUB_TOKEN` qui est fourni automatiquement.

### Erreur : `psycopg2.OperationalError: FATAL: password authentication failed`

**Cause :** `DATABASE_URL` est incorrect ou manquant.

**Solution :**
1. Vérifiez que le secret `DATABASE_URL` est bien configuré sur GitHub
2. Copiez à nouveau l'**Internal Database URL** depuis Render
3. Assurez-vous qu'il n'y a pas d'espaces avant/après l'URL

### Erreur : `ModuleNotFoundError: No module named 'src'`

**Cause :** Le workflow ne trouve pas le package Python.

**Solution :** Vérifiez que `src/` contient un fichier `__init__.py` :
```bash
touch src/__init__.py
git add src/__init__.py
git commit -m "fix: Ajouter __init__.py pour package src"
git push
```

---

## 📊 Prochaines Étapes

Après configuration des secrets :

1. ✅ Configurer `DATABASE_URL` sur GitHub
2. ✅ Tester le workflow manuellement (Actions > Run workflow)
3. ✅ Vérifier que l'ETL s'exécute sans erreur
4. 📅 Le workflow s'exécutera automatiquement tous les jours à 2h UTC
5. 📈 Les données seront visibles dans Superset : https://questions-assemblee-superset.onrender.com

---

## 🆘 Besoin d'Aide ?

Consultez les logs du workflow dans l'onglet **Actions** pour voir les erreurs détaillées.
