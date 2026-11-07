# Fuentes del panorama de la sesión 1

Todas las cifras del panorama vienen de estas fuentes. Las marcadas **NO VERIFICADO** no se usan en el deck.

## Datos calculados en este repositorio

| Dato | Fuente | Cómo se obtiene |
|---|---|---|
| CVE publicados por año, 1999–2026 | NVD (NIST), API 2.0 | `python3 nvd_cve.py anios 1999 2026 > cve_por_anio.csv` |
| CVE de 2025 por CWE | NVD (NIST), API 2.0 | `python3 nvd_cve.py cwe 2025 > cwe_2025.csv` |
| Vulnerabilidades explotadas (KEV) | CISA, catálogo KEV, versión 2026.11.06 | `curl -o kev.json https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` |
| Gráficos | Los tres archivos anteriores, `paquetes.csv` y `dbir.csv` | `docker build -t ucp-graficos . && docker run --rm -v "$PWD":/datos ucp-graficos python graficos.py` |

## Informes de la industria

| Cifra | Fuente |
|---|---|
| Paquetes maliciosos 2019–2022: ~0, 1.200, 12.000, 88.000 | Sonatype vía The Stack, 18 oct. 2022: <https://thestack.technology/malicious-open-source-packages-up-633-percent/> |
| 245.032 paquetes maliciosos en 2023 (ene–sep) | Sonatype vía Infosecurity Magazine, 3 oct. 2023: <https://www.infosecurity-magazine.com/news/open-source-supply-chain-attacks-2/> |
| +156 % en 2024; 704.102 acumulados desde 2019 | Sonatype, nota de prensa del 10.º informe, 10 oct. 2024: <https://www.sonatype.com/en/press-releases/sonatypes-10th-annual-state-of-the-software-supply-chain-report> |
| 512.847 en 2024 | Cifra de prensa (Infosecurity, SiliconANGLE); no aparece en la nota de Sonatype |
| 454.648 nuevos en 2025; 1,233 millones acumulados; 99 % en npm | Sonatype 2026: <https://sonatype.com/state-of-the-software-supply-chain/2026/open-source-malware> · cifra exacta: <https://www.infosecurity-magazine.com/news/454000-malicious-open-source/> |
| +73 % de detecciones en 2025 | ReversingLabs 2026: <https://www.reversinglabs.com/press-releases/reversinglabs-2026-software-supply-chain-security-report-identifies-73-increase-in-malicious-open-source-packages> |
| DBIR 2024: explotación +180 %; terceros 15 % | <https://www.verizon.com/about/news/2024-data-breach-investigations-report-vulnerability-exploitation-boom> |
| DBIR 2025: explotación 20 %; terceros 30 % | <https://www.verizon.com/about/news/2025-data-breach-investigations-report> |
| DBIR 2026: explotación 31 %, primer vector; terceros 48 % | SecurityWeek, 19 may. 2026: <https://www.securityweek.com/verizon-dbir-2026-vulnerability-exploitation-overtakes-credential-theft-as-top-breach-vector/> |
| Costo promedio de una brecha: 4,88 / 4,44 / 4,99 M USD | IBM 2024: <https://newsroom.ibm.com/2024-07-30-ibm-report-escalating-data-breach-disruption-pushes-costs-to-new-highs> · 2025: <https://newsroom.ibm.com/2025-07-30-ibm-report-13-of-organizations-reported-breaches-of-ai-models-or-applications,-97-of-which-reported-lacking-proper-ai-access-controls> · 2026: <https://newsroom.ibm.com/2026-07-29-ibm-study-one-in-four-malicious-breaches-are-ai-enabled,-costing-companies-6-million-on-average> |

## Colombia

| Cifra | Fuente |
|---|---|
| 36.998 denuncias ene–may 2026 frente a 27.228 en 2025 (+36 %) | Ministerio de Defensa vía Portafolio, 26 jul. 2026: <https://www.portafolio.co/tecnologia/delitos-informaticos-aumentaron-36-en-colombia-estudio-revela-como-operan-hoy-los-ciberdelincuentes-498974> |
| 67.216 denuncias en 2025 | Centro Cibernético Policial vía Vanguardia, 27 jul. 2026: <https://www.vanguardia.com/area-metropolitana/2026/07/27/alerta-por-fraude-cibernetico-en-bucaramanga-866-denuncias-y-tres-claves-para-proteger-sus-cuentas/> |
| «44.773 denuncias en el primer semestre de 2026» | **NO VERIFICADO**: no aparece en ninguna fuente |
| «10,9 billones de intentos de ciberataque en 2025, tercer país de la región» | **PARCIALMENTE VERIFICADO**: cifra atribuida a FortiGuard Labs por la prensa; la posición varía entre fuentes y la unidad («billones») es ambigua |

## Incidentes de la línea de tiempo

| Incidente | Fecha | Fuente |
|---|---|---|
| SolarWinds Orion | dic. 2020 | CISA: <https://www.cisa.gov/news-events/news/cisa-issues-emergency-directive-mitigate-compromise-solarwinds-orion-network-management-products> |
| Codecov | abr. 2021 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/popular-codecov-code-coverage-tool-hacked-to-steal-dev-credentials/> |
| Kaseya VSA | jul. 2021 | The Record: <https://therecord.media/kaseya-more-than-1500-downstream-businesses-impacted-by-ransomware-attack> |
| ua-parser-js | oct. 2021 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/popular-npm-library-hijacked-to-install-password-stealers-miners/> |
| Log4Shell | dic. 2021 | CISA: <https://www.cisa.gov/news-events/alerts/2021/12/10/apache-releases-log4j-version-2150-address-critical-rce-vulnerability-under-exploitation> |
| PyTorch torchtriton | dic. 2022 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/pytorch-discloses-malicious-dependency-chain-compromise-over-holidays/> |
| 3CX | mar. 2023 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/hackers-compromise-3cx-desktop-app-in-a-supply-chain-attack/> |
| MOVEit | jun. 2023 | The Record: <https://therecord.media/data-of-sixteen-million-exposed-moveit> · CISA AA23-158A |
| xz utils | mar. 2024 | CISA: <https://www.cisa.gov/news-events/alerts/2024/03/29/reported-supply-chain-compromise-affecting-xz-utils-data-compression-library-cve-2024-3094> |
| polyfill.io | jun. 2024 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/polyfillio-javascript-supply-chain-attack-impacts-over-100k-sites/> |
| tj-actions/changed-files | mar. 2025 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/github-action-supply-chain-attack-exposed-secrets-in-218-repos/> |
| chalk y debug | sep. 2025 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/hackers-hijack-npm-packages-with-2-billion-weekly-downloads-in-supply-chain-attack/> |
| Shai-Hulud | sep. 2025 | CISA: <https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem> |
| Shai-Hulud 2.0 | nov. 2025 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/shai-hulud-20-npm-malware-attack-exposed-up-to-400-000-dev-secrets/> |
| Trivy | mar. 2026 | BleepingComputer: <https://www.bleepingcomputer.com/news/security/trivy-vulnerability-scanner-breach-pushed-infostealer-via-github-actions/> |
| ChainDrop | ago. 2026 | BleepingComputer: <https://bleepingcomputer.com/news/security/massive-chaindrop-npm-supply-chain-attack-infects-hundreds-of-packages> · StepSecurity: <https://www.stepsecurity.io/blog/chaindrop-npm-worm> |
