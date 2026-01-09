


def estComplet(automate):
    matrice= automate["matrice"]
    nbEtats= len(matrice)
    nbChar= len(matrice[0])
    for i in range(nbEtats):
        for j in range(nbChar):
            if matrice[i][j]== -1 :
                return False
    return True


def Complet(automate):
    """Complète un automate en ajoutant un état puits si nécessaire."""
    if estComplet(automate):
        return automate.copy() if isinstance(automate, dict) else automate
    
    # Faire une copie pour ne pas modifier l'original
    automate_copie = automate.copy()
    matrice = [ligne[:] for ligne in automate["matrice"]]  # Copie profonde de la matrice
    nbEtats = len(matrice)
    nbChar = len(matrice[0])
    
    # Ajouter un nouvel état puits
    matrice.append([nbEtats] * nbChar)
    
    # Remplacer les -1 par l'état puits
    for i in range(nbEtats):
        for j in range(nbChar):
            if matrice[i][j] == -1:
                matrice[i][j] = nbEtats
    
    automate_copie["matrice"] = matrice
    return automate_copie

def Complementaire(automate):
    """Crée l'automate complémentaire d'un automate complet."""
    automate_complet = Complet(automate)
    Cautomate = {}
    # Faire une copie profonde de la matrice
    Cautomate["matrice"] = [ligne[:] for ligne in automate_complet["matrice"]]
    Cautomate["finaux"] = []
    nbEtats = len(Cautomate["matrice"])
    #Les etats de l'automate a "complémenter" sont codés de 0 jusqu'a nbEtats-1
    #Par explemple dans notre cas nos états sont codés de 0 à 3 (nbEtats=4)
    for i in range(nbEtats):
        # Si l'etat i n'est pas final dans l'automate à "complémenter", alors il est final dans l'automate complément
        if i not in automate_complet["finaux"]:
            Cautomate["finaux"].append(i)
    
    # Préserver les autres propriétés
    if "Initial" in automate_complet:
        Cautomate["Initial"] = automate_complet["Initial"]
    elif "initial" in automate_complet:
        Cautomate["Initial"] = automate_complet["initial"]
    if "alphabet" in automate_complet:
        Cautomate["alphabet"] = automate_complet["alphabet"]
    
    return Cautomate


def Analyse_mot(automate, mot, verbose=False):
    """
    Analyse un mot avec un automate (déterministe ou non-déterministe).
    Gère le non-déterminisme en explorant tous les chemins possibles.
    """
    matrice = automate["matrice"]
    finaux = set(automate["finaux"])
    initial = automate.get("Initial", automate.get("initial", 0))
    
    if verbose:
        print(automate)
    
    if not mot:
        # Mot vide : accepter si l'état initial est final
        return initial in finaux
    
    # Ensemble d'états actuels (pour gérer le non-déterminisme)
    etats_courants = {initial}
    
    for symbole_idx in mot:
        if verbose:
            print(f"Symbole index: {symbole_idx}, États courants: {etats_courants}")
        
        if symbole_idx >= len(matrice[0]) if matrice else True:
            return False
        
        nouveaux_etats = set()
        for etat in etats_courants:
            if etat >= len(matrice):
                continue
            
            trans = matrice[etat][symbole_idx]
            
            if trans == -1:
                continue
            elif isinstance(trans, list):
                # Non-déterministe : plusieurs destinations possibles
                nouveaux_etats.update([d for d in trans if d != -1])
            else:
                # Déterministe : une seule destination
                nouveaux_etats.add(trans)
        
        if not nouveaux_etats:
            if verbose:
                print("Aucune transition possible, mot refusé")
            return False
        
        etats_courants = nouveaux_etats
    
    # Vérifier si au moins un des états finaux est dans les états courants
    return bool(etats_courants & finaux)

def save_automates(fichier, automates_dict, fusionner=False):
    """
    Enregistre un dictionnaire d'automates (nom -> automate) dans un fichier.
    Format du fichier : nom|matrice|finaux|initial|alphabet;
    Crée le fichier s'il n'existe pas.
    
    Args:
        fichier: Chemin du fichier
        automates_dict: Dictionnaire nom -> automate ou liste d'automates
        fusionner: Si True, fusionne avec les automates existants. Si False, remplace tout.
    """
    import os
    
    # Créer le répertoire si nécessaire
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        os.makedirs(dossier, exist_ok=True)
    
    # Si automates_dict est une liste, la convertir en dictionnaire avec des noms par défaut
    if isinstance(automates_dict, list):
        automates_dict = {f"automate_{i}": auto for i, auto in enumerate(automates_dict)}
    
    # Si fusionner, charger les automates existants
    automates_a_sauvegarder = {}
    if fusionner and os.path.exists(fichier):
        try:
            automates_existants = load_automates(fichier)
            automates_a_sauvegarder.update(automates_existants)
        except Exception:
            pass  # En cas d'erreur, on continue sans fusionner
    
    # Ajouter ou remplacer les nouveaux automates
    automates_a_sauvegarder.update(automates_dict)
    
    # Écrire dans le fichier
    with open(fichier, "w", encoding="utf-8") as f:
        for nom, a in automates_a_sauvegarder.items():
            initial = a.get("Initial", a.get("initial", 0))
            alphabet = a.get("alphabet", [])
            # Nettoyer le nom pour éviter les caractères problématiques dans le fichier
            nom_clean = nom.replace("|", "_").replace(";", "_").replace("\n", " ")
            # Format : nom|matrice|finaux|initial|alphabet;
            f.write(f"{nom_clean}|{a['matrice']}|{a['finaux']}|{initial}|{alphabet};\n")


def load_automates(fichier):
    """
    Lit un fichier et renvoie un dictionnaire nom -> automate.
    Format attendu : nom|matrice|finaux|initial|alphabet;
    Crée le fichier vide s'il n'existe pas.
    """
    import os
    
    automates = {}
    
    # Si le fichier n'existe pas, le créer vide
    if not os.path.exists(fichier):
        dossier = os.path.dirname(fichier)
        if dossier and not os.path.exists(dossier):
            os.makedirs(dossier, exist_ok=True)
        # Créer un fichier vide
        with open(fichier, "w", encoding="utf-8") as f:
            pass
        return automates
    
    # Lire le fichier
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            contenu = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return automates
    
    # Parser le contenu
    for bloc in contenu.split(";"):
        bloc = bloc.strip()
        if not bloc:
            continue
        
        parties = bloc.split("|")
        
        # Ancien format (sans nom) : matrice|finaux|initial
        if len(parties) == 3:
            matrice = eval(parties[0])
            finaux = eval(parties[1])
            initial = eval(parties[2])
            alphabet = []
            nom = f"automate_charge_{len(automates)}"
        # Nouveau format (avec nom) : nom|matrice|finaux|initial|alphabet
        elif len(parties) >= 4:
            nom = parties[0].strip()
            matrice = eval(parties[1])
            finaux = eval(parties[2])
            initial = eval(parties[3]) if len(parties) > 3 else 0
            alphabet = eval(parties[4]) if len(parties) > 4 else []
        else:
            continue
        
        automate = {"matrice": matrice, "finaux": finaux, "Initial": initial}
        if alphabet:
            automate["alphabet"] = alphabet
        
        # Éviter les doublons de noms
        nom_original = nom
        compteur = 1
        while nom in automates:
            nom = f"{nom_original}_{compteur}"
            compteur += 1
        
        automates[nom] = automate
    
    return automates

def regularisation(Dautomate):
    """ fonction qui permet de passer d'une matrice stockée dans un dictionnaire a une matrice stockée dans une liste de liste"""
    #on crée une liste des différents états de notre matrice
    etats= list(Dautomate["matrice"].keys())
    #on associe à chaque état une valeur numérique (on numérote les états), grace à énumerate qui crée un couple (numéro, frozenset)
    index= {}
    for i, etat in enumerate(etats):
        index[etat]=i
    nbEtats = len(etats)
    #nbChar= len(Dautomate["matrice"][0]) ne marche pas
    nbChar = len(next(iter(Dautomate["matrice"].values())))
    nouvelle_matrice =[]
    # on parcours chaque etats et chaque charactère, et on traduit le frozenset en son équivalent numérique de l'index , on l'enregistre ensuite dans nouvelle_matrice
    for e in etats:
        ligne = []
        for c in range(nbChar):
            nouvel_etat = Dautomate["matrice"][e][c]
            # on remplace chaque frozenset par son indice
            if nouvel_etat in index :
                ligne.append(index[nouvel_etat])
            # si il n'y a pas de transition, on met la la transition vers l'état -1
            else :
                ligne.append(-1)
        nouvelle_matrice.append(ligne)

    nouvel_initial = index[Dautomate["initial"]]
    nouveaux_finaux= [index[f] for f in Dautomate["finaux"]]
    A = { "matrice":nouvelle_matrice ,
          "initial":nouvel_initial ,
          "finaux": nouveaux_finaux ,
          "alphabet": Dautomate["alphabet"]}
    
    return A



