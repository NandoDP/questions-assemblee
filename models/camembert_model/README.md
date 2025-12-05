# Modèle CamemBERT

Ce dossier contient un modèle CamemBERT fine-tuné pour la classification des questions parlementaires.

## 📥 Téléchargement du modèle

Le fichier `model.safetensors` (422 MB) n'est pas inclus dans le dépôt GitHub en raison de sa taille.

### Options de téléchargement :

#### **Option 1 : HuggingFace Hub** (RECOMMANDÉ)

Si le modèle est hébergé sur HuggingFace :

```bash
# Installer huggingface_hub
pip install huggingface_hub

# Télécharger le modèle
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='VOTRE_REPO_ID', local_dir='models/camembert_model')"
```

#### **Option 2 : Google Drive / OneDrive**

1. Télécharger le modèle depuis : [LIEN_A_AJOUTER]
2. Placer `model.safetensors` dans ce dossier

#### **Option 3 : Git LFS** (si configuré)

```bash
git lfs pull
```

## 📋 Fichiers du modèle

- `config.json` - Configuration du modèle
- `model.safetensors` - Poids du modèle (⚠️ non tracké par Git)
- `tokenizer_config.json` - Configuration du tokenizer
- `sentencepiece.bpe.model` - Modèle BPE
- `special_tokens_map.json` - Tokens spéciaux
- `added_tokens.json` - Tokens ajoutés

## 🔄 Alternative : Utiliser le modèle de base

Si le modèle fine-tuné n'est pas disponible, vous pouvez utiliser le modèle CamemBERT de base :

```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("camembert-base")
```

## 📊 Informations sur le modèle

- **Type** : CamemBERT (BERT français)
- **Taille** : 422 MB
- **Format** : SafeTensors
- **Usage** : Classification thématique des questions parlementaires
