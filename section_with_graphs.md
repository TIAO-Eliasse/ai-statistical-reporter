## Statistiques univariées

## Statistiques Univariées

L'analyse univariée constitue la première étape fondamentale de toute exploration statistique, visant à décrire les caractéristiques intrinsèques de chaque variable prise isolément. Cette section détaille la distribution, la tendance centrale, la dispersion et la forme de chaque variable étudiée, fournissant ainsi une compréhension exhaustive de leurs propriétés individuelles avant toute investigation de leurs relations potentielles.

### Méthodologie

Pour les variables numériques, l'analyse a englobé le calcul des mesures de tendance centrale telles que la moyenne et la médiane, offrant des indicateurs du "cœur" de la distribution. Les mesures de dispersion, incluant l'écart-type, la variance, le minimum, le maximum et l'étendue (range), ont été utilisées pour quantifier la variabilité des données. En complément, l'asymétrie (skewness) et l'aplatissement (kurtosis) ont été évalués pour caractériser la forme de la distribution, notamment sa symétrie et son degré d'aplatissement par rapport à une distribution normale. Une asymétrie positive indique une queue de distribution plus longue vers les valeurs élevées, tandis qu'une asymétrie négative pointe vers une queue plus longue vers les valeurs faibles. L'aplatissement mesure la "lourdeur" des queues et la "pointualité" du pic ; une valeur négative suggère une distribution plus aplatie (platykurtique) et moins de valeurs extrêmes que la distribution normale.

Concernant les variables catégorielles, la méthodologie a consisté à dénombrer les occurrences de chaque modalité afin d'obtenir des fréquences absolues. Ces dernières ont ensuite été converties en fréquences relatives, exprimées en pourcentages, pour faciliter l'interprétation de la proportion de chaque catégorie au sein de l'ensemble des observations. L'identification du nombre de modalités uniques a également été réalisée pour apprécier la diversité de la variable.

### Résultats et Interprétation

#### Analyse de la variable numérique 'age'

La variable 'age' présente une distribution dont la tendance centrale est caractérisée par une moyenne de **30.83** ans et une médiane de **30.00** ans. La proximité de ces deux mesures suggère une distribution relativement équilibrée, sans décalage majeur induit par des valeurs extrêmes. En termes de dispersion, l'âge minimal enregistré est de **25.00** ans et l'âge maximal est de **40.00** ans, ce qui donne une étendue de **15.00** ans. L'écart-type, s'établissant à **5.85** ans, et la variance, à **34.17**, indiquent une dispersion modérée des âges autour de la moyenne.

Les mesures de forme de distribution révèlent une légère asymétrie positive de **0.67**, signifiant que la distribution des âges tend légèrement à avoir une queue plus longue vers les valeurs supérieures, suggérant une présence un peu plus marquée d'individus légèrement plus âgés que la moyenne. L'aplatissement de **-0.45** indique une distribution platykurtique, c'est-à-dire plus aplatie et avec des queues moins prononcées que celles d'une distribution normale. Cela suggère que les âges sont répartis de manière relativement uniforme sur l'étendue, plutôt que d'être fortement concentrés autour d'une valeur centrale.

#### Analyse de la variable numérique 'salaire'

L'analyse de la variable 'salaire' révèle une moyenne de **62833.33** unités monétaires et une médiane de **60000.00** unités monétaires. Similairement à la variable 'age', la moyenne est légèrement supérieure à la médiane, ce qui, combiné à l'asymétrie positive, indique une distribution avec une légère tendance à avoir des valeurs plus élevées tirant la moyenne vers le haut. La dispersion des salaires est plus prononcée, avec un écart-type de **12172.37** unités monétaires et une variance de **148166666.67**. Les salaires varient de **50000.00** unités monétaires (minimum) à **80000.00** unités monétaires (maximum), couvrant une étendue de **30000.00** unités monétaires.

En ce qui concerne la forme de la distribution, l'asymétrie positive est de **0.57**, ce qui confirme la légère queue vers les hauts salaires. Cette valeur est légèrement inférieure à celle de l'âge, indiquant une asymétrie un peu moins prononcée. L'aplatissement, avec une valeur de **-1.47**, est significativement négatif. Cela caractérise une distribution fortement platykurtique, impliquant une dispersion des salaires plus étalée avec moins de pic central et des queues très légères par rapport à une distribution normale. En d'autres termes, les salaires sont relativement bien répartis sur l'ensemble de l'étendue observée, sans concentration excessive autour de la moyenne.

#### Analyse de la variable catégorielle 'nom'

La variable 'nom' a été examinée pour ses propriétés d'identification. Il a été confirmé l'existence de **6** valeurs uniques pour cette variable. Chacun des noms représente un identifiant individuel distinct au sein de l'ensemble des enregistrements. Cette unicité est cruciale car elle permet de garantir que chaque observation est associée à une entité unique, sans duplication ou ambiguïté, ce qui est essentiel pour la gestion et l'analyse ultérieure des données.

#### Analyse de la variable catégorielle 'ville'

L'analyse de la variable 'ville' révèle une distribution géographique des enregistrements. Un total de **4** villes uniques a été identifié. La distribution des fréquences absolues montre que Paris et Lyon comptent chacune **2** occurrences, tandis que Marseille et Toulouse n'en ont qu'une seule. En termes de fréquences relatives, Paris et Lyon représentent chacune **33.33%** des observations, soulignant une concentration notable des enregistrements dans ces deux métropoles. Marseille et Toulouse contribuent chacune pour **16.67%** des observations.

Il ressort de cette analyse que la ville la plus représentée est Paris, avec **2** occurrences. Cependant, il est important de noter que Paris et Lyon sont ex aequo en termes de fréquence absolue et relative, se partageant la première place des villes les plus représentées dans cet échantillon. Cette répartition inégale des observations entre les différentes villes pourrait influencer toute analyse géographique subséquente et met en évidence la prédominance de quelques centres urbains dans l'ensemble de données.

### Conclusion Générale

L'analyse univariée a permis de dresser un portrait détaillé des caractéristiques fondamentales de chaque variable. Pour les variables numériques 'age' et 'salaire', des distributions relativement symétriques mais légèrement positives ont été observées, avec des aplatissements négatifs suggérant une dispersion plus uniforme des valeurs. L'âge présente une étendue et une variabilité modérées, tandis que le salaire montre une étendue plus large et une dispersion plus marquée. La variable 'nom' a été confirmée comme un identifiant unique, indispensable à la bonne gestion des enregistrements. Enfin, la variable 'ville' révèle une concentration des observations dans deux villes majeures, Paris et Lyon, avec une représentation moindre pour Marseille et Toulouse. Ces informations essentielles constituent la base pour des analyses bivariées et multivariées ultérieures, offrant un contexte riche pour l'interprétation des relations entre ces variables.