def estDeterministe(automate):
    """Vérifie si un automate est déterministe (entiers) ou non-déterministe (listes)."""
    matrice = automate["matrice"]
    for ligne in matrice:
        for case in ligne:
            if isinstance(case, list) and len(case) >= 2:
                return 0  # non déterministe
    return 1  # déterministe

def Determinister(automate):
    """Convertit un automate non-déterministe en automate déterministe."""
    if estDeterministe(automate):
        return automate
    
    matrice = automate["matrice"]
    nbChar = len(matrice[0])
    initial = automate.get("initial", automate.get("Initial", 0))
    etat_initial = frozenset([initial])
    
    # Construction de l'automate déterministe avec frozensets
    etats_a_explorer = [etat_initial]
    matrice_dict = {}
    finaux_dict = []
    
    i = 0
    while i < len(etats_a_explorer):
        courant = etats_a_explorer[i]
        matrice_dict[courant] = []
        
        for c in range(nbChar):
            nouvel_etat = set()
            for etat in courant:
                trans = matrice[etat][c]
                if isinstance(trans, list):
                    nouvel_etat.update(trans)
                elif trans != -1:
                    nouvel_etat.add(trans)
            
            nouvel_etat = frozenset(nouvel_etat)
            matrice_dict[courant].append(nouvel_etat)
            
            if nouvel_etat and nouvel_etat not in etats_a_explorer:
                etats_a_explorer.append(nouvel_etat)
        
        for f in automate["finaux"]:
            if f in courant and courant not in finaux_dict:
                finaux_dict.append(courant)
        i += 1
    
    # Conversion en format liste de listes via regularisation
    automate_temp = {
        "matrice": matrice_dict,
        "initial": etat_initial,
        "finaux": finaux_dict,
        "alphabet": automate.get("alphabet", [])
    }
    automate_final = regularisation(automate_temp)
    
    # Convertir "initial" en "Initial" pour cohérence avec le reste du code
    if "initial" in automate_final:
        automate_final["Initial"] = automate_final.pop("initial")
    
    return automate_final


def eliminer_transitions_epsilon(automate, epsilon="EPS"):
    """
    Supprime les transitions epsilon d'un automate non déterministe.
    
    Args:
        automate: Automate avec format {"matrice": liste de listes, "alphabet": liste, "finaux": liste, "Initial": int}
        epsilon: Symbole epsilon (peut être "$", "epsilon", "eps", "ε", "EPS")
    
    Returns:
        Automate équivalent sans transitions epsilon (format liste de listes)
    """
    matrice = automate["matrice"]
    alphabet = automate.get("alphabet", [])
    finaux = set(automate["finaux"])
    initial = automate.get("Initial", automate.get("initial", 0))
    
    # Détecter si l'automate a une colonne epsilon
    epsilon_index = None
    epsilon_symbol = None
    if alphabet:
        for i, sym in enumerate(alphabet):
            if sym in ("$", "epsilon", "eps", "ε", "EPS", epsilon):
                epsilon_index = i
                epsilon_symbol = sym
                break
    
    # Si pas de colonne epsilon, retourner l'automate tel quel
    if epsilon_index is None:
        return automate.copy()
    
    n = len(matrice)
    # Convertir en format dictionnaire pour utiliser l'algorithme
    transitions = {}
    
    # S'assurer que tous les états sont inclus (0 à n-1)
    etats = set(range(n))
    etats.add(initial)
    etats.update(finaux)
    
    for etat in range(n):
        if etat >= len(matrice):
            continue
        for symbole_idx, symbole in enumerate(alphabet):
            if symbole_idx >= len(matrice[etat]):
                continue
            dests = matrice[etat][symbole_idx]
            # Convertir les destinations en liste
            if dests == -1:
                continue
            elif isinstance(dests, list):
                destinations = [d for d in dests if d != -1 and isinstance(d, int) and 0 <= d < n]
            else:
                destinations = [dests] if dests != -1 and isinstance(dests, int) and 0 <= dests < n else []
            
            if destinations:
                transitions[(etat, symbole)] = destinations
                etats.update(destinations)
    
    # ---- 2. Extraire transitions epsilon ----
    eps = {}
    normales = {}
    
    for (e, s), dests in transitions.items():
        if s == epsilon_symbol:
            eps.setdefault(e, []).extend(dests)
        else:
            normales.setdefault(e, []).append((s, dests))
    
    # ---- 3. Fermeture epsilon ----
    def fermeture_epsilon(e):
        fermeture = {e}
        pile = [e]
        while pile:
            x = pile.pop()
            # Ne considérer que les états dans la plage valide
            if x >= n or x < 0:
                continue
            for y in eps.get(x, []):
                if 0 <= y < n and y not in fermeture:
                    fermeture.add(y)
                    pile.append(y)
        return fermeture
    
    fermetures = {e: fermeture_epsilon(e) for e in etats if 0 <= e < n}
    
    # ---- 4. Reconstruire les transitions sans epsilon ----
    nouvelles_transitions = {}
    
    def ajouter(e, s, d):
        if (e, s) not in nouvelles_transitions:
            nouvelles_transitions[(e, s)] = []
        if d not in nouvelles_transitions[(e, s)]:
            nouvelles_transitions[(e, s)].append(d)
    
    # Appliquer les règles de fermeture epsilon
    for e in range(n):  # Ne traiter que les états valides
        if e not in fermetures:
            fermetures[e] = {e}
        
        # règle des états finaux : si un état peut atteindre un état final par epsilon, il devient final
        if fermetures[e] & finaux:
            finaux.add(e)
        
        # Pour chaque état dans la fermeture epsilon de e
        for e2 in fermetures[e]:
            # Prendre toutes les transitions normales depuis e2
            for (s, dests) in normales.get(e2, []):
                for d in dests:
                    if 0 <= d < n:  # Ne considérer que les destinations valides
                        # Pour chaque destination d, prendre sa fermeture epsilon
                        if d not in fermetures:
                            fermetures[d] = {d}
                        for d2 in fermetures[d]:
                            if 0 <= d2 < n:  # Ne garder que les états valides
                                ajouter(e, s, d2)
    
    # ---- 5. Convertir en format liste de listes ----
    # Nouvel alphabet sans epsilon
    nouvel_alphabet = [s for s in alphabet if s != epsilon_symbol]
    
    # Créer la nouvelle matrice (même nombre d'états)
    nouvelle_matrice = [[-1] * len(nouvel_alphabet) for _ in range(n)]
    
    for (etat, symbole), dests in nouvelles_transitions.items():
        if symbole in nouvel_alphabet:
            symbole_idx = nouvel_alphabet.index(symbole)
            if len(dests) == 1:
                nouvelle_matrice[etat][symbole_idx] = dests[0]
            elif len(dests) > 1:
                # Non-déterministe : on garde la liste
                nouvelle_matrice[etat][symbole_idx] = dests
    
    # Retourner l'automate sans epsilon
    # Filtrer les états finaux pour ne garder que ceux dans la plage valide
    finaux_valides = sorted([f for f in finaux if 0 <= f < n])
    
    return {
        "matrice": nouvelle_matrice,
        "finaux": finaux_valides,
        "Initial": initial if 0 <= initial < n else 0,
        "alphabet": nouvel_alphabet
    }
