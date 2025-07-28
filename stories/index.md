# A Data Story about analysing research data on baroque artworks in Germany and their associated artists

This is a test to see how the container and the data story is working. If you see this message I'm happy :)

## With a SPARQL query
<details>
  <summary><b>SPARQL query to extract information from the Bildindex dataset</b></summary>
```sparql linenums="1" title="Query to extract Bildindex data about the artists located in the CbDD dataset"
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rico: <https://www.ica.org/standards/RiC/ontology#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX virtrdfdata: <http://www.openlinksw.com/virtrdf-data-formats#>
PREFIX virtrdf: <http://www.openlinksw.com/schemas/virtrdf#>
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX swrl: <http://www.w3.org/2003/11/swrl#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX shmarql: <https://shmarql.com/>
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX nfdicore: <https://nfdi.fiz-karlsruhe.de/ontology/>
PREFIX factgrid: <https://database.factgrid.de/entity/>


SELECT DISTINCT 
  ?creatorGND      # die GND-URI
  ?bildindexEntity # Bildindex-URI
  ?predicate       # über welches Property der Link läuft
  ?label           # optionaler Label des Bildindex-Objekts
WHERE {
  # 1) alle GND-IDs aus E6077
  ?art cto:elementOf n4c:E6077 ;
       schema:creator    ?creatorGND .

  # 2) finde alle Tripel, in denen diese GNDs Objekt sind
  ?bildindexEntity ?predicate ?creatorGND .

  # 3) filtere nur die Subjects, die auf bildindex.de verweisen
  FILTER regex(str(?bildindexEntity), "https?://(www\\.)?bildindex\\.de/")

  # 4) optional: Label mit ausgeben
  OPTIONAL { ?bildindexEntity rdfs:label ?label }
}
ORDER BY ?creatorGND ?bildindexEntity
LIMIT 999
</details>
```
