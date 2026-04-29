# Configuration du Rôle Public en Lecture Seule

## Pourquoi ce script ?

Le rôle Public doit être configuré **après le premier démarrage** de Superset pour ne pas ralentir le déploiement sur Render.

## Comment l'utiliser ?

### Option 1 : Script Python (RAPIDE - 5 secondes)

Connecte-toi via Shell Render ou SSH et lance :

```bash
cd /app/docker
python configure_public_role.py
```

Le script va :
- ✅ Supprimer toutes les permissions dangereuses (explore, export, edit, etc.)
- ✅ Ajouter uniquement les permissions de lecture (Dashboard, Chart, Dataset)
- ✅ Afficher un résumé des permissions finales

### Option 2 : Script Bash (LENT - 2 minutes)

```bash
bash /app/docker/superset_readonly_public.sh
```

### Option 3 : Configuration manuelle via l'interface

1. Se connecter en tant qu'admin
2. Aller dans **Security** → **List Roles** → **Public**
3. Supprimer toutes les permissions contenant : `write`, `edit`, `delete`, `explore`, `export`, `sql`
4. Garder uniquement :
   - `can_read on Dashboard`
   - `can_list on Dashboard`
   - `can_get_embedded on Dashboard`
   - `can_read on Chart`
   - `can_list on Chart`
   - `can_read on Dataset`
   - `can_read on Database`
   - `menu_access on Dashboards`

## Publier le Dashboard

Après avoir configuré le rôle Public :

1. Ouvrir le dashboard
2. Menu **⋯** → **Edit properties**
3. Section **Roles** → Ajouter "Public"
4. Section **Published** → Cocher
5. Sauvegarder

Le dashboard est maintenant accessible sans authentification en mode lecture seule.

## Vérification

Pour vérifier que la configuration est correcte :

1. Ouvrir une fenêtre de navigation privée
2. Aller sur `https://questions-assemblee-superset.onrender.com/superset/dashboard/1/`
3. Vérifier qu'aucun bouton "Explore", "Export", "Edit" n'est visible
4. Vérifier que les visualisations s'affichent correctement