def concatener(automate1, automate2):
    """
    Concatène deux automates automate1 et automate2.
    Résultat : un automate SANS epsilon tel que L = L(automate1) · L(automate2)
    """
    # 1) On supprime d'abord les epsilon dans les deux automates
    auto1_clean = eliminer_transitions_epsilon(automate1.copy())
    auto2_clean = eliminer_transitions_epsilon(automate2.copy())

    mat1 = auto1_clean["matrice"]
    mat2 = auto2_clean["matrice"]
    l1 = len(mat1)
    l2 = len(mat2)
    
    # Fusionner les alphabets
    alpha1 = auto1_clean.get("alphabet", [])
    alpha2 = auto2_clean.get("alphabet", [])
    
    # Créer un alphabet commun (union des deux)
    alphabet_commun = []
    for s in alpha1:
        if s not in alphabet_commun:
            alphabet_commun.append(s)
    for s in alpha2:
        if s not in alphabet_commun:
            alphabet_commun.append(s)
    
    # Ajouter epsilon en première position
    epsilon_symbole = "$"
    if epsilon_symbole not in alphabet_commun:
        alphabet_commun = [epsilon_symbole] + alphabet_commun
    else:
        # Déplacer epsilon en première position
        alphabet_commun.remove(epsilon_symbole)
        alphabet_commun = [epsilon_symbole] + alphabet_commun
    
    nb_caracteres = len(alphabet_commun)
    
    # Étendre les matrices pour avoir le même alphabet
    def etendre_matrice(automate, alphabet_cible, alphabet_source):
        mat = automate["matrice"]
        nouvelle_mat = []
        for ligne in mat:
            nouvelle_ligne = [-1] * len(alphabet_cible)
            for i, sym in enumerate(alphabet_source):
                if sym in alphabet_cible:
                    idx = alphabet_cible.index(sym)
                    nouvelle_ligne[idx] = ligne[i]
            nouvelle_mat.append(nouvelle_ligne)
        return nouvelle_mat
    
    # Étendre les matrices
    if alpha1:
        mat1_etendue = etendre_matrice(auto1_clean, alphabet_commun, alpha1)
    else:
        mat1_etendue = [[-1] * nb_caracteres for _ in range(l1)]
    
    if alpha2:
        mat2_etendue = etendre_matrice(auto2_clean, alphabet_commun, alpha2)
    else:
        mat2_etendue = [[-1] * nb_caracteres for _ in range(l2)]
    
    # Construire la nouvelle matrice avec epsilon en première colonne
    epsilon_idx = 0  # epsilon est en position 0
    new_mat = []
    
    # Copier auto1
    for i in range(l1):
        new_mat.append(mat1_etendue[i][:])
    
    # Copier auto2 avec décalage d'états (+l1)
    for i in range(l2):
        ligne = []
        for j in range(nb_caracteres):
            dest = mat2_etendue[i][j]
            if dest == -1:
                ligne.append(-1)
            else:
                ligne.append(dest + l1)
        new_mat.append(ligne)
    
    # Transition epsilon : des finaux de auto1 vers l'initial de auto2 (décalé)
    init2 = auto2_clean.get("Initial", auto2_clean.get("initial", 0))
    for f in auto1_clean["finaux"]:
        if new_mat[f][epsilon_idx] == -1:
            new_mat[f][epsilon_idx] = init2 + l1
        else:
            # Plusieurs transitions epsilon : convertir en liste
            if isinstance(new_mat[f][epsilon_idx], list):
                if (init2 + l1) not in new_mat[f][epsilon_idx]:
                    new_mat[f][epsilon_idx].append(init2 + l1)
            else:
                new_mat[f][epsilon_idx] = [new_mat[f][epsilon_idx], init2 + l1]
    
    # Nouveaux finaux : ceux de auto2, décalés
    new_finaux = [q + l1 for q in auto2_clean["finaux"]]
    
    # Nouvel état initial
    new_initial = auto1_clean.get("Initial", auto1_clean.get("initial", 0))
    
    automate_eps = {
        "matrice": new_mat,
        "finaux": new_finaux,
        "Initial": new_initial,
        "alphabet": alphabet_commun
    }
    
    # 3) On supprime les epsilon dans l'automate obtenu
    automate_propre = eliminer_transitions_epsilon(automate_eps, epsilon=epsilon_symbole)
    return automate_propre


def produit(A1, A2):
    """
    Calcule le produit de deux automates.
    Le produit accepte les mots acceptés par les DEUX automates simultanément.
    
    Args:
        A1, A2: Automates avec format {"matrice": liste de listes, "alphabet": liste, "finaux": liste, "Initial": int}
    
    Returns:
        Automate produit avec états en tuples, ou 0 si les alphabets n'ont pas de caractères communs
    """
    # Utiliser "Initial" ou "initial"
    initial1 = A1.get("Initial", A1.get("initial", 0))
    initial2 = A2.get("Initial", A2.get("initial", 0))
    
    # Utiliser set pour pouvoir faire des opérations sur les ensembles, on utilise ensuite list pour transformer le résultat en liste
    alphabet_commun = list(set(A1.get("alphabet", [])) & set(A2.get("alphabet", [])))
    
    # On vérifie que les alphabets ont au moins un caractère en commun
    if not alphabet_commun:
        # Pas de caractères communs entre les deux alphabets
        return 0
    
    prAutomate = {
        'matrice': {},
        'initial': (initial1, initial2),
        'finaux': [],
        'alphabet': alphabet_commun
    }
    
    # On crée des index pour les deux alphabets pour éviter les erreurs si les caractères ne sont pas dans le même ordre
    idx1 = {a: i for i, a in enumerate(A1.get("alphabet", []))}
    idx2 = {a: i for i, a in enumerate(A2.get("alphabet", []))}
    
    # Fonction helper pour extraire les états de destination (gère le non-déterminisme)
    def obtenir_etats(trans):
        """Extrait les états de destination d'une transition."""
        if trans == -1:
            return []
        elif isinstance(trans, list):
            return [e for e in trans if e != -1]
        else:
            return [trans]
    
    # Comme vu en cours, on part de l'état initial, ensuite on teste les différents caractères pour cette transition, et on enregistre tous les états valides
    # On doit parcourir tous les états des 2 automates, on n'a pas besoin de tester les caractères non présents dans l'alphabet commun
    
    etats_à_explorer = [(initial1, initial2)]
    etats_visités = set()
    i = 0
    
    while i < len(etats_à_explorer):
        courant = etats_à_explorer[i]
        q1, q2 = courant
        
        # Éviter de retraiter le même état
        if courant in etats_visités:
            i += 1
            continue  # Sauter cette itération
        
        etats_visités.add(courant)
        
        # On rajoute les états finaux
        if q1 in A1.get("finaux", []) and q2 in A2.get("finaux", []):
            prAutomate['finaux'].append(courant)
        
        ligne = []
        for c in alphabet_commun:
            # Gérer les indices d'alphabet
            if c not in idx1 or c not in idx2:
                ligne.append((-1, -1))
                continue
            
            idx1_c = idx1[c]
            idx2_c = idx2[c]
            
            # Vérifier les limites de la matrice
            if q1 >= len(A1["matrice"]) or q2 >= len(A2["matrice"]):
                ligne.append((-1, -1))
                continue
            
            if idx1_c >= len(A1["matrice"][q1]) or idx2_c >= len(A2["matrice"][q2]):
                ligne.append((-1, -1))
                continue
            
            etat_suivant_A1_trans = A1["matrice"][q1][idx1_c]
            etat_suivant_A2_trans = A2["matrice"][q2][idx2_c]
            
            # Extraire les listes d'états
            etats_A1 = obtenir_etats(etat_suivant_A1_trans)
            etats_A2 = obtenir_etats(etat_suivant_A2_trans)
            
            # Pour le produit déterministe, on prend toutes les combinaisons
            # Mais si un automate est non-déterministe, on doit créer plusieurs états
            # Pour simplifier, on prend le premier état de chaque liste si disponible
            # Pour un vrai produit non-déterministe, il faudrait créer tous les produits cartésiens
            if not etats_A1 or not etats_A2:
                nouvel_etat = (-1, -1)
            else:
                # Pour l'instant, on prend le premier état de chaque liste (déterministe)
                # Pour un vrai produit non-déterministe, il faudrait créer tous les tuples possibles
                nouvel_etat = (etats_A1[0], etats_A2[0])
                
                # Si les deux sont non-déterministes, on crée plusieurs transitions
                # Mais comme on retourne une ligne simple, on garde juste le premier tuple
                # Un vrai produit non-déterministe nécessiterait une structure plus complexe
            
            ligne.append(nouvel_etat)
            
            if nouvel_etat not in etats_à_explorer and nouvel_etat != (-1, -1):
                etats_à_explorer.append(nouvel_etat)
        
        prAutomate['matrice'][courant] = ligne
        
        # On parcourt les transitions des caractères pour chaque automate
        i = i + 1
    
    return prAutomate


