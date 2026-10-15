import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        if len(sys.argv) > 2 and sys.argv[2] == "setup":
            from .installer import setup
            setup()
            return

    from .agent import run
    run()

if __name__ == "__main__":
    main()
