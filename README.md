Speaker Identification in Novels
================================

Le but de ce projet, inspiré par l’article Identification of Speakers in Novels de Hua He (University of Maryland),
Denilson Barbosa et Grzegorz Kondrak (University of Alberta), est d’identifier les locuteurs dans les dialogues de romans.
Le dataset est constitué des dialogues du roman Pride and Prejudice de Jane Austen.

Nous avons developpé trois solutions s'éloignant un peu de l'article, les deux premières donnant des résultats intéressants
tandis que la dernière rélève plus de l'expérimentation
- un classifieur XGBoost opérant sur des features manufacturées
- une heuristique à base de règles et d'une base de connaissance ontologique sur les relations sociales entre les personnages
- un classifieur à base de RNN opérant sur le texte (les séquences d'uttérances au sein de chaque discussion) aggrégé avec les résultats de l'heuristique

Un rapport plus détaillé se trouve à la racine du repertoire sous le nom `Rapport.pdf`
