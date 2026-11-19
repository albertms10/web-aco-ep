# Web de l’Associació Catalana de l’Orgue

Web de l’Associació Catalana de l’Orgue. Utilitza `jekyll` per crear la pàgina web estàtica car no hi ha la necessitat de
disposar d’elements dinàmics, tipus la interacció d’un usuari amb una base de dades, donar-se d’alta com a soci, fòrum, etc.

En lloc de començar utilitzant una plantilla de `jekyll`, que tantes en circulen, he preferit muntar aquesta pàgina des
de zero, que és el que l’experiència m’ha ensenyat creant la pàgina web per l’associació de Vilafranca, la prova de fa un any (2021) vaig fer per
aquesta associació i la que vaig haver de fer de personal. Aquestes plantilles tenen llargs fitxers d’estil molt complexos que
jo no entenc i són difícils de personalitzar. Utilitzen funcions molt concretes i remodelar l’aspecte és difícil havent
de seguir unes vies que desconec.

He tingut algunes experiències amb Bootstrap; et proporciona estils _responsive_ sense haver de fer gaire feina. Estèticament,
és plaent i no és difícil de modificar. Pel que fa als elements de la pàgina, amb una mica de paciència amb Bootstrap i `liquid`
de Shopify, que és el que utilitza `jekyll` per defecte, n’hi ha de sobres.

