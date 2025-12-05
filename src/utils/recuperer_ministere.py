# from rapidfuzz import fuzz, process

# ministeres = [
#     "Ministre du Travail, de l'Emploi et des Relations avec les Institutions",
#     "Ministre de l'Intégration africaine et des Affaires étrangères",
#     "Ministre des Forces armées",
#     "Ministre de la Justice, Garde des Sceaux",
#     "Ministre de l'Intérieur et de la Sécurité publique",
#     "Ministre de l'Énergie, du Pétrole et des Mines",
#     "Ministre de l'Économie du Plan et de la Coopération",
#     "Ministre des Finances et du Budget",
#     "Ministre de l'Environnement et de la Transition écologique",
#     "Ministre de la Formation professionnelle et Porte-parole du Gouvernement",
#     "Ministre de l'Hydraulique et de l'Assainissement",
#     "Ministre de la Communication, des Télécommunications et du Numérique",
#     "Ministre de l'Enseignement supérieur, de la Recherche et de l'Innovation",
#     "Ministre de l'Industrie et du Commerce",
#     "Ministre des Pêches, des Infrastructures maritimes et portuaires",
#     "Ministre de la Famille et des Solidarités",
#     "Ministre des Infrastructures, des Transports terrestres et aériens",
#     "Ministre de l'Urbanisme, des Collectivités territoriales et de l'Aménagement des Territoires",
#     "Ministre de l'Education nationale",
#     "Ministre de la Santé et de l'Action sociale",
#     "Ministre de la Fonction publique et de la Réforme du Service public",
#     "Ministre de la Jeunesse, des Sports et de la Culture",
#     "Ministre de l'Agriculture, de la Souveraineté alimentaire et de l'Elevage",
#     "Ministre de la Microfinance, de l'Economie sociale et solidaire",
#     "Ministre du Tourisme et de l'Artisanat",
# ]

# def ministere_fuzzy(sentence, seuil=5):
#     sentence = sentence.lower()
#     # On cherche la phrase la plus proche
#     best_match = process.extract(
#         sentence, [m.lower() for m in ministeres], scorer=fuzz.token_sort_ratio
#     )
#     # if best_match and best_match[1] >= seuil:
#     #     return best_match[0]
#     # return "Non trouvé"
#     return best_match


# result = ministere_fuzzy("Ministre de l éducation nationale")
# print(result)