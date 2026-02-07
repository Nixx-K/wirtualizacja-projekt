# 📊 Monitoring Platform - Project Virtualization & Containerization

Projekt przedstawia zaawansowaną architekturę mikrousługową z pełnym stossem monitorującym. Został zbudowany z naciskiem na bezpieczeństwo sieciowe (izolacja warstw), limity zasobów oraz automatyczną konfigurację (Infrastructure as Code).

## 🚀 Architektura Systemu

Projekt składa się z 6 współpracujących kontenerów podzielonych na 3 dedykowane sieci typu `bridge`:

1.  **Nginx (Frontend Network)**: Reverse Proxy stanowiący jedyny punkt wejścia do systemu.
2.  **Demo-App (Frontend/Backend/Monitoring Networks)**: Aplikacja w Pythonie generująca metryki.
3.  **PostgreSQL (Backend Network)**: Relacyjna baza danych dla aplikacji.
4.  **Redis (Backend Network)**: Warstwa cache przyspieszająca operacje.
5.  **Prometheus (Monitoring/Backend Networks)**: System zbierający metryki (scraping) z aplikacji i infrastruktury.
6.  **Grafana (Monitoring Network)**: Narzędzie do wizualizacji danych z automatycznie skonfigurowanym dashboardem.



## 🛠️ Technologie
* **Docker & Docker Compose**
* **Python** (Application)
* **Nginx** (Reverse Proxy)
* **Prometheus** (Monitoring)
* **Grafana** (Visualization)
* **PostgreSQL & Redis** (Data layer)

## 🚦 Jak uruchomić projekt?

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/Nixx-K/wirtualizacja-projekt.git](https://github.com/Nixx-K/wirtualizacja-projekt.git)
    cd monitoring-platform
    ```

2.  **Uruchom cały stos:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Dostęp do usług:**
    * **Aplikacja (przez Proxy):** [http://localhost](http://localhost)
    * **Panel Prometheus:** [http://localhost:9090](http://localhost:9090)
    * **Dashboard Grafana:** [http://localhost:3000](http://localhost:3000)

## 🔐 Bezpieczeństwo i Konfiguracja
* **Sieci:** Zastosowano pełną izolację. Baza danych i Redis nie są dostępne bezpośrednio z hosta.
* **Poświadczenia:**
    * Grafana: `admin` / `admin`
    * Postgres: `userappki` / `haslotakzwanesekretne#321`
    * DB Name: `bazkadanych`
* **Limity:** Każdy serwis posiada zdefiniowane limity CPU (`0.25 - 0.5`) oraz RAM (`128MB - 512MB`).

## 📈 Monitoring (Grafana Provisioning)
Projekt wykorzystuje mechanizm **Provisioning**. Oznacza to, że po uruchomieniu kontenera Grafana automatycznie:
1. Dodaje Prometheusa jako źródło danych (Datasource).
2. Wczytuje gotowy dashboard z pliku `monitoring_dashboard.json`.
3. Jest gotowa do pracy bez manualnej konfiguracji.
