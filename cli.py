import argparse
import requests
import sys
import time
import subprocess
import threading
from app.reset_index_prices import reset_table, fetch_and_store_index_prices
from app.db import SessionLocal, Index, IndexPrice, Base, engine
def init_db():
    print("[CLI] Initializing database and creating all tables if not exist...")
    Base.metadata.create_all(engine)
    print("[CLI] Database initialized. All tables are created.")


def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url)
            return True
        except Exception:

            # English CLI implementation
            import argparse
            import requests
            import sys
            import time
            import subprocess
            import threading
            from app.reset_index_prices import reset_table, fetch_and_store_index_prices
            from app.db import SessionLocal, Index, IndexPrice, Base, engine

            def init_db():
                print("[CLI] Initializing database and creating all tables if not exist...")
                Base.metadata.create_all(engine)
                print("[CLI] Database initialized. All tables are created.")

            def wait_for_server(url, timeout=15):
                start = time.time()
                while time.time() - start < timeout:
                    try:
                        requests.get(url)
                        return True
                    except Exception:
                        time.sleep(1)
                return False

            def stream_output(proc):
                while True:
                    line = proc.stdout.readline()
                    if line:
                        print("[uvicorn]", line.rstrip(), flush=True)
                    if proc.poll() is not None:
                        break

            def ensure_server():
                url = "http://localhost:8000/"
                try:
                    requests.get(url)
                    return None
                except Exception:
                    print("[CLI] FastAPI server is not running. Starting uvicorn ...")
                    proc = subprocess.Popen(
                        [sys.executable, "-u", "-m", "uvicorn", "app.main:app",
                         "--host", "127.0.0.1", "--port", "8000",
                         "--access-log", "--use-colors", "--log-level", "debug"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        bufsize=1,
                        universal_newlines=True,
                        encoding='utf-8'
                    )
                    threading.Thread(target=stream_output, args=(proc,), daemon=True).start()
                    if wait_for_server(url, timeout=15):
                        print("[CLI] FastAPI server started.", flush=True)
                        return proc
                    else:
                        print("[CLI] Failed to start FastAPI server.", flush=True)
                        proc.terminate()
                        sys.exit(1)

            def reset_index_prices():
                print("[CLI] Resetting index_prices table...")
                session = SessionLocal()
                indices = session.query(Index).all()
                session.close()
                reset_table(IndexPrice)
                fetch_and_store_index_prices([idx.name for idx in indices])
                print("[CLI] Index prices reset completed.")

            def fetch_index_prices():
                print("[CLI] Fetching and storing index prices...")
                session = SessionLocal()
                indices = session.query(Index).all()
                session.close()
                fetch_and_store_index_prices([idx.name for idx in indices])
                print("[CLI] Fetch completed.")

            def fix_index_prices():
                print("[CLI] Fixing index prices data...")
                session = SessionLocal()
                session.query(IndexPrice).filter(IndexPrice.high.is_(None)).update({"high": IndexPrice.close, "low": IndexPrice.close})
                session.query(IndexPrice).filter(IndexPrice.open.is_(None)).update({"open": IndexPrice.close})
                session.commit()
                session.close()
                print("[CLI] Index prices fixed.")

            def main():
                parser = argparse.ArgumentParser(description="Gravity TSETMC CLI")
                subparsers = parser.add_subparsers(dest="command")

                # Existing commands
                subparsers.add_parser("init", help="Initialize and store all initial data")
                update_parser = subparsers.add_parser("update", help="Update database data")
                update_parser.add_argument("what", nargs="?", default=None, help="Type of data to update (e.g. usd)")

                # New commands
                subparsers.add_parser("init-db", help="Create all database tables if not exist")
                subparsers.add_parser("reset-index-prices", help="Reset index_prices table and reload data")
                subparsers.add_parser("fetch-index-prices", help="Fetch and store index prices")
                subparsers.add_parser("fix-index-prices", help="Fix index prices data (fill NaNs)")
                subparsers.add_parser("init-all", help="Professional full initialization and update of all database tables and data")

                args = parser.parse_args()

                if args.command == "init-db":
                    print("[CLI] Initializing database and creating all tables if not exist...")
                    init_db()
                    print("[CLI] Database initialized. All tables are created.")
                    return
                elif args.command == "reset-index-prices":
                    print("[CLI] Resetting index_prices table...")
                    reset_index_prices()
                    print("[CLI] Index prices reset completed.")
                    return
                elif args.command == "fetch-index-prices":
                    print("[CLI] Fetching and storing index prices...")
                    fetch_index_prices()
                    print("[CLI] Fetch completed.")
                    return
                elif args.command == "fix-index-prices":
                    print("[CLI] Fixing index prices data...")
                    fix_index_prices()
                    print("[CLI] Index prices fixed.")
                    return
                elif args.command == "init-all":
                    print("[CLI] Starting professional full initialization and update of all tables and data ...", flush=True)
                    import subprocess
                    subprocess.run([sys.executable, "-m", "app.init_all"], check=True)
                    print("[CLI] init-all operation completed successfully.", flush=True)
                    return

                proc = ensure_server()

                if args.command == "init":
                    print("[CLI] Sending request to /fetch-all/ ...", flush=True)
                    r = requests.post("http://localhost:8000/fetch-all/")
                    print("[CLI] Request sent. Waiting for completion...", flush=True)
                    while proc and proc.poll() is None:
                        time.sleep(0.1)
                    print(r.json())
                elif args.command == "update":
                    if args.what == "usd":
                        print("[CLI] Sending request to /update-usd/ ...", flush=True)
                        r = requests.post("http://localhost:8000/update-usd/")
                        print("[CLI] Request sent. Waiting for completion...", flush=True)
                        while proc and proc.poll() is None:
                            time.sleep(0.1)
                        print(r.json())
                    else:
                        print("[CLI] Sending request to /update-db/ ...", flush=True)
                        payload = {
                            "symbols": ["FMLI", "KHODRO"],
                            "indices": ["Main Index"],
                            "industries": ["Automotive and Parts"],
                            "adjust": True
                        }
                        r = requests.post("http://localhost:8000/update-db/", json=payload)
                        print("[CLI] Request sent. Waiting for completion...", flush=True)
                        while proc and proc.poll() is None:
                            time.sleep(0.1)
                        print(r.json())
                else:
                    parser.print_help()

            if __name__ == "__main__":
                main()
