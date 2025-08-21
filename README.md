# LangGraph v0.3 — POC Multi-Agent Supervisor (Azure OpenAI)

POC multi-agent basé sur l’architecture **Supervisor** de LangGraph v0.3, intégrant **Azure OpenAI**.

## Points clés
- **Supervisor** préconstruit via `create_supervisor`, délégation par **handoff tools**, et **forwarding tool**.  
- Handoffs avancés via `Send/Command` pour passer un **brief ciblé** sans exposer tout l’historique.  
- **Agents prébâtis** `create_react_agent` pour aller vite (research, math, writer).  
- **Mémoire**: checkpointer + store en mémoire.

Docs / annonces: tutoriel supervisor, référence API supervisor + forwarding, handoffs & Send/Command, release 0.3 (prebuilts), agents préconstruits, init modèles & Azure. :contentReference[oaicite:7]{index=7}

## Installation
- **Cloner le dépôt**
```bash
git clone https://github.com/Tomikz/LangGraph.git
cd Supervisor
```
- **Créer un environnement virtuel**
```bash
python -m venv .venv
```
- **Activer l’environnement**
```bash
.venv\Scripts\activate (Windows)
source .venv/bin/activate (Linux/MacOS)
```
- **Installer les dépendances**
```bash
pip install -U -r requirements.txt
```
## Configuration
Créer un fichier `.env` et renseigner:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_BASE` (endpoint Azure)
- `AZURE_OPENAI_API_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_VERSION`

## Lancer et changer le prompt selon le souhait
```bash
python -m src.app "Résume la stratégie IA de l'UE en 2024/2025 en 5 points, cite les sources, et évalue l'impact économique."
