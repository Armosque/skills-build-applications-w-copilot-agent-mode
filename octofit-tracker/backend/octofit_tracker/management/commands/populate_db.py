from django.core.management.base import BaseCommand
from octofit_tracker.models import User, Team, Activity, Leaderboard, Workout
from django.conf import settings
from pymongo import MongoClient
from datetime import timedelta
from bson import ObjectId
from octofit_tracker.test_data import test_users, test_teams, test_activities, test_leaderboard, test_workouts

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activities, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        # Conectar a MongoDB
        client = MongoClient(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['PORT'])
        db = client[settings.DATABASES['default']['NAME']]

        # Eliminar colecciones existentes
        db.users.drop()
        db.teams.drop()
        db.activities.drop()
        db.leaderboard.drop()
        db.workouts.drop()

        # Crear usuarios
        users = [User(_id=ObjectId(), **user) for user in test_users]
        User.objects.bulk_create(users)

        # Crear equipos
        for team_data in test_teams:
            team = Team(_id=ObjectId(), name=team_data['name'])
            team.save()
            for username in team_data['members']:
                user = User.objects.get(username=username)
                team.members.add(user)

        # Crear actividades
        activities = [
            Activity(_id=ObjectId(), user=User.objects.get(username=activity['user']),
                     activity_type=activity['activity_type'], duration=timedelta(hours=int(activity['duration'].split(':')[0]), minutes=int(activity['duration'].split(':')[1])))
            for activity in test_activities
        ]
        Activity.objects.bulk_create(activities)

        # Crear entradas de la tabla de clasificación
        leaderboard_entries = [
            Leaderboard(_id=ObjectId(), user=User.objects.get(username=entry['user']), score=entry['score'])
            for entry in test_leaderboard
        ]
        Leaderboard.objects.bulk_create(leaderboard_entries)

        # Crear entrenamientos
        workouts = [Workout(_id=ObjectId(), **workout) for workout in test_workouts]
        Workout.objects.bulk_create(workouts)

        self.stdout.write(self.style.SUCCESS('Base de datos poblada con datos de prueba correctamente.'))
