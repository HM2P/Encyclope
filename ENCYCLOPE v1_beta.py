# ===========================================================
# ENCYCLOPE
# Encyclopédie locale générale
# Jusqu'à 10 000 articles
# ===========================================================

import sqlite3
import requests
import re
import time
import webbrowser
import os

from collections import deque
from urllib.parse import urljoin, quote, unquote
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

DB = "encyclope.db"
MAX_PAGES = 10000

WIKI = "https://fr.wikipedia.org"
API = WIKI + "/w/api.php"

session = requests.Session()
session.headers.update({
    "User-Agent": "Encyclope/1.0 (encyclopedie locale)"
})


# ============================================================
# COULEURS
# ============================================================

RESET = "\033[0m"

NOIR = "\033[30m"
ROUGE = "\033[31m"
VERT = "\033[32m"
JAUNE = "\033[33m"
BLEU = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BLANC = "\033[37m"

GRAS = "\033[1m"

ROUGE_GRAS = "\033[1;31m"
VERT_GRAS = "\033[1;32m"
JAUNE_GRAS = "\033[1;33m"
BLEU_GRAS = "\033[1;34m"
MAGENTA_GRAS = "\033[1;35m"
CYAN_GRAS = "\033[1;36m"


def couleur(texte, code):
    return f"{code}{texte}{RESET}"


def titre(texte):
    print("\n" + CYAN_GRAS + "=" * 72)
    print(texte.center(72))
    print("=" * 72 + RESET)


def info(texte):
    print(CYAN + texte + RESET)


def succes(texte):
    print(VERT_GRAS + texte + RESET)


def erreur(texte):
    print(ROUGE_GRAS + texte + RESET)


def avertissement(texte):
    print(JAUNE_GRAS + texte + RESET)


# ============================================================
# BASE DE DONNÉES
# ============================================================

def ouvrir_db():
    con = sqlite3.connect(DB)

    con.execute("""
        CREATE TABLE IF NOT EXISTS articles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            titre TEXT NOT NULL,
            texte TEXT NOT NULL,
            resume TEXT,
            theme TEXT,
            cree_le INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS liens(
            source_id INTEGER NOT NULL,
            cible_url TEXT NOT NULL,
            UNIQUE(source_id, cible_url)
        )
    """)

    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_titre ON articles(titre)"
    )

    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_theme ON articles(theme)"
    )

    con.commit()

    return con


def nb_articles(con):
    return con.execute(
        "SELECT COUNT(*) FROM articles"
    ).fetchone()[0]


# ============================================================
# NETTOYAGE DES ARTICLES
# ============================================================

def nettoyer(soup):

    for x in soup([
        "script",
        "style",
        "noscript",
        "table",
        "sup",
        "math",
        "nav",
        "form"
    ]):
        x.decompose()

    zone = soup.select_one("#mw-content-text") or soup

    morceaux = []

    for x in zone.select("h2,h3,h4,p,li"):

        texte = x.get_text(" ", strip=True)

        if texte and len(texte) > 1:
            morceaux.append(texte)

    texte = "\n\n".join(morceaux)

    texte = re.sub(
        r"\[\s*\d+\s*\]",
        "",
        texte
    )

    texte = re.sub(
        r"[ \t]+",
        " ",
        texte
    )

    texte = re.sub(
        r"\n{3,}",
        "\n\n",
        texte
    )

    return texte.strip()


# ============================================================
# EXTRACTION DES LIENS
# ============================================================

def extraire_liens(soup, actuelle):

    resultat = set()

    interdits = (
        "Spécial:",
        "Special:",
        "Fichier:",
        "File:",
        "Catégorie:",
        "Category:",
        "Modèle:",
        "Template:",
        "Aide:",
        "Help:",
        "Portail:",
        "Projet:",
        "Discussion:"
    )

    for a in soup.select("a[href]"):

        href = a.get("href", "")

        if not href.startswith("/wiki/"):
            continue

        url = urljoin(
            WIKI,
            href
        ).split("#")[0]

        nom = unquote(
            url.split("/wiki/", 1)[-1]
        )

        if (
            url.startswith(WIKI + "/wiki/")
            and not nom.startswith(interdits)
            and url != actuelle
        ):
            resultat.add(url)

    return resultat


# ============================================================
# URL WIKIPEDIA
# ============================================================

def url_article(titre_article):

    return (
        WIKI
        + "/wiki/"
        + quote(
            titre_article.replace(" ", "_"),
            safe="()'_-," 
        )
    )


