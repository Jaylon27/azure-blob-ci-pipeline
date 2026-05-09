from adls_client import filter_blobs


def test_filter_blobs_empty_input():
    assert filter_blobs([], ".csv.gz") == []


def test_filter_blobs_no_matches():
    blob_names = ["report.txt", "data.json", "archive.zip"]
    assert filter_blobs(blob_names, ".csv.gz") == []


def test_filter_blobs_mixed():
    blob_names = [
        "vmtable.csv.gz",
        "vm_cpu_readings.csv",
        "notes.txt",
        "trace_2017.csv.gz",
        "archive.gz",
    ]

    # Only files ending in the full ".csv.gz" suffix should match;
    # plain ".gz" or ".csv" must NOT be returned. This is the reason
    # endswith is the right primitive here rather than splitting on ".".
    assert filter_blobs(blob_names, ".csv.gz") == [
        "vmtable.csv.gz",
        "trace_2017.csv.gz",
    ]


def test_filter_blobs_preserves_order():
    blob_names = ["c.csv.gz", "a.csv.gz", "b.csv.gz"]
    assert filter_blobs(blob_names, ".csv.gz") == ["c.csv.gz", "a.csv.gz", "b.csv.gz"]


def test_filter_blobs_is_case_sensitive():
    # Documents the chosen behavior: filter_blobs is case-sensitive.
    # The public dataset uses lowercase ".csv.gz" so this is safe; we
    # surface the trade-off in the submission notes.
    blob_names = ["UPPER.CSV.GZ", "lower.csv.gz"]
    assert filter_blobs(blob_names, ".csv.gz") == ["lower.csv.gz"]


def test_filter_blobs_empty_extension_returns_empty():
    # Without this guard, "".endswith("") is True for every string, so
    # an empty extension would silently return the entire input. We
    # explicitly choose to return [] instead.
    assert filter_blobs(["a.csv.gz", "b.txt"], "") == []


def test_filter_blobs_accepts_generator():
    def gen():
        yield "one.csv.gz"
        yield "two.txt"
        yield "three.csv.gz"

    assert filter_blobs(gen(), ".csv.gz") == ["one.csv.gz", "three.csv.gz"]
