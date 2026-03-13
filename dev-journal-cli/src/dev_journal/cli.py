import argparse
from pathlib import Path

from dev_journal.service import TaskService
from dev_journal.storage import TaskStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dev-journal", description="Developer task journal CLI")
    parser.add_argument("--db", default="tasks.db", help="Path to SQLite database file")
    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add", help="Add a new task")
    add_cmd.add_argument("title", help="Task title")
    add_cmd.add_argument("--priority", default="medium", choices=["low", "medium", "high"])
    add_cmd.add_argument("--tags", default="", help="Comma-separated list of tags")

    list_cmd = sub.add_parser("list", help="List tasks")
    list_cmd.add_argument("--all", action="store_true", help="Include completed tasks")

    done_cmd = sub.add_parser("done", help="Mark a task as complete")
    done_cmd.add_argument("task_id", type=int)

    delete_cmd = sub.add_parser("delete", help="Delete a task")
    delete_cmd.add_argument("task_id", type=int)

    sub.add_parser("stats", help="Show task stats")
    return parser


def _print_tasks(tasks) -> None:
    if not tasks:
        print("No tasks found.")
        return

    print(f"{'ID':<4}{'Status':<8}{'Priority':<10}{'Tags':<20}Title")
    for task in tasks:
        status = "DONE" if task.is_done else "OPEN"
        priority = task.priority.upper()
        tags = task.tags if task.tags else "-"
        print(f"{task.task_id:<4}{status:<8}{priority:<10}{tags:<20}{task.title}")


def _print_stats(stats: dict[str, int]) -> None:
    print("Task Stats")
    print(f"  Total tasks:        {stats['total']}")
    print(f"  Open tasks:         {stats['open']}")
    print(f"  Completed tasks:    {stats['done']}")
    print(f"  High-priority open: {stats['high_priority_open']}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db_path = Path(args.db)
    service = TaskService(TaskStorage(db_path))

    if args.command == "add":
        task_id = service.create_task(args.title, priority=args.priority, tags=args.tags)
        print(f"Created task #{task_id}.")
        return 0

    if args.command == "list":
        tasks = service.list_tasks(include_done=args.all)
        _print_tasks(tasks)
        return 0

    if args.command == "done":
        if service.complete_task(args.task_id):
            print(f"Task #{args.task_id} marked as complete.")
            return 0
        print(f"Task #{args.task_id} was not found or is already completed.")
        return 1

    if args.command == "delete":
        if service.remove_task(args.task_id):
            print(f"Task #{args.task_id} deleted.")
            return 0
        print(f"Task #{args.task_id} was not found.")
        return 1

    if args.command == "stats":
        _print_stats(service.get_stats())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())