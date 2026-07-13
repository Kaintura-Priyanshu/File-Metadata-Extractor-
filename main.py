#!/usr/bin/env python3
import sys
import argparse

from src.core.extractor import FileMetadataExtractor
from src.output.json_formatter import JSONFormatter
from src.output.console_formatter import ConsoleFormatter
from src.utils.file_utils import is_valid_file_path

__version__ = "1.0.0"

def main():
    parser = argparse.ArgumentParser(
        description="Extract comprehensive metadata from files"
    )
    parser.add_argument(
        "file_path",
        help="Path to the file to analyze"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["console", "json"],
        default="console",
        help="Output format (console or json)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save output to a file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output including raw metadata"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if not is_valid_file_path(args.file_path):
        print(f"Error: Invalid file path: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        extractor = FileMetadataExtractor()
        metadata = extractor.extract(args.file_path)

        if args.format == "json":
            output = JSONFormatter.format(metadata, pretty=True)
        else:
            output = ConsoleFormatter.format(metadata)

        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Output saved to: {args.output}")
            except OSError as e:
                print(f"Error: Could not write to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error extracting metadata: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

