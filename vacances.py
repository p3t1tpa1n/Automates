#X={a,b,c} L={a*bac*}
import re

# Exemples de test (utilisés uniquement si --test est passé en argument)
atrice = [[0,1,-1],[2,-1,-1],[-1,-1,2]]
# version complète de matrice
Etats_Finaux=[2]
m=[0,0,1,0,2,2,2,2] #aabacccc
m1=[0,0,1,0,2,2,2,2,0] #aabacccca
automate={"matrice":atrice,#un automate est décrit par un dictionnaire, une cle donne sa matrice d'adjacense et une autre ses états finaux
          "finaux": [2]}



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

#la fonction dépend 1)du nombre de caractères de l'alphabet 2) du nombre de noeuds de la matrice
# soit n le nombre de charactères de la fonction et m le nombre de noeuds dans l'automate, on a deux boucles imbriquées,l'une dépend de n, l'autre de n, donc on a une complexité temporelle en O(n*m), la complexitée est quadratique
# on alloue de l'espace mémoire  pour nbEtats,nbChar, mais surtout pour la matrice (de n par m, que l'on transforme en matrice de n+1 par m), donc on occupe n*m+2 espace mémoires, et on a une complexitée spatiale en O((n+1)*m)+2
#=O(n*m)

def Analyse_mot(automate,mot, verbose=False):
    matrice=automate["matrice"]
    finaux=automate["finaux"]
    initial = automate.get("Initial", automate.get("initial", 0))
    
    if verbose:
        print(automate)
    
    Etat = initial  #on commence l'analyse à partir de l'état initial de l'automate
    """
    i=0
    while i<len(mot):
        S=mot[i]
        print(S)
        Etat=matrice[Etat][S]
        if Etat== -1:
            return False
        i=i+1
    return Etat in finaux
    """
    for i in mot:
        if verbose:
            print("i=",i)
        if Etat >= len(matrice) or i >= len(matrice[0]):
            return False
        Etat=matrice[Etat][i]
        if Etat== -1:
            return False
    if Etat in finaux:
        return True
    if verbose:
        print("ici blocquage",i)
    return False

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

    print(index)
    nouvel_initial= index[Dautomate["initial"]]
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
    
    # Conversion en format liste de listes
    mapping = {etat: idx for idx, etat in enumerate(etats_a_explorer)}
    nouvelle_matrice = []
    for etat in etats_a_explorer:
        ligne = []
        for trans in matrice_dict[etat]:
            ligne.append(mapping.get(trans, -1) if trans else -1)
        nouvelle_matrice.append(ligne)
    
    nouveaux_finaux = [mapping[f] for f in finaux_dict if f in mapping]
    
    return {
        "matrice": nouvelle_matrice,
        "finaux": nouveaux_finaux,
        "Initial": mapping.get(etat_initial, 0)
    }


def epsilon_closure(eps, states):
    """Retourne la ε-clôture d'un ensemble d'états."""
    vus = set(states)
    file = list(states)
    while file:
        q = file.pop(0)
        for d in eps.get(q, []):
            if d not in vus:
                vus.add(d)
                file.append(d)
    return vus


