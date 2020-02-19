# Approach

The goal of CodeClusters is to group the code submissions into distinct groups, which then the teacher can view and use to analyze and give feedback on to the students.

What makes this type of clustering harder than your regular coordinate-based KNN is, that the code itself can be quite heterogenous and ambiguous thus hard to distinguish between two equal representations of a same thing.

Luckily there has already been thought put into this problem, and prior solutions exist such as [OverCode](https://github.com/eglassman/overcode). It is pioneering work on this field, on which this solution too is partly based on.

In OverCode and in CodeClusters, the submitted code is split into tokens called Abstract Syntax Tree (AST). This enables us to omit the less useful details (names of variables, whitespaces, ordering) and rather see the structure of the code.

So all the unnecessary information such as variable names or comments are either normalized or discarded, even though code style wise it would be nice to review the code quality as well as the actual implementation.

By having these sets of code tokens at our disposal, we can cluster the pieces in either single blocks, or in sequences of n-grams whichever is the most useful.

## model

* edit distance between the submissions
* the use of model answer?
* edit distance to the model answer
* use of constraints to set tight boundaries inside which "good" submissions should reside?
* eg how many lines, variables, function calls, used libraries
* performance analysis
* give automatic feedback based on the code complexity / style? based on some simple model eg amount of lines / function calls

## features

* sort by the most common tokens/lines with ability to filter them
* use the rest for the actual clustering
* show clusters / samples of highest variation?

eli siis käli, josta voi valita minkä rivien perusteella valitsee koodipalautukset -> klusteroi

sitten antaa niille kaikille jonkin palautteen, klikkaa doneksi

ottaa seuraavan, vähän pienemmän klusterin ja tekee saman yms

mahdollisuus lisätä avainsanoja, jotka automaattisesti "vääriä" esim kirjastofunktion käyttö, joku hölmö tapa koodissa

ehkä jopa yhdistä aikaisemmat laskaripisteet, jotta voi filtteröidä vain huonoimmat oppilaat (kuitenkin joku anonymisaatio)

parsi rivi kerrallaan
merkitse avainsana mäpistä avainsanat jos on, huomaa nimet ja anna niille joku id
appendaa jonkin scopen sisällä olevat asiat sen lapsiksi esim luokan muuttujat, funktiot
pidä kirjaa määristä, monta käytetty, monta riviä, monta merkkiä
merkkaa käytety stringit id:eillä
merkkaa kirjastometodit
erikoislogiikkaa while, do-while, for, if-else, break, continue yms lukemiseen...

ehkä opettaja voi etsiä haluamansa virheet, esim tietyn merkki/rivi määrän ylittäviä vastauksia
regex haku?
aika jopa automaattisia virheilmoituksia saa noista...
avainsanojen käytön määrä esim monta while:a käytetty

## antlr

eli eli eli eli eli.......

keywordeja käyttämällä saa countit, joista saa tarvittaessa matriisit, paljon käytetty per dokumentti

niiden avulla näkee nopeasti ainakin harvinaisimmat keyword sekä anomaliat, joissa käytetty paljon whitespacea,
yms häröilyä

eli joka dokumentille voisi antaa avg term freq jossa dokumentin termi frekvenssit jaettuna kaikki termit * (dokumentit / termiä käyttävät dokumentit) -> melkein kuin TF-IDF mutta ei logaritmia joten ei tule nollaa jos kaikki dokumentit käyttävät termiä (mikä on varsin yleistä)

sitten tämä vektori vielä voisi supistaa yhdeksi arvoksi, kuten TF-IDF, eli log sum?

_peculiarity score_

tämän lisäksi siis myös string matchaus, eli lista regexejä, jotka ajetaan per rivi? vai per token?
ja näille vielä keino valita joku thresholdi, eli esim monta while:ä käytetty
