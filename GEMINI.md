## **Projet : Système Automatisé d'Enrichissement des Données Débiteurs**

### **Phase 1 : Configuration et Préparation de l'Environnement**

*Objectif : Mettre en place les fondations techniques et la configuration initiale du projet.*

*   **Tâche 1.1 : Mettre en Place le repo Bitbucket et créer la structure initial du projet**

*   **Tâche 1.2 : Mettre en Place la Base de Données Locale (SQLite)**
    *   **Description :** Pour un développement initial rapide et isolé, nous utiliserons une base de données SQLite pour stocker toutes les informations extraites par le processus d'automatisation pendant les premières phases de développement.

    *   **Actions :**
        1.  **Créer une table `EnrichmentData`** dans un fichier de base de données SQLite (ex: `data/enrichment.sqlite`). Cette table contiendra toutes les données collectées.
        2.  **Définir le schéma de la table `EnrichmentData`** avec les colonnes suivantes :
            *   `id` (INTEGER, PRIMARY KEY)
            *   `debtor_id` (INTEGER) : Clé externe faisant référence à l'ID du débiteur dans votre table `Debtor` principale. C'est le lien entre les deux systèmes.
            *   `operational_status` (TEXT ou ENUM) : Statut de l'entreprise ('Active', 'Likely Closed', etc.).
            *   `extracted_owners` (TEXT) : la liste des propriétaires.
            *   `extracted_phones` (TEXT) : la liste de numéros de téléphone.
            *   `extracted_emails` (TEXT) : la liste de emails.
            *   `extracted_addresses` (TEXT) : la liste des adresses.
            *   `relevant_urls` (TEXT) : la liste des URLs pertinentes.

            *   **Autre données stockées :**
            *   `/data/debtor_id/` (Directory) : Un répertoire contenant tous les résultats bruts de recherche pour chaque débiteur, organisés par ID de débiteur.
            *   `/data/debtor_id/serp_result.json` (JSON) : Le résultat brut de la recherche SerpApi pour ce débiteur.
            *   `/data/debtor_id/crawled_pages/` (Directory) : Un répertoire contenant toutes les pages Markdown crawlé pour ce débiteur, organisées par URL.
            *   `/data/debtor_id/crawled_pages/*.md` (Markdown) : Les pages crawlé, nommées par leur URL ou un identifiant unique.

*   **Tâche 1.3 : Créer une table Files and Debtors**.
  * Utiliser les fichiers `data/Debtors.csv` et `data/Files.csv` pour populer les tables

## **Phase 2 : Analyse Superficielle et Collecte Initiale de Données**

*   **Objectif :** Construire le premier module de collecte de données, chargé d'effectuer une analyse de surface rapide et à faible coût pour chaque débiteur afin de recueillir les informations les plus accessibles.

*   **Description :** Cette phase consiste à développer le composant qui interagit avec **SerpApi**. Pour un nom d'entreprise donné, ce module effectuera une recherche Google programmatique et analysera intelligemment les résultats. Il accomplira deux tâches principales :

    1.  **Filtrage de Pertinence :** En appliquant des règles de correspondance strictes, il identifiera et sélectionnera uniquement les URLs les plus pertinentes, écartant ainsi le bruit non pertinent.

    2.  **Extraction de Surface :** Il analysera les titres et descriptions (snippets) de ces résultats pertinents pour extraire toutes les informations de contact "faciles" directement visibles.

    L'ensemble de cette logique sera encapsulé dans un **conteneur Docker du service d'orchestration** qui sera finalisé en Phase 6.

*   **Livrable :** Un composant Python robuste et testable, destiné à être intégré dans le service d'orchestration principal. Ce module formera le premier pilier fonctionnel de l'application et retournera, pour un débiteur, deux ensembles de données essentiels :

    1.  Une liste d'URLs hautement pertinentes et prioritaires, prêtes à être envoyées au service de crawling.

    2.  Un premier lot de données de contact de base, récupérées instantanément à partir des résultats de recherche.

---

## **Phase 3 : Finalisation des Services Externes**

*   **Objectif :** Finaliser les choix technologiques pour les services externes.

*   **Description :** Cette phase se concentre sur 2 tâches principales :
    1.  **Choisir et configurer le Proxy Provider :**
        *   **Description :** Rechercher et sélectionner un proxy provider répondant aux besoins du projet.
        *   **Critères :** Fiabilité, nombre d'IPs au Canada, gestion des CAPTCHAs, coût.
    2.  **Choisir le LLM Provider:**
         *   **Description :** Sélectionner un llm provider (OpenAI, Anthropic ou notre LLM local) pour l'extraction de données structurées à partir du texte brut.
         *   **Critères :** coût, exactitude, et rapidité de réponse.

*   **Livrable :** Un .env configuré avec les clés d'API pour le Proxy et LLM Provider.
---

### **Phase 4 : Intégration du Service de Crawling Spécialisé**

*   **Objectif :** Intégrer et configurer un service de crawling robuste et pré-construit, capable de naviguer et d'extraire le contenu des sites web cibles de manière anonyme et efficace.

*   **Description :** Au lieu de construire un crawler à partir de zéro, nous allons utilise l'image Docker officielle de **Crawl4AI**. Ce service sera configuré pour acheminer toutes ses requêtes via le **Proxy Provider** sélectionné lors de la Phase 1. Nous développerons également, dans notre service principal, un client HTTP simple capable de soumettre des tâches (URLs) à ce service de crawling et de recevoir le contenu des pages en retour.

*   **Livrable :** Une configuration `docker-compose.yml` capable de lancer le service Crawl4AI.

---

### **Phase 5 : Transition vers la Base de Données de Production et Raffinement du Modèle de Données**

*   **Objectif :** Valider la pertinence des données collectées, finaliser le schéma de la base de données de production, et effectuer la transition technique de la base de données locale (SQLite) vers la base de données de production.

*   **Description :** Maintenant que tous les modules d'extraction sont fonctionnels, nous avons une vision claire de la qualité et du format des données que le système peut générer. Cette phase sert de pont entre le développement et la mise en production. Nous allons :
    1.  **Analyser les données prototypes** collectées dans SQLite pour décider quelles informations sont les plus utiles et méritent d'être stockées à long terme.
    2.  **Concevoir le schéma final** pour la table `Debtor` (ou une table liée) dans la base de données de production, en optimisant les types de données et les structures.
    3.  **Mettre à jour la configuration** de l'application pour qu'elle se connecte à la base de données de production MS SQL Server au lieu du fichier SQLite local.

*   **Livrable :** Une configuration d'application mise à jour, capable de lire et d'écrire dans la base de données de production.

---

### **Phase 6 : Orchestration Complète et "Dockerisation"**

*   **Objectif :** Assembler tous les modules développés précédemment en un flux de travail unique et cohérent, et l'encapsuler dans un conteneur Docker pour un déploiement facile et fiable.

*   **Description :** Construire le script principal d'orchestration qui pilotera l'ensemble du processus de A à Z : lire les données depuis la DB, appeler le module SerpApi, mettre à jour les DB, déléguer les tâches de crawling, envoyer le contenu à l'analyse IA, et enregistrer les résultats finaux. Une fois le workflow validé.

*   **Livrable :** Un service d'orchestration, défini dans le `docker-compose.yml` aux côtés du service de crawling.