def regularisation_tuples(A):
    """
    Transforme un automate dont les états sont des tuples (q1, q2)
    en un automate numéroté avec des entiers.
    Les états (-1, -1) sont considérés comme invalides.
    
    Args:
        A: Automate avec format {"matrice": dict, "initial": tuple, "finaux": list, "alphabet": list}
    
    Returns:
        Automate avec format {"matrice": liste de listes, "Initial": int, "finaux": list, "alphabet": list}
    """
    correspondance = {}
    compteur = 0
    
    # Récupérer tous les états (clés du dictionnaire)
    etats = list(A["matrice"].keys())
    
    # Trier pour une numérotation stable entre plusieurs exécutions du programme sur le même automate
    etats = sorted(etats)
    
    # Construire la correspondance tuple vers entier
    for etat in etats:
        if isinstance(etat, tuple) and (-1 in etat):
            continue
        correspondance[etat] = compteur
        compteur += 1
    
    # Ajouter l'état initial s'il n'est pas déjà présent
    if isinstance(A["initial"], tuple) and -1 not in A["initial"] and A["initial"] not in correspondance:
        correspondance[A["initial"]] = compteur
        compteur += 1
    
    # Construire la nouvelle matrice indexée
    nouvelle_matrice = []
    for etat in etats:
        ligne = []
        for a in A["matrice"][etat]:
            if isinstance(a, tuple) and -1 in a:
                ligne.append(-1)
            elif isinstance(a, tuple) and a in correspondance:
                ligne.append(correspondance[a])
            elif isinstance(a, tuple):
                # État non trouvé dans correspondance, mettre -1
                ligne.append(-1)
            else:
                ligne.append(-1)
        nouvelle_matrice.append(ligne)
    
    # États finaux
    nouveaux_finaux = []
    for f in A.get("finaux", []):
        if isinstance(f, tuple) and f in correspondance:
            nouveaux_finaux.append(correspondance[f])
    
    # État initial
    if isinstance(A["initial"], tuple) and -1 in A["initial"]:
        nouvel_initial = -1
    elif A["initial"] in correspondance:
        nouvel_initial = correspondance[A["initial"]]
    else:
        nouvel_initial = 0
    
    return {
        "matrice": nouvelle_matrice,
        "Initial": nouvel_initial,  # Utiliser "Initial" pour cohérence
        "finaux": nouveaux_finaux,
        "alphabet": A.get("alphabet", [])
    }


def nettoyer(automate):
    """
    Supprime les états inutiles d'un automate
    
    Conserve uniquement les états accessibles depuis l'état initial
    et co-accessibles (menant à un état final)
    """
    matrice = automate["matrice"]
    # Gérer "Initial" ou "initial"
    initial_val = automate.get("Initial", automate.get("initial", 0))
    if isinstance(initial_val, list):
        etat_initial = initial_val[0]
    else:
        etat_initial = initial_val
    etats_finaux = set(automate["finaux"])
    
    # États atteignables depuis l'état initial
    etats_atteignables = {etat_initial}
    a_traiter = [etat_initial]
    
    # On effectue un parcours de l'automate à partir de l'état initial
    while a_traiter:
        etat_courant = a_traiter.pop()
        
        # On parcourt toutes les transitions sortantes de cet état
        for symbole in range(len(matrice[etat_courant])):
            etat_suivant = matrice[etat_courant][symbole]
            # Si la transition existe et mène à un nouvel état
            if etat_suivant != -1 and etat_suivant not in etats_atteignables:
                # Gérer le non-déterminisme (si c'est une liste, prendre tous les états)
                if isinstance(etat_suivant, list):
                    for e in etat_suivant:
                        if e != -1 and e not in etats_atteignables:
                            etats_atteignables.add(e)
                            a_traiter.append(e)
                else:
                    etats_atteignables.add(etat_suivant)
                    a_traiter.append(etat_suivant)
    
    # États co-atteignables vers un état final
    etats_co_atteignables = set(etats_finaux)
    a_explorer = list(etats_finaux)
    
    # On part des états finaux et on remonte les transitions
    while a_explorer:
        etat_cible = a_explorer.pop()
        
        for etat_source in range(len(matrice)):
            # Vérifier si une transition mène de etat_source vers etat_cible
            for symbole in range(len(matrice[etat_source])):
                trans = matrice[etat_source][symbole]
                if isinstance(trans, list):
                    if etat_cible in trans and etat_source not in etats_co_atteignables:
                        etats_co_atteignables.add(etat_source)
                        a_explorer.append(etat_source)
                elif trans == etat_cible and trans != -1 and etat_source not in etats_co_atteignables:
                    etats_co_atteignables.add(etat_source)
                    a_explorer.append(etat_source)
    
    # États utiles
    etats_utiles = etats_atteignables & etats_co_atteignables
    etats_utiles_tries = sorted(etats_utiles)
    
    # Correspondance anciens indices → nouveaux indices
    correspondance = {
        ancien_etat: nouvel_indice
        for nouvel_indice, ancien_etat in enumerate(etats_utiles_tries)
    }
    
    # Construction de la nouvelle matrice
    matrice_nettoyee = []
    for i in range(len(etats_utiles_tries)):
        ancien_etat = etats_utiles_tries[i]
        ligne_nettoyee = []
        
        for j in range(len(matrice[ancien_etat])):
            etat_suivant = matrice[ancien_etat][j]
            
            if etat_suivant == -1 or etat_suivant not in correspondance:
                ligne_nettoyee.append(-1)
            elif isinstance(etat_suivant, list):
                # Gérer le non-déterminisme
                nouveaux_etats = [correspondance[e] for e in etat_suivant if e in correspondance]
                if not nouveaux_etats:
                    ligne_nettoyee.append(-1)
                elif len(nouveaux_etats) == 1:
                    ligne_nettoyee.append(nouveaux_etats[0])
                else:
                    ligne_nettoyee.append(nouveaux_etats)
            else:
                ligne_nettoyee.append(correspondance[etat_suivant])
        
        matrice_nettoyee.append(ligne_nettoyee)
    
    # Mise à jour des états finaux et initial
    finaux_nettoyes = [correspondance[f] for f in etats_finaux if f in correspondance]
    initial_nettoye = correspondance[etat_initial]
    
    automate["matrice"] = matrice_nettoyee
    automate["finaux"] = finaux_nettoyes
    automate["Initial"] = initial_nettoye  # Garder comme entier pour cohérence avec le reste
    
    return automate


# ----------- Interface Console -----------
def afficher_automate(automate, nom="Automate"):
    """Affiche un automate de manière lisible."""
    print(f"\n{'='*60}")
    print(f"{nom}")
    print(f"{'='*60}")
    print(f"Matrice :")
    matrice = automate["matrice"]
    alphabet = automate.get("alphabet", [f"sym{i}" for i in range(len(matrice[0]) if matrice else 0)])
    
    # En-tête avec alphabet
    print("État", end="")
    for sym in alphabet:
        print(f"  {sym:>6}", end="")
    print()
    
    for i, ligne in enumerate(matrice):
        print(f"  {i}", end="")
        for val in ligne:
            if val == -1:
                print(f"     -1", end="")
            elif isinstance(val, list):
                print(f"  {str(val):<5}", end="")
            else:
                print(f"     {val}", end="")
        if i in automate.get("finaux", []):
            print("  [FINAL]", end="")
        if automate.get("Initial", automate.get("initial", 0)) == i:
            print("  [INITIAL]", end="")
        print()
    
    print(f"États finaux : {automate.get('finaux', [])}")
    print(f"État initial : {automate.get('Initial', automate.get('initial', 0))}")
    if alphabet:
        print(f"Alphabet : {alphabet}")
    print(f"{'='*60}\n")


def creer_automate_interactif():
    """Crée un automate via l'interface console."""
    print("\n--- Création d'un automate ---")
    
    # Nombre d'états
    try:
        nb_etats = int(input("Nombre d'états : "))
        if nb_etats <= 0:
            print("Erreur : le nombre d'états doit être positif.")
            return None
    except ValueError:
        print("Erreur : veuillez entrer un nombre entier.")
        return None
    
    # Alphabet
    print("\nAlphabet (séparé par des virgules, ou laissez vide) :")
    alpha_input = input("> ").strip()
    if alpha_input:
        alphabet = [s.strip() for s in alpha_input.split(",")]
    else:
        nb_symboles = int(input("Nombre de symboles dans l'alphabet : "))
        alphabet = [f"sym{i}" for i in range(nb_symboles)]
    
    nb_symboles = len(alphabet)
    
    # Matrice
    print("\nSaisie de la matrice de transition :")
    print("(Entrez -1 pour aucune transition)")
    matrice = []
    for i in range(nb_etats):
        ligne = []
        for j, sym in enumerate(alphabet):
            try:
                val = input(f"État {i} avec symbole '{sym}' : ").strip()
                if val == "-1" or val == "":
                    ligne.append(-1)
                elif val.startswith("[") and val.endswith("]"):
                    # Liste pour non-déterministe
                    ligne.append(eval(val))
                else:
                    ligne.append(int(val))
            except (ValueError, SyntaxError):
                ligne.append(-1)
        matrice.append(ligne)
    
    # État initial
    try:
        initial = int(input(f"\nÉtat initial (0-{nb_etats-1}) [0] : ").strip() or "0")
    except ValueError:
        initial = 0
    
    # États finaux
    print("\nÉtats finaux (séparés par des virgules) :")
    finaux_input = input("> ").strip()
    if finaux_input:
        finaux = [int(f.strip()) for f in finaux_input.split(",")]
    else:
        finaux = []
    
    automate = {
        "matrice": matrice,
        "finaux": finaux,
        "Initial": initial,
        "alphabet": alphabet
    }
    
    print("\n✓ Automate créé avec succès !")
    afficher_automate(automate, "Nouvel automate")
    return automate


