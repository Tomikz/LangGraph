"""
Gestionnaire de rapports - Utilitaires pour gérer les rapports générés
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class ReportManager:
    """Gestionnaire pour les rapports générés"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.index_file = self.reports_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Charge l'index des rapports"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {"reports": []}
    
    def _save_index(self):
        """Sauvegarde l'index des rapports"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def add_report(self, filepath: str, query: str, metadata: Dict = None):
        """Ajoute un rapport à l'index"""
        report_info = {
            "id": len(self.index["reports"]) + 1,
            "filepath": str(filepath),
            "filename": os.path.basename(filepath),
            "query": query,
            "created_at": datetime.now().isoformat(),
            "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
            "metadata": metadata or {}
        }
        self.index["reports"].append(report_info)
        self._save_index()
        return report_info["id"]
    
    def list_reports(self, limit: int = 10) -> List[Dict]:
        """Liste les derniers rapports"""
        reports = sorted(
            self.index["reports"], 
            key=lambda x: x["created_at"], 
            reverse=True
        )
        return reports[:limit]
    
    def get_report(self, report_id: int) -> Optional[Dict]:
        """Récupère un rapport par son ID"""
        for report in self.index["reports"]:
            if report["id"] == report_id:
                return report
        return None
    
    def delete_report(self, report_id: int) -> bool:
        """Supprime un rapport"""
        report = self.get_report(report_id)
        if report:
            filepath = Path(report["filepath"])
            if filepath.exists():
                filepath.unlink()
            
            self.index["reports"] = [
                r for r in self.index["reports"] if r["id"] != report_id
            ]
            self._save_index()
            return True
        return False
    
    def clean_old_reports(self, keep_last: int = 10):
        """Nettoie les anciens rapports en gardant les N derniers"""
        reports = sorted(
            self.index["reports"], 
            key=lambda x: x["created_at"], 
            reverse=True
        )
        
        to_delete = reports[keep_last:]
        for report in to_delete:
            self.delete_report(report["id"])
        
        return len(to_delete)
    
    def export_report(self, report_id: int, export_dir: str = "exports") -> Optional[str]:
        """Exporte un rapport vers un autre dossier"""
        report = self.get_report(report_id)
        if not report:
            return None
        
        export_path = Path(export_dir)
        export_path.mkdir(exist_ok=True)
        
        source = Path(report["filepath"])
        if not source.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = export_path / f"export_{timestamp}_{report['filename']}"
        
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        export_meta = f"""<!--
RAPPORT EXPORTÉ
Date export: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source: {report['filepath']}
Requête originale: {report['query']}
-->

"""
        
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(export_meta)
            f.write(content)
        
        return str(dest)
    
    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur les rapports"""
        if not self.index["reports"]:
            return {
                "total": 0,
                "total_size": 0,
                "average_size": 0,
                "oldest": None,
                "newest": None
            }
        
        total_size = sum(r.get("size", 0) for r in self.index["reports"])
        dates = [r["created_at"] for r in self.index["reports"]]
        
        return {
            "total": len(self.index["reports"]),
            "total_size": total_size,
            "average_size": total_size // len(self.index["reports"]),
            "oldest": min(dates),
            "newest": max(dates),
            "formats": {
                "markdown": len([r for r in self.index["reports"] if r["filename"].endswith(".md")])
            }
        }


def main():
    """Interface CLI pour gérer les rapports"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de rapports")
    parser.add_argument("action", choices=["list", "stats", "clean", "export", "delete"],
                       help="Action à effectuer")
    parser.add_argument("--id", type=int, help="ID du rapport")
    parser.add_argument("--keep", type=int, default=10, 
                       help="Nombre de rapports à garder (pour clean)")
    parser.add_argument("--export-dir", default="exports",
                       help="Dossier d'export")
    
    args = parser.parse_args()
    
    manager = ReportManager()
    
    if args.action == "list":
        reports = manager.list_reports()
        if not reports:
            print("Aucun rapport trouvé.")
        else:
            print(f"\n{len(reports)} derniers rapports:\n")
            print(f"{'ID':<5} {'Date':<20} {'Taille':<10} {'Requête':<50}")
            print("-" * 85)
            for r in reports:
                date = datetime.fromisoformat(r["created_at"]).strftime("%Y-%m-%d %H:%M")
                size = f"{r['size']:,} B"
                query = r["query"][:47] + "..." if len(r["query"]) > 50 else r["query"]
                print(f"{r['id']:<5} {date:<20} {size:<10} {query:<50}")
    
    elif args.action == "stats":
        stats = manager.get_statistics()
        print("\nStatistiques des rapports:\n")
        print(f"  Total: {stats['total']} rapports")
        print(f"  Taille totale: {stats['total_size']:,} octets")
        if stats['total'] > 0:
            print(f"  Taille moyenne: {stats['average_size']:,} octets")
            print(f"  Plus ancien: {stats['oldest']}")
            print(f"  Plus récent: {stats['newest']}")
    
    elif args.action == "clean":
        deleted = manager.clean_old_reports(args.keep)
        print(f"{deleted} anciens rapports supprimés.")
        print(f"   {args.keep} derniers rapports conservés.")
    
    elif args.action == "export":
        if not args.id:
            print("Erreur: --id requis pour exporter")
        else:
            dest = manager.export_report(args.id, args.export_dir)
            if dest:
                print(f"Rapport exporté: {dest}")
            else:
                print(f"Erreur: Rapport {args.id} introuvable")
    
    elif args.action == "delete":
        if not args.id:
            print("Erreur: --id requis pour supprimer")
        else:
            if manager.delete_report(args.id):
                print(f"Rapport {args.id} supprimé")
            else:
                print(f"Erreur: Rapport {args.id} introuvable")


if __name__ == "__main__":
    main()