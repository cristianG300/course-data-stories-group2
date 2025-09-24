# A Data Story about analysing research data on baroque artworks in Germany and their associated artists

/// html | div[class='tile']
**Authors:** Cristian Ghinea, Jacob Kühner, Niklas Spachmann
///
<br>
[![Introductory Image](intro.jpg)](https://previous.bildindex.de/bilder/fmd494334a.jpg)
/// caption
Tommasso Guisti, Die Decke im Zimmer des Winters, 1696-1698, [CbDD](https://www.deckenmalerei.eu/7811eafd-4f5f-4b17-96c7-d0d9ab35f530), Public Domain
///


**Abstract:**
This data story investigates baroque ceiling paintings in Germany, based on the database of CbDD (Corpus of baroque ceiling paintings in Germany, see also [deckenmalerei.eu](https://deckenmalerei.eu)). The authors 

## SPARQL query to find additional images from Bildindex der Kunst & Architektur
/// details | **Show SPARQL query 01**
    type: plain
``` sparql linenums="1" title="sparql-01.rq"
--8<-- "sparql-01.rq"
```
///

# Baroque ceiling paintings in Germany — map

<div id="map" style="height: 70vh; border-radius: 8px; margin: 1rem 0;"></div>

<!-- Leaflet CSS/JS (from CDN) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<!-- Add custom styles for cluster-count icons and popup list -->
<style>
  /* cluster count icon */
  .cluster-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,120,200,0.95);
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    font-weight: 600;
    box-shadow: 0 1px 4px rgba(0,0,0,0.6);
    border: 2px solid white;
  }
  .single-marker-dot {
    width: 12px;
    height: 12px;
    background: rgba(0,120,200,0.95);
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.6);
  }

  /* popup contents: fixed size and scrollable */
  /* widened to make space for thumbnails on the right */
  .popup-list {
    width: 520px;     /* increased from 320 to allow image column */
    height: 300px;
    overflow-y: auto;
    box-sizing: border-box;
    padding: 0.4rem;
    font-size: 0.9rem;
  }

  /* each item is a two-column row: meta (left) + thumbnail (right) */
  .popup-list .item {
    display: flex;
    gap: 0.6rem;
    align-items: center; /* fixed square thumbs, don't stretch with text */
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.35rem;
  }

  .popup-list .item .meta {
    flex: 1 1 auto;
    min-width: 0; /* for proper word-wrap inside flex */
  }
  .popup-list .item .meta strong { display:block; font-weight:600; margin-bottom:0.15rem; }

  /* thumbnail column */
  .popup-list .item .thumb-wrap {
    width: 160px;           /* thumbnail width (square) */
    height: 160px;          /* fixed square height -> 1:1 aspect ratio */
    flex: 0 0 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;       /* hide parts outside the square */
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    border: 1px solid #ddd;
    background: #fff;
  }
  .popup-list .item .thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;      /* crop & fill the square */
    object-position: center center; /* center the image inside the square */
    display: block;
    border-radius: 0;       /* rounded container already applied to wrapper */
  }

  .popup-list a { color: #065a8a; word-break: break-all; }
</style>

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
    ?art    ?eLoc    ?eLat    ?eLon    ?nameArtist    ?nameLoc
    ?bild   ?bLoc    ?bLat    ?bLon    ?nameArt    ?imgUrl
  WHERE {
    ## 1) Test auf 5 verschiedene Künstler-GNDs
    {
      SELECT DISTINCT ?creatorGND WHERE {
        ?art cto:elementOf nfdi4culture:E6077 ;
            a/rdfs:subClassOf* schema:VisualArtwork ;
            (schema:creator|schema:artist) ?creatorGND .
      }
      LIMIT 20
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
    ?creatorGND rdfs:label ?nameArtist .
    ?art rdfs:label ?nameArt .
    ?eLoc rdfs:label ?nameLoc .
    ?art schema:image ?imgUrl .

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

  // helper: robust number parsing (accept "49.2", "49,2", trim)
  function toNumber(val) {
    if (val == null) return null;
    const s = String(val).trim().replace(',', '.');
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  }

  // 4) Transform rows -> grouped markers
  const rows = json.results?.bindings || [];
  const groups = new Map(); // key "lat,lon" => array of row objects

  for (const row of rows) {
    const rawLat = row.eLat?.value ?? null;
    const rawLon = row.eLon?.value ?? null;
    const latNum = toNumber(rawLat);
    const lonNum = toNumber(rawLon);
    if (latNum == null || lonNum == null) continue;

    const key = `${latNum.toFixed(6)},${lonNum.toFixed(6)}`; // stable key
    if (!groups.has(key)) groups.set(key, { lat: latNum, lon: lonNum, rows: [] });
    groups.get(key).rows.push(row);
  }

  const markers = [];
  for (const [key, g] of groups.entries()) {
    // dedupe rows for this location so count and popup reflect unique entries
    const seenLocation = new Set();
    const dedupRows = [];
    for (const r of g.rows) {
      const artUri = (r.art?.value || '').trim();
      const artName = (r.nameArt?.value || '').trim();
      const artistUri = (r.creatorGND?.value || '').trim();
      const artistName = (r.nameArtist?.value || '').trim();
      const locUri = (r.eLoc?.value || '').trim();
      const locName = (r.nameLoc?.value || '').trim();
      const k = `${artUri}|${artName}|${artistUri}|${artistName}|${locUri}|${locName}`;
      if (seenLocation.has(k)) continue;
      seenLocation.add(k);
      dedupRows.push(r);
    }

    const count = dedupRows.length;
    if (count === 0) continue; // nothing to show

    let icon;
    if (count > 1) {
      icon = L.divIcon({
        className: '',
        html: `<div class="cluster-count">${count}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });
    } else {
      icon = L.divIcon({
        className: '',
        html: `<div class="single-marker-dot"></div>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });
    }

    const latlng = L.latLng(g.lat, g.lon);
    const m = L.marker(latlng, { icon }).addTo(map);
    // attach deduped rows to the marker for use in the popup
    m._dedupRows = dedupRows;

    // click handler shows a fixed-size scrollable popup with the list of unique entries
    m.on('click', function () {
        // prepare popup HTML
        // small helper to avoid injecting raw HTML from labels
        function escapeHtml(s) {
          return String(s || '').replace(/[&<>"']/g, function (c) {
            return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]);
          });
        }

        const rowsForPopup = this._dedupRows || [];
        const items = rowsForPopup.map(r => {
          const nameArt = r.nameArt?.value || '—';
          const nameLoc = r.nameLoc?.value || '—';
          const nameArtist = r.nameArtist?.value || '—';

          // prefer ?imgUrl (from your SPARQL), fall back to other vars if present
          const imgUrl = (r.imgUrl?.value || r.bildImage?.value || r.bild?.value || '').trim();

          // quick image test (jpg/png/gif/webp) — note single backslashes in the regex
          const isImage = /\.(jpe?g|png|gif|webp|svg)(\?|$)/i.test(imgUrl);

          const metaHtml = `<div class="meta">
            <div><strong>Artwork</strong>${escapeHtml(nameArt)}</div>
            <div><strong>Location</strong>${escapeHtml(nameLoc)}</div>
            <div><strong>Artist</strong>${escapeHtml(nameArtist)}</div>
          </div>`;

          const thumbHtml = isImage
            ? `<div class="thumb-wrap"><a href="${escapeHtml(imgUrl)}" target="_blank" rel="noopener"><img class="thumb" src="${escapeHtml(imgUrl)}" alt="${escapeHtml(nameArt)}"></a></div>`
            : `<div class="thumb-wrap"></div>`;

          return `<div class="item">${metaHtml}${thumbHtml}</div>`;
        });
        const itemsHtml = items.join('');
        const popupContent = `<div class="popup-list">${itemsHtml}</div>`;

        // NEW: ensure the popup will be fully visible in the current map view
        const popupWidth = 520;    // must match .popup-list width
        const popupHeight = 300;   // must match .popup-list height
        const margin = 12;         // padding between popup and map border

        const mapSize = map.getSize();
        const markerPoint = map.latLngToContainerPoint(latlng);

        // horizontal: ensure popup won't overflow left/right.
        const minX = popupWidth / 2 + margin;
        const maxX = Math.max(mapSize.x - popupWidth / 2 - margin, minX);
        const desiredX = Math.min(Math.max(markerPoint.x, minX), maxX);

        // vertical: popup is shown above the marker, so top of popup will be marker.y - popupHeight.
        const minY = popupHeight + margin;
        const maxY = Math.max(mapSize.y - margin, minY);
        const desiredY = Math.min(Math.max(markerPoint.y, minY), maxY);

        const delta = L.point(desiredX - markerPoint.x, desiredY - markerPoint.y);

        // open popup after panning (if needed)
        map.once('moveend', () => {
          const popup = L.popup({
            maxWidth: popupWidth + 40,
            minWidth: 200,
            closeButton: true,
            autoPan: false // we handle panning manually
          })
          .setLatLng(latlng)
          .setContent(popupContent)
          .openOn(map);
        });

        if (Math.abs(delta.x) < 1 && Math.abs(delta.y) < 1) {
          map.fire('moveend');
        } else {
          map.panBy(L.point(delta.x, -delta.y * 1.3), { animate: true, duration: 0.25 });
        }
      });

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