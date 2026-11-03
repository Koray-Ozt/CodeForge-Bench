#!/bin/sh
# Runs inside the sandbox container. Layout:
#   /in   read-only  repo/, tests/, bench/, candidate.patch (optional)
#   /work tmpfs      writable working copy
#   /out  bind mount results (junit.xml, output.log, patch.log, bench.json)
# Exit code 10 means the candidate patch did not apply; 70 is an internal error.
MODE="$1"
# Cap the size of any single file written (512-byte blocks, ~10 MB).
ulimit -f 20000

cp -r /in/repo /work/repo || exit 70
cd /work/repo || exit 70

if [ -f /in/candidate.patch ]; then
    git apply --verbose /in/candidate.patch >/out/patch.log 2>&1 || exit 10
fi

export PYTHONPATH=/work/repo PYTHONDONTWRITEBYTECODE=1 HOME=/tmp

case "$MODE" in
    test)
        # Tests are copied in only after patching and live outside the repo,
        # so a candidate cannot ship its own conftest.py next to them.
        cp -r /in/tests /work/_cf_tests || exit 70
        # Visible tests double as the shared helper location (e.g. support.py).
        export PYTHONPATH=/work/repo:/work/_cf_tests/visible
        python -m pytest /work/_cf_tests -p no:cacheprovider -q \
            --rootdir=/work/_cf_tests --import-mode=importlib \
            --junitxml=/out/junit.xml -o junit_family=xunit2 \
            >/out/output.log 2>&1
        exit $?
        ;;
    bench)
        python "/in/bench/$2" --out /out/bench.json >/out/output.log 2>&1
        exit $?
        ;;
    *)
        exit 70
        ;;
esac