# ============================================================
# RECHERCHE WIKIPEDIA
# ============================================================

def recherche_web(sujet):

    try:

        r = session.get(
            API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": sujet,
                "srlimit": 10,
                "format": "json",
                "utf8": 1
            },
            timeout=20
        )

        r.raise_for_status()

        return r.json().get(
            "query",
            {}
        ).get(
            "search",
            []
        )

    except Exception as e:

        erreur(
            f"\nErreur Internet : {e}"
        )

        return []


# ============================================================
# CHOIX D'UN ARTICLE
# ============================================================

def choisir_sujet(sujet):

    resultats = recherche_web(sujet)

    if not resultats:

        erreur("\nAucun résultat trouvé.")

        return None

    titre("\nRÉSULTATS WIKIPEDIA")

    for i, resultat in enumerate(resultats, 1):

        extrait = BeautifulSoup(
            resultat.get("snippet", ""),
            "html.parser"
        ).get_text(
            " ",
            strip=True
        )

        print(
            JAUNE_GRAS
            + f"{i}. "
            + RESET
            + BLEU
            + resultat["title"]
            + RESET
        )

        if extrait:

            print(
                "   "
                + extrait[:200]
            )

        print()

    try:

        choix = int(
            input(
                CYAN
                + "Choisis un numéro [1] : "
                + RESET
            )
            or "1"
        )

    except ValueError:

        choix = 1

    if not 1 <= choix <= len(resultats):

        erreur("Choix invalide.")

        return None

    titre_choisi = resultats[
        choix - 1
    ]["title"]

    return url_article(
        titre_choisi
    )


# ============================================================
# ENREGISTRER UNE PAGE
# ============================================================

