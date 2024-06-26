import json
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import shlex
import csv
import os


class TaskManager:
    def __init__(self, file_path, log_path):
        self.file_path = file_path
        self.log_path = log_path
        self.tasks = self.load_tasks()
        self.current_id = self.get_max_id() + 1

    def load_tasks(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Erreur: Fichier JSON mal formé.")
            return []

    def save_tasks(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def log_action(self, action, task_id=None, field=None, new_value=None):
        with open(self.log_path, 'a') as log_file:
            log_file.write(
                f"{datetime.now()} - Action: {action}, ID: {task_id}, Field: {field}, New Value: {new_value}\n")

    def get_max_id(self):
        def get_max_id_recursively(tasks, current_max):
            for task in tasks:
                current_max = max(current_max, task['id'])
                current_max = get_max_id_recursively(task['subtasks'], current_max)
            return current_max

        return get_max_id_recursively(self.tasks, 0)

    def add_task(self, title, description, due_date, priority, status, parent_id=None):
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Erreur: Format de date incorrect. Utilisez AAAA-MM-JJ HH:MM.")
            return

        if due_date_obj < datetime.now():
            print("Erreur: La date d'échéance ne peut pas être inférieure à la date actuelle.")
            return

        valid_priorities = ["haute", "moyenne", "basse"]
        if priority not in valid_priorities:
            print(f"Erreur: Priorité incorrecte. Utilisez {', '.join(valid_priorities)}.")
            return

        task = {
            "id": self.current_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "status": status,
            "subtasks": []
        }
        self.current_id += 1

        if parent_id:
            parent_task = self.find_task_by_id(int(parent_id))
            if parent_task:
                parent_task['subtasks'].append(task)
                self.save_tasks()
                self.log_action("add_subtask", parent_id)
                print(f"Sous-tâche ajoutée à la tâche ID: {parent_id}")
            else:
                print(f"Erreur: Tâche parente avec ID {parent_id} non trouvée.")
        else:
            self.tasks.append(task)
            self.save_tasks()
            self.log_action("add_task", task['id'])
            print(f"Tâche ajoutée: {title}")

    def find_task_by_id(self, task_id):
        def find_task_recursively(tasks, task_id):
            for task in tasks:
                if task["id"] == task_id:
                    return task
                subtask = find_task_recursively(task["subtasks"], task_id)
                if subtask:
                    return subtask
            return None

        return find_task_recursively(self.tasks, task_id)

    def delete_task(self, task_id):
        try:
            task_id = int(task_id)
            self.tasks = self._delete_task_recursively(self.tasks, task_id)
            self.save_tasks()
            self.log_action("delete_task", task_id)
            print(f"Tâche supprimée: {task_id}")
        except ValueError:
            print("Erreur: ID de tâche incorrect.")

    def _delete_task_recursively(self, tasks, task_id):
        new_tasks = []
        for task in tasks:
            if task["id"] == task_id:
                continue
            task["subtasks"] = self._delete_task_recursively(task["subtasks"], task_id)
            new_tasks.append(task)
        return new_tasks

    def list_tasks(self):
        if not self.tasks:
            print("Aucune tâche trouvée.")
        else:
            self.tasks.sort(key=lambda task: datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M"))
            for task in self.tasks:
                self.print_task(task)

    def print_task(self, task, indent=0):
        print(f"{' ' * indent}ID: {task['id']}, Titre: {task['title']}, Description: {task['description']}, "
              f"Échéance: {task['due_date']}, Priorité: {task['priority']}, Statut: {task['status']}")

        task['subtasks'].sort(key=lambda subtask: datetime.strptime(subtask['due_date'], "%Y-%m-%d %H:%M"))

        for subtask in task['subtasks']:
            self.print_task(subtask, indent + 4)

    def update_task(self, task_id, field, new_value):
        try:
            task_id = int(task_id)
        except ValueError:
            print("Erreur: ID de tâche incorrect.")
            return

        task = self.find_task_by_id(task_id)
        if task:
            if field not in task:
                print(f"Erreur: Champ {field} incorrect.")
                return
            task[field] = new_value
            self.save_tasks()
            self.log_action("update_task", task_id, field, new_value)
            print(f"Tâche mise à jour: {task_id}")
        else:
            print(f"Erreur: Tâche avec ID {task_id} non trouvée.")

    def update_task_status(self, task_id, new_status):
        self.update_task(task_id, "status", new_status)

    def filter_tasks(self, status):
        filtered_tasks = [task for task in self.tasks if task["status"] == status]
        if not filtered_tasks:
            print("Aucune tâche trouvée avec ce statut.")
            return

        for task in filtered_tasks:
            self.print_task(task)

    def send_reminder(self, task):
        email = "ayatadili75@gmail.com"
        password = "wfye nqcq mwhi ejob"
        recipient_email = "omaraator075@gmail.com"
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = recipient_email
        message["Subject"] = f"Rappel de tâche: {task['title']}"

        body = f"Vous avez une tâche en attente:\n\nTitre: {task['title']}\nDescription: {task['description']}\nÉchéance: {task['due_date']}"
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(email, password)
                server.sendmail(email, recipient_email, message.as_string())
                print("Email de rappel envoyé avec succès.")
        except smtplib.SMTPException as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")

    def check_due_tasks(self):
        for task in self.tasks:
            self.check_due_subtask(task)

    def check_due_subtask(self, task):
        try:
            due_date = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
            if due_date <= datetime.now() and task['status'] == "pending":
                self.send_reminder(task)
        except ValueError:
            print(f"Erreur: Date mal formée pour la tâche ID {task['id']}")
        for subtask in task['subtasks']:
            self.check_due_subtask(subtask)

    def export_tasks(self, file_path):
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ["id", "title", "description", "due_date", "priority", "status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for task in self.tasks:
                self.export_subtask(writer, task)

    def export_subtask(self, writer, task):
        writer.writerow({
            "id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "due_date": task["due_date"],
            "priority": task["priority"],
            "status": task["status"]
        })
        for subtask in task['subtasks']:
            self.export_subtask(writer, subtask)

    def import_tasks(self, file_path):
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    required_fields = ['title', 'description', 'due_date', 'priority', 'status']
                    if all(field in row for field in required_fields):
                        self.add_task(row['title'], row['description'], row['due_date'], row['priority'], row['status'])
                    else:
                        print(f"Erreur: Ligne invalide dans le fichier CSV: {row}")
        except FileNotFoundError:
            print(f"Erreur: Fichier CSV introuvable: {file_path}")


def print_help():
    print("\nCommandes disponibles:")
    print("  add <titre> <description> <échéance> <priorité> <statut> [<parent_id>]")
    print("  delete <id>")
    print("  list")
    print("  update <id> <champ> <nouvelle_valeur>")
    print("  update_status <id> <nouveau_statut>")
    print("  filter <statut>")
    print("  check")
    print("  export <file_path>")
    print("  import <file_path>")
    print("  help")
    print("  exit")


if __name__ == "__main__":
    file_path = "tasks.json"
    log_path = "task_log.txt"
    manager = TaskManager(file_path, log_path)

    while True:
        print("\nCommandes disponibles:")
        print("  1. Ajouter une tâche: add <titre> <description> <échéance> <priorité> <statut> [<parent_id>]")
        print("  2. Supprimer une tâche: delete <id>")
        print("  3. Lister toutes les tâches: list")
        print("  4. Mettre à jour une tâche: update <id> <champ> <nouvelle_valeur>")
        print("  5. Mettre à jour le statut d'une tâche: update_status <id> <nouveau_statut>")
        print("  6. Filtrer les tâches par statut: filter <statut>")
        print("  7. Vérifier les tâches dues et envoyer des rappels: check")
        print("  8. Exporter les tâches vers un fichier CSV: export <file_path>")
        print("  9. Importer les tâches à partir d'un fichier CSV: import <file_path>")
        print("  10. Afficher cette aide: help")
        print("  11. Quitter le programme: exit")

        user_input = input("\nEntrez une commande: ").strip().split(maxsplit=1)
        command = user_input[0].lower()

        if command == "add":
            if len(user_input) > 1:
                args = shlex.split(user_input[1])
                if len(args) >= 5:
                    title, description, due_date, priority, status = args[:5]
                    parent_id = args[5] if len(args) > 5 else None
                    manager.add_task(title, description, due_date, priority, status, parent_id)
                else:
                    print("Erreur: Paramètres manquants pour ajouter une tâche.")
            else:
                print(
                    "Erreur: Utilisation incorrecte de la commande add. Utilisez: add <titre> <description> <échéance> <priorité> <statut> [<parent_id>]")

        elif command == "delete":
            if len(user_input) > 1:
                task_id = user_input[1].strip()
                manager.delete_task(task_id)
            else:
                print("Erreur: Utilisation incorrecte de la commande delete. Utilisez: delete <id>")

        elif command == "list":
            manager.list_tasks()

        elif command == "update":
            if len(user_input) > 1:
                args = user_input[1].split(maxsplit=2)
                if len(args) == 3:
                    task_id, field, new_value = args
                    manager.update_task(task_id, field, new_value)
                else:
                    print("Erreur: Paramètres manquants pour mettre à jour une tâche.")
            else:
                print(
                    "Erreur: Utilisation incorrecte de la commande update. Utilisez: update <id> <champ> <nouvelle_valeur>")

        elif command == "update_status":
            if len(user_input) > 1:
                args = user_input[1].split(maxsplit=1)
                if len(args) == 2:
                    task_id, new_status = args
                    manager.update_task_status(task_id, new_status)
                else:
                    print("Erreur: Paramètres manquants pour mettre à jour le statut d'une tâche.")
            else:
                print(
                    "Erreur: Utilisation incorrecte de la commande update_status. Utilisez: update_status <id> <nouveau_statut>")

        elif command == "filter":
            if len(user_input) > 1:
                status = user_input[1].strip()
                manager.filter_tasks(status)
            else:
                print("Erreur: Utilisation incorrecte de la commande filter. Utilisez: filter <statut>")

        elif command == "check":
            manager.check_due_tasks()

        elif command == "export":
            if len(user_input) > 1:
                file_path = user_input[1].strip()
                manager.export_tasks(file_path)
            else:
                print("Erreur: Utilisation incorrecte de la commande export. Utilisez: export <file_path>")

        elif command == "import":
            if len(user_input) > 1:
                file_path = user_input[1].strip()
                manager.import_tasks(file_path)
            else:
                print("Erreur: Utilisation incorrecte de la commande import. Utilisez: import <file_path>")

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Fermeture du programme...")
            break

        else:
            print(f"Erreur: Commande inconnue '{command}'.")
            print_help()
