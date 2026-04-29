# 🚀 Guide de gestion du modèle CamemBERT

## 📊 Problème

Le fichier `models/camembert_model/model.safetensors` (422 MB) dépasse la limite GitHub de 100 MB.

## ✅ Solutions implémentées

### 1. **Exclusion Git** (✅ FAIT)
Le fichier est exclu du dépôt via `.gitignore` :
```
models/camembert_model/model.safetensors
```

### 2. **Documentation** (✅ FAIT)
- `models/camembert_model/README.md` : Instructions de téléchargement
- Note dans le README principal du projet

### 3. **Script de téléchargement** (✅ FAIT)
`scripts/ml/download_model.py` : Script Python pour télécharger automatiquement le modèle

### 4. **Docker optimisé** (✅ FAIT)
`.dockerignore` mis à jour pour éviter de copier le gros fichier dans les images Docker

---

## 🎯 Options de déploiement

### **Option A : Héberger sur HuggingFace** ⭐ RECOMMANDÉ

1. Créer un compte sur [huggingface.co](https://huggingface.co)
2. Créer un nouveau modèle (repo)
3. Uploader le modèle :

```bash
pip install huggingface_hub

# Login
huggingface-cli login

# Upload
huggingface-cli upload VOTRE_USERNAME/questions-assemblee-camembert models/camembert_model
```

4. Mettre à jour `scripts/ml/download_model.py` avec votre `repo_id`

**Avantages** :
- ✅ Gratuit pour modèles publics
- ✅ Versioning automatique
- ✅ Téléchargement rapide
- ✅ Intégration facile avec transformers

### **Option B : Google Drive / OneDrive**

1. Uploader `model.safetensors` sur Drive/OneDrive
2. Créer un lien de partage public
3. Mettre à jour `models/camembert_model/README.md` avec le lien

**Avantages** :
- ✅ Simple et rapide
- ✅ Pas besoin de compte HuggingFace

**Inconvénients** :
- ❌ Pas de versioning
- ❌ Téléchargement manuel

### **Option C : Git LFS** (Git Large File Storage)

⚠️ **Attention** : GitHub LFS a des limites de bande passante (1 GB/mois gratuit)

```bash
# Installer Git LFS
git lfs install

# Tracker le fichier
git lfs track "models/camembert_model/model.safetensors"

# Commit
git add .gitattributes models/camembert_model/model.safetensors
git commit -m "Add model via Git LFS"
git push
```

### **Option D : Render Disk Storage**

Pour le déploiement sur Render, monter un volume persistant :

1. Dans Render : Create Disk (10 GB gratuit)
2. Monter le disk sur `/app/models`
3. Uploader le modèle via SSH ou script

---

## 📦 Pour les contributeurs

Si vous clonez ce repo et voulez utiliser le modèle :

```bash
# Cloner le repo
git clone https://github.com/NandoDP/questions-assemblee.git
cd questions-assemblee

# Télécharger le modèle (Option A : HuggingFace)
python scripts/ml/download_model.py

# OU télécharger manuellement depuis le lien fourni
```

---

## 🐳 Pour Docker

### Développement local

```bash
# Placer le modèle dans models/camembert_model/ AVANT de build
docker build -f Dockerfile.etl -t etl-pipeline .
docker run etl-pipeline
```

### Production (Render)

Le modèle sera téléchargé automatiquement au démarrage via `scripts/ml/download_model.py` ou monté depuis un Disk Storage.

---

## ❓ FAQ

**Q : Le pipeline ETL fonctionne sans le modèle ?**
R : Non, le modèle est nécessaire pour la classification. Il doit être téléchargé avant l'exécution.

**Q : Peut-on utiliser un autre modèle ?**
R : Oui, modifiez `src/transformers/classifier.py` pour charger un autre modèle (ex: `camembert-base`)

**Q : Combien coûte l'hébergement sur HuggingFace ?**
R : Gratuit pour les modèles publics, 9$/mois pour modèles privés

---

## 🔗 Ressources

- [HuggingFace Hub Documentation](https://huggingface.co/docs/hub/index)
- [Git LFS Documentation](https://git-lfs.github.com/)
- [Render Disk Storage](https://render.com/docs/disks)