La pàgina web està allotjada en un repositori de GitLab privat ([https://gitlab.com/borgue95/web-aco](https://gitlab.com/borgue95/web-aco)),
propietat de Berenguer Montserrat. Estic obert a donar accés a qui sàpiga com funcionen les dinàmiques amb la gestió de
codi font de Git.

La pàgina web està servida per GitLab pages, ja que els requisits de la pàgina concorden amb el servei gratuït d’allotjament que
ofereix GitLab.

[TOC]

# Desenvolupament tècnic

## Instal·lació de dependències

1. Clona el repositori
2. Instal·la `npm`. En Arch Linux és `sudo pacman -Sy nodejs`.
3. Des de la carpeta arrel, fes `npm install --prefix assets`.
4. Instal·la `ruby`. En Arch Linux és `sudo pacman -S ruby base-devel`.
5. Els plugins de `ruby` es diuen `gem` (gemmes). Cal instal·lar `jekyll` i `bundler`, les dues gemmes que es necessiten per
   construir la pàgina web. Fes `gem install bundler jekyll`.
6. Cal instal·lar les gemmes addicionals de la pàgina. Fes `bundle install`.
7. Instal·la `python`, en la versió més recent (3.12, per exemple).
8. Crea un entorn virtual de python a la carpeta arrel. Fes `python -m venv venv`
9. Entra a l’entorn virtual (i ja t’hi pots quedar durant el desenvolupament de la pàgina). Fes `source venv/bin/activate`.
10. Instal·la les dependències de python per aquest projecte. Fes `pip install -r requirements.txt`.

### Bug a _owncloud_

`owncloud` és la llibreria de python per accedir a les dades del servidor _nextcloud_ que emmagatzema les imatges
de la web. Té un bug perquè està pensada per servidors _owncloud_ i no _nextcloud_.

Aquest bug salta quan s’intenta afegir una nova pàgina a la web amb un error com aquest:

    Error! img/orgues/barcelona/barcelones/barcelona/palau-nacional/IMG_8848.JPG. 'NoneType' object has no attribute 'text'

El bug es troba a la funció `share_file_with_link` (línia 861, aproximadament) del fitxer `owncloud.py`. Si es treballa
amb un `venv` (virtual environment), el fitxer es troba a `venv/lib/python3-12/owncloud/owncloud.py`. Cal comprovar que
l’objecte retornat `data_el.find(...)` no sigui null abans de demanar l’atribut `.text`. Si és null, retorna un string
buit. Canvia la línia de `return` per aquesta:

```python
return ShareInfo(
    {
        'id': data_el.find('id').text if data_el.find('id') is not None else '',
        'path': path,
        'url': data_el.find('url').text if data_el.find('url') is not None else '',
        'token': data_el.find('token').text if data_el.find('token') is not None else '',
        'name': data_el.find('name').text if data_el.find('name') is not None else ''
    }
)
```

## Execució de la pàgina

### Generació de dependències

Abans d’executar el servidor web en local **per primera vegada**, cal generar les dependències. Són un seguit d’_scripts_ de Python que
s’encarreguen de llegir els fitxers de la web i generar-ne de nous. El motiu principal és per facilitar l’obtenció
de dades parametritzades a través de _Liquid_, el generador de plantilles de Jekyll.

```bash
  export OC_USER="web-aco"
  export OC_PASSWORD="-the-password-"
  python scripts/manage-nuvol.py -d

  python scripts/create-comptadors.py
  python scripts/create-geo-limits.py
  python scripts/create-orgues-per-orgueners.py
  python scripts/create-pobles.py
  python scripts/sort-bibliografia.py
```

La contrasenya `OC_PASSWORD` del [núvol](https://nextcloud.acorgue.cat) es troba al [tresor](https://bitwarden.acorgue.cat). Demana
accés al tresor als responsables del desenvolupament de la pàgina.

Si **no és la primera vegada** que executes la pàgina, els scripts que s’executen de manera regular són lleugerament
diferents. Vés a la secció [He canviat una cosa. Què cal executar?](#he-canviat-una-cosa-què-cal-executar)

#### Llistes de fitxers de dades

Generats manualment:

- `/_data/disposicions/*/*.yml`.
- `/_data/ceoc.yml`. Conté la informació bàsica de cada concert del cicle «Els Orgues de Catalunya».
- `/_data/enllacos-externs.yml`. S’ha intentat concentrar aquí tots els enllaços al
  [núvol](https://nextcloud.acorgue.cat). Si mai s’haguessin de canviar tots, estarien agrupats.
- `/_data/llibres.yml`. Conté les diferents entrades bibliogràfiques referents a l’orgue. Sense ordre alfabètic.
- `/_data/navbar.yml`. Conté la definició de la barra de navegació.
- `/_data/orgues.yml`. Conté definicions de província, comarca i municipi. Conté la definició de cadascun dels edificis
  que tenen orgue o orgues. Referiu-vos a [Format del fitxer `/_data/orgues.yml`](#format-del-fitxer-_dataorguesyml)
  per conèixer-ne el format.

Generats automàticament:

- `/_data/bibliografia.yml`. Llegeix la informació de `llibres.yml` i l’ordena segons uns criteris. Així no cal afegir
  les dades ordenades alfabèticament.
- `/_data/comptadors.yml`. Conté informació, majoritàriament interna, de l’estat dels
  orgues. Quants n’hi ha, quines dades falten de cadascun dels orgues, etc. Alguna d’aquesta informació es mostra a la
  pàgina.
- `/_data/edificis.yml`. Conté cadascun dels edificis (un sol nivell) amb totes les seves dades. La informació surt del
  fitxer `/_data/orgues.yml`.
- `/_data/imatges.yml`. Conté la definició de cadascuna de les imatges de cadascun dels orgues (un sol nivell).
  La secció [Tractament de les imatges](#tractament-de-les-imatges) explica detalladament el procés de generació
  d’aquest fitxer.
- `/_data/limits-geografics.yml`. Conté el quadrat delimitador de cadascuna de les entitats geogràfiques (província,
  comarca i municipi). S’utilitza per centrar correctament cada entitat en el mapa Leaflet.
- `/_data/orgueners.yml`. Conté la informació de cadascun dels orgueners i en quins orgues ha treballat. La informació
  és una recopilació de les dades escampades per tots els fitxers `*.yml` de `/_data/disposicions/`.
- `/_data/pobles.yml`. Conté cadascun dels municipis (un sol nivell) amb els edificis que tenen orgue.
- `/assets/geojson/*`. Conté les coordenades GPS dels polígons que conformen cada entitat geogràfica (província, comarca
  i municipi).

#### Descripció dels _scripts_ de Python

La manera que té _Jekyll_ de tractar tota la informació que hi ha a la carpeta `/_data/` és un poc limitada. Per això,
existeixen un seguit d’_scripts_ de Python per facilitar l’obtenció de les dades parametritzades a través de _Liquid_,
el generador de plantilles que utilitza Jekyll.

- `create-breadcrumb-pages.py`. Crea les pàgines pel breadcrumb. Cada província, comarca i municipi té una pàgina amb
  un layout concret on es llisten els orgues. Si s’afegeix un municipi nou, cal executar aquest script i crearà les
  pàgines corresponents.
- `create-comptadors.py` genera `/_data/comptadors.yml`.
- `create-geo-limits.py` genera `/_data/limits-geografics.yml`.
- `create-imatges.py` genera `/_data/imatges.yml`.
- `create-orgues-per-orgueners.py` genera `/_data/orgueners.yml`.
- `create-pobles.py` genera `/_data/pobles.yml` i `/_data/edificis.yml`.
- `get-geojson.py`. Obté les dades GPS dels límits territorials. Referiu-vos a la secció
  [Mapes del breadcrumb](#mapes-del-breadcrumb) per a més informació, sobretot abans d’executar-los!
- `sort-bibliografia.py` genera `/_data/bibliografia.yml`.
- `test-redirect-from-duplicates.py`. En noves versions de la web, s’ha afegit un plugin de Jekyll (JekyllRedirectFrom)
  que gestiona automàticament el fet de tenir dos URL per una pàgina. És interessant tenir URL curts (fins i tot,
  crípticament curts) per compartir-les a les xarxes o mitjançant codis QR. Aquest _script_, de moment, té una classe
  que serveix per comprovar que no hi hagi cap URL duplicat a la llista de `redirect_from` escampada per tots els fitxers
  `*.md` de l’inventari. A més, té un parell més de classes (o més, si creix) que s’han creat per ser executades una
  sola vegada per crear els URL curts i per afegir els URL antics per no trencar la compatibilitat amb el món.

### Execució del servidor web local

```bash
JEKYLL_ENV=devel; bundle exec jekyll serve --host 0.0.0.0 --port 4001 --livereload --trace --config _config.yml,_config_dev.yml
```

Hi ha dues configuracions: la primera, és la de producció, la que s’ha d’utilitzar tant sí com no; la segona, només durant el desenvolupament
en local; el que fa aquesta segona configuració és sobreescriure alguns paràmetres que en local són diferents o bé no tenen sentit.

### He canviat una cosa. Què cal executar?

Els _scripts_ de Python masteguen la informació de la web. Per aquest motiu, si es realitza algun canvi en algun dels
fitxers, caldrà tornar a mastegar.

- Si he afegit imatges (les he pujades al servidor i les he llistat al corresponent fitxer `*.md`), o bé he canviat
  alguna metadada en els fitxers `*.md`, caldrà executar:

  ```bash
  export OC_USER="web-aco"
  export OC_PASSWORD="-the-password-"
  python create-images.py
  python manage-nuvol.py -u  # abans de llençar el build de CI, a la branca corresponent, normalment, producció
  ```

- Si he afegit un orgue nou (he creat els corresponents fitxers `*.yml` i `*.md` i l’he llistat a `/_data/orgues.yml`),
  llavors caldrà fer:

  ```bash
  python scripts/create-breadcrumb-pages.py
  python scripts/create-comptadors.py
  python scripts/get-geojson.py  # Nota 1
  python scripts/create-geo-limits.py  # Nota 1
  python scripts/create-orgues-per-orgueners.py
  python scripts/create-pobles.py
  ```

  **Nota 1**: Si s’ha afegit un orgue en un municipi que no en tenia cap, caldrà executar aquests dos scripts. Primer
  `get-geojson.py` perquè es baixi la informació d’OpenStreetMaps i, després, `create-geo-limits.py` per calcular el
  requadre que conté el nou municipi.

- Si he canviat alguna cosa del fitxer `/_data/llibres.yml`, cal executar:

  ```bash
  python sort-bibliografia.py
  ```

- Si no he fet res de l’anterior i només he corregit errors a les pàgines `*.md` o als fitxers `*.yml`, no hauria de
  caldre fer res.

Tots els _scripts_ estan bastant optimitzats perquè sigui segur i ràpid executar-los tots de cop.

### CI (GitLab)

El fitxer `/.gitlab-ci.yml` conté les instruccions per construir la pàgina i fer-la pública.

**NOTA IMPORTANT**: com he dit a sobre, els _scripts_ estan optimitzats per ser relativament ràpids. Hi ha dues excepcions:
`create-imatges.py` i `get-geojson.py`. Cal assegurar-se d’executar aquests dos _scripts_ en local a la branca de
producció i, abans de pujar-la (abans de fer `git push`), executar `python manage-nuvol.py -u` per pujar els resultats.

# Organització dels fitxers de la pàgina

## Explicació de cada element de l’arrel

### `/_data/`

Referiu-vos a la secció [Generació de dependències](#generació-de-dependències) per conèixer el paper principal de
cadascun dels fitxers d’aquesta carpeta.

Referiu-vos a les seccions corresponents per conèixer el format de cadascun dels fitxers generats manualment d’aquesta
carpeta.

### `/_includes/`

Forma part de Jekyll. Són trossos d’HTML parametritzats amb Liquid que s’utilitzen freqüentment en altres llocs, normalment
en _layouts_ ([secció següent](#_layouts)) i en pàgines _Markdown_. Estan més o menys organitzats en subcarpetes segons
on s’utilitzen.

### `/_layouts/`

Forma part de Jekyll. Són pàgines HTML (que poden tenir herències) que donen format als fitxers _Markdown_. Cadascun
dels fitxers _Markdown_ de la web té un _layout_ assignat.

#### Descripció dels layouts

Els layouts són les plantilles que permeten generar la pàgina web amb l’aspecte desitjat. Les plantilles són jeràrquiques,
i així ho indiquen les carpetes dins de `/_layouts` (ho vaig fer així per claredat; no és imprescindible):

- `base.html`: és la que conté la definició principal de l’HTML. Hi ha els enllaços a les fulles d’estil i els scripts necessaris.
  - `404.html`: genera el format de la pàgina quan un document no s’ha trobat. No s’hauria de veure mai.
  - `bc-comarca.html`, `bc-edifici.html`, `bc-municipi.html` i `bc-provincia.html`: generen les pàgines per a cadascuna
    d’aquestes entitats. Hi surt el llistat dels orgues que conté cada entitat.
  - `ceoc.html`: pàgina per a un concert concret del cicle «Els Orgues de Catalunya».
  - `home.html`: genera la pàgina principal. Aquí hi ha el bàner i el llistat d’articles recents.
  - `innocentada.html`: una bajanada. És per la innocentada del 2024, que vam crear un layout de notícia perquè, al cap
    de _n_ segons sortís una llufa a la pantalla.
  - `noticia.html`: genera el contingut d’una notícia. Per norma general, tots els fitxers `.md` de la carpeta `/_posts`
    haurien d’utilitzar aquest layout.
  - `orgue.html`: genera el contingut d’un orgue en concret.
  - `page.html`: genera el contingut d’una pàgina genèrica qualsevol. És poc utilitzat. `about.md` usa, per exemple, aquest layout.
    - `article.html`: genera el contingut d’un article, que és diferent del d’una notícia. Un article és més acadèmic, serà més extens,
      tindrà un índex de continguts, un autor i un llarg etcètera.
    - `categories.html`: genera la pàgina on s’ordenen els articles i notícies (el contingut de `/_posts`) per categories.
    - `orgues.html`: genera la pàgina principal amb el buscador i les llistes dels orgues del principat.
    - `publicacions.html`: genera la pàgina on s’ordenen els articles i notícies (el contingut de `/_posts`) per anys.
    - `tags.html`: genera la pàgina on s’ordenen els articles i notícies (el contingut de `/_posts`) per etiquetes.

### `/_plugins/`

Són petits _scripts_ de _Ruby_ que augmenten la funcionalitat de les plantilles _Liquid_ de Jekyll. Els que hi ha aquí
són els que s’han creat ad hoc per aquesta pàgina.

### `/_posts/`

Són aquelles pàgines que per la seva naturalesa tenen una data. Bàsicament, són notícies i articles publicats, amb data,
autor, etc.

### `/_sass/`

Estils CSS de la pàgina. He intentat separar cada entitat en un fitxer per trobar més fàcilment el que es busca.

### `/_site/`

Generat automàticament quan s’executa la pàgina. Directori de només lectura.

### `/assets/`

Se sobreentén. Hi ha la càrrega mestra de CSS, les fonts, les coordenades GPS de les entitats geogràfiques, unes imatges
obsoletes, _scripts_ de _JavaScript_ que cal executar i els _node_modules_.

### `/ceoc/`

Són les pàgines individuals de cadascun dels concerts del cicle (començant per 2024). Hi apareix l’orgue, el programa,
l’intèrpret i els comentaris al programa. En un futur també s’hi inclourà referències al turisme i altres activitats
a realitzar (té més sentit en poblacions aïllades).

### `/orgues/`

Són les pàgines individuals de cadascun dels orgues de l’inventari.

### `/pages/`

Són tota la resta de pàgines individuals. Totes tenen un `permalink` que fa que el seu URL no comenci per `pages/`.
És per no tenir-les soltes a l’arrel.

### `/scripts/`

Conté tots els _scripts_ de Python per mastegar les dades de la web. Referiu-vos a la secció
[Generació de dependències](#generació-de-dependències) per a més informació.

### `/venv/`

Autogenerat. Conté l’entorn virtual per executar els _scripts_ de Python.

### `Fitxers solts`

- `.gitlab-ci.yml`. Definició per construir la web a CI i publicar-la al món. Vegeu [CI (GitLab)](#ci-gitlab).
- `.jekyll-metadata`. Autogenerat.
- `_config.yml`. Configuració de Jekyll.
- `_config_dev.yml`. Configuració de Jekyll específica durant el desenvolupament de la pàgina.
- `Gemfile`. Definició dels plugins de Ruby externs.
- `Gemfile.lock`. Autogenerat.
- `google….html`. Galeta de màgia negra per fer el seguiment de la pàgina amb Google Analytics.
- `index.md`. Ha d’existir. És la pàgina inicial. És un fitxer buit.
- `requirements.txt`. Definició de dependències de Python.

## Descripció del _breadcrumb_

Es tracta de crear pàgines intermèdies, com les que ja existeixen pels edificis
que tenen més d’un orgue, per a cada província, comarca i poble (municipi) de la web. Aquestes pàgines tenen molts
enllaços interns, que ajuden a un bon SEO.

La pàgina es gestiona mitjançant un layout segons si és edifici, municipi, comarca o província. En aquest layout hi ha
la llista dels orgues. Cada llista té enllaços. En aquests enllaços s’hi afegeixen metadades que les llegirà JavaScript
quan creï el mapa.

Tenir un breadcrumb ajuda l’usuari a navegar dins el territori de manera ordenada i elegant. Cada pàgina generada té
la llista d’orgues netament ordenada i un mapa.

### Mapes del breadcrumb

Hi ha gent que s’ha dedicat a traçar els límits territorials amb OSM (OpenStreetMaps) i ha pujat aquestes dades al
servidor, disponibles per a tothom. Aquests límits, o, potser millor dit, la descripció de les limitacions territorials
(comarques, províncies, municipis) vé en forma de _relation_, una espècia d’entitat on hi ha els polígons dels límits
dibuixats, la capital, el nombre d’habitants i tantes altres característiques.

De moment, només ens interessen els límits. OSM té un sistema de crides/API per demanar aquesta informació. Es diu
Overpass API. Hi ha una utilitat en línia per crear _queries_ a aquesta immensa base de dades i baixar-se la informació
en diferents formats; el que ens interessa és GeoJSON. Però fer això per a cada província, comarca o municipi és molt
laboriós. Existeix una API escrita en Python per accedir a aquesta base de dades i obtenir la informació per tractar-la
directament. Es diu [osm-python-tools](https://github.com/mocnik-science/osm-python-tools/blob/main/docs/overpass.md).
Bé, doncs ja que existeix la farem servir.

El procés és, a grans trets, el següent:

- Obtenir les id dels diferents límits territorials
- Descarregar-se les coordenades GPS d’aquests límits
- Recuperar aquestes dades amb JavaScript i mostrar-les al mapa amb la llibreria Leaflet.

#### Obtenir les _id_ dels límits territorials

A grans trets, buscant a Google «Alt Penedès osm relation» surt
[aquesta pàgina](https://www.openstreetmap.org/relation/2809672). D’aquí es pot copiar el codi de la relació, en aquest
cas, 2809672, i apuntar-lo al fitxer `/_dades/orgues.yml`. En aquesta mateixa pàgina hi ha un cercador, que és prou ràpid per
buscar altres límits. Només cal fixar-se en el `border-type` que sigui el que busquem: `comarca`, `municipi` etc.

**Nota**: per les dues Cerdanyes, no he trobat el límit territorial de la part de Girona; sí la de Lleida. Totes dues
tenen el límit de la comarca sencera.

#### Com descarregar-se les coordenades GPS dels límits

Hi ha un script, `scripts/get-geojson.py`, que es connecta a la base de dades d’OSM, li demana la relació i guarda només
tota la informació relacionada amb el perímetre. Aquest procés és molt lent, ja que les queries que fa internament la
llibreria així ho són. Va tardar ben bé mitja hora a baixar-me totes les dades. Són 12 MB de coordenades GPS. Com que són
dades estàtiques i com que en són moltes, no convé tenir-les controlades amb Git; així que es pugen al servidor
nextcloud automàticament, com les imatges, i CI se les baixa per compilar la web.

Abans de preguntar com funciona, llegeix el codi; és curt i prou fàcil d’entendre. El que ens interessa és dibuixar els
contorns dels límits territorials. Els límits territorials (ja dic, províncies, comarques, etc.) es diuen _relations_.
El contorn està dins la geometria d’aquestes relacions. Doncs això és el que fa l’_script_. Per a cada límit,
el qual hem obtingut la id de la relació manualment cercant per internet, li demanem totes les relacions i la geometria
d’aquestes. Les guardem en format geoJSON dins dels assets. I, amb JavaScript, només cal carregar aquest fitxer i
passar-lo a l’API dels mapes, que és LeafLet.

Per això, hi ha l’altre script, `scripts/get-geo-limits.py`, que s’encarrega de baixar-se els fitxers generats que viuen
al _nextcloud_ i col·locar-los a l’arbre de fitxers de la web. A més, calcula el requadre que ocupa el límit territorial
en coordenades GPS i el desa en un altre fitxer: `/_data/limits-geografics.yml`.

Els límits descrits amb GeoJSON es mereixen una [pàgina de documentació](https://en.wikipedia.org/wiki/GeoJSON) a part.
Com que els límits que estem tractant sempre són polígons, només n’hi ha de dos tipus: els normals i els que en tenen
més d’un. Seguint la descripció de les dades d’aquesta pàgina de documentació, es pot decidir com ajuntar totes les
coordenades GPS i buscar-ne el mínim o el màxim segons procedeixi.

#### Com mostrar aquests límits en un mapa

Com he dit, aquestes pàgines del _breadcrumb_ es gestionen amb un _layout_. Amb Jekyll (Liquid) és molt senzill
recuperar la informació del fitxer `limits-geografics.yml`. Aquesta s’incrusta en els atributs del mapa.

Pel que fa al dibuix del contorn del límit, Leaflet té una funció per llegir dades GeoJSON. Només fa falta carregar
el fitxer des de disc (canvia la manera si n’hi ha una de millor) i passar-lo directament a la llibreria. S’hi poden
afegir estils gràfics, com ara gruix i color de la línia, color d’emplenament, etc. Aquest treball es fa en el fitxer
`/assets/js/leafletMapGeneric.js`. Aquest script és cridat per a cada _layout_ que l’ha de menester, utilitzant el
_frontmatter_ d’aquest.

## Descripció de la pàgina principal de l’inventari

Hi ha tres tipus de fitxers involucrats per crear la pàgina principal dels orgues automàticament.

- `/_data/orgues.yml`. És un fitxer que conté la informació necessària per crear enllaços amb els noms de les províncies,
  comarques, pobles i edificis amb orgues. Té quatre apartats: `provincies`, `comarques` , `bisbats` i `orgues`. Mentre es mantingui
  l’organització territorial actual, només cal modificar l’apartat d’`orgues`. Aquest últim apartat conté la informació
  dels edificis que tenen orgue:
  - `nom`: nom de l’edifici. S’utilitza per generar el títol de la pàgina d’orgues. També s’utilitza per generar
    la pàgina amb els concerts del cicle.
  - `link`: és la cadena de caràcters que s’utilitza per anomenar els fitxers i/o carpetes. No pot contenir espais
    ni altres caràcters que no pertanyin als caràcters visibles del codi [ASCII](https://ss64.com/ascii.html).
  - `adreca`. Carrer, núm., CP Poble. Província
  - `geolocalitzacio`. Dos camps: `latitud` i `longitud`. Per posar una icona al mapa dels orgues.
  - `wip`. Booleà opcional. Un edifici o orgue amb `wip: true` apareix als llistats, però sense enllaç ni pàgina individual; els scripts també l'exclouen dels comptadors i de les llistes d'orgueners.

  Aquesta informació s’utilitza en força llocs per ordenar el contingut. Altres _scripts_ la processen.

- `/_layouts/orgues.html`. Llegeix el fitxer anterior i d’altres generats (ara ho explicaré) per crear la pàgina amb
  tots els orgues del principat, que de moment té una taula de cerca i uns desplegables amb els orgues ordenats de diferents
  maneres. Aquest fitxer dóna l’estil visual a la pàgina dels orgues.

- `/pages/orgues.md`. Fitxer de markdown que utilitza el layout d’orgues. No té cap mena de contingut i només serveix
  en l’àmbit intern de la pàgina. No cal ni s’ha de modificar.

És important mantenir l’estructura de fitxers definida a `_data/orgues.yml`, és a dir: `provincia/comarca/poble/edifici/`
o bé `provincia/comarca/poble/edifici/orgue`. D’aquesta manera, els enllaços es poden generar automàticament.

## Descripció de les pàgines individuals per a cada orgue

Hi ha 3 directoris que contenen la informació, la disposició i les imatges (obsolet) que segueixen l’estructura
mencionada a `orgues.yml`:

- `/orgues/`. Aquí hi ha les pàgines dels orgues. Aquestes pàgines contenen la història i la resta de material per
  presentar, com ara enllaços a associacions, bibliografia, documents externs, etc. No hi ha ni les imatges ni la disposició
  de l’orgue de manera explícita; només hi ha "`include`s" que s’encarreguen de generar aquesta informació per tots els
  orgues de manera automàtica. I sap d’on treure la informació perquè tota la informació segueix la mateixa estructura de
  fitxers.

- `/_data/disposicions/`. Aquí hi ha les disposicions dels orgues i altres dades, com el temprament,
  constructors i les diferents actuacions que s’hi han fet. És important ser molt estrictes amb el format.
  Vegeu [Detall de la informació de cada orgue (`yml`)](#detall-de-la-informació-de-cada-orgue-yml) per a tenir la
  informació completa.

- `/assets/img/orgues`. _OBSOLET, de moment_ Aquí hi ha les fotografies. **Només són previsualitzacions**, molt petites i de mala qualitat; les
  fotografies seran servides per un proveïdor extern a la pàgina web, com qualsevol núvol. Aquí hi ha una previsualització
  en cas que el núvol fallés. Les imatges no tenen una mida superior a 150 píxels i ocupen al voltant de 5kB. Hi ha disponible
  un script a `/scripts/` per fer la conversió d’imatges i arxivar-les correctament.

Referiu-vos a [Com afegir nous orgues a l’inventari](#com-afegir-nous-orgues-a-linventari) si és del vostre interès.

# Organització jeràrquica dels orgues

No hi ha ni dos ni tres ni quatre orgues en aquesta pàgina; n’hi ha centenars, cadascun amb les seves explicacions,
fotografies i disposicions. Per aquest motiu,
és important que estigui tot ben organitzat per poder-ho automatitzar.

El criteri per organitzar els orgues és el següent:

    província/comarca/municipi/edifici

I si l’edifici té més d’un orgue:

    província/comarca/municipi/edifici/orgue-major
    província/comarca/municipi/edifici/orgue-menor

Tot el que es refereixi als orgues anirà amb aquesta estructura:

- `/_data/orgues.yml`
- Disposicions i dades tècniques dels orgues a `/_data/disposicions/`
- Història i definició de la pàgina individual a `/orgues/`
- Imatges dels orgues al núvol

## Format del fitxer `/_data/orgues.yml`

Aquest fitxer és la mare dels ous. Hi ha tota la informació necessària per localitzar programàticament un orgue. Hi ha
tota la informació referent a l’instrument fins a l’edifici que el conté. Tota la descripció tècnica no apareix, aquí.
L’estructura principal és la següent:

```yaml
orgues:
  - link: barcelona
    comarques:
      - link: alt-penedes
        poblacions:
          - nom: Vilafranca del Penedès
            link: vilafranca
            bisbat: sant-feliu
            relation: 344518
            edificis:
              - nom: Basílica parroquial de Santa Maria
                link: santa-maria
                adreca: Plaça de Jaume I, S/N, 08720…
                geolocalitzacio:
                  latitud: 41.38557761813415
                  longitud: 1.7208841749660506
                civil: false # especificar-ho només quan sigui 'true'
              - nom: Església parroquial de la Santíssima Trinitat
                link: santissima-trinitat
                adreca: Carrer de la Cort, 1, 08720…
                geolocalitzacio:
                  latitud: 41.38557761813415
                  longitud: 1.7208841749660506
                orgues:
                  - nom: Orgue major
                    link: orgue-major
                  - nom: Positiu
                    link: positiu
```

## Format de la capçalera dels fitxers `*.md`

El frontmatter dels fitxers dels orgues han de contenir la següent informació:

```yml
layout: base/orgue # obligatori i és sempre base/orgue
redirect_from: # obligatori
  - pages/orgues/girona/ripolles/queralbs/santuari-nuria # obligatori per a orgues afegits abans del canvi d'enllaços (06/01/2025)
  - orgues/queralbs # obligatori. Enllaç curt per a compartir a les xarxes (nota 1)

fotos: # opcional (nota 2)
  - nom: foto.jpg # obligatori
    alt: Descripció de la fotografia # obligatori
    caption: Peu de foto # opcional. Accepta sintaxi markdown
    autor: Pau Xic # opcional. Es dóna prioritat a aquest camp davant de "Creator", "Rights" o "Artist" de les dades Exif. Accepta sintaxi markdown
    portada: 21% o bé 410 # opcional. Object position o píxel superior esquerra (alçada) on comença el retall
links: # opcional. Enllaços recomanats
  - nom: Späth Orgelbau AG # obligatori. Accepta sintaxi markdown
    link: http://spaeth.ch/Orgelbau/Orgeln/santa-margarida-i-els-monjos-cataluna/ # obligatori
documents: # opcional. Documents relacionats
  - nom: L'orgue de Santa Maria del Mar # obligatori. Accepta sintaxi markdown
    autor: Pau Xic # opcional, però recomanat
    link: https://nextcloud.acorgue.cat/s/P5dXP39WmmsyGfi/download # obligatori
    type: pdf # obligatori. S'utilitza per triar la icona
```

**Nota 1**: l'enllaç per a compartir a les xarxes és l'últim de la llista. Així, quan es vol compartir
la pàgina es pot recuperar fàcilment i programàticament.

- Si només hi ha un edifici amb orgue en un municipi:
  - Si només hi ha un orgue a l'edifici: `orgues/municipi`
  - Si hi ha més d'un orgue a l'edifici: `orgues/municipi-orgue`
- Si hi ha més d'un edifici amb orgue en un municipi:
  - Si només hi ha un orgue a l'edifici: `orgues/edifici-municipi`
  - Si hi ha més d'un orgue a l'edifici: `orgues/edifici-municipi-orgue`

**Nota 2**: referiu-vos a la secció [Afegir imatges en un orgue](#afegir-imatges-en-un-orgue).

# Com afegir nous orgues a l’inventari

## Passos

1. Triar un nom curt, però digne, per l’enllaç de l’edifici. Amb això vull dir, que enlloc de posar `monges` perquè és
   l’únic monestir de monges del municipi, posar `monestir`, que queda més net de cara a la galeria. Per a esglésies amb
   més d’un orgue (punt núm. 3), és habitual anomenar el _gran_ `orgue-major` i el _petit_, `orgue-menor` si ambdós es troben dins el
   mateix espai sonor. Hi poden haver excepcions. Si un és el de la nau i l’altre el d’una capella més o menys aïllada
   de la nau, he seguit el criteri d’anomenar el _gran_ `orgue-major` i l’altre, `capella` o `santíssim`. Hi poden haver
   excepcions.

2. _Per edificis amb un sol orgue_. Cal crear dos fitxers:
   - `/orgues/provincia/comarca/poble/edifici.md`. Conté la història, la descripció de l’instrument, els enllaços i
     documents relacionats i una descripció de les fotografies (vegeu algun dels fitxers com a exemple).
   - `/_data/disposicions/provincia/comarca/poble/edifici.yml`, on hi ha la disposició de l’orgue i altres dades
     tècniques. Vegeu [Detall de la informació de cada orgue (`yml`)](#detall-de-la-informació-de-cada-orgue-yml) per a
     tenir la informació completa.

3. _Per edificis amb més d’un orgue_. Cal crear més fitxers i alguna carpeta. Preneu com a exemple el Conservatori de Barcelona:
   - `/orgues/provincia/comarca/poble/edifici.md`. És un fitxer que només conté el _frontmatter_ dient que és un fitxer
     d’edifici. Si es vol escriure la història de l’edifici, va aquí.
   - Una carpeta anomenada `/orgues/provincia/comarca/poble/edifici/`. A dins, hi aniran els fitxers `*.md` de cadascun
     dels orgues de l’edifici.
   - Una carpeta anomenada `/_data/disposicions/provincia/comarca/poble/edifici/`. A dins, hi aniran els fitxers `*.yml`
     de cadascun dels orgues de l’edifici.

4. Després cal afegir, al lloc corresponent, l’edifici al fitxer `/_data/orgues.yml`. Si l’edifici té més d’un orgue,
   cal afegir un nivell extra `orgues:` i llistar-los amb el nom i l’enllaç corresponent. Preneu com a exemple el Conservatori
   de Barcelona.

## Múltiples versions del mateix orgue

Ara bé, per fitxes on es vol especificar diferents disposicions del mateix orgue, com en el Palau Nacional o com a Sant
Cugat del Vallès, el que he explicat a sobre no val, perquè tindríem dos orgues diferents amb dues fitxes diferents; i el
que cerquem és tenir una sola fitxa (un sol orgue, un sol edifici) amb dues disposicions diferents.

De moment, la manera que he trobat és crear dos (o més) fitxers `*.yml`, un d’ells amb el nom de l’edifici (normalment, el que
té la disposició actual). I, a la fitxa `*.md`, cridar la disposició amb el paràmetre `edifici="edifici-antic"` per referenciar
altres disposicions.

Fet així, s’aconsegueix que la taula principal dels orgues pugui aconseguir la composició correcta de l’instrument (i, en
un futur, altres dades de l’instrument actual).

## Afegir imatges en un orgue

S’afegeixen al fitxer `.md`, en el _frontmatter_. Referiu-vos a la secció [Format de la capçalera
dels fitxers `*.md`](#format-de-la-capçalera-dels-fitxers-md).

El camp `nom` és obligatori per identificar la fotografia. El camp `alt` és obligatori per
l’accessibilitat de la pàgina. El camp `caption`, `autor` i `portada` són opcionals.

Els camps `caption` i `autor` accepten sintaxi `Markdown`. El camp `portada` accepta un percentatge,
corresponent a l’etiqueta CSS `background-position: 0% 25%` o bé el píxel superior esquerra de
l’inici del retall de la imatge. Vegeu la secció [Com designar una imatge
portada](#com-designar-una-imatge-portada).

Les imatges s’han d’afegir al [núvol](https://nextcloud.acorgue.cat) (usuari `web-aco`, carpeta
`web/img/orgues`), seguint l’estructura de `orgues.yml`, com és habitual. S’accepten imatges en
`*.jpg` i `*.webp` (`*.heic` no està suportat). Altres formats d’imatge no estan prou comprimits per
ser útils en una pàgina web.

Recorda executar l’_script_ corresponent després d’afegir les imatges. Referiu-vos a la secció [He
canviat una cosa. Què cal executar?](#he-canviat-una-cosa-què-cal-executar).

## Detall de la informació de cada orgue (`yml`)

En un fitxer `.yml` que en facilita l’edició (per un humà) i posteriorment, una màquina en pot crear una base de dades.

### Resum o plantilla

```yaml
historic:

constructor:
  nom:
  sort-nom:
  any:
  sort-any:
  opus:

actuacions:
  - nom:
    sort-nom:
    any:
    sort-any:
    actuacio: N, AC, AM, RO, RC, RS, RP, RH, AF, TR, TF, MO
    detalls:

diapaso:
  nota:
  frequencia:
  temperatura:
  registre:

temperament:

estat:
  - any:
    nota: [0-4]
    detalls:

emplacament:

transmissio:
  notes:
  registres:

composicio:

teclats:
  - nom:
    extensio:
    registres:
      - nom:
        peus:
        partit:
        llengueta:
        falta:

pedal:
  nom:
  extensio:
  registres:
    - nom:
      peus:
      partit:
      llengueta:
      falta:

acoblaments:
  - nom:
    partit:
    falta:

efectes:
  - nom:
    falta:
```

### Secció d’història

- `historic`. Booleà. És un indicador per no comptabilitzar l’orgue com a orgue existent. S’utilitza quan en un article
  es vol fer menció d’una disposició d’un orgue anterior a l’actual, que ja no existeix o previ a una modificació o una
  restauració.

- `constructor`. Cal especificar un `nom` i un `any` (el primer que va fer alguna cosa). És molt relatiu. Per exemple, a la
  catedral de Barcelona, la caixa és de 1540, però l’orgue de dins és d’en Gabriel Blancafort dels anys 70–80. En aquest cas, seria partidari
  de posar Gabriel Blancafort. A la història (l’article) ja s’especificarà que la caixa és antiga i que hi han hagut
  tants orgues de tal i tal.
  - `nom`: Organería Española, SA
  - `sort-nom`: Organería Española, SA. En cas que el nom en si porti coma, cal especificar aquest camp.
  - `any`: mitjan s. XVIII
  - `sort-any`: 1750. En cas que `any` no sigui un nombre enter, cal especificar aquest camp.
  - `opus`: Número d’opus, si es té. De moment no es mostra.

- `actuacions` (llista). És una llista d’actuacions.

  Cada element:
  - `nom`: Organería Española, SA
  - `sort-nom`: Organería Española, SA. En cas que el nom en si porti coma, cal especificar aquest camp.
  - `any`: mitjan s. XVIII
  - `sort-any`: 1750. En cas que `any` no sigui un nombre enter, cal especificar aquest camp.
  - `actuacio`: AC, AM (separats per coma). No sempre cada actuació acomplerta es contindrà en només un d’aquests codis; potser en dos.
    Per exemple: Manresa, Sant Cugat del Vallès, Sarrià, etc. Els acrònims següents són els vàlids:
    - `N`. Orgue nou. Pot implicar l’aprofitament de material anterior, sobretot sonor, però sense seguir la mateixa línia
      estètica. La concepció, moble, etc. és completament nou.
    - `AC`. Acabament. Acabament del projecte inicial, normalment dut a terme pel mateix orguener en fases diferents. El
      material original no va arribar a existir mai.
    - `AM`. Ampliació. Ampliació de l’orgue. Implica la creació de material nou i reaprofitament de l’anterior per fer un
      orgue més gran. Normalment, la part existent es manté intacte o quasi intacta.
    - `RO`. Reorganització. Amb el material existent, reordenar la disposició. Pot implicar canvi de secrets. La majoria
      del material sonor es conserva. Se’n pot afegir de nou.
    - `RC`. Reconstrucció. Treball històric per recuperar un material inexistent. Habitual en els treballs per repoblar orgues
      espoliats durant la Guerra Civil. Implica treballs implícits de restauració.
    - `RS`. Restauració. Recuperació de la funcionalitat de l’orgue. Pot implicar la creació de material nou però no per
      la falta de l’original, sinó pel seu impossible aprofitament a causa del mal estat.
    - `RP`. Reparació. No és una restauració perquè l’abast dels treballs és petit. Quelcom lleu ha passat i s’ha reparat.
    - `AF`. Afinació general.
    - `RH`. Reharmonització. S’entén que un orgue només s’harmonitza una vegada, que és quan es construeix. Que tota
      harmonització posterior és una reharmonització.
    - `TR`. Trasllat de l’instrument.
    - `TF`. Transformació de l’instrument. Es canvien registres, etc. El que feia OESA i Blancafort amb el moviment _orgelbewegung_.
    - `MO`. Manteniment ordinari.
    - `NE`. Neteja. Desmuntar, netejar i tornar a muntar. Implica afinació i repàs d’harmonització, però és inherent a
      la tasca de neteja.
  - `detalls`: Quelcom que es vulgui especificar de tal actuació. El gruix de l’explicació ha d’anar a l’article, no pas aquí. De moment, no s’utilitza aquest camp.

#### Fusió de constructors i actuacions (futur)

**S’està treballant en aquesta nova aproximació**. En lloc de `constructor` i `actuacions`, seria convenient posar `orgueners`:

```yaml
orgueners:
  - nom: Vallès i Vallès, Isidre
    any: 2003
    categoria: N
  - nom: Vallès i Vallès, Isidre
    any: 2005
    categoria: AC
```

o bé

```yaml
orgueners:
  - nom: Puggina, Silvio
    any: 1922
    categoria: N
  - nom: Blancafort, Gabriel
    any: 1988
    categoria: RS, AM
    detall: Restauració, canvi de pedaler i petita ampliació
  - nom: Álvarez, Carlos M.
    any: 2022
    categoria: RO
```

### Detalls tècnics

- `diapaso`. El camp `registre` és opcional. La resta, tot i que es contempla que hi puguin faltar, són necessaris per
  la integritat de l’inventari. Sense unitats. El separador decimal és un punt.
  - `nota`: a'
  - `frequencia`: 440.2
  - `temperatura`: 20.5
  - `registre`: **Resum: nom del registre com més breu millor**. `Flautat`; `Flautat 8'` si cal desambiguar-lo d’un altre
    registre amb el mateix nom i diferent tessitura; `Flautat de l’orgue major` si existeix un altre registre amb el
    mateix nom en un altre teclat; `Flautat 8'` de l’orgue major si existeixen altres registres amb el mateix nom i diferent
    tessitura en el mateix teclat i en altres teclats.

    **Nota**: el símbol de peu és una prima «′» (U+2032).

- `temperament`. Temperament amb minúscula: «igual» o «mesotònic de quart de coma».

- `estat` (llista manualment ordenada de més antic a més actual). Manera interna de classificar els orgues per saber com es troben, si mai
  surten diners de sota les pedres per restaurar-los. És una mica subjectiva i potser sota el criteri de diferents organistes
  i orgueners, un mateix orgue pot estar en dues categories diferents. Hi haurà orgues que serà difícil posar-los-hi una nota,
  perquè pot restar en dues categories segons com es miri. **Només es mostra l’estat més recent**.

  Cada element:
  - `any`: 2017
  - `estat`: (obsolet)
  - `nota`: 4 (nombre enter)
    - `0`: Intocable per falta de tubs, teclats, manxes, etc. Exemple: Bràfim.
    - `1`: Sona, però el seu estat és deplorable. No pot tocar ni una missa. Exemple: Santes Creus.
    - `2`: En funcionament precari. La majoria de l’orgue no es pot fer sonar i el fa un orgue limitat.
      Pot tocar una missa (amb certa dificultat) però no és apte per un concert. Exemple: Jesuïtes de Casp.
    - `3`: En funcionament. Quasi tot l’orgue pot sonar i té activitat musical regular. Pot tocar concerts, tot i que s’han
      de fer filigranes per fer sonar l’orgue dignament. Necessita una restauració. Exemple: Sant Pere de Figueres.
    - `4`: En bon funcionament. Té manteniment i activitat concertística regular. Pot no estar al 100%, però s’hi acosta molt.
      No s’han de fer filigranes per tocar un concert.
  - `detalls`: Qualsevol cosa que es vulgui afegir al respecte. El gruix de l’explicació ha d’anar a l’article, no aquí. De moment, no s’utilitza aquest camp.

- `emplacament`: on es troba l’orgue actualment. Breu i concís:
  - Lateral, costat de l’Evangeli/Epístola
  - Tribuna
  - Cor

- `transmissio`. Breu i concís. Qualsevol apreciació, a l’article de l’orgue
  - `notes`: mecànica, màquina Barker, elèctrica
  - `registres`: mecànica, pneumàtica, elèctrica

### Composició

- `composicio`: 30, III/P. Resum del nombre de jocs (vegeu la secció [Registre vs. joc](#registre-vs-joc)), teclats i pedalers.
  El nombre de jocs, en nombres aràbics, el nombre de teclats manuals, en nombres romans. Si disposa de pedaler o contres,
  segueix una barra i una `P` per pedaler (alemany o francès) i una `C` per contres (ibèriques).

- `teclats` (llista). `nom`, `extensio` i `registres` dels manuals.
  - `nom`: I. Manual. O bé: I. Cadireta
  - `extensio`: "56 notes: C-g'''" (entre cometes). Notació Helmholtz. _(v. nota 1)_
  - `registres` (llista):

    Cada element:
    - `nom`: Bordó
    - `peus`: 8' _(v. nota 2)_
    - `partit`: c'/cs' _(v. nota 1)_
    - `llengueta`: `true` (booleà). Només cal especificar-ho si és vertader.
    - `falta`: `true` (booleà). Només cal especificar-ho si és vertader.

- `pedal`. `nom` (opcional), `extensio` i `registres` del pedal.
  - `nom`: (opcional)
  - `extensio`: "30 notes: C-f'" (entre cometes). Notació Helmholtz. _(v. nota 1)_
  - `registres` (llista): com la dels teclats

- `acoblaments` (llista):

  Cada element:
  - `nom`: I/P. Amb números i barres creuades: II/I, II/P i no *II-I, *II-P
  - `partit`: c'/cs' _(v. nota 1)_
  - `falta`: `true` (booleà). Només cal especificar-ho si és vertader.

- `efectes` (llista). Aquest camp apareix amb el títol de «Miscel·lània» al web; així que tot el que no hi càpiga en els altres apartats i que
  sigui rellevant en una disposició d’un instrument, va aquí.

  Cada element:
  - `nom`: Expressió III. O bé: Rossinyol, Trémolo II, Combinador electrònic, Combinacions fixes, etc.
  - `falta`: `true` (booleà). Només cal especificar-ho si és vertader.

**Nota 1**: L’extensió dels teclats utilitza caràcters UTF-8. El guió per denotar una extensió de notes cromàtiques separades
per un semitò es denota amb un guió mitjà «–» (U+2013). Les diferents octaves usen el caràcter prima. Existeixen
caràcters per una, dues, tres i quatre primes seguides: «′» (U+2032), «″» (U+2033), «‴» (U+2034) i «⁗» (U+2057).
Aneu a la secció [Introducció de caràcters especials](#introducció-de-caràcters-especials).

**Nota 2**: El símbol de peus s’expressa amb una prima «′» (U+2032).

### Consideracions generals

#### Camp `partit`

S’utilitza aquest camp com un calaix de sastre per observacions curtes i concises:

- Partits de registres: c'/cs' (un joc amb dos tiradors), c'|cs' (un joc amb partició interna i un tirador)
- **en batalla**
- **C-h prestat del Subbaix**
- I poca cosa més. Si hi ha altres consideracions, cal especificar-les a l’article, no aquí.

#### Registre vs. joc

Un joc és una família de tubs que canten amb el mateix timbre. Un registre és el mecanisme a la consola per activar o
desactivar un joc o altres mecanismes interns de l’orgue (segons Jordi Alcaraz).

Cada entrada en els teclats i pedaler és un joc. Hi ha diferents casuístiques:

- 1 joc, 1 tirador. L’habitual. S’especifica l’extensió si no és la del teclat.
- 2 jocs, 1 tirador. És on hi ha confusions. L’organista pot escollir? Si és que no, com un _bajoncillo y clarín_, el
  considero 1 joc i tindrà una entrada a la base de dades; s’especificarà opcionalment a on parteix: c'|cs'. Si l’organista
  pot escollir, per exemple, estirant més o menys el tirador per afegir una rengla de tercera en un ple, llavors els
  considero 2 jocs diferents, amb dues entrades a la base de dades. Caldrà, però, afegir una nota a l’article que expliqui aquest mecanisme.
- 1 joc, 2 tiradors. És el partit comú. Les etiquetes tenen el mateix nom. Tenen una entrada i es denota la partició amb
  c'/cs'. També pot ser una transmissió. En aquest cas, s’anoten dues o més entrades a la base de dades i es denota
  qui és transmissió de qui.
- 2 jocs, 2 tiradors. Són les parelles de registres que s’acostumen a fer en moltes descripcions, com les de Sant Felip
  Neri. Tot i que els _baixons_ i la _trompeta magna_ es llisten com un registre (i tenen el mateix número), els considero
  dos jocs diferents, amb dues entrades independents, anotant la seva extensió corresponent.

Pels orgues que fan trampa (extensions i préstecs). No es pot generar la informació de la composició automàticament; si
els jocs són famílies de tubs, i només té tres famílies (de 80 o més tubs), llavors només té tres jocs.

### Dissertació sobre extensió, préstec o manlleu i transmissió de registres i jocs

**Definició**: Un _joc_ és una col·lecció de tubs de la mateixa família.

**Definició**: Un _registre_ és un mecanisme per activar una part o la totalitat d’un o més jocs, altres elements sonors
o efectes.

**Axioma**: Els teclats manuals tenen base de 8′ i el pedaler, de 16′.

**Axioma**: El teclat més important és l’orgue major. Segueixen en igual importància el pedal i el segon teclat després de l’orgue major (sigui
cadireta, positiu, recitatiu). Segueix el recitatiu, etc.

#### Extensió

**Definició**: El registre _A_ es considera extensió del registre _B_ quan _A_ i _B_ són de la mateixa família,
tenen alçades diferents i comparteixen la totalitat dels tubs corresponents a la tessitura coincident. A més, és requerit
que _A_ posseeixi, **en exclusiva**, els tubs necessaris per a completar la tessitura resultant de no tenir la mateixa alçada
que _B_. És requerit que _B_ sigui un registre real o una extensió d'un altre; no pot ser una transmissió. 

Per definir qui és extensió de qui, _A_ serà extensió de _B_ quan _B_ coincideixi amb la base del cos sonor al qual pertany,
o, en tot, cas, quan _B_ està més a prop de la base del cos sonor que _A_.

Si existeix una cadena d’extensions, per exemple, _A_ 8′, _B_ 4′ i _C_ 2′, _B_ no comparteix en exclusiva els tubs per
completar l’octava superior, car són utilitzats també per _C_. En aquest cas, es llegeix que _B_ és extensió d’_A_ i que
_C_ és extensió de _B_.

El registre i totes les seves extensions computen com un sol joc.

**Exemples**:

- Bordó 8′ (P) és extensió del Bordó 16′ (P).
- Bordó 16′ (I) és extensió del Bordó 8′ (I).
- Greu 32′ (P) és extensió del Subbaix 16′ (P). 

#### Préstec o manlleu

**Definició**: Un registre _A_ presta o manlleva _N_ notes d’un altre registre _B_ d’un joc diferent, sent _N_ < tessitura d’_A_ i _B_, per
a completar la tessitura del teclat al qual pertany _A_ utilitzant menys tubs, ja sigui per economia d’espai, de vent o
de diners.

_A_ presta o manlleva de _B_ quan la totalitat dels tubs de _B_ es corresponen a la família que indica el registre.

Els préstecs o manlleus de registres computen com a jocs diferents, car, per norma general, _N_ no acostuma a ser més
gran de 12, implicant que gran part de la tessitura d’_A_ i de _B_ tenen caràcter propi.

**Exemples**:

- Salicional 8′ presta C–G de Bordó 8′
- Bordó 8′ presta C–H de Bordó 16′ (se sobreentén que en la tessitura c–h respecte del Bordó de 16′)

#### Transmissions

**Definició**: Un registre _A_ és transmissió d’un registre _B_ quan _A_ fa sonar tubs de _B_ sense comportar cap
mena d’extensió. Si _A_ i _B_ pertanyen a cossos sonors distints, _A_ és transmissió de _B_ quan el cos sonor al qual pertany
_B_ posseeix els tubs. Quan _A_ i _B_ comparteixen el mateix cos sonor, _A_ és transmissió de _B_ quan _B_ està associat al
teclat (cos sonor _virtual_) més important.

Els registres i les seves transmissions computen com un sol joc.

**Exemples**:

- Subbaix 16′ (P) és transmissió del Bordó 16′ (I)
- Bordó major 16′ (I) és transmissió del Bordó major 16′ (III), car els tubs es troben en el cos sonor del III.
- Principal 4′ (P) és transmissió del Flautat 8′ (I)
- Baixons 4′ (C–c') és transmissió de la Trompeta de batalla 8′ (C–g‴)

#### Altres casos

- Extensions que es realitzen amb préstecs. Trompeta de batalla 16′ és l’extensió de la Trompeta de batalla 8′ i
  l’extensió C–H és prestada de la Tuba 16′.

#### Exemple real

**La Seu d'Urgell, Sagrada Família**

Proposo aquest esquema del recorregut de l'Octava entre els teclats manuals:

    II:      P4   12a --e--> Q
             ^    ^           \
             |   /             e
             t  e               \
             | /                 v
    I:       O                   19a --e--> 22a
           / | \
         t+p t  t
         /   |   \
        v    v    v
    P: P8    F4   Lleno

Debat:
- És clar que `P4` és la transmissió d'`O`. Diu la definició:

    > Quan _A_ i _B_ comparteixen el mateix cos sonor, _A_ és transmissió de _B_ quan _B_ està associat al
      teclat (cos sonor _virtual_) més important.

- **No està permès extensionar una transmissió**. Una extensió és d'un registre real, no pas d'una còpia. Per això, 
  la `12a` no és una extensió de `P4`.
- Està clar que `Q` és una extensió de `12a`. 
- Entre `O`, `Q` i `19a`, és més difícil de decidir. Plantejo aquest altre escenari, més senzill:

        I: 8' --e--> 4' (+12) --e--> 2' (+12)
  Aquí, a cada extensió, s'afegeixen 12 tubs. Si el teclat té 61 tecles, en total, el joc tindria 61 + 12 + 12 = 85 tubs.
  Ara bé, plantejo aquest altre escenari, més rar:

        I: 8' --e--> 4' (+12)        2' (+24)
           |                         ^
           |-------------e-----------|
 
  Continuem tenint dues octaves extra, tres registres en total, però el nombre de tubs no és el mateix. Si es fa una
  extensió de 8′ a 2′, cal afegir 24 tubs; sumats a una segona extensió de 8′ a 4′, en total hi ha 97 tubs, 12 dels quals
  seran ben bé iguals. Hom s'hauria de plantejar aquest escenari si són un o dos jocs a computar. Tanmateix, aquest
  escenari és hipotètic perquè no té molt sentit constructivament parlant.

  Tornant al cas inicial, com que es tracta d'un salmer `UNIT`, tot i que les diferents alçades no estan a tots els 
  teclats, la línia d'extensió ha d'anar de `Q` a `19a` per no _crear_ tubs extres que no existeixen. 
- No cal comentar l'última extensió, de `19a` a `22a`, perquè és clara. 
- Pel que fa al pedal. Estem davant d'un cas d'una **transmissió amb préstec**, és a dir, que es presta un registre, en 
  aquest cas, en una altra tessitura, i, en lloc d'afegir els 12 tubs per completar la nova tessitura, es presten d'un 
  altre joc. 
 
  Hom es podria preguntar si això no podria ser una **extensió amb préstec**. Segons la definició, una extensió ha 
  d'incorporar tubs nous _propis_ del registre extensionat. El cas que ens ocupa no utilitza tubs nous, sinó que els 
  presta d'un altre joc. Per això, no pot ser una extensió i es tracta d'una transmissió. A més, la definició 
  de transmissió explicita que no hi pot haver cap mena d'extensió, és a dir, tubs extres.  

Proposo aquest segon cas, de la trompeta:

    I: T8 -e-> T4 
       |       | 
       t       t
       |       | 
       v       v
    P: T8      T4

Debat:
- La transmissió de la trompeta de 8′ al pedal, és clara; l'extensió de la trompeta de 4′ al manual també.
- La trompeta de 4′ del pedal no és extensió de ningú, car no té tubs propis (ja que la tessitura del pedal és més 
  reduïda). Així doncs, és transmissió de la trompeta de 8′ del manual o de la trompeta de 4′ del manual?
  
  Si les tessitures dels dos teclats fossin la mateixa, la `T4` del pedal no podria ser una transmissió de la `T8` del
  manual, car li mancarien tubs; tampoc seria una extensió de la `T8` del pedal perquè no té tubs propis. L'únic camí
  per arribar-hi, seria essent una transmissió de `T4` del manual.  

  Per tant, **es prefereix una transmissió d'una extensió que una transmissió a una octava diferent**, si es compleix 
  el següent:
    - Que l'extensionat i el punt d'arribada tinguin la mateixa tessitura.
    - Quan no hi hagi tubs extres involucrats. 

# CEOC

## Pàgines dels concerts

Dins una carpeta amb l'edició del cicle. Cada fitxer a dins és un concert. Cada fitxer té aquest _frontmatter_:

    layout: base/concert-ceoc
    title: Concert a l'església parroquial de Sant Pere Apòstol
    turisme: de Montbrió del Camp [de + municipi, per les excepcions d'apostrofació]
    sense_comentaris: true [opcional]
    autor_comentaris: Pau Riuró i Bofill [opcional - per defecte: Marcel Martínez i Bonifacio]

El primer bloc fins a l'etiqueta `<!--separador-->` és el programa. Mira exemples de com formatar-lo. El segon bloc, que
es troba entre els dos separadors, són els comentaris al programa. Si no hi ha comentaris, entre les etiquetes es pot deixar
buit i no es mostrarà l'apartat. L'últim apartat és la biografia o CV de l'organista o intèrprets. Per múltiples intèrprets,
es pot consultar el concert d'Àger del 44è cicle.

## Pàgina de l'edició del cicle

És un fitxer amb el número d'edició per nom que es troba dins la carpeta `ceoc`. Hi ha la presentació del cicle, s'hi
mostraran tots els concerts en forma d'etiqueta i es podrà descarregar el programa en PDF. Mira la resta per entendre
què canvia entre les diferents edicions.
## Com fer que tot es mostri?

- Cal omplir el fitxer `_data/ceoc.yml` amb les dades de cada concert, dins l'apartat `concerts`. Mira els dels anys anteriors
  per saber com funcionen. La fotografia de l'orgue és el nom de fitxer d'una de les fotografies de la galeria de l'orgue en qüestió.
- Cal modificar la pàgina `pages/ceoc.md`, canviar la presentació, canviar l'enllaç cap al nou cicle.
- Cal afegir el cicle anterior a l'apartat `cicles` de `_data/ceoc.yml`.

## Com crear els enllaços de redirecció?

En el programa imprès apareix un codi QR per anar a la pàgina web, on es mostra més informació del concert. El problema
és que els enllaços a aquestes pàgines són llargs, l'espai del QR imprès és petit, i queda un QR amb els punts molt petits,
dificultant-ne la lectura en condicions de poca llum i poc contrast.

Per això, proposo crear un enllaç curt que permeti tenir un QR petit, de 25×25 punts, i no de 33×33, com els de l'edició
passada, la 45a.

Escapçant les tres _w_ de l'url i mantenint una correcció d'errors de nivell mitjà `M`, queda espai per 5 caràcters
just després del domini.

Format enllaços:

    https://acorgue.cat/codi_concert

Codi concert:

    46 + tres lletres en minúscula

Les tres lletres són les primeres. Si el poble té més d'una paraula, la inicial de cadascuna, obviant els articles
inicials i prenent els intermedis, si convé. És completament arbitrari. Però és el sentit que li he donat.

Llista pel 2026 (46è cicle):

| Poble                   | Codi  |
|-------------------------|-------|
| Àger                    | 46age |
| Barcelona               | 46bar |
| Castelló d'Empúries     | 46cde |
| El Pla de Santa Maria   | 46psm |
| Girona                  | 46gir |
| La Pobla de Cérvoles    | 46pdc |
| Manresa                 | 46man |
| Les Masies de Voltregà  | 46mdv |
| Montbrió del Camp       | 46mdc |
| Santa Coloma de Farners | 46scf |
| Torredembarra           | 46tor |
| Torroja del Priorat     | 46tdp |
| Ulldemolins             | 46udm |
| Vallmoll                | 46val |
| Vilafranca del Penedès  | 46vdp |

# Miscel·lània pel desenvolupador

## Introducció de caràcters especials

La introducció de caràcters especials amb un teclat normal pot ser força difícil. Així i tot, existeixen modificadors
que permeten introduir una bona colla de caràcters que no formen part de l’alfabet propi de la llengua del teclat i
altres caràcters tipogràfics.

Per coneixença, només puc cobrir la introducció de caràcters des de Linux. Usuaris de Windows i MacOS hauran de seguir
mètodes alternatius, i, si convé, documentar-los aquí.

### Linux

Segueix una llista de caràcters comuns en la llengua catalana i en el desenvolupament d’aquesta pàgina web i la manera
d’introduir-los.

- `«` (U+00AB) i `»` (U+00BB). Són les cometes que s’utilitzen dins el cos d’un text en català. `AltGr + <z>` i `AltGr + <x>` respectivament.
- `’` (apòstrof tipogràfic) (U+2019). L’apòstrof tipogràfic no és el caràcter ASCII 27 que està present en el teclat. `AltGr + Shift + <n>`.
- `–` (guió mitjà) (U+2013). El guió mitjà s’utilitza per especificar un rang, generalment, com dates i extensions de teclats. `<Multi_key> <-> <-> <.>`.
- `—` (guió llarg) (U+2014). El guió llarg s’utilitza com a interjecció o aclariment enmig d’una frase. `<Multi_key> <-> <-> <->`.
- `…` (punts suspensius) (U+2026). Ja se’n coneix l’ús i l’ús dels tres punts és incorrecte tipogràficament parlant. `<Multi_key> <.> <.>`.
- `ŀ` (ela geminada). Tipogràficament parlant, la primera ela i el punt volat formen un sol caràcter. `<dead_abovedot> <l>` (v. nota).
- `′` (prima) (U+2032). Símbol de la unitat de mesura _peu_, polzada, minut i de l’octava en la notació Helmholtz. Configurada manualment com `<Multi_key> <'> <1>`.
- `″` (prima doble) (U+2032). Símbol de la unitat de mesura de segon i de l’octava en la notació Helmholtz. Configurada manualment com `<Multi_key> <'> <2>`.
- `‴` (prima doble) (U+2033). Símbol de l’octava en la notació Helmholtz. Configurada manualment com `<Multi_key> <'> <3>`.
- `⁗` (prima doble) (U+2057). Símbol de l’octava en la notació Helmholtz. Configurada manualment com `<Multi_key> <'> <4>`.

Vegeu les seccions [`<Multi_key>`](#tecla-multi_key-xorg) i [`<dead...>`](#tecles-dead) per entendre com introduir llurs caràcters.

#### Tecla `<Multi_key>` (Xorg)

En Linux existeix una tecla anomenada `Compose` (altrament anomenada `<Multi_key>`) que permet introduir caràcters especials més enllà dels assignats a les
tecles i els seus modificadors `Shift`, `AltGr` i `Shift + AltGr`. La majoria de teclats moderns no disposen d’aquesta
tecla i s’ha de configurar manualment. Algunes distribucions la porten configurada; d’altres no. Per configurar-la, es
pot fer de la següent manera:

1.  Llistar les combinacions de tecles aptes per a fer de `<Multi_key>`:

        grep "compose:" /usr/share/X11/xkb/rules/base.lst

2.  Configurar-la amb `setxkbmap`, per exemple:

        setxkbmap -option compose:menu-altgr es

La introducció de caràcters amb aquesta tecla és d’aquesta manera: es pitja la tecla `<Multi_key>` o la combinació de tecles
configurada en lloc seu, es deixa o deixen anar i segueix la seqüència de caràcters indicada. Les
seqüències vàlides es troben en aquest fitxer: `/usr/share/X11/locale/en_US.UTF-8/Compose`. Si hi ha caràcters que no
estan definits en aquest fitxer, es pot editar el fitxer `~/.XCompose` i afegir-los.

#### Tecla `<Multi_key>` (Wayland)

M'he actualitzat i ara utilitzo Wayland, i això funciona diferent. El concepte és el mateix. A part d'actualitzar-me,
també he actualitzat el meu maquinari i he perdut una de les tecles comunes per assignar la tecla _compose_ o _multi_key_.

Per tant, abans de tot, cal assignar una tecla a una tecla que permeti ser utilitzada com a _compose_. Tecles que poden
ser assignades com a compose:

    grep "compose:" /usr/share/X11/xkb/rules/base.lst

He escollit _Scroll lock_. Tecles que no utilitzo: `Fn + F12`. Quina tecla és? Instal·la `keyd`, aixeca el servei i

    sudo keyd monitor

Llavors, tal com es descriu a la documentació, creo el fitxer `/etc/keyd/default.conf` amb:

    [ids]
    *
    [main]
    media = scrolllock

Ara només queda assignar la tecla _compose_ a _Scroll lock_. Utilitzo Hyperland com a gestor de finestres. Cal afegir
això a la secció d'`input`:

    kb_options = compose:sclk

No he trobat manera directa d'assignar la tecla `media` perquè sigui `compose`. He hagut d'utilitzar un pas intermedi.

##### Configuració de caràcters amb `<Multi_key>`

Per defecte, la prima i les seves variants no estan configurades. Per això, he editat el fitxer `~/.XCompose` de la
següent manera:

    include "%L"
    <Multi_key> <apostrophe> <1> : "′" # U2032 prime (peus)
    <Multi_key> <apostrophe> <2> : "″" # U2033 double prime (polzades)
    <Multi_key> <apostrophe> <3> : "‴" # U2034 triple prime
    <Multi_key> <apostrophe> <4> : "⁗" # U2057 quadruple prime

Un cop editat aquest fitxer, cal reiniciar `Xorg` o `Wayland`.

#### Tecles `<dead...>`

Investigant el fitxer `/usr/share/X11/locale/en_US.UTF-8/Compose`, hom pot buscar el caràcter UTF-8 de la ela geminada i veurà aquesta definició:

    <dead_abovedot> <l> : "ŀ"   U0140 # LATIN SMALL LETTER L WITH MIDDLE DOT

Quan una tecla es declara com a `dead`, vol dir que actua com els accents. La primera pulsació no entra cap caràcter; el
caràcter s’aplica a la pròxima tecla premuda. Com he trobat que el `<dead_abovedot>` es fa amb `AltGr + Shift + -` ha
sigut per prova i error. No trobo la manera de fer un mapping d’aquestes tecles automàticament. Si hom investiga el
fitxer `/usr/share/X11/xkb/symbols/es` trobarà aquesta paraula juntament amb `minus` en el codi de tecla `<AB10>`, que
en el layout espanyol, es correspon al signe menys, al costat esquerre del `shift` dret.

## Tractament de les imatges

Explicació de l’script `manage-images.py`. Resulta que gestionar les dades i metadades de, ara mateix, més de 700
fotografies es fa una mica feixuc. Per això, les imatges estan organitzades de la mateixa manera que els orgues.
Com que no hi ha prou espai (gratuït) a l’aparcament de la pàgina (GitLab Pages), i, com que si estiguessin allà,
s’hi haurien de pujar manualment (perquè ser gestionades per Git no té sentit), seria un merder modificar i afegir
imatges noves.

Per tant, les imatges viuen en un servidor Nextcloud, que té una API per accedir-hi des de Python. Les dades principals
de cada fotografia es troben juntament amb l’article de l’orgue, és a dir, en el fitxer `.md`. Aquestes dades principals
són el nom de la imatge, el peu, `alt`, autor i si és portada. Poca cosa més; només el que no es pot saber
programàticament. La resta d’informació s’obté a través de l’script mencionat. Llegeix els fitxers `*.md` i aconsegueix
les altres metadades (com ara la mida de la imatge, necessària per al visor d’imatges `photoswipe`), a més de preocupar-se
de crear els enllaços per a la correcta visualització de les imatges a la web. Aquesta informació s’emmagatzema en un
fitxer yml convenientment estructurat per ser llegit pel generador de la web (Jekyll).

Aquest fitxer yml és pujat al Nextcloud i CI (GitLab Pages) se’l baixa per crear la web. D’aquesta manera s’estalvien
entre 6 i 7 minuts de temps de CI i possibles errors deguts a fallades de connexió (els runners de CI de GitLab els hi passa
sovint).

Resumint: per pujar imatges noves, que és el que hom ha de fer més sovint, només cal anomenar-les a l’article en
l’ordre desitjat, pujar-les al servidor Nextcloud i executar aquest script.

### Reducció de la mida de les imatges rebudes

`photoswipe` diu que no accepta imatges més grans de 3000×3000 píxels. Això no és ben bé cert, però
tampoc cal abusar de la seva confiança; diu que imatges més grans tenen problemes de rendiment i s’ha
d’utilitzar un altre sistema de visionament (per tessel·les), el qual no estic preparat per afrontar,
de moment.

Per això, és necessari que les imatges de la web no superin els 3000 píxels d’alçada o d’amplada. La
manera ràpida de redimensionar les imatges és amb aquesta comanda d’`imagemagik`:

     mogrify -resize 3000x3000 file1.jpg file2.jpg

El redimensionament es fa substituent la imatge original.

La majoria d’imatges que tinc i que són en bona qualitat, són meves, i, per tant, conservo els
originals. Les que de vegades m’arriben són d’una qualitat pobra (objectivament, estèticament i
funcionalment parlant). De moment, si m’arriben per correu, conservo el correu i es podrien rescatar.
Però, com a norma general, d’aquestes no en conservo l’original i guardo només la imatge redimensionada.

Com a justificació: la majoria no estan ben enfocades i estan mogudes: tenir més resolució no incrementarà
la seva nitidesa.

### Gestió de les portades dels orgues

Des d’un inici, a les imatges de la galeria hi havia una etiqueta `portada` que indicava el percentatge CSS per centrar
la imatge dins del bàner superior de cada pàgina dels orgues. Això ha generat un problema de rendiment, ja que les
imatges de la portada s’havien de baixar a la resolució original (de vegades, més de 3 o 4 MB), i redimensionar en viu
utilitzant CSS.

Es va millorar més tard afegint que primer es baixés el _preview_ de la imatge perquè es mostrés de seguida i després
ja es baixaria la imatge original. La idea és bona, però, així i tot, encara s’havia de baixar la imatge gran.

A partir del 3 de maig de 2024, això canvia. Internament, més aviat, perquè la interfície de text per marcar les imatges
com a portada és la mateixa.

L’script de python examina les fotografies de la pàgina. La que troba marcada com a `portada` en crea una còpia, la
baixa, la retalla segons el valor de l’etiqueta, la redimensiona a la màxima mida que tindrà en qualsevol dispositiu i
la puja en format `webp` amb el sufix `_portada`. Les imatges de portada ocupen ara, com a màxim 120 kB, algunes d’elles
potser només 70 kB, depèn de la imatge. La càrrega d’una pàgina pot veure’s reduïda 4 vegades (de 32 segons a tan
sols 8).

#### Com designar una imatge portada

La imatge que es desitja que sigui la portada, només cal afegir el camp `portada: <núm>` a l’article, de fet, boi boi
fins com es feia fins ara.

Ara no cal indicar un percentatge CSS (bé, sí que es pot, però sort si el pots trobar fàcilment); ara s’indica el píxel
superior esquerre de l’inici del retall, però només la coordenada de les `y` (vertical), ja que l’horitzontal és
sempre `0`. Per trobar-lo, es pot fer amb el GIMP, simulant un retall de relació d’aspecte `4,6:1` i anotant la posició
del requadre de retallat.

#### Transformació del percentatge CSS a píxels

El percentatge indica el següent: el `%` de la imatge (alçada o amplada) es correspondrà amb el mateix `%` del
contenidor. Fent algun dibuixet es veu més clarament. Ho intento explicar ara.

Per sort, la mida del contenidor és fixa, o, si més no, té una relació d’aspecte fixada, que és `4,6`. Agafant la mida
del contenidor més gran (pàgina al 100% en una pantalla gran), el contenidor de Bootstrap és l’`xxl`, que segons la
documentació té `1320 px`, però que en el meu CSS he rebaixat a `1260 px`, perquè el trobava excessivament ample.

El contenidor dels orgues fa, doncs, 1260 px menys els paddings afegits, que són de mida `3` per banda. La mida `3` es
correspon a `1 rem`, que, per norma general, són `16 px`. Si canvia la mida base de la lletra en algun navegador, mala
sort, no es veurà la imatge òptimament. Per tant, el nostre contenidor fa `1228 px` d’amplada, i, segons la seva
relació d’aspecte, `267 px` d’alçada.

Com que els dos percentatges han de coincidir, parlant ara per l’alçada, que és el que ens interessa, el `25 %` de
l’alçada de la imatge menys el `25 %` del contenidor resulta ser el píxel superior esquerra de l’inici del retall.

Pel que fa a la mida del retall, és l’amplada de la imatge i, la seva alçada es calcula amb la relació d’aspecte del
contenidor.

Exemple:

    Imatge: 1666×2242 (vertical)
    Contenidor: 1228×267 (horitzontal). Relació d’aspecte: 4,6
    portada: 25%

    25% de la imatge: 2242×0,25 = 561
    25% del contenidor: 267×0,25 = 67
    Cantonada superior equerra de la imatge on comença el retall és: 561–67 = 494

    La mida del retall és 1666×(1666÷4,6) = 1666×362

L’script de python està preparat per acceptar el percentatge, però també per acceptar el píxel superior esquerra
del retall, ara que amb el nou sistema no es pot trobar el percentatge fàcilment, però sí el píxel superior esquerra
utilitzant el GIMP, per exemple.

Cal tenir en compte que ara el retall és físic, que no es pot anar provant sense tornar a retallar la imatge.

#### Actualització de les dades de portada

Si es té en compte la memòria cau, cal eliminar la seva entrada de la memòria cau i actualitzar el fitxer
(opció `--update`)

Si no es té en compte la memòria cau, doncs no hi ha problema. El procés tarda 6 minuts (156 orgues, 106 portades)
(opció `--create`)

### FAQ

#### Fotografies que no surten ben girades

**Nota: en principi, això no hauria de passar més**. L’`script` `manage-imatges.py` interpreta la casuística explicada
a continuació i la corregeix.

Hi ha càmeres de fotografia que desen les imatges verticals de manera estranya o, si més no, d’una
manera que aquesta web és incapaç d’entendre. La manera que queden guardades és la següent: sempre
en horitzontal i s’afegeix una etiqueta de rotació EXIF que indica que s’ha de tractar la `width` per
la `height` i al revés. Com que les meves imatges surten, la
majoria de vegades, del programa d’edició com a imatge exportada, la informació de rotació queda
desada correctament.

M’he trobat amb un cas d’imatges verticals provinents d’un iPhone, que ha costat Déu i sa mare donar-les-hi
la volta perquè no quedessin xates. Girar-les amb EXIF no s’hi val, perquè quan l’script de python
llegeix la mida, la llegeix incorrectament. L’etiqueta de rotació EXIF només és una guia pels visualitzadors
d’imatge; si carrego malament la mida d’aquesta, _tururut viola_.

Opcions:

- Modificar l’script de python perquè busqui l’etiqueta de rotació EXIF, fent que, si no està present,
  calgui descarregar-se la imatge sencera, fent ineficient el procés de creació de la informació
  de les imatges.
- Exportar les imatges amb el GIMP, per exemple. En carregar imatges conflictives, aquest demanarà
  de girar-les. Dient-li que sí, la mida de la imatge canviarà.

De moment, per evitar fer més feixuga la tasca de recopilació de la mida de les imatges, he utilitzat
la segona opció.

## Fonts i subset de fonts

Les fonts que arriben per la CDN pesen molt:

- AvrileSans-Light.woff 303 kB
- AvrileSans-Regular.woff 299 kB
- AvrileSans-Medium.woff 315 kB
- AvrileSans-Bold.woff 308 kB
- AvrileSans-LightItalic.woff 318 kB
- AvrileSans-Italic.woff 317 kB

i, a més, no es carreguen utilitzant `font-display`. I, a més, no sé per quins set sous a la pàgina de producció es
renderitza correctament AvrileSans amb versaletes i a la pàgina de desenvolupament, no. Bé, sí que ho sé, perquè per
algun motiu, fer el subset (veieu la següent secció) esborra aquesta capacitat, que ja de per si era inexistent (Avrile
no té suport per a versaletes).

#### Subset de fonts

Si es fa un subset de les fonts i s’eliminen tots aquells caràcters que no s’utilitzaran (hebreu, grec, cirílic, àrab, i
un llarg etcètera), el pes de les fonts es pot reduir fins a sis vegades.

Cal saber els [rangs utf-8](https://jrgraphix.net/r/Unicode/) per decidir quins caràcters eliminar. També es poden
els rangs d’una font amb:

    fc-query --format='%{charset}\n' AvrileSans-Regular.ttf

i també es poden llistar les `features` d’una font per saber si té versaletes:

    fc-query AvrileSans-Regular.ttf

i buscar a dins la paraula `feature`. Es poden comprovar quins són
[els codis de `features`](https://en.wikipedia.org/wiki/List_of_typographic_features) disponibles a Wikipedia.

Cal instal·lar el paquet de python `fonttools`:

```shell
sudo pacman -S python-fonttools python-brotli
```

- Breu tutorial de com tractar les fonts: [https://walterebert.com/blog/subsetting-web-fonts/](https://walterebert.com/blog/subsetting-web-fonts/).

Subsets que s’utilitzen en català i altres llengües europees (de l’oest):

- 20-7e: Basic Latin
- a0-17f: Latin Suplement, Extended A
- 1e00-1eff: Latin extended additional
- 2000-209f: super and sub scripts and general punctuation
- 20a4, 20ac: Currency
- 2100-214f: letter like
- 2150-218f: numberforms

Cal escriure un fitxer amb aquests codis `unicodes.txt`:

    20-7e,a0-17f,1e00-1eff,2000-209f,20a4,20ac,2100-214f,2150-218f

I després, executar `pyftsubset` per cadascuna de les tipografies que s’han d’utilitzar:

    pyftsubset AvrileSans-Regular.ttf --flavor=woff2 --output-file="avrilesans-regular.woff2" --unicodes-file=unicodes.txt

o bé executar això dins el directori de la font:

```shell
for f in *.ttf; do
    pyftsubset $f --flavor=woff2 --unicodes="U+0020-007e,U+00a0-017F,U+1e00-1eff,U+2000-209f,U+20a4,U+20ac,U+2100-214f,U+2150-218f"
done
```

# Prendre nota d’una visita a un orgue

He creat una fitxa com Déu mana per anar a prendre nota d’un orgue. Disponible [aquí](https://nextcloud.acorgue.cat/s/brjZPFGAnetxTip/download).

# TODOs de la web, en general

Sistema d’issues habilitat al GitLab. Aquí, si convé, algunes idees vagues.

- [ ] JS. Transformació de les temperatures a 18 °C i que es pugui canviar dinàmicament.
- [ ] Un apartat per saber què falta d’un orgue.
- [ ] Gestió d’imatges i previsualitzacions
  - Les imatges petites de previsualització, se les podria baixar el worker de CI, en baixa qualitat i desar-les al
    directori. Ocupa espai de CI? Sí. N’ocupa poc? També. ~10k per imatge (màx. 150px).
  - Així, puc tenir /preview decent i un /download per fer clic.
  - Es podrien tenir també imatges en diferents mides: 200x200 per la galeria, etc.

# Orgues que falten

## Muts

- [ ] L’Albi
- [ ] Bràfim
- [ ] Sant Feliu (Constantí)
- [ ] Capella de l’hospital de Santa Creu (BCN)
- [ ] Sant Sadurní d’Anoia
- [ ] Barcelona. Convent de Santa Caterina. No sé ara mateix quin és

## Tinc les fotos i la informació, però no les he posades encara

- [ ] Concepció (Orgue major)
- [ ] La Gleva
- [ ] Montblanc (Blancafort)
- [ ] Pi (consola)
- [ ] Torredembarra
- [ ] Torroja (meu i JL Viladot)
- [ ] Ulldemolins
- [ ] Vendrell
- [ ] Vilafranca
- [ ] Casa Sant Josep de Cambrils (dos correus)

## Tinc només informació

- [ ] Altres (museu de la música)
- [ ] Santuari de Rocaprevera (bertran)

## Tinc fotos, però no tinc disposició

- [ ] Notre Dame de Lourdes de BCN
- [ ] Santa Maria del Teulat BCN
- [ ] Sant Andreu de Llavaneres
- [ ] Montalegre BCN
- [ ] Betlem BCN

## Revisió

Hi ha massa interrogants en la disposició. Cal anar-los a veure per resoldre els conflictes

- [ ] Montbrió del Camp. Hi ha massa discrepàncies
- [ ] Claviorgue (museu de la música) -> queden molts interrogants!
- [ ] Tremp (Valldeflors)
- [ ] Sant Josep Oriol. Crec que hi ha més préstecs. Esbrinar com funcionen les 3 combinacions lliures. Millorar les fotografies.

## Falten dades per situar-los a la llista de l’Escalona

- [ ] BCN Salesians Rocafort - Floridablanca. OESA. No sé quin és
- [ ] BCN Jesuïtes de Sarrià (col·legi)? Sant Ignasi?
- [ ] BCN Hospital de Sant Joan de Déu (Antoni i Klaus). Potser ja no hi és. Esplugues de llobregat, potser?
- [ ] BCN Parroquia de Nostra Senyora de la Pau. Pl. Ferran Casablancas. Allí se instaló un órgano de estudio que había sido de Montserrat Torrent, construido por Gabriel Blancafort.

## La gran llista

Orgues de la llista de l’Escalona (i algun que s’hi ha afegit posteriorment)

- Alt Empordà
  - [ ] Figueres. EP Immaculada Concepció de la MDD i Sant Pau
  - [x] ~~Vilabertran. EP Santa Maria~~. Es va cremar durant la Guerra. Escalona només menciona el constructor.
- Alt Penedès
  - [ ] Sant Pere de Riudebitlles. EP Sant Pere
- Anoia
  - [ ] Igualada. Església de la Immaculada Concepció de la MDD. Caputxins. Blancafort
  - [ ] La Llacuna. EP de Santa Maria
  - [ ] Sant Martí de Tous. EP Sant Martí de Tours
- Baix Camp
  - [x] Vinyols i els Arcs. Info p. 214 Vergés
- Baix Ebre
  - [ ] L’Aldea, EP Sant Josep. Blancafort
  - [ ] Tortosa. Catedral. Capella de la MDD Cinta. Blancafort 8 II/P
  - [ ] Tortosa. EP Sant Pere. Rossend Aymí 4/I 977 440 665
  - [ ] Tortosa. Monestir de la Puríssima. Rossend Aymí 3/I
- Baix Empordà
  - [ ] Palafrugell. EP Sant Martí de Tours
  - [ ] Pals. EP de Sant Pere
- Baix Llobregat
  - [ ] Esparreguera. EP Santa Eulàlia
  - [ ] Esparreguera. Teatre de la Passió (Blancafort)
  - [ ] Gavà. Església de la MDD de Brugués
- Bages
  - [ ] Artés. EP Santa Maria Assumpta
  - [ ] Cardona. EP Sant Miquel i Sant Vicenç
  - [ ] Marganell. Monestir de Sant Benet. Benedictines (Benetes-Blancafort?)
  - [ ] Moià. EP de la MDD de la Misericòrdia
  - [ ] Monistrol de Montserrat. Monestir. Positiu
  - [ ] Monistrol de Montserrat. Monestir. Escolania/Biblioteca
  - [ ] Navàs. Església del Sagrat Cor de Jesús, Colònia Valls
- Barcelonès
  - [ ] Barcelona. Santa Maria del Mar (positiu Grenzing)
  - [ ] Barcelona. Mare de Déu de Betlem
  - [ ] Barcelona. MDD Carme. Estadella
  - [ ] Barcelona. EP Sant Agustí
  - [ ] Barcelona. EP Santa Anna (la major? Centre? crec que sí. Miquel González)
  - [ ] Barcelona. Santa Maria de Montalegre
  - [ ] Barcelona. Mare de Déu de la Victòria del Palau. Jesuïtes
  - [ ] Barcelona. Casa de la Misericòrdia. Companyia filles de la Caritat
  - [ ] Barcelona. Col·legi la Salle Comptal
  - [ ] Barcelona. Església Evangèlica Barcelona Centre
  - [ ] Barcelona. EP MDD Àngels
  - [-] Barcelona. EP Puríssima Concepció. Santíssim
  - [-] Barcelona. EP Puríssima Concepció. Mediòfon capella de la MDD Montserrat?
  - [ ] Barcelona. EP Sant Francesc de Sales
  - [ ] Barcelona. EP Sants Sever i Vicenç de Paül. Congregació de la missió
  - [ ] Barcelona. MDD del Roser. Dominics
  - [ ] Barcelona. Santuari de la MMD Sagrat Cor. Missioners del Sagrat Cor de Jesús
  - [ ] Barcelona. Col·legi Sant Josep. Salesians
  - [?] Barcelona. Església Cristiana Adventista del Setè Dia -> he trobat diverses esglésies a barcelona, sense indicis de quines podrien tenir orgue
  - [ ] Barcelona. Església evangèlica de Sant pau
  - [-] Barcelona. Museu de la Música MDMB 54
  - [-] Barcelona. Museu de la Música MDMB 55
  - [-] Barcelona. Museu de la Música MDMB 431
  - [-] Barcelona. Museu de la Música MDMB 596
  - [-] Barcelona. Museu de la Música MDMB 820
  - [?] Barcelona. Museu de la Música Orgue Ars Musicae? -> orgue de maneta Evans? (MDMB 35)
  - [ ] Barcelona. EP Maria Reina
  - [ ] Barcelona. Monestir de Santa Maria de Pedralbes. Clarisses (segurament invisitable)
  - [ ] Barcelona. El Conventet
  - [ ] Barcelona. Tibidabo Orgue major
  - [ ] Barcelona. Tibidabo Cripta
  - [ ] Barcelona. EP MDD Lourdes (francesa)
  - [ ] Barcelona. EP Verge de la Pau
  - [ ] Barcelona. EP Sant Albert Magne (alemanya)
  - [ ] Barcelona. EP Sants Gervasi i Protasi
  - [ ] Barcelona. Sant Gregori Taumaturg
  - [ ] Barcelona. Monestir Sant Pere de les Puel·les. Benedictines
  - [ ] Barcelona. Sant Frances d’Assís. Franciscans menors
  - [ ] Barcelona. Col·legi Jesús Maria
  - [-] Barcelona. Col·legi major Sagrat Cor -> Sant Joan de Déu Serveis Socials, Barcelona - CRI Hort de la Vila?
  - [-] Barcelona. Col·legi Sagrat Cor Sarrià (diferent del de sobre) -> Carrer del Sagrat Cor, 25, Sarrià-Sant Gervasi, 08034 Barcelona?
  - [ ] Barcelona. Col·legi Sant Ignasi
  - [ ] Barcelona. Col·legi La Salle Bonanova
  - [ ] Barcelona. Escola Pia Sarrià. Escolapis
  - [ ] Barcelona. Col·legi Santa Isabel d’Hongria
  - [ ] Barcelona. Col·legi Santa Teresa de Jesús Tribuna
  - [ ] Barcelona. Col·legi Santa Teresa de Jesús Cor
  - [ ] Barcelona. Institut musicologia Josep Ricart i Matas
  - [ ] Barcelona. EP MDD Salut. Franciscans
  - [?] Barcelona. A&K Órganos de Viento? -> què vols dir? on és aquest orgue?
  - [ ] Barcelona. Monestir de la Visitació de Santa Maria. Saleses. Tribuna
  - [ ] Barcelona. Monestir de la Visitació de Santa Maria. Saleses. Cor
  - [ ] Barcelona. EP Sant Andreu de Palomar. Nau principal
  - [ ] Barcelona. EP Sant Andreu de Palomar. Façana Santíssim
  - [ ] Barcelona. EP Santa Maria del Taulat
  - [ ] Esplugues de Llobregat. Monestir de la MDD del Mont Sió. Dominiques
  - [ ] Esplugues de Llobregat. Hospital de Sant Joan de Déu. Hospitalaris de Sant Joan de Déu
  - [ ] Hospitalet de Llobregat. EP Sant Isidre
- Berguedà
  - [ ] Bagà. EP Sant Esteve
  - [ ] Puig-reig. Església de la Puríssima, Colonia Vidal
- Garraf
  - [ ] Sitges. Santuari del Vinyet
  - [ ] Vilanova. EMM
- Garrigues
  - [ ] l’Espluga Calba. EP Santa Maria
- Garrotxa
  - [ ] Beuda. EP Santa Maria de Segueró
  - [ ] Sant Feliu de Pallerols. Santuari MDD de la Font de la Salut
- Gironès
  - [ ] Cassà de la Selva. EP Sant Martí de Tours. info al llibret de l’Escalona
  - [ ] Girona. EP Santa Susanna del Mercadal
  - [ ] Girona. Església SF. Butinyanes
  - [ ] Girona. Santuari de Maria Auxiliadora
  - [ ] Girona. Seminari Sant Martí de Tours
  - [ ] Girona. Casa de Cultura (llibre Escalona)
- Maresme
  - [ ] Canet de Mar. EP Sant Pere i Sant Pau
  - [ ] Mataró. EP MDD Esperança
  - [ ] Mataró. EP Sant Josep
  - [ ] Mataró. Monestir Immaculada Concepció. Carmelites Descalces
  - [ ] Sant Andreu de Llavaneres. EP Sant Andreu
  - [ ] Sant Cebrià de Vallalta. EP Sant Cebrià
  - [ ] Vilassar de Dalt. Hospital de Sant Pere
- Noguera
  - [ ] Balaguer. Església de Sant Domènec; Franciscans. Sembla ser un Blancafort
  - [ ] Castelló de Farfanya. EP Assumpció de la Mare de Déu
- Osona
  - [ ] Manlleu. Col·legi de la Salle
  - [ ] Sant Boi de Lluçanès. EP Sant Boi
  - [ ] Torelló. EP Sant Feliu
  - [ ] Torelló. Santuari MDD Rocaprevera
  - [ ] Vic. EP MDD Carme
  - [ ] Vic. EP Sant Domènec
  - [ ] Vic. Monestir de l’Adoració Perpètua
  - [ ] Vic. Església Sant Antoni Maria Claret
  - [ ] Vic. MDD dels Dolors
- Pallars Jussà
  - [ ] Isona i Conca Dellà. EP de Snat Miquel de Conques
- Pla de l’Estany
  - [ ] Banyoles. EP de Santa maria dels Turers
- Ribera d’Ebre
  - [ ] La Palma d’Ebre. EP de l’Assumpció de la MDD. Orgue Rossend Aymí 1990 3/I
- Ripollès
  - [ ] Ripoll. EP Santa Maria
- Segarra
  - [ ] Sant Ramon de Portell. EP i del santuari de Sant Ramon Nonat. Mercedaris
- Selva
  - [ ] Lloret de Mar. EP de Sant Romà
  - [ ] Lloret de Mar. Església de la Mare de Déu de Gràcia i Dant Pere, de Sant Pere del Bosc
- Tarragonès
  - [ ] Tarragona. Monestir de Sant Josep i Santa Anna. Carmelites Descalces. Vergés p249
  - [ ] Tarragona. Conservatori Tarragona (x2). Vergés p249
- Vallès Occidental
  - [ ] Cerdanyola del Vallès. EP Santa Creu
  - [?] Cerdanyola del Vallès. Capella Reial de Catalunya?
  - [ ] Palau-solità i Plegamans. EP Santa Maria de Palu-solità
  - [ ] Sabadell. EP Santíssima Trinitat. Blancafort. 937 27 49 09
  - [ ] Sabadell. EP Sant Feliu. OESA. 937 25 47 58
  - [ ] Sabadell. EP Sant Oleguer. 937 25 97 80
  - [ ] Sabadell. Santuari MDD Salut. 937 25 13 82
  - [-] Sabadell. El Redemptor. 937 26 34 40
  - [-] Sabadell. Castellarnau. 683 41 76 40
  - [?] Sabadell. Església evangèlica Baptista -> les dues anteriors ja són les baptistes.
  - [-] Terrassa. Conservatori
  - [ ] Terrassa. Catedral gran
  - [ ] Terrassa. Catedral Santíssim
  - [-] Terrassa. Església protestant Betel
  - [?] Terrassa. Cor Madrigal/Cor Montserrat
- Vallès Oriental
  - [ ] Caldes de Montbui. Santuari de la MDD Remei
  - [ ] Franqueses del Vallès. EP Santa Coloma de Marata
  - [ ] Granollers. EP Sant Esteve. OESA
  - [ ] Sant Celoni. EP Sant Martí de Tours