def epsilon_closure_automate(auto):
    """
    Prend un automate avec epsilon (colonne 0 = ε)
    Renvoie un automate SANS epsilon.
    """
    matrice = auto["matrice"]
    finaux = set(auto["finaux"])
    initial = auto.get("Initial", 0)

    n = len(matrice)
    sigma = len(matrice[0]) - 1   # colonne 0 = epsilon → on l'enlève

    # eps[q] = états atteignables en 1 epsilon-transition
    eps = {}
    for q in range(n):
        dest = matrice[q][0]
        if dest == -1:
            eps[q] = set()
        else:
            eps[q] = {dest}

    # ε-clôtures
    closures = [epsilon_closure(eps, {q}) for q in range(n)]

    # trans[q][a] = ensemble d'états atteignables par le symbole a (sans ε)
    trans = [[set() for _ in range(sigma)] for _ in range(n)]

    for q in range(n):
        for p in closures[q]:
            for a in range(1, sigma + 1):
                d = matrice[p][a]
                if d != -1:
                    for d2 in closures[d]:
                        trans[q][a - 1].add(d2)

    # Nouveaux finaux
    new_finaux = {q for q in range(n) if closures[q] & finaux}

    # Conversion en matrice d'entiers (on ignore le non-déterminisme multiple)
    new_mat = []
    for q in range(n):
        row = []
        for a in range(sigma):
            if len(trans[q][a]) == 1:
                row.append(next(iter(trans[q][a])))
            elif len(trans[q][a]) == 0:
                row.append(-1)
            else:
                # plusieurs états possibles -> ici on simplifie en -1
                row.append(-1)
        new_mat.append(row)

    alpha = auto.get("alphabet", [])
    new_alpha = alpha[1:] if len(alpha) > 1 else []

    return {
        "matrice": new_mat,
        "finaux": sorted(new_finaux),
        "Initial": initial,
        "alphabet": new_alpha
    }


def supprimer_epsilon(automate):
    """
    Renvoie un automate équivalent SANS epsilon.
    Utilise epsilon_closure_automate.
    """
    matrice = automate["matrice"]
    alphabet = automate.get("alphabet", None)
    n = len(matrice)
    m = len(matrice[0])

    # Cas 1 : l'automate a déjà une colonne epsilon
    if alphabet is not None and len(alphabet) > 0 and alphabet[0] in ("$", "epsilon", "eps", "ε"):
        auto_eps = {
            "matrice": [ligne[:] for ligne in matrice],
            "finaux": automate["finaux"][:],
            "Initial": automate.get("Initial", automate.get("initial", 0)),
            "alphabet": alphabet[:]
        }
        res = epsilon_closure_automate(auto_eps)
        return res

    # Cas 2 : pas de colonne epsilon, on en crée une artificielle
    new_mat = []
    for i in range(n):
        new_mat.append([-1] + matrice[i][:])   # colonne epsilon à -1

    if alphabet is not None:
        new_alpha = ["$"] + alphabet[:]
    else:
        new_alpha = ["$"] + [f"s{i}" for i in range(m)]

    auto_eps = {
        "matrice": new_mat,
        "finaux": automate["finaux"][:],
        "Initial": automate.get("Initial", automate.get("initial", 0)),
        "alphabet": new_alpha
    }

    res = epsilon_closure_automate(auto_eps)
    return res

def add_epsilon_column(automate):
    """Ajoute une colonne epsilon (tout -1) en position 0."""
    mat = automate["matrice"]
    nbEtats = len(mat)

    new_mat = []
    for i in range(nbEtats):
        new_mat.append([-1] + mat[i][:])

    alphabet = automate.get("alphabet", None)
    if alphabet is not None:
        new_alphabet = ["$"] + alphabet[:]
    else:
        new_alphabet = None

    initial = automate.get("Initial", automate.get("initial", 0))

    return {
        "matrice": new_mat,
        "finaux": automate["finaux"][:],
        "Initial": initial,
        "alphabet": new_alphabet
    }
