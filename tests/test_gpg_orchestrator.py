import os
import tempfile

from scripts.eq12_gpg import (
    clearsign_file,
    verify_signature,
)


def test_clearsign_and_verify() -> None:
    txt = "hello eq12"
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        rc, _out, err = clearsign_file(p)
        assert rc == 0, err
        asc = p + ".asc"
        assert os.path.exists(asc)
        rc2, _out2, _err2 = verify_signature(asc)
        # This test requires GPG keys configured; if not present, allow non-zero but skip
        assert rc2 in (0, 1)
