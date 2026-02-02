import argparse
import sys
import json
from agents.knowledge_memory.memory_store import MemoryStore

def main():
    parser = argparse.ArgumentParser(description="Knowledge Memory Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Store command
    store_parser = subparsers.add_parser("store", help="Store a new knowledge entry")
    store_parser.add_argument("--title", required=True, help="Title of the entry")
    store_parser.add_argument("--problem", required=True, help="Description of the problem")
    store_parser.add_argument("--solution", required=True, help="The solution or knowledge content")
    store_parser.add_argument("--tags", nargs="*", help="Tags for categorization")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for knowledge entries")
    search_parser.add_argument("--query", help="Keywords to search for")
    search_parser.add_argument("--tags", nargs="*", help="Tags that must be present")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")

    # List command
    subparsers.add_parser("list", help="List all knowledge entries")

    args = parser.parse_args()
    store = MemoryStore()

    if args.command == "store":
        result = store.add_entry(args.title, args.problem, args.solution, args.tags)
        print(json.dumps(result.model_dump(mode='json'), indent=2))
    elif args.command == "search":
        result = store.search(args.query, args.tags, args.limit)
        print(json.dumps(result.model_dump(mode='json'), indent=2))
    elif args.command == "list":
        entries = store.get_all()
        print(json.dumps([e.model_dump(mode='json') for e in entries], indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
