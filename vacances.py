#X={a,b,c} L={a*bac*}
import re

Automate = {
    "matrice": [
        [[1,3], [1]], 
        [[2], [1,2]],
        [[2], [1,3]], 
        [[3],[]]     
    ],
    "initial": 0,
    "finaux": [2,3],
    "alphabet": ["$","a","b","c"]
}
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

print(estComplet(automate))


def Complet(automate):
    matrice= automate["matrice"]
    if estComplet(automate):
        return automate
    nbEtats= len(matrice)
    nbChar= len(matrice[0])
    matrice.append([nbEtats,nbEtats,nbEtats])
    for i in range(nbEtats):
        for j in range(nbChar):
            if matrice[i][j]==-1:
                matrice[i][j]= nbEtats
    automate["matrice"]= matrice
    return automate
print(automate)
automate=Complet(automate)
print(automate)

def Complementaire(automate):
    automate= Complet(automate)
    Cautomate ={}
    Cautomate["matrice"]=automate["matrice"]
    Cautomate["finaux"]=[]
    nbEtats= len(Cautomate["matrice"])
    #Les etats de l'automate a "complémenter" sont codés de 0 jusqu'a nbEtats-1
    #Par explemple dans notre cas nos états sont codés de 0 à 3 (nbEtats=4)
    for i in range(nbEtats):
        # Si l'etat i n'est pas final dans l'automate à "complémenter", alors il est final dans l'automate complément
        if i not in automate["finaux"]:
            Cautomate["finaux"].append(i)
    return Cautomate
print("/----------------/")
print(Complementaire(automate))

#la fonction dépend 1)du nombre de caractères de l'alphabet 2) du nombre de noeuds de la matrice
# soit n le nombre de charactères de la fonction et m le nombre de noeuds dans l'automate, on a deux boucles imbriquées,l'une dépend de n, l'autre de n, donc on a une complexité temporelle en O(n*m), la complexitée est quadratique
# on alloue de l'espace mémoire  pour nbEtats,nbChar, mais surtout pour la matrice (de n par m, que l'on transforme en matrice de n+1 par m), donc on occupe n*m+2 espace mémoires, et on a une complexitée spatiale en O((n+1)*m)+2
#=O(n*m)

def Analyse_mot(automate,mot):
    matrice=automate["matrice"]
    finaux=automate["finaux"]
    print(automate)
    Etat=0 #on commence l'analyse à partir de l'état initial de l'automate
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
        print("i=",i)
        Etat=matrice[Etat][i]
        if Etat== -1:
            return False
    if Etat in finaux:
        return True
    print("ici blocquage",i)
    return False


print(Analyse_mot(automate,m))

def save_automates(fichier, automates):
    """Enregistre une liste d'automates dans un fichier."""
    with open(fichier, "w", encoding="utf-8") as f:
        for a in automates:
            initial = a.get("Initial", a.get("initial", 0))
            f.write(f"{a['matrice']}|{a['finaux']}|{initial};\n")


def load_automates(fichier):
    """Lit un fichier et renvoie la liste des automates."""
    with open(fichier, "r", encoding="utf-8") as f:
        contenu = f.read()
    
    automates = []
    for bloc in contenu.split(";"):
        bloc = bloc.strip()
        if not bloc:
            continue
        parties = bloc.split("|")
        matrice = eval(parties[0])
        finaux = eval(parties[1])
        initial = eval(parties[2]) if len(parties) > 2 else 0
        automates.append({"matrice": matrice, "finaux": finaux, "Initial": initial})
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
    initial = auto.get("initial", auto.get("Initial", 0))

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

# ----------- Exemple -----------
if __name__ == "__main__":
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
    