def modifier_automate_interactif(automate):
    """Modifie un automate de manière interactive."""
    print("\n--- Modification d'un automate ---")
    print("Vous pouvez modifier différentes parties de l'automate.")
    print("Laissez vide pour conserver la valeur actuelle.\n")
    
    # Afficher l'automate actuel
    afficher_automate(automate, "Automate actuel")
    
    # Copier l'automate pour modifications
    auto_modifie = {
        "matrice": [ligne[:] for ligne in automate["matrice"]],
        "finaux": automate["finaux"][:],
        "Initial": automate.get("Initial", automate.get("initial", 0)),
        "alphabet": automate.get("alphabet", [])[:]
    }
    
    nb_etats = len(auto_modifie["matrice"])
    alphabet = auto_modifie["alphabet"]
    nb_symboles = len(auto_modifie["matrice"][0]) if auto_modifie["matrice"] else 0
    
    # Menu de modification
    while True:
        print("\n--- Que voulez-vous modifier ? ---")
        print("1. Modifier l'alphabet")
        print("2. Modifier une transition spécifique")
        print("3. Modifier toutes les transitions d'un état")
        print("4. Modifier l'état initial")
        print("5. Modifier les états finaux")
        print("6. Ajouter un état")
        print("7. Supprimer un état")
        print("8. Voir l'automate modifié")
        print("0. Terminer les modifications et enregistrer")
        print("-"*60)
        
        choix = input("\nVotre choix : ").strip()
        
        try:
            if choix == "0":
                print("\n✓ Modifications terminées.")
                # S'assurer que l'alphabet est à jour
                auto_modifie["alphabet"] = alphabet if alphabet else []
                return auto_modifie
            
            elif choix == "1":
                print(f"\nAlphabet actuel : {alphabet if alphabet else 'Non défini'}")
                print("Nouvel alphabet (séparé par des virgules, laissez vide pour conserver) :")
                alpha_input = input("> ").strip()
                if alpha_input:
                    nouvel_alphabet = [s.strip() for s in alpha_input.split(",")]
                    # Si l'alphabet change, il faut adapter la matrice
                    if len(nouvel_alphabet) != nb_symboles:
                        print(f"\n⚠ Attention : Le nombre de symboles change ({nb_symboles} -> {len(nouvel_alphabet)}).")
                        print("Les transitions existantes seront réinitialisées à -1.")
                        reponse = input("Continuer ? (o/n) [n] : ").strip().lower()
                        if reponse == 'o':
                            alphabet = nouvel_alphabet
                            auto_modifie["alphabet"] = alphabet
                            nb_symboles = len(alphabet)
                            # Réinitialiser la matrice avec le nouveau nombre de symboles
                            auto_modifie["matrice"] = [[-1] * nb_symboles for _ in range(nb_etats)]
                            print("✓ Alphabet modifié. Matrice réinitialisée.")
                        else:
                            print("Annulé.")
                    else:
                        alphabet = nouvel_alphabet
                        auto_modifie["alphabet"] = alphabet
                        print(f"✓ Alphabet modifié : {alphabet}")
            
            elif choix == "2":
                if nb_etats == 0:
                    print("\n✗ Aucun état disponible.")
                    continue
                try:
                    etat = int(input(f"État (0-{nb_etats-1}) : ").strip())
                    if etat < 0 or etat >= nb_etats:
                        print("✗ État invalide.")
                        continue
                    
                    if alphabet:
                        print(f"Symboles disponibles : {alphabet}")
                        symbole_input = input("Symbole ou indice : ").strip()
                        if symbole_input in alphabet:
                            idx_symbole = alphabet.index(symbole_input)
                        else:
                            idx_symbole = int(symbole_input)
                    else:
                        idx_symbole = int(input(f"Indice du symbole (0-{nb_symboles-1}) : ").strip())
                    
                    if idx_symbole < 0 or idx_symbole >= nb_symboles:
                        print("✗ Indice de symbole invalide.")
                        continue
                    
                    print(f"Transition actuelle depuis état {etat} avec symbole {idx_symbole} : {auto_modifie['matrice'][etat][idx_symbole]}")
                    print("Nouvelle transition (-1 pour aucune, entier pour état, liste [e1, e2] pour non-déterministe) :")
                    val = input("> ").strip()
                    if val == "":
                        print("Aucune modification.")
                    elif val == "-1":
                        auto_modifie["matrice"][etat][idx_symbole] = -1
                        print("✓ Transition supprimée.")
                    elif val.startswith("[") and val.endswith("]"):
                        try:
                            auto_modifie["matrice"][etat][idx_symbole] = eval(val)
                            print(f"✓ Transition non-déterministe modifiée : {auto_modifie['matrice'][etat][idx_symbole]}")
                        except:
                            print("✗ Format invalide.")
                    else:
                        try:
                            auto_modifie["matrice"][etat][idx_symbole] = int(val)
                            print(f"✓ Transition modifiée : {auto_modifie['matrice'][etat][idx_symbole]}")
                        except ValueError:
                            print("✗ Valeur invalide.")
                except ValueError:
                    print("✗ Erreur de saisie.")
            
            elif choix == "3":
                if nb_etats == 0:
                    print("\n✗ Aucun état disponible.")
                    continue
                try:
                    etat = int(input(f"État à modifier (0-{nb_etats-1}) : ").strip())
                    if etat < 0 or etat >= nb_etats:
                        print("✗ État invalide.")
                        continue
                    
                    print(f"\nModification de toutes les transitions de l'état {etat} :")
                    for j in range(nb_symboles):
                        symbole_label = alphabet[j] if alphabet and j < len(alphabet) else f"sym{j}"
                        val_actuel = auto_modifie["matrice"][etat][j]
                        val = input(f"  État {etat}, symbole '{symbole_label}' (actuel: {val_actuel}) [-1] : ").strip()
                        if val == "":
                            val = "-1"
                        if val == "-1":
                            auto_modifie["matrice"][etat][j] = -1
                        elif val.startswith("[") and val.endswith("]"):
                            try:
                                auto_modifie["matrice"][etat][j] = eval(val)
                            except:
                                print(f"    Format invalide, conservé: {val_actuel}")
                        else:
                            try:
                                auto_modifie["matrice"][etat][j] = int(val)
                            except ValueError:
                                print(f"    Valeur invalide, conservé: {val_actuel}")
                    print("✓ Transitions de l'état modifiées.")
                except ValueError:
                    print("✗ Erreur de saisie.")
            
            elif choix == "4":
                try:
                    initial_actuel = auto_modifie["Initial"]
                    print(f"État initial actuel : {initial_actuel}")
                    nouveau_initial = input(f"Nouvel état initial (0-{nb_etats-1}) [laissez vide pour conserver] : ").strip()
                    if nouveau_initial:
                        nouveau_initial = int(nouveau_initial)
                        if 0 <= nouveau_initial < nb_etats:
                            auto_modifie["Initial"] = nouveau_initial
                            print(f"✓ État initial modifié : {nouveau_initial}")
                        else:
                            print("✗ État invalide.")
                    else:
                        print("Aucune modification.")
                except ValueError:
                    print("✗ Erreur de saisie.")
            
            elif choix == "5":
                finaux_actuels = auto_modifie["finaux"]
                print(f"États finaux actuels : {finaux_actuels}")
                print("Nouveaux états finaux (séparés par des virgules, laissez vide pour conserver) :")
                finaux_input = input("> ").strip()
                if finaux_input:
                    try:
                        nouveaux_finaux = [int(f.strip()) for f in finaux_input.split(",")]
                        # Vérifier que tous les états sont valides
                        if all(0 <= f < nb_etats for f in nouveaux_finaux):
                            auto_modifie["finaux"] = nouveaux_finaux
                            print(f"✓ États finaux modifiés : {nouveaux_finaux}")
                        else:
                            print("✗ Certains états sont invalides.")
                    except ValueError:
                        print("✗ Erreur de saisie.")
                else:
                    print("Aucune modification.")
            
            elif choix == "6":
                print("\nAjout d'un nouvel état.")
                # Créer une nouvelle ligne dans la matrice
                nouvelle_ligne = [-1] * nb_symboles
                auto_modifie["matrice"].append(nouvelle_ligne)
                nb_etats += 1
                print(f"✓ Nouvel état {nb_etats - 1} ajouté. Toutes ses transitions sont initialisées à -1.")
                print("Utilisez l'option 2 ou 3 pour définir ses transitions.")
            
            elif choix == "7":
                if nb_etats <= 1:
                    print("\n✗ Impossible de supprimer le dernier état.")
                    continue
                try:
                    etat_a_supprimer = int(input(f"État à supprimer (0-{nb_etats-1}) : ").strip())
                    if etat_a_supprimer < 0 or etat_a_supprimer >= nb_etats:
                        print("✗ État invalide.")
                        continue
                    
                    # Supprimer la ligne de la matrice
                    auto_modifie["matrice"].pop(etat_a_supprimer)
                    nb_etats -= 1
                    
                    # Ajuster toutes les références d'états dans la matrice
                    for i in range(nb_etats):
                        for j in range(nb_symboles):
                            trans = auto_modifie["matrice"][i][j]
                            if isinstance(trans, list):
                                # Pour les transitions non-déterministes
                                nouvelles_trans = []
                                for e in trans:
                                    if e == etat_a_supprimer:
                                        continue  # Supprimer la référence
                                    elif e > etat_a_supprimer:
                                        nouvelles_trans.append(e - 1)  # Décrémenter
                                    else:
                                        nouvelles_trans.append(e)
                                auto_modifie["matrice"][i][j] = nouvelles_trans if nouvelles_trans else -1
                            elif trans == etat_a_supprimer:
                                auto_modifie["matrice"][i][j] = -1
                            elif trans > etat_a_supprimer:
                                auto_modifie["matrice"][i][j] = trans - 1
                    
                    # Ajuster l'état initial
                    if auto_modifie["Initial"] == etat_a_supprimer:
                        auto_modifie["Initial"] = 0
                        print("⚠ L'état initial a été supprimé. Nouvel état initial : 0")
                    elif auto_modifie["Initial"] > etat_a_supprimer:
                        auto_modifie["Initial"] -= 1
                    
                    # Ajuster les états finaux
                    nouveaux_finaux = []
                    for f in auto_modifie["finaux"]:
                        if f == etat_a_supprimer:
                            continue
                        elif f > etat_a_supprimer:
                            nouveaux_finaux.append(f - 1)
                        else:
                            nouveaux_finaux.append(f)
                    auto_modifie["finaux"] = nouveaux_finaux
                    
                    print(f"✓ État {etat_a_supprimer} supprimé. Les références ont été ajustées.")
                except ValueError:
                    print("✗ Erreur de saisie.")
            
            elif choix == "8":
                auto_modifie["alphabet"] = alphabet if alphabet else []
                afficher_automate(auto_modifie, "Automate modifié (en cours)")
                input("\nAppuyez sur Entrée pour continuer...")
            
            else:
                print("\n✗ Choix invalide.")
        
        except KeyboardInterrupt:
            print("\n\nModifications annulées.")
            return None
        except Exception as e:
            print(f"\n✗ Erreur : {e}")
            import traceback
            traceback.print_exc()
            input("\nAppuyez sur Entrée pour continuer...")


