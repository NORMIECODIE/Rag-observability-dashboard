import time 
from contextlib import contextmanager


@contextmanager
def span(name: str, trace: list):
    start = time.time()


    record = {
        "name": name,
        "start": start
    }


    try: 
        yield record

        record["status"] = "ok"


    except Exception as e:

        record["status"] = "error"
        record["error"] = str(e)

        raise

    finally:

        record["end"] = time.time()

        record["duration_ms"] = round(
            (record["end"] - record["start"]) * 1000,
            1
        )

        trace.append(record)