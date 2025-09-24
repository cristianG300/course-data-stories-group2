# A Data Story about analysing research data on baroque artworks in Germany and their associated artists

This is a test to see how the container and the data story is working. If you see this message I'm happy :)

## With a SPARQL query
<details>
  <summary><b>SPARQL query to extract information from the Bildindex dataset</b></summary>
    ```sparql linenums="1" title="Query to extract Bildindex data about the artists located in the CbDD dataset"
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX cto: <https://nfdi4culture.de/ontology#>

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
    ```
</details>

# Baroque ceiling paintings in Germany — map

<div id="map" style="height: 70vh; border-radius: 8px; margin: 1rem 0;"></div>

<!-- Leaflet CSS/JS (from CDN) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<script>
(async function () {
  // 1) Create the map
  const map = L.map('map', { scrollWheelZoom: true }).setView([51.2, 10.4], 6); // Germany-ish
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // 2) SPARQL code
  const sparql = `
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX schema: <http://schema.org/>
  PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
  PREFIX geos: <http://www.opengis.net/ont/geosparql#>
  PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
  PREFIX cto: <https://nfdi4culture.de/ontology#>
  PREFIX nfdi4culture: <https://nfdi4culture.de/id/>
  PREFIX gndo: <https://d-nb.info/standards/elementset/gnd#>

  SELECT DISTINCT
    ?creatorGND
    ?art    ?eLoc    ?eLat    ?eLon
    ?bild   ?bLoc    ?bLat    ?bLon
  WHERE {
    ## 1) Test auf 5 verschiedene Künstler-GNDs
    {
      SELECT DISTINCT ?creatorGND WHERE {
        ?art cto:elementOf nfdi4culture:E6077 ;
            a/rdfs:subClassOf* schema:VisualArtwork ;
            (schema:creator|schema:artist) ?creatorGND .
      }
      LIMIT 5
    }

    ## 2) E6077 artwork
    ?art cto:elementOf nfdi4culture:E6077 ;
        (schema:creator|schema:artist) ?creatorGND .

    # try to get a deckenmalerei location
    OPTIONAL {
      ?art cto:relatedLocation ?deckLoc .
      FILTER (STRSTARTS(STR(?deckLoc), "https://www.deckenmalerei.eu/"))
    }

    # fallback: a GND location
    OPTIONAL {
      ?art cto:relatedLocation ?gndLoc .
      FILTER STRSTARTS(STR(?gndLoc), "https://d-nb.info/gnd/")
    }

    # pick deckenmalerei if present, otherwise GND
    BIND( COALESCE(?deckLoc, ?gndLoc) AS ?eLoc )
    FILTER(BOUND(?eLoc))

    ## Direct coordinates (deckenmalerei.eu etc.)
    OPTIONAL {
      ?eLoc schema:latitude  ?eLat ;
            schema:longitude ?eLon .
    }

    ## 3) Bildindex-Einträge desselben Künstlers + Location
    ?bild ?predicate ?creatorGND .
    FILTER (STRSTARTS(STR(?bild), "http://www.bildindex.de/"))

    OPTIONAL {
      ?bild cto:relatedLocation ?bLoc .

      ## direkte Koordinaten am bLoc
      OPTIONAL {
        SERVICE SILENT <https://zbw.eu/beta/sparql-lab/sparql> {
          ?bLoc gndo:place ?place.
          ?place  geos:hasGeometry ?geom .
          ?geom   geos:asWKT ?bWKT .
        }
      }
    }
  }
  ORDER BY ?creatorGND
  `;

  // 3) Query the same-origin /sparql exposed by SHMARQL
  const res = await fetch('/sparql', {
    method: 'POST',
    headers: {
      'Accept': 'application/sparql-results+json',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: new URLSearchParams({ query: sparql })
  });
  if (!res.ok) {
    console.error('SPARQL error', res.status, await res.text());
    return;
  }
  const json = await res.json();
  console.log('SPARQL full response', json); // debug: inspect returned variables / bindings

  // helper: robust number parsing (accept "49.2", "49,2", trim)
  function toNumber(val) {
    if (val == null) return null;
    const s = String(val).trim().replace(',', '.');
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  }

  // 4) Transform rows -> markers
  const rows = json.results?.bindings || [];
  console.log('rows count', rows.length, rows);
  const markers = [];
  for (const row of rows) {
    // read raw literal values (strings)
    const rawLat = row.eLat?.value ?? null;
    const rawLon = row.eLon?.value ?? null;

    // parse safely
    const latNum = toNumber(rawLat);
    const lonNum = toNumber(rawLon);

    if (latNum == null || lonNum == null) {
      console.warn('Skipping row without usable coords', { rawLat, rawLon, row });
      continue; // skip rows that do not contain usable numeric lat/lon
    }

    const art = row.art?.value || '';
    const loc = row.eLoc?.value || '';
    const creator = row.creatorGND?.value || '';

    const m = L.marker([latNum, lonNum]).addTo(map);
    m.bindPopup(`
      <div style="font-size: 0.95rem; line-height:1.35;">
        <div><strong>Artwork</strong><br><a href="${art}" target="_blank" rel="noopener">${art}</a></div>
        <div style="margin-top:0.25rem;"><strong>Location</strong><br><a href="${loc}" target="_blank" rel="noopener">${loc}</a></div>
        <div style="margin-top:0.25rem;"><strong>Artist (GND)</strong><br><a href="${creator}" target="_blank" rel="noopener">${creator}</a></div>
      </div>
    `);
    markers.push(m);
  }

  // 5) Fit map to markers if we have any
  if (markers.length) {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.2));
  } else {
    console.warn('No markers created - check SPARQL response for eLat/eLon bindings. See console logs.');
  }
})();
</script>