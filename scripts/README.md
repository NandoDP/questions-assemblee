# Scripts Techniques

Ce dossier regroupe les scripts qui n'ont pas vocation a rester visibles a la racine du depot.

## Structure

### `superset/`

Bootstrap et administration de l'environnement Superset :

- `init-superset.sh` : sequence d'initialisation au demarrage du service.
- `configure_public_role.py` : configuration du role `Public` en lecture seule.
- `assign_public_to_datasets.py` : attribution des permissions datasets au role `Public`.
- `assign_public_to_dashboards.py` : partage des dashboards publies avec `Public`.
- `create_guest_user.py` : creation ou alignement du compte guest.
- `create_embed_service_user.py` : creation du compte de service pour l'embed SDK.
- `create_embedded_dashboard_config.py` : creation des configurations d'embed par dashboard.
- `fix_regions_chart.py` : reparation du graphique cartographique des regions.
- `superset_readonly_public.sh` : variante shell minimaliste pour verrouiller le role `Public`.

### `ml/`

Utilitaires lies au modele de classification :

- `download_model.py` : telechargement du modele CamemBERT depuis HuggingFace.

### `legacy/`

Elements conserves pour reference historique :

- `public_dashboard_prototype.py` : ancien prototype Flask d'exposition publique du dashboard.

## Principe

La racine du depot doit rester reservee aux points d'entree produit, a l'infrastructure et a la documentation principale.
Les scripts d'exploitation, de bootstrap et les prototypes archives sont centralises ici pour garder un depot plus lisible.