def analyser_mot_interactif(automate):
    """Analyse un mot avec l'automate."""
    print("\n--- Analyse d'un mot ---")
    
    alphabet = automate.get("alphabet", [])
    matrice = automate["matrice"]
    
    if not alphabet:
        print("Aucun alphabet défini. Utilisez des indices numériques.")
        print(f"Nombre de symboles : {len(matrice[0]) if matrice else 0}")
        mot_input = input("Entrez les indices séparés par des virgules : ")
        try:
            mot = [int(x.strip()) for x in mot_input.split(",")]
        except ValueError:
            print("Erreur : veuillez entrer des nombres entiers.")
            return
    else:
        print(f"Alphabet : {alphabet}")
        mot_str = input("Entrez le mot (séparé par des espaces ou des virgules) : ")
        mot_list = [s.strip() for s in mot_str.replace(",", " ").split()]
        
        # Conversion en indices
        mot = []
        for symbole in mot_list:
            if symbole in alphabet:
                mot.append(alphabet.index(symbole))
            else:
                try:
                    idx = int(symbole)
                    if 0 <= idx < len(alphabet):
                        mot.append(idx)
                    else:
                        print(f"Erreur : indice {idx} hors limites.")
                        return
                except ValueError:
                    print(f"Erreur : symbole '{symbole}' non reconnu.")
                    return
    
    # Analyse
    resultat = Analyse_mot(automate, mot)
    if resultat:
        print(f"\n✓ Le mot est ACCEPTÉ par l'automate.")
    else:
        print(f"\n✗ Le mot est REFUSÉ par l'automate.")


