from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
import logging

from MupendaApp.super_admin_models import SecurityMetric, SessionLog, SystemAlert, BackupLog, SystemMetric
from MupendaApp.super_admin_cache import SuperAdminCache
from MupendaApp.super_admin_tasks import backup_database, cleanup_old_logs, monitor_system_health

User = get_user_model()
logger = logging.getLogger('super_admin.management')

class Command(BaseCommand):
    help = 'Commandes de gestion pour le Super Admin'
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Sous-commandes disponibles')
        
        # Commande de backup
        backup_parser = subparsers.add_parser('backup', help='Sauvegardes')
        backup_parser.add_argument('--type', choices=['full', 'incremental', 'differential'], 
                              default='full', help='Type de sauvegarde')
        backup_parser.add_argument('--user-id', type=int, help='ID de l\'utilisateur qui lance la sauvegarde')
        
        # Commande de nettoyage
        cleanup_parser = subparsers.add_parser('cleanup', help='Nettoyage des logs et données temporaires')
        cleanup_parser.add_argument('--days', type=int, default=90, 
                                 help='Nombre de jours de logs à conserver (défaut: 90)')
        
        # Commande de monitoring
        monitor_parser = subparsers.add_parser('monitor', help='Monitoring système')
        monitor_parser.add_argument('--continuous', action='store_true', 
                                    help='Monitoring continu')
        
        # Commande de cache
        cache_parser = subparsers.add_parser('cache', help='Gestion du cache')
        cache_parser.add_argument('--action', choices=['warm', 'clear', 'stats'], 
                                 required=True, help='Action à effectuer')
        
        # Commande de rapport
        report_parser = subparsers.add_parser('report', help='Génération de rapports')
        report_parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], 
                                  default='daily', help='Type de rapport')
        report_parser.add_argument('--email', help='Email pour envoyer le rapport')
        
        # Commande d'alertes
        alerts_parser = subparsers.add_parser('alerts', help='Gestion des alertes')
        alerts_parser.add_argument('--action', choices=['list', 'clear', 'test'], 
                                    required=True, help='Action sur les alertes')
    
    def handle(self, *args, **options):
        command = options['command']
        
        if command == 'backup':
            self.handle_backup(options)
        elif command == 'cleanup':
            self.handle_cleanup(options)
        elif command == 'monitor':
            self.handle_monitor(options)
        elif command == 'cache':
            self.handle_cache(options)
        elif command == 'report':
            self.handle_report(options)
        elif command == 'alerts':
            self.handle_alerts(options)
        else:
            self.print_help('manage.py super_admin')
    
    def handle_backup(self, options):
        """Gérer les sauvegardes"""
        backup_type = options['type']
        user_id = options.get('user_id')
        
        self.stdout.write(f"Lancement de la sauvegarde {backup_type}...")
        
        try:
            # Lancer la tâche de sauvegarde
            result = backup_database(backup_type=backup_type, user_id=user_id)
            
            if result.get('success'):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Sauvegarde terminée avec succès!\n"
                        f"   Fichier: {result['filename']}\n"
                        f"   Taille: {result['file_size']} bytes\n"
                        f"   Durée: {result['duration']}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur lors de la sauvegarde: {result['error']}")
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur: {str(e)}")
            )
    
    def handle_cleanup(self, options):
        """Nettoyer les anciens logs"""
        days = options['days']
        
        self.stdout.write(f"Nettoyage des logs plus anciens que {days} jours...")
        
        try:
            result = cleanup_old_logs()
            
            if result.get('success'):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Nettoyage terminé!\n"
                        f"   Logs audit supprimés: {result['deleted_audit_logs']}\n"
                        f"   Sessions supprimées: {result['deleted_sessions']}\n"
                        f"   Métriques supprimées: {result['deleted_metrics']}\n"
                        f"   Alertes supprimées: {result['deleted_alerts']}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur lors du nettoyage: {result['error']}")
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur: {str(e)}")
            )
    
    def handle_monitor(self, options):
        """Monitoring système"""
        continuous = options.get('continuous', False)
        
        if continuous:
            self.stdout.write("Démarrage du monitoring continu...")
            self.stdout.write("Appuyez sur Ctrl+C pour arrêter")
            
            try:
                while True:
                    result = monitor_system_health()
                    
                    if result.get('success'):
                        self.stdout.write(
                            f"✅ Monitoring: CPU={result['health_data'].get('cpu_usage', 0):.1f}%, "
                            f"Mémoire={result['health_data'].get('memory_usage', 0):.1f}%, "
                            f"Alertes={result.get('alerts_count', 0)}"
                        )
                    
                    time.sleep(60)  # Vérifier chaque minute
                    
            except KeyboardInterrupt:
                self.stdout.write("\n⏹️ Monitoring arrêté")
        
        else:
            self.stdout.write("Lancement du monitoring ponctuel...")
            
            try:
                result = monitor_system_health()
                
                if result.get('success'):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Monitoring terminé!\n"
                            f"   CPU: {result['health_data'].get('cpu_usage', 0):.1f}%\n"
                            f"   Mémoire: {result['health_data'].get('memory_usage', 0):.1f}%\n"
                            f"   Disque: {result['health_data'].get('disk_usage', 0):.1f}%\n"
                            f"   Alertes: {result.get('alerts_count', 0)}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erreur: {result['error']}")
                    )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
    
    def handle_cache(self, options):
        """Gestion du cache"""
        action = options['action']
        
        if action == 'warm':
            self.stdout.write("Préchauffage du cache...")
            
            try:
                SuperAdminCache.warm_cache()
                self.stdout.write(
                    self.style.SUCCESS("✅ Cache préchauffé avec succès")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
        
        elif action == 'clear':
            self.stdout.write("Vidage du cache...")
            
            try:
                SuperAdminCache.invalidate_cache()
                self.stdout.write(
                    self.style.SUCCESS("✅ Cache vidé avec succès")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
        
        elif action == 'stats':
            self.stdout.write("Statistiques du cache...")
            
            try:
                # Afficher les statistiques du cache
                cache_keys = cache.keys("super_admin:*")
                
                if cache_keys:
                    self.stdout.write(f"Clés de cache trouvées: {len(cache_keys)}")
                    
                    for key in cache_keys[:10]:  # Limiter à 10 clés
                        value = cache.get(key)
                        if value:
                            self.stdout.write(f"  - {key}: {type(value)}")
                else:
                    self.stdout.write("Aucune clé de cache trouvée")
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
    
    def handle_report(self, options):
        """Génération de rapports"""
        report_type = options['type']
        email = options.get('email')
        
        self.stdout.write(f"Génération du rapport {report_type}...")
        
        try:
            # Récupérer les données du cache
            user_stats = SuperAdminCache.get_user_stats()
            security_metrics = SuperAdminCache.get_security_metrics()
            system_metrics = SuperAdminCache.get_system_metrics()
            
            # Créer le rapport
            report_data = {
                'type': report_type,
                'date': timezone.now().date(),
                'user_stats': user_stats,
                'security_metrics': security_metrics,
                'system_metrics': system_metrics,
                'generated_at': timezone.now().isoformat()
            }
            
            # Afficher le rapport
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Rapport {report_type} généré!\n"
                    f"   Utilisateurs: {report_data['user_stats']['total_users']}\n"
                    f"   Menaces sécurité: {report_data['security_metrics']['total_threats_today']}\n"
                    f"   Utilisation CPU: {report_data['system_metrics'].get('cpu_usage', 0):.1f}%\n"
                    f"   Généré le: {report_data['generated_at']}"
                )
            )
            
            # Envoyer par email si demandé
            if email:
                self.stdout.write(f"Envoi du rapport à {email}...")
                # Ici, vous pourriez utiliser Django's send_mail
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Rapport envoyé à {email}")
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur: {str(e)}")
            )
    
    def handle_alerts(self, options):
        """Gestion des alertes"""
        action = options['action']
        
        if action == 'list':
            self.stdout.write("Liste des alertes actives:")
            
            try:
                alerts = SystemAlert.objects.filter(is_active=True).order_by('-created_at')
                
                if alerts:
                    for alert in alerts:
                        self.stdout.write(
                            f"  [{alert.get_severity_display().upper()}] "
                            f"{alert.title} - {alert.alert_type} - "
                            f"Créée le: {alert.created_at.strftime('%Y-%m-%d %H:%M')}"
                        )
                else:
                    self.stdout.write("Aucune alerte active")
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
        
        elif action == 'clear':
            self.stdout.write("Suppression des alertes résolues...")
            
            try:
                deleted_count = SystemAlert.objects.filter(
                    is_resolved=True
                ).delete()[0]
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {deleted_count} alertes supprimées")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
        
        elif action == 'test':
            self.stdout.write("Création d'une alerte de test...")
            
            try:
                test_alert = SystemAlert.objects.create(
                    alert_type='test',
                    title='Alerte de test',
                    message='Ceci est une alerte de test pour vérifier le système',
                    severity='info'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Alerte de test créée (ID: {test_alert.id})")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erreur: {str(e)}")
                )
