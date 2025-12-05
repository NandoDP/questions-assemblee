# ✅ Solutions pour le modèle CamemBERT (422 MB)

## 🎯 Problème résolu

Le fichier `models/camembert_model/model.safetensors` (422 MB) dépassait la limite GitHub (100 MB).

## ✅ Ce qui a été fait

### 1. **Fichiers mis à jour**

- ✅ `.gitignore` - Exclut `model.safetensors` du versioning
- ✅ `.dockerignore` - Évite de copier le modèle dans les images Docker
- ✅ `README.md` - Ajout d'une note sur le modèle manquant
- ✅ `Dockerfile.etl` - Adapté pour gérer l'absence du modèle

### 2. **Nouveaux fichiers créés**

- ✅ `download_model.py` - Script pour télécharger le modèle automatiquement
- ✅ `models/camembert_model/README.md` - Instructions de téléchargement
- ✅ `MODEL_MANAGEMENT.md` - Guide complet de gestion du modèle

---

## 🚀 Prochaines étapes

### **Immédiat (avant de push sur GitHub)**

1. **Vérifier que le modèle n'est pas tracké** ✅
   ```bash
   git status  # model.safetensors ne doit PAS apparaître
   ```

2. **Commit les changements**
   ```bash
   git add .
   git commit -m "feat: Exclure model.safetensors (422MB) et ajouter script de téléchargement"
   git push origin main
   ```

### **Recommandé (pour le déploiement)**

3. **Héberger le modèle sur HuggingFace** ⭐ MEILLEURE OPTION

   ```bash
   # Installer huggingface_hub
   pip install huggingface_hub[cli]
   
   # Login
   huggingface-cli login
   
   # Créer un repo (sur le site web huggingface.co)
   # Puis uploader le modèle
   huggingface-cli upload NandoDP/questions-assemblee-camembert models/camembert_model
   ```

   Ensuite, mettre à jour `download_model.py` ligne 33 :
   ```python
   repo_id = "NandoDP/questions-assemblee-camembert"  # Votre repo
   ```

4. **Tester le téléchargement**
   ```bash
   # Renommer temporairement le modèle local
   mv models/camembert_model/model.safetensors models/camembert_model/model.safetensors.bak
   
   # Tester le script
   python download_model.py
   
   # Vérifier que ça fonctionne
   ls -lh models/camembert_model/
   ```

### **Pour GitHub Actions (ETL automatisé)**

5. **Ajouter le téléchargement dans le workflow**

   Modifier `.github/workflows/cron_etl.yml` :
   ```yaml
   - name: Download ML model
     run: python download_model.py
   ```

### **Pour Render (déploiement)**

6. **Option A : Télécharger au démarrage** (plus simple)
   - Le modèle sera téléchargé à chaque redémarrage
   - Temps de démarrage : +2-3 minutes

7. **Option B : Render Disk Storage** (plus rapide)
   - Créer un Disk sur Render (10 GB gratuit)
   - Uploader le modèle une fois
   - Monter le disk : `/app/models`

---

## 📊 Taille des fichiers

```
models/camembert_model/
├── model.safetensors         422 MB  ❌ Ignoré par Git
├── config.json                 <1 KB  ✅ Versionné
├── tokenizer_config.json       <1 KB  ✅ Versionné
├── sentencepiece.bpe.model   770 KB  ✅ Versionné
├── special_tokens_map.json     <1 KB  ✅ Versionné
├── added_tokens.json           <1 KB  ✅ Versionné
└── README.md                   <1 KB  ✅ Versionné
```

**Total versionné** : ~771 KB ✅  
**Total exclu** : ~422 MB ❌

---

## ⚠️ Important

- ❌ **NE JAMAIS** faire `git add models/camembert_model/model.safetensors`
- ❌ **NE JAMAIS** retirer la ligne du `.gitignore`
- ✅ **TOUJOURS** vérifier avec `git status` avant de push
- ✅ **DOCUMENTER** le lien de téléchargement dans le README

---

## 🔗 Liens utiles

- [HuggingFace Hub](https://huggingface.co/NandoDP) - Hébergement gratuit de modèles
- [Git LFS](https://git-lfs.github.com/) - Alternative (payant pour gros fichiers)
- [Render Disk Storage](https://render.com/docs/disks) - Stockage persistant

---

## ✅ Checklist finale

Avant de considérer cette tâche comme terminée :

- [x] `model.safetensors` exclu du `.gitignore`
- [x] `.dockerignore` mis à jour
- [x] Script `download_model.py` créé
- [x] Documentation dans `models/camembert_model/README.md`
- [x] Note dans le README principal
- [ ] Modèle uploadé sur HuggingFace (À FAIRE)
- [ ] `download_model.py` mis à jour avec le bon `repo_id` (À FAIRE)
- [ ] Test du téléchargement automatique (À FAIRE)
- [ ] Push sur GitHub sans le gros fichier (À FAIRE)

---

**Vous pouvez maintenant pusher sur GitHub sans problème ! 🎉**
