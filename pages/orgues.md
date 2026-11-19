---
layout: base/page/orgues
permalink: /orgues/
title: Els orgues del principat
description: >-
  Inventari dels orgues de Catalunya. Aquí hi trobareu un resum dels orgues del principat i dels orgueners que hi han
  treballat, un mapa interactiu i llistes d’orgues ordenades per diferents criteris.

header:
  src: https://nextcloud.acorgue.cat/s/gszBZZFxKeJna8p/download
  alt: orgues
scripts:
  - taulaOrgues.js
redirect_from:
  - orgues
---

{% include llista-orgues/estadistiques-orgues.html %}

## Cercador

{% include llista-orgues/main-table.html %}

## Mapa

{% include llista-orgues/mapa.html %}

## Llistats d’orgues

{% include llista-orgues/main-llistat.html %}
