#!/usr/bin/env python3
"""
Script pour télécharger le modèle CamemBERT depuis HuggingFace
Usage: python download_model.py
"""

import os
import sys
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("❌ huggingface_hub n'est pas installé.")
    print("📦 Installation: pip install huggingface_hub")
    sys.exit(1)


def download_model():
    """Télécharge le modèle CamemBERT depuis HuggingFace"""
    
    model_dir = Path("models/camembert_model")
    model_file = model_dir / "model.safetensors"
    
    # Vérifier si le modèle existe déjà
    if model_file.exists():
        print(f"✅ Le modèle existe déjà : {model_file}")
        return
    
    print("📥 Téléchargement du modèle CamemBERT...")
    print("⚠️  Cela peut prendre plusieurs minutes (422 MB)")
    
    # Option 1 : Depuis votre propre repo HuggingFace (à configurer)
    repo_id = "NandoDP/questions-assemblee-camembert"
    
    # Option 2 : Utiliser le modèle de base CamemBERT
    # repo_id = "camembert-base"
    
    try:
        # Télécharger tous les fichiers nécessaires
        files_to_download = [
            "config.json",
            "pytorch_model.bin",  # ou model.safetensors selon le modèle
            "tokenizer_config.json",
            "sentencepiece.bpe.model",
            "special_tokens_map.json",
        ]
        
        for filename in files_to_download:
            try:
                downloaded_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    cache_dir=None,
                    local_dir=str(model_dir),
                    local_dir_use_symlinks=False
                )
                print(f"✅ {filename} téléchargé")
            except Exception as e:
                print(f"⚠️  {filename} non disponible: {e}")
        
        print("\n✅ Téléchargement terminé !")
        print(f"📁 Modèle enregistré dans : {model_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        print("\n💡 Alternatives :")
        print("   1. Télécharger manuellement depuis HuggingFace")
        print("   2. Utiliser le modèle de base camembert-base")
        print("   3. Contacter le propriétaire du repo pour obtenir le modèle")
        sys.exit(1)


if __name__ == "__main__":
    print("🤖 Script de téléchargement du modèle CamemBERT")
    print("=" * 50)
    download_model()
