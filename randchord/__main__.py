from .app import Root
import sys

def main():
    Root(sys.argv[1] if len(sys.argv) > 1 else None)

if __name__ == "__main__":
    main()