def enregistrer_page(
    con,
    url,
    theme,
    afficher=True
):

    connue = con.execute(
        """
        SELECT id,titre,texte
        FROM articles
        WHERE url=?
        """,
        (url,)
    ).fetchone()

    if connue:

        return (
            connue[0],
            connue[1],
            connue[2],
            False,
            None
        )

    if nb_articles(con) >= MAX_PAGES:

        return (
            None,
            None,
            None,
            False,
            None
        )

    try:

        r = session.get(
            url,
            timeout=25
        )

        r.raise_for_status()

    except Exception as e:

        if afficher:

            print(
                ROUGE
                + f"Impossible : {e}"
                + RESET
            )

        return (
            None,
            None,
            None,
            False,
            None
        )

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )

    heading = soup.select_one(
        "#firstHeading"
    )

    if heading:

        titre_article = heading.get_text(
            " ",
            strip=True
        )

    else:

        titre_article = (
            unquote(
                url.split("/wiki/")[-1]
            ).replace("_", " ")
        )

    texte = nettoyer(
        soup
    )

    if len(texte) < 150:

        return (
            None,
            None,
            None,
            False,
            soup
        )

    cur = con.execute(
        """
        INSERT INTO articles(
            url,
            titre,
            texte,
            resume,
            theme,
            cree_le
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            url,
            titre_article,
            texte,
            texte[:1200],
            theme,
            int(time.time())
        )
    )

    article_id = cur.lastrowid

    for lien in extraire_liens(
        soup,
        url
    ):

        con.execute(
            """
            INSERT OR IGNORE INTO liens(
                source_id,
                cible_url
            )
            VALUES(?,?)
            """,
            (
                article_id,
                lien
            )
        )

    con.commit()

    if afficher:

        print(
            VERT
            + f"  + {titre_article}"
            + RESET
            + f" [{nb_articles(con)}/{MAX_PAGES}]"
        )

    return (
        article_id,
        titre_article,
        texte,
        True,
        soup
    )


# ============================================================
# CRAWLER D'UN SUJET
# ============================================================

def crawler_un_sujet(
    con,
    sujet,
    limite=50,
    profondeur=1
):

    url = choisir_sujet(
        sujet
    )

    if not url:

        return 0

    titre(
        f"CRAWL : {sujet}"
    )

    article_id, titre_article, texte, ajoute, soup = (
        enregistrer_page(
            con,
            url,
            sujet
        )
    )

    if article_id is None:

        erreur(
            "Impossible d'enregistrer l'article."
        )

        return 0

    ajoutes = 1 if ajoute else 0

    if soup is None or limite <= 1:

        return ajoutes

    queue = deque(
        (
            lien,
            1
        )
        for lien in extraire_liens(
            soup,
            url
        )
    )

    vus = {
        url
    }

    while (
        queue
        and ajoutes < limite
        and nb_articles(con) < MAX_PAGES
    ):

        url_suivante, niveau = queue.popleft()

        if url_suivante in vus:

            continue

        vus.add(
            url_suivante
        )

        avant = nb_articles(
            con
        )

        _, _, _, nouveau, page_soup = (
            enregistrer_page(
                con,
                url_suivante,
                sujet
            )
        )

        apres = nb_articles(
            con
        )

        if apres > avant:

            ajoutes += 1

        if (
            page_soup is not None
            and niveau < profondeur
        ):

            for lien in extraire_liens(
                page_soup,
                url_suivante
            ):

                if lien not in vus:

                    queue.append(
                        (
                            lien,
                            niveau + 1
                        )
                    )

        time.sleep(
            0.15
        )

    return ajoutes


# ============================================================
# CRAWLER SIMPLE
# ============================================================

def crawler():

    titre(
        "CRAWLER"
    )

    sujet = input(
        CYAN
        + "\nSujet à crawler : "
        + RESET
    ).strip()

    if not sujet:

        return

    try:

        limite = int(
            input(
                CYAN
                + "Nombre maximum de pages [50] : "
                + RESET
            )
            or "50"
        )

    except ValueError:

        limite = 50

    try:

        profondeur = int(
            input(
                CYAN
                + "Profondeur [1] : "
                + RESET
            )
            or "1"
        )

    except ValueError:

        profondeur = 1

    limite = max(
        1,
        min(
            limite,
            MAX_PAGES
        )
    )

    profondeur = max(
        1,
        profondeur
    )

    con = ouvrir_db()

    try:

        total = crawler_un_sujet(
            con,
            sujet,
            limite,
            profondeur
        )

        succes(
            f"\nCrawler terminé : {total} article(s) ajouté(s)."
        )

        info(
            f"Base : {nb_articles(con)}/{MAX_PAGES}"
        )

    finally:

        con.close()


# ============================================================
# CRAWLER MULTIPLE
# ============================================================

def crawler_multiple():

    titre(
        "CRAWLER MULTIPLE"
    )

    print(
        CYAN
        + "Entre plusieurs sujets séparés par des virgules."
        + RESET
    )

    print(
        "Exemple : "
        + JAUNE
        + "Napoléon, Mars, Python, Paris"
        + RESET
    )

    texte = input(
        CYAN
        + "\nSujets > "
        + RESET
    ).strip()

    sujets = [
        x.strip()
        for x in texte.split(",")
        if x.strip()
    ]

    if not sujets:

        erreur(
            "Aucun sujet."
        )

        return

    try:

        limite = int(
            input(
                CYAN
                + "Pages maximum par sujet [20] : "
                + RESET
            )
            or "20"
        )

    except ValueError:

        limite = 20

    try:

        profondeur = int(
            input(
                CYAN
                + "Profondeur [1] : "
                + RESET
            )
            or "1"
        )

    except ValueError:

        profondeur = 1

    limite = max(
        1,
        min(
            limite,
            MAX_PAGES
        )
    )

    profondeur = max(
        1,
        profondeur
    )

    con = ouvrir_db()

    total = 0

    try:

        for numero, sujet in enumerate(
            sujets,
            1
        ):

            if nb_articles(con) >= MAX_PAGES:

                avertissement(
                    "\nLa base est pleine."
                )

                break

            print(
                "\n"
                + MAGENTA_GRAS
                + "=" * 72
                + RESET
            )

            print(
                MAGENTA_GRAS
                + f"SUJET {numero}/{len(sujets)} : {sujet}"
                + RESET
            )

            print(
                MAGENTA_GRAS
                + "=" * 72
                + RESET
            )

            total += crawler_un_sujet(
                con,
                sujet,
                limite,
                profondeur
            )

        succes(
            f"\nCrawler multiple terminé."
        )

        info(
            f"Articles ajoutés : {total}"
        )

        info(
            f"Base : {nb_articles(con)}/{MAX_PAGES}"
        )

    finally:

        con.close()


# ============================================================
# RECHERCHE DANS LA BASE
# ============================================================

def chercher():

    titre(
        "RECHERCHE"
    )

    q = input(
        CYAN
        + "Recherche > "
        + RESET
    ).strip()

    if not q:

        return

    con = ouvrir_db()

    mots = [
        m
        for m in re.findall(
            r"[A-Za-zÀ-ÿ0-9_-]+",
            q
        )
        if len(m) > 1
    ]

    if not mots:

        con.close()

        return

    conditions = []
    params = []

    for mot in mots:

        conditions.append(
            "(titre LIKE ? OR texte LIKE ?)"
        )

        params += [
            "%" + mot + "%",
            "%" + mot + "%"
        ]

    rows = con.execute(
        """
        SELECT titre,theme,resume
        FROM articles
        WHERE
        """
        + " AND ".join(conditions)
        + """
        ORDER BY titre
        LIMIT 30
        """,
        params
    ).fetchall()

    if not rows:

        erreur(
            "\nAucun résultat."
        )

    else:

        titre(
            "RÉSULTATS"
        )

        for i, (
            titre_article,
            theme,
            resume
        ) in enumerate(
            rows,
            1
        ):

            print(
                JAUNE_GRAS
                + f"{i}. "
                + RESET
                + BLEU
                + titre_article
                + RESET
            )

            print(
                "   Thème : "
                + MAGENTA
                + str(theme)
                + RESET
            )

            print(
                "   "
                + resume[:250]
            )

            print()

    con.close()


# ============================================================
# LIRE UN ARTICLE
# ============================================================

def lire_article():

    titre(
        "LECTEUR"
    )

    q = input(
        CYAN
        + "Nom de l'article > "
        + RESET
    ).strip()

    if not q:

        return

    con = ouvrir_db()

    rows = con.execute(
        """
        SELECT id,titre,theme,url
        FROM articles
        WHERE titre LIKE ?
        ORDER BY
            CASE
                WHEN lower(titre)=lower(?)
                THEN 0
                ELSE 1
            END,
            length(titre)
        LIMIT 10
        """,
        (
            "%" + q + "%",
            q
        )
    ).fetchall()

    if not rows:

        erreur(
            "\nArticle absent."
        )

        con.close()

        return

    for i, (
        ident,
        titre_article,
        theme,
        url
    ) in enumerate(
        rows,
        1
    ):

        print(
            JAUNE_GRAS
            + f"{i}. "
            + RESET
            + BLEU
            + titre_article
            + RESET
            + " ("
            + MAGENTA
            + str(theme)
            + RESET
            + ")"
        )

    try:

        choix = int(
            input(
                CYAN
                + "\nNuméro [1] : "
                + RESET
            )
            or "1"
        )

    except ValueError:

        choix = 1

    if not 1 <= choix <= len(rows):

        con.close()

        return

    ident, titre_article, theme, url = rows[
        choix - 1
    ]

    resultat = con.execute(
        "SELECT texte FROM articles WHERE id=?",
        (ident,)
    ).fetchone()

    if not resultat:

        con.close()

        return

    texte = resultat[0]

    titre(
        titre_article.upper()
    )

    print(
        MAGENTA
        + "Thème : "
        + RESET
        + str(theme)
    )

    print(
        CYAN
        + "Source : "
        + RESET
        + url
    )

    print(
        "\n"
        + texte
    )

    action = input(
        CYAN
        + "\nEntrée = retour | web = Wikipédia : "
        + RESET
    ).strip().lower()

    if action == "web":

        webbrowser.open(
            url
        )

    con.close()


# ============================================================
# SUPPRIMER UN OU PLUSIEURS ARTICLES
# ============================================================

def supprimer_article(
    recherche=None
):

    con = ouvrir_db()

    try:

        if recherche is None:

            recherche = input(
                CYAN
                + "\nArticle à supprimer > "
                + RESET
            ).strip()

        if not recherche:

            return

        rows = con.execute(
            """
            SELECT id,titre,theme
            FROM articles
            WHERE titre LIKE ?
            ORDER BY length(titre)
            LIMIT 50
            """,
            (
                "%" + recherche + "%",
            )
        ).fetchall()

        if not rows:

            erreur(
                "\nAucun article trouvé."
            )

            return

        titre(
            "ARTICLES TROUVÉS"
        )

        for i, (
            ident,
            titre_article,
            theme
        ) in enumerate(
            rows,
            1
        ):

            print(
                JAUNE_GRAS
                + f"{i}. "
                + RESET
                + titre_article
                + " — "
                + MAGENTA
                + str(theme)
                + RESET
            )

        print(
            "\n"
            + CYAN
            + "Tu peux entrer un numéro ou 'tous'."
            + RESET
        )

        choix = input(
            CYAN
            + "> "
            + RESET
        ).strip().lower()

        # SUPPRESSION EN MASSE
        if choix in (
            "tous",
            "tout",
            "all"
        ):

            confirmation = input(
                ROUGE_GRAS
                + f"\nSupprimer les {len(rows)} articles ? (o/n) [n] : "
                + RESET
            ).strip().lower()

            if confirmation not in (
                "o",
                "oui",
                "y",
                "yes"
            ):

                avertissement(
                    "Suppression annulée."
                )

                return

            for ident, _, _ in rows:

                con.execute(
                    "DELETE FROM liens WHERE source_id=?",
                    (ident,)
                )

                con.execute(
                    "DELETE FROM articles WHERE id=?",
                    (ident,)
                )

            con.commit()

            succes(
                f"\n{len(rows)} article(s) supprimé(s)."
            )

            return

        # SUPPRESSION PRÉCISE
        try:

            numero = int(
                choix or "1"
            )

        except ValueError:

            erreur(
                "Choix invalide."
            )

            return

        if not 1 <= numero <= len(rows):

            erreur(
                "Choix invalide."
            )

            return

        ident, titre_article, theme = rows[
            numero - 1
        ]

        confirmation = input(
            ROUGE_GRAS
            + f'\nSupprimer "{titre_article}" ? (o/n) [n] : '
            + RESET
        ).strip().lower()

        if confirmation not in (
            "o",
            "oui",
            "y",
            "yes"
        ):

            avertissement(
                "Suppression annulée."
            )

            return

        con.execute(
            "DELETE FROM liens WHERE source_id=?",
            (ident,)
        )

        con.execute(
            "DELETE FROM articles WHERE id=?",
            (ident,)
        )

        con.commit()

        succes(
            f'\nArticle "{titre_article}" supprimé.'
        )

    except Exception as e:

        erreur(
            f"\nErreur : {e}"
        )

    finally:

        con.close()


# ============================================================
# SUPPRIMER TOUTE LA BASE
# ============================================================

def supprimer_toute_base():

    con = ouvrir_db()

    try:

        total = nb_articles(
            con
        )

        if total == 0:

            info(
                "\nLa base est déjà vide."
            )

            return

        print(
            "\n"
            + ROUGE_GRAS
            + "!" * 72
            + RESET
        )

        print(
            ROUGE_GRAS
            + f"ATTENTION : {total} ARTICLES VONT ÊTRE SUPPRIMÉS"
            + RESET
        )

        print(
            ROUGE_GRAS
            + "!" * 72
            + RESET
        )

        confirmation = input(
            '\nTape exactement "SUPPRIMER" : '
        ).strip()

        if confirmation != "SUPPRIMER":

            avertissement(
                "\nSuppression annulée."
            )

            return

        con.execute(
            "DELETE FROM liens"
        )

        con.execute(
            "DELETE FROM articles"
        )

        con.execute(
            "DELETE FROM sqlite_sequence "
            "WHERE name='articles'"
        )

        con.commit()

        succes(
            "\nBase entièrement vidée."
        )

        info(
            "Encyclope repart avec 0 article."
        )

    finally:

        con.close()


# ============================================================
# THÈMES
# ============================================================

def themes():

    con = ouvrir_db()

    rows = con.execute(
        """
        SELECT theme,COUNT(*)
        FROM articles
        GROUP BY theme
        ORDER BY COUNT(*) DESC
        """
    ).fetchall()

    titre(
        "THÈMES"
    )

    if not rows:

        info(
            "Aucun thème pour le moment."
        )

    for theme, nombre in rows:

        print(
            MAGENTA
            + str(theme)
            + RESET
            + " : "
            + JAUNE
            + str(nombre)
            + RESET
            + " article(s)"
        )

    con.close()


# ============================================================
# STATISTIQUES
# ============================================================

def stats():

    con = ouvrir_db()

    total = nb_articles(
        con
    )

    caracteres = con.execute(
        """
        SELECT COALESCE(
            SUM(length(texte)),
            0
        )
        FROM articles
        """
    ).fetchone()[0]

    liens = con.execute(
        "SELECT COUNT(*) FROM liens"
    ).fetchone()[0]

    titre(
        "STATISTIQUES"
    )

    print(
        "Articles        : "
        + VERT
        + f"{total}"
        + RESET
        + f"/{MAX_PAGES}"
    )

    print(
        "Places restantes: "
        + CYAN
        + str(MAX_PAGES - total)
        + RESET
    )

    print(
        "Caractères      : "
        + JAUNE
        + f"{caracteres:,}"
        + RESET
    )

    print(
        "Liens enregistrés: "
        + MAGENTA
        + f"{liens:,}"
        + RESET
    )

    con.close()


# ============================================================
# AIDE
# ============================================================

def aide():

    titre(
        "COMMANDES ENCYCLOPE"
    )

    commandes = [
        ("crawler", "Crawler un sujet"),
        ("multi", "Crawler plusieurs sujets en même temps"),
        ("chercher", "Rechercher dans la base"),
        ("article", "Lire un article"),
        ("supp", "Supprimer un article précis"),
        ("supp <nom>", "Rechercher un article à supprimer"),
        ("supp <nom> + tous", "Supprimer tous les résultats"),
        ("supp t", "Supprimer toute la base"),
        ("themes", "Voir les thèmes"),
        ("stats", "Voir les statistiques"),
        ("aide", "Afficher cette aide"),
        ("quitter", "Fermer Encyclope")
    ]

    for commande, description in commandes:

        print(
            JAUNE_GRAS
            + f"{commande:<25}"
            + RESET
            + description
        )

    print()
    info(
        "Encyclope peut stocker jusqu'à 10 000 articles."
    )

    info(
        "Les articles viennent de Wikipédia et sont conservés localement."
    )


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main():

    ouvrir_db().close()

    os.system("")

    print(
        "\n"
        + CYAN_GRAS
        + "=" * 72
        + RESET
    )

    print(
        CYAN_GRAS
        + "ENCYCLOPE"
        + RESET
    )

    print(
        BLANC
        + "Encyclopédie locale générale"
        + RESET
    )

    print(
        CYAN_GRAS
        + "=" * 72
        + RESET
    )

    print(
        "\n"
        + VERT
        + "✓ Histoire"
        + RESET
        + "   "
        + BLEU
        + "✓ Sciences"
        + RESET
        + "   "
        + MAGENTA
        + "✓ Géographie"
        + RESET
        + "   "
        + JAUNE
        + "✓ Culture"
        + RESET
    )

    print(
        "\nTape "
        + CYAN_GRAS
        + "aide"
        + RESET
        + " pour voir toutes les commandes."
    )

    while True:

        con = ouvrir_db()

        total = nb_articles(
            con
        )

        con.close()

        print(
            "\n"
            + MAGENTA_GRAS
            + "BASE "
            + RESET
            + f"{total}/{MAX_PAGES}"
        )

        cmd = input(
            CYAN_GRAS
            + "ENCYCLOPE > "
            + RESET
        ).strip()

        cmd_lower = cmd.lower()

        # QUITTER
        if cmd_lower in (
            "quitter",
            "quit",
            "exit",
            "q"
        ):

            print(
                VERT
                + "\nFermeture d'Encyclope."
                + RESET
            )

            break

        # CRAWLER
        elif cmd_lower in (
            "crawler",
            "crawl"
        ):

            crawler()

        # CRAWLER MULTIPLE
        elif cmd_lower in (
            "multi",
            "crawler multiple",
            "crawl multiple"
        ):

            crawler_multiple()

        # RECHERCHE
        elif cmd_lower in (
            "chercher",
            "recherche",
            "search"
        ):

            chercher()

        # LIRE
        elif cmd_lower in (
            "article",
            "lire",
            "read"
        ):

            lire_article()

        # SUPP SIMPLE
        elif cmd_lower == "supp":

            supprimer_article()

        # SUPP AVEC NOM
        elif cmd_lower.startswith(
            "supp "
        ):

            argument = cmd_lower[
                5:
            ].strip()

            if argument in (
                "t",
                "tout",
                "all"
            ):

                supprimer_toute_base()

            elif argument:

                supprimer_article(
                    argument
                )

        # THÈMES
        elif cmd_lower in (
            "themes",
            "thèmes",
            "theme",
            "thème"
        ):

            themes()

        # STATS
        elif cmd_lower in (
            "stats",
            "statistiques"
        ):

            stats()

        # AIDE
        elif cmd_lower in (
            "aide",
            "help",
            "?"
        ):

            aide()

        # VIDE
        elif not cmd_lower:

            continue

        # INCONNU
        else:

            erreur(
                "Commande inconnue. Tape 'aide'."
            )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n"
            + JAUNE
            + "Arrêt d'Encyclope."
            + RESET
        )

    except Exception as e:

        print(
            "\n"
            + ROUGE_GRAS
            + "Erreur générale :"
            + RESET,
            e
        )
