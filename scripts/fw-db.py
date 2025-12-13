import argparse
import os
import sys
from datetime import datetime
import importlib

# Add project root to sys.path to allow importing fishwrap
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Placeholder for _config and repository, to be reloaded/configured dynamically
_config = None
repository = None

def configure_repository(config_path):
    """Sets FISHWRAP_CONFIG env var and reloads _config and repository module."""
    global _config, repository
    
    if config_path:
        os.environ['FISHWRAP_CONFIG'] = config_path
    else:
        # Default or clear if not specified
        if 'FISHWRAP_CONFIG' in os.environ:
            del os.environ['FISHWRAP_CONFIG']

    # Reload _config to pick up new env var
    _config = importlib.import_module('fishwrap._config')
    importlib.reload(_config)

    # Reload repository to ensure it picks up the current _config.DATABASE_URL
    repository = importlib.import_module('fishwrap.db.repository')
    importlib.reload(repository)


def status_command(args):
    """Shows basic status of the database."""
    # configure_repository(args.config) # Handled in main()

    print("--- Database Status ---")

    db_url = getattr(_config, 'DATABASE_URL', 'sqlite:///newsroom.db')
    print(f"Configured Database: {db_url}")

    # Resolve absolute path for SQLite
    db_file_path = None
    if db_url.startswith('sqlite:///'):
        db_file = db_url.replace('sqlite:///', '')
        if not os.path.isabs(db_file):
            # Assumes CWD is the project root for relative paths in config
            db_file_path = os.path.abspath(db_file) 
        else:
            db_file_path = db_file
    
    if db_file_path and not os.path.exists(db_file_path):
        print(f"Error: Database file not found: {db_file_path}")
        return

    if db_file_path:
        print(f"Database File: {db_file_path}")
        print(f"Size on Disk: {os.path.getsize(db_file_path) / (1024*1024):.2f} MB")

    # Total Articles
    total_articles = repository.get_total_count()
    print(f"Total Articles: {total_articles}")

    # Total Runs
    total_runs = repository.get_total_runs()
    print(f"Total Runs: {total_runs}")

    # Last Run Date (if any)
    last_run = repository.get_last_run()
    if last_run:
        print(f"Last Run: {last_run.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({last_run.id[:8]})")
    
    print("Database Integrity: OK (basic connection test)")


def runs_command(args):
    """Lists recent runs."""
    # configure_repository(args.config) # Handled in main()
    
    runs = repository.get_recent_runs(limit=args.limit)
    
    if not runs:
        print("No runs recorded.")
        return

    print(f"{'ID':<10} | {'Date':<20} | {'Total':<8} | {'Pub':<5} | {'Signal %'}")
    print("-" * 65)
    
    for r in runs:
        total = r.get('stats_input', 0)
        selected = r.get('stats_selected', 0)
        signal_pct = (selected / total * 100) if total > 0 else 0.0
        
        run_id = r.get('id', '')[:8]
        ts = r.get('timestamp')
        if hasattr(ts, 'strftime'):
            date_str = ts.strftime('%Y-%m-%d %H:%M')
        else:
            try:
                date_str = str(ts)[:16].replace('T', ' ')
            except:
                date_str = "Unknown"

        print(f"{run_id:<10} | {date_str:<20} | {total:<8} | {selected:<5} | {signal_pct:.1f}%")
    print("-" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="Fishwrap Database Utility - Manage and inspect Fishwrap's SQLite databases."
    )
    
    # Define --config as a global argument
    parser.add_argument(
        '--config',
        type=str,
        help='Path to the Fishwrap configuration file (e.g., demo/config.py) to specify which database to operate on.'
    )

    # Parse KNOWN args first to get --config before subparsers might consume it confusingly
    args, remaining_argv = parser.parse_known_args()

    # Configure repository based on parsed arguments
    configure_repository(args.config)

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show basic database status (read-only).')
    status_parser.set_defaults(func=status_command)

    # Prune command
    prune_parser = subparsers.add_parser('prune', help='Clean old articles from the database.')
    prune_parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Articles older than this many days will be pruned. Default is 7 days.'
    )
    prune_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be pruned without actually deleting anything.'
    )
    prune_parser.add_argument(
        '--yes',
        action='store_true',
        help='Execute prune operation without confirmation.'
    )
    prune_parser.set_defaults(func=lambda args: print("Prune not yet implemented. Use --dry-run for now."))

    # Runs command
    runs_parser = subparsers.add_parser('runs', help='List recent runs (editions).')
    runs_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Limit the number of recent runs to display. Default is 10.'
    )
    runs_parser.set_defaults(func=runs_command)

    # Re-parse args including subparsers
    # We pass 'remaining_argv' to parse_args, but we need to merge with the 'args' namespace we already have?
    # Actually, standard parse_args() on remaining might fail if it expects 'status' to be the first arg
    # if we already consumed --config.
    
    # Simpler approach: Just re-parse everything now that we've side-effected the config.
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()