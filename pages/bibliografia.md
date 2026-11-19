---
layout: base/page
permalink: /bibliografia/
title: Bibliografia sobre els orgues
description: >-
  Recull de la bibliografia sobre els orgues de Catalunya i sobre l’orgue en general.

header:
  src: https://nextcloud.acorgue.cat/s/FWi9W5FyitZFpRg/download
  alt: llibres

redirect_from:
  - bibliografia
---

## Llibres

Història sobre els orgues de Catalunya:

{% include bibliografia/llibres.html data=site.data.bibliografia.llibres %}

Llibrets informatius:

{% include bibliografia/llibres.html data=site.data.bibliografia.llibrets %}

Bibliografia general

{% include bibliografia/llibres.html data=site.data.bibliografia.general %}

## CD

CDs de música gravats en orgues catalans:

{% include bibliografia/cd.html data=site.data.bibliografia.cd %}