def concatener(automate1, automate2):
    """
    Concatène deux automates automate1 et automate2.
    Résultat : un automate SANS epsilon tel que L = L(automate1) · L(automate2)
    """

    # 1) On supprime d'abord les epsilon dans les deux automates
    auto1_clean = supprimer_epsilon(automate1)
    auto2_clean = supprimer_epsilon(automate2)

    # 2) On ajoute une colonne epsilon pour la concaténation
    eps_1 = add_epsilon_column(auto1_clean)
    eps_2 = add_epsilon_column(auto2_clean)

    mat1 = eps_1["matrice"]
    mat2 = eps_2["matrice"]
    l1 = len(mat1)
    l2 = len(mat2)
    nbCaracteres = len(mat1[0])  # epsilon + alphabet

    if len(mat2[0]) != nbCaracteres:
        raise ValueError("concatener : les deux automates doivent avoir le même nombre de colonnes (même alphabet).")

    new_mat = []

    # Copier auto1
    for i in range(l1):
        new_mat.append(mat1[i][:])

    # Copier auto2 avec décalage d'états (+l1)
    for i in range(l2):
        ligne = []
        for j in range(nbCaracteres):
            dest = mat2[i][j]
            if dest == -1:
                ligne.append(-1)
            else:
                ligne.append(dest + l1)
        new_mat.append(ligne)

    # Transition epsilon : des finaux de auto1 vers l'initial de auto2 (décalé)
    init2 = eps_2["Initial"]
    for f in eps_1["finaux"]:
        new_mat[f][0] = init2 + l1   # colonne 0 = epsilon

    # Nouveaux finaux : ceux de auto2, décalés
    new_finaux = [q + l1 for q in eps_2["finaux"]]

    # Alphabet : on garde celui de auto1 si possible
    new_alphabet = eps_1.get("alphabet", eps_2.get("alphabet", None))
    new_initial = eps_1["Initial"]

    automate_eps = {
        "matrice": new_mat,
        "finaux": new_finaux,
        "Initial": new_initial,
        "alphabet": new_alphabet
    }

    # 3) On supprime les epsilon dans l'automate obtenu
    automate_propre = supprimer_epsilon(automate_eps)
    return automate_propre

def concatenation_alphabet(automate1, automate2):
    """Concaténation des alphabets de deux automates."""


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
                return None, None
            
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
                return automates, nom_courant
            
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
                        afficher_automate(auto, f"Automate '{nom_fichier}' du fichier")
                        nom = input(f"Nom pour cet automate [{nom_fichier}] : ").strip() or nom_fichier
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
                            else:
                                break
                        
                        automates[nom] = auto
                        print(f"  → '{nom}' ajouté.")
                        if not nom_courant:  # Sélectionner le premier par défaut
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
        print("12. Changer l'automate courant")
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
                auto_no_eps = supprimer_epsilon(auto.copy())
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
            
            else:
                print("\n✗ Choix invalide. Veuillez choisir entre 0 et 12.")
        
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
                automates, nom_courant = menu_gestion_automates(automates, nom_courant)
            
            elif choix == "2":
                automates, nom_courant = menu_operations(automates, nom_courant)
            
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


def selectionner_automate(automates, nom_par_defaut=None):
    """Sélectionne un automate dans la liste."""
    if not automates:
        print("\n✗ Aucun automate disponible.")
        return None
    
    print("\nAutomates disponibles :")
    for nom in automates:
        print(f"  • {nom}")
    
    nom = input(f"\nNom de l'automate [{nom_par_defaut}] : ").strip() or nom_par_defaut
    if nom and nom in automates:
        return automates[nom]
    else:
        print(f"✗ Automate '{nom}' introuvable.")
        return None


# ----------- Exemple -----------
if __name__ == "__main__":
    import sys
    
    # Si des arguments sont passés, exécuter les tests
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Automates déterministes simples (sans epsilon)
        a1 = {
            "matrice": [[0,1,-1],[2,-1,-1],[-1,-1,2]],
            "finaux": [2],
            "Initial": 0,
            "alphabet": ["a", "b", "c"]
        }
        a2 = {
            "matrice": [[0,2],[1,2],[2,2]],
            "finaux": [1,2],
            "Initial": 0,
            "alphabet": ["a", "b"]
        }

        # Automate avec epsilon
        a_eps = {
            "matrice": [
                [1, -1, -1],   # 0 --ε--> 1
                [-1, 2, -1],   # 1 --a--> 2
                [-1, -1, 2]    # 2 --b--> 2
            ],
            "finaux": [2],
            "Initial": 0,
            "alphabet": ["$", "a", "b"]
        }

        print("Automate avec epsilon :", a_eps)
        A_no_eps = epsilon_closure_automate(a_eps)
        print("Automate sans epsilon :", A_no_eps)
    else:
        # Interface console
        menu_principal()
    