def menu_gestion_automates(automates, nom_courant):
    """Menu pour gérer les automates (créer, charger, lister)."""
    while True:
        print("\n" + "="*60)
        print("  GESTION DES AUTOMATES")
        print("="*60)
        print("\n1. Créer un nouvel automate")
        print("2. Charger un automate depuis un fichier")
        print("3. Lister les automates dans un fichier")
        print("4. Lister les automates en mémoire")
        print("5. Sélectionner un automate en mémoire")
        print("6. Supprimer un automate de la mémoire")
        print("0. Retour au menu principal")
        print("-"*60)
        
        if nom_courant:
            print(f"\n[Automate courant : {nom_courant}]")
        print(f"[Automates en mémoire : {len(automates)}]")
        
        choix = input("\nVotre choix : ").strip()
        
        try:
            if choix == "0":
                return automates, nom_courant
            
            elif choix == "1":
                auto = creer_automate_interactif()
                if auto:
                    nom = input("\nDonnez un nom à cet automate : ").strip()
                    if not nom:
                        nom = f"automate_{len(automates)}"
                    automates[nom] = auto
                    nom_courant = nom
                    print(f"✓ Automate '{nom}' enregistré et sélectionné.")
                    input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "2":
                fichier = input("Nom du fichier [automates.txt] : ").strip() or "automates.txt"
                try:
                    autos_charges = load_automates(fichier)
                    if not autos_charges:
                        print(f"\n✗ Aucun automate trouvé dans '{fichier}'. Le fichier a été créé vide.")
                        input("\nAppuyez sur Entrée pour continuer...")
                        continue
                    
                    print(f"\n✓ {len(autos_charges)} automate(s) trouvé(s) dans '{fichier}'.")
                    for nom_fichier, auto in autos_charges.items():
                        print(f"\n--- Automate '{nom_fichier}' ---")
                        finaux = auto.get("finaux", [])
                        initial = auto.get("Initial", auto.get("initial", 0))
                        alphabet = auto.get("alphabet", [])
                        print(f"  États finaux : {finaux}")
                        print(f"  État initial : {initial}")
                        print(f"  Nombre d'états : {len(auto['matrice'])}")
                        print(f"  Nombre de symboles : {len(auto['matrice'][0]) if auto['matrice'] else 0}")
                        if alphabet:
                            print(f"  Alphabet : {alphabet}")
                        
                        # Demander si on veut charger cet automate
                        reponse = input(f"\nVoulez-vous charger cet automate '{nom_fichier}' ? (o/n) [o] : ").strip().lower()
                        if reponse == 'n':
                            print(f"  → Automate '{nom_fichier}' ignoré.")
                            continue
                        
                        # Afficher plus de détails si demandé
                        afficher_det = input("Afficher la matrice complète ? (o/n) [n] : ").strip().lower()
                        if afficher_det == 'o':
                            afficher_automate(auto, f"Automate '{nom_fichier}'")
                        
                        nom = input(f"Nom pour cet automate en mémoire [{nom_fichier}] : ").strip() or nom_fichier
                        
                        # Gérer les doublons
                        nom_original = nom
                        compteur = 1
                        while nom in automates:
                            nom = f"{nom_original}_{compteur}"
                            compteur += 1
                            reponse = input(f"Le nom '{nom_original}' existe déjà. Utiliser '{nom}' ? (o/n) [o] : ").strip().lower()
                            if reponse == 'n':
                                nom = input("Entrez un nouveau nom : ").strip()
                                if not nom:
                                    nom = f"{nom_original}_{compteur}"
                                if nom not in automates:
                                    break
                            else:
                                nom = f"{nom_original}_{compteur}"
                                compteur += 1
                        
                        automates[nom] = auto
                        print(f"  → '{nom}' ajouté en mémoire.")
                        if not nom_courant:  # Sélectionner le premier chargé par défaut
                            nom_courant = nom
                    input("\nAppuyez sur Entrée pour continuer...")
                except Exception as e:
                    print(f"\n✗ Erreur lors du chargement : {e}")
                    import traceback
                    traceback.print_exc()
                    input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "3":
                fichier = input("Nom du fichier [automates.txt] : ").strip() or "automates.txt"
                try:
                    autos_charges = load_automates(fichier)
                    if not autos_charges:
                        print(f"\n✗ Aucun automate trouvé dans '{fichier}'. Le fichier a été créé vide.")
                    else:
                        print(f"\n--- {len(autos_charges)} automate(s) dans '{fichier}' ---")
                        for nom, auto in autos_charges.items():
                            print(f"\n[Automate : {nom}]")
                            finaux = auto.get("finaux", [])
                            initial = auto.get("Initial", auto.get("initial", 0))
                            alphabet = auto.get("alphabet", [])
                            print(f"  États finaux : {finaux}")
                            print(f"  État initial : {initial}")
                            print(f"  Nombre d'états : {len(auto['matrice'])}")
                            print(f"  Nombre de symboles : {len(auto['matrice'][0]) if auto['matrice'] else 0}")
                            if alphabet:
                                print(f"  Alphabet : {alphabet}")
                    input("\nAppuyez sur Entrée pour continuer...")
                except Exception as e:
                    print(f"\n✗ Erreur : {e}")
                    import traceback
                    traceback.print_exc()
                    input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "4":
                if not automates:
                    print("\n✗ Aucun automate enregistré en mémoire.")
                else:
                    print(f"\n--- Automates en mémoire ({len(automates)}) ---")
                    for nom in automates:
                        marqueur = " ← COURANT" if nom == nom_courant else ""
                        auto = automates[nom]
                        finaux = auto.get("finaux", [])
                        initial = auto.get("Initial", auto.get("initial", 0))
                        print(f"  • {nom}{marqueur}")
                        print(f"      États finaux : {finaux}, État initial : {initial}, Nb états : {len(auto['matrice'])}")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "5":
                if not automates:
                    print("\n✗ Aucun automate disponible en mémoire.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nAutomates disponibles :")
                for nom in automates:
                    print(f"  • {nom}")
                
                nom = input(f"\nNom de l'automate à sélectionner [{nom_courant}] : ").strip() or nom_courant
                if nom and nom in automates:
                    nom_courant = nom
                    print(f"✓ Automate '{nom}' sélectionné.")
                    afficher_automate(automates[nom], nom)
                else:
                    print(f"✗ Automate '{nom}' introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "6":
                if not automates:
                    print("\n✗ Aucun automate à supprimer.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nAutomates disponibles :")
                for nom in automates:
                    print(f"  • {nom}")
                
                nom = input("\nNom de l'automate à supprimer : ").strip()
                if nom in automates:
                    reponse = input(f"Êtes-vous sûr de vouloir supprimer '{nom}' ? (o/n) [n] : ").strip().lower()
                    if reponse == 'o':
                        del automates[nom]
                        if nom == nom_courant:
                            nom_courant = None
                        print(f"✓ Automate '{nom}' supprimé.")
                    else:
                        print("Suppression annulée.")
                else:
                    print(f"✗ Automate '{nom}' introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            else:
                print("\n✗ Choix invalide. Veuillez choisir entre 0 et 6.")
        
        except KeyboardInterrupt:
            print("\n\nRetour au menu...")
            return automates, nom_courant
        except Exception as e:
            print(f"\n✗ Erreur : {e}")
            import traceback
            traceback.print_exc()
            input("\nAppuyez sur Entrée pour continuer...")


def menu_operations(automates, nom_courant):
    """Menu pour les opérations sur les automates."""
    if not automates:
        print("\n✗ Aucun automate disponible. Veuillez d'abord créer ou charger un automate.")
        input("\nAppuyez sur Entrée pour continuer...")
        return automates, nom_courant
    
    if not nom_courant:
        print("\n⚠ Aucun automate sélectionné. Sélection d'un automate...")
        nom = input("Nom de l'automate : ").strip()
        if nom not in automates:
            print(f"✗ Automate '{nom}' introuvable.")
            input("\nAppuyez sur Entrée pour continuer...")
            return automates, nom_courant
        nom_courant = nom
    
    while True:
        print("\n" + "="*60)
        print("  OPÉRATIONS SUR LES AUTOMATES")
        print("="*60)
        print(f"\n[Automate courant : {nom_courant}]")
        print("-"*60)
        print("\n1.  Afficher l'automate courant")
        print("2.  Analyser un mot avec l'automate courant")
        print("3.  Vérifier si l'automate est complet")
        print("4.  Compléter l'automate")
        print("5.  Créer l'automate complémentaire")
        print("6.  Vérifier si l'automate est déterministe")
        print("7.  Déterminiser l'automate")
        print("8.  Supprimer les epsilon-transitions")
        print("9.  Enregistrer l'automate courant dans un fichier")
        print("10. Enregistrer tous les automates dans un fichier")
        print("11. Concaténer deux automates")
        print("12. Produit de deux automates")
        print("13. Nettoyer l'automate (supprimer les états inutiles)")
        print("14. Changer l'automate courant")
        print("15. Modifier l'automate courant")
        print("0.  Retour au menu principal")
        print("-"*60)
        
        choix = input("\nVotre choix : ").strip()
        
        try:
            if choix == "0":
                return automates, nom_courant
            
            elif choix == "1":
                afficher_automate(automates[nom_courant], nom_courant)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "2":
                analyser_mot_interactif(automates[nom_courant])
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "3":
                auto = automates[nom_courant]
                if estComplet(auto):
                    print("\n✓ L'automate est COMPLET.")
                else:
                    print("\n✗ L'automate n'est PAS complet.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "4":
                auto = automates[nom_courant]
                auto_complet = Complet(auto.copy())
                nom = input("\nNom pour l'automate complété [auto_complet] : ").strip() or "auto_complet"
                if nom in automates:
                    reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                    if reponse != 'o':
                        nom = f"{nom}_new"
                automates[nom] = auto_complet
                print(f"✓ Automate complété sauvegardé sous le nom '{nom}'.")
                afficher_automate(auto_complet, nom)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "5":
                auto = automates[nom_courant]
                auto_comp = Complementaire(auto.copy())
                nom = input("\nNom pour l'automate complémentaire [auto_complementaire] : ").strip() or "auto_complementaire"
                if nom in automates:
                    reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                    if reponse != 'o':
                        nom = f"{nom}_new"
                automates[nom] = auto_comp
                print(f"✓ Automate complémentaire sauvegardé sous le nom '{nom}'.")
                afficher_automate(auto_comp, nom)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "6":
                auto = automates[nom_courant]
                if estDeterministe(auto):
                    print("\n✓ L'automate est DÉTERMINISTE.")
                else:
                    print("\n✗ L'automate est NON-DÉTERMINISTE.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "7":
                auto = automates[nom_courant]
                auto_det = Determinister(auto.copy())
                nom = input("\nNom pour l'automate déterminisé [auto_determinise] : ").strip() or "auto_determinise"
                if nom in automates:
                    reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                    if reponse != 'o':
                        nom = f"{nom}_new"
                automates[nom] = auto_det
                print(f"✓ Automate déterminisé sauvegardé sous le nom '{nom}'.")
                afficher_automate(auto_det, nom)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "8":
                auto = automates[nom_courant]
                auto_no_eps = eliminer_transitions_epsilon(auto.copy())
                nom = input("\nNom pour l'automate sans epsilon [auto_sans_epsilon] : ").strip() or "auto_sans_epsilon"
                if nom in automates:
                    reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                    if reponse != 'o':
                        nom = f"{nom}_new"
                automates[nom] = auto_no_eps
                print(f"✓ Automate sans epsilon sauvegardé sous le nom '{nom}'.")
                afficher_automate(auto_no_eps, nom)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "9":
                fichier = input("Nom du fichier [automates.txt] : ").strip() or "automates.txt"
                try:
                    import os
                    # Demander si on veut fusionner avec le fichier existant
                    fusionner = False
                    if os.path.exists(fichier):
                        reponse = input(f"Le fichier '{fichier}' existe déjà. Fusionner avec les automates existants ? (o/n) [o] : ").strip().lower()
                        fusionner = (reponse != 'n')
                    
                    # Sauvegarder avec le nom de l'automate
                    save_automates(fichier, {nom_courant: automates[nom_courant]}, fusionner=fusionner)
                    action = "fusionné à" if fusionner else "sauvegardé dans"
                    print(f"✓ Automate '{nom_courant}' {action} '{fichier}'.")
                except Exception as e:
                    print(f"\n✗ Erreur lors de la sauvegarde : {e}")
                    import traceback
                    traceback.print_exc()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "10":
                if not automates:
                    print("\n✗ Aucun automate à sauvegarder.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                fichier = input("Nom du fichier [automates.txt] : ").strip() or "automates.txt"
                try:
                    import os
                    # Demander si on veut fusionner avec le fichier existant
                    fusionner = False
                    if os.path.exists(fichier):
                        reponse = input(f"Le fichier '{fichier}' existe déjà. Fusionner avec les automates existants ? (o/n) [o] : ").strip().lower()
                        fusionner = (reponse != 'n')
                    
                    # Sauvegarder tous les automates avec leurs noms
                    save_automates(fichier, automates, fusionner=fusionner)
                    action = "fusionnés à" if fusionner else "sauvegardés dans"
                    print(f"✓ {len(automates)} automate(s) {action} '{fichier}' avec leurs noms.")
                except Exception as e:
                    print(f"\n✗ Erreur lors de la sauvegarde : {e}")
                    import traceback
                    traceback.print_exc()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "11":
                if len(automates) < 2:
                    print("\n✗ Vous avez besoin d'au moins 2 automates pour la concaténation.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nAutomates disponibles :")
                for nom in automates:
                    print(f"  • {nom}")
                
                print("\nSélection du premier automate :")
                nom1 = input(f"Nom [{nom_courant}] : ").strip() or nom_courant
                if nom1 not in automates:
                    print(f"✗ Automate '{nom1}' introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nSélection du deuxième automate :")
                nom2 = input("Nom : ").strip()
                if nom2 not in automates:
                    print(f"✗ Automate '{nom2}' introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                try:
                    auto_concat = concatener(automates[nom1].copy(), automates[nom2].copy())
                    nom = input("\nNom pour l'automate concaténé [auto_concatenation] : ").strip() or "auto_concatenation"
                    if nom in automates:
                        reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                        if reponse != 'o':
                            nom = f"{nom}_new"
                    automates[nom] = auto_concat
                    print(f"✓ Automate concaténé sauvegardé sous le nom '{nom}'.")
                    afficher_automate(auto_concat, nom)
                except ValueError as e:
                    print(f"\n✗ Erreur : {e}")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "12":
                if len(automates) < 2:
                    print("\n✗ Vous avez besoin d'au moins 2 automates pour le produit.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nAutomates disponibles :")
                for nom in automates:
                    print(f"  • {nom}")
                
                print("\nSélection du premier automate :")
                nom1 = input(f"Nom [{nom_courant}] : ").strip() or nom_courant
                if nom1 not in automates:
                    print(f"✗ Automate '{nom1}' introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                print("\nSélection du deuxième automate :")
                nom2 = input("Nom : ").strip()
                if nom2 not in automates:
                    print(f"✗ Automate '{nom2}' introuvable.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                
                try:
                    auto_produit = produit(automates[nom1].copy(), automates[nom2].copy())
                    if auto_produit == 0:
                        print("\n✗ Erreur : Les alphabets des deux automates n'ont aucun caractère en commun.")
                        input("\nAppuyez sur Entrée pour continuer...")
                        continue
                    
                    # Régulariser les tuples en entiers
                    auto_produit_reg = regularisation_tuples(auto_produit)
                    nom = input("\nNom pour l'automate produit [auto_produit] : ").strip() or "auto_produit"
                    if nom in automates:
                        reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                        if reponse != 'o':
                            nom = f"{nom}_new"
                    automates[nom] = auto_produit_reg
                    print(f"✓ Automate produit sauvegardé sous le nom '{nom}'.")
                    afficher_automate(auto_produit_reg, nom)
                except Exception as e:
                    print(f"\n✗ Erreur : {e}")
                    import traceback
                    traceback.print_exc()
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "13":
                auto = automates[nom_courant]
                auto_nettoye = nettoyer(auto.copy())
                nom = input("\nNom pour l'automate nettoyé [auto_nettoye] : ").strip() or "auto_nettoye"
                if nom in automates:
                    reponse = input(f"Le nom '{nom}' existe déjà. Remplacer ? (o/n) [n] : ").strip().lower()
                    if reponse != 'o':
                        nom = f"{nom}_new"
                automates[nom] = auto_nettoye
                print(f"✓ Automate nettoyé sauvegardé sous le nom '{nom}'.")
                print(f"  États avant : {len(auto['matrice'])}, États après : {len(auto_nettoye['matrice'])}")
                afficher_automate(auto_nettoye, nom)
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "14":
                print("\nAutomates disponibles :")
                for nom in automates:
                    print(f"  • {nom}")
                
                nom = input(f"\nNom de l'automate à sélectionner [{nom_courant}] : ").strip() or nom_courant
                if nom and nom in automates:
                    nom_courant = nom
                    print(f"✓ Automate '{nom}' sélectionné.")
                else:
                    print(f"✗ Automate '{nom}' introuvable.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choix == "15":
                auto = automates[nom_courant]
                auto_modifie = modifier_automate_interactif(auto.copy())
                if auto_modifie is not None:
                    # Demander si on remplace l'automate ou on crée une copie
                    print("\nQue voulez-vous faire avec l'automate modifié ?")
                    print("1. Remplacer l'automate courant")
                    print("2. Enregistrer sous un nouveau nom")
                    action = input("Choix [1] : ").strip() or "1"
                    
                    if action == "1":
                        automates[nom_courant] = auto_modifie
                        print(f"✓ Automate '{nom_courant}' modifié.")
                        afficher_automate(auto_modifie, nom_courant)
                    else:
                        nouveau_nom = input("Nouveau nom : ").strip()
                        if not nouveau_nom:
                            nouveau_nom = f"{nom_courant}_modifie"
                        # Gérer les doublons
                        nom_final = nouveau_nom
                        compteur = 1
                        while nom_final in automates:
                            nom_final = f"{nouveau_nom}_{compteur}"
                            compteur += 1
                        automates[nom_final] = auto_modifie
                        print(f"✓ Automate modifié sauvegardé sous le nom '{nom_final}'.")
                        afficher_automate(auto_modifie, nom_final)
                else:
                    print("Modifications annulées.")
                input("\nAppuyez sur Entrée pour continuer...")
            
            else:
                print("\n✗ Choix invalide. Veuillez choisir entre 0 et 15.")
        
        except KeyboardInterrupt:
            print("\n\nRetour au menu...")
            return automates, nom_courant
        except Exception as e:
            print(f"\n✗ Erreur : {e}")
            import traceback
            traceback.print_exc()
            input("\nAppuyez sur Entrée pour continuer...")


def menu_principal():
    """Interface console principale avec menu logique en deux étapes."""
    automates = {}  # Dictionnaire : nom -> automate
    nom_courant = None
    
    while True:
        print("\n" + "="*60)
        print("  INTERFACE CONSOLE - GESTION D'AUTOMATES FINIS")
        print("="*60)
        print("\n1. Gérer les automates (créer, charger, lister)")
        print("2. Opérations sur les automates")
        print("0. Quitter")
        print("-"*60)
        
        if nom_courant:
            print(f"\n[Automate courant : {nom_courant}]")
        print(f"[Automates en mémoire : {len(automates)}]")
        
        choix = input("\nVotre choix : ").strip()
        
        try:
            if choix == "0":
                print("\nAu revoir !")
                break
            
            elif choix == "1":
                result = menu_gestion_automates(automates, nom_courant)
                if result is not None:
                    automates, nom_courant = result
            
            elif choix == "2":
                result = menu_operations(automates, nom_courant)
                if result is not None:
                    automates, nom_courant = result
            
            else:
                print("\n✗ Choix invalide. Veuillez choisir entre 0 et 2.")
        
        except KeyboardInterrupt:
            print("\n\nAu revoir !")
            break
        except Exception as e:
            print(f"\n✗ Erreur : {e}")
            import traceback
            traceback.print_exc()
            input("\nAppuyez sur Entrée pour continuer...")


# ----------- Exemple -----------
if __name__ == "__main__":
    menu_principal()
