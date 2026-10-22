"""Measure real loopback HTTP with ten signed-in sessions and inspect their ORM SQL."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from http.cookiejar import CookieJar
from math import ceil
from pathlib import Path
from threading import Barrier
from time import perf_counter
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPCookieProcessor, OpenerDirector, build_opener

from django.conf import settings
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from scripts.t24_fixture import BenchmarkFixture, SessionWorkload, require_benchmark_database


@dataclass(frozen=True)
class Sample:
    path: str
    seconds: float
    status: int


@dataclass(frozen=True)
class RouteResult:
    path: str
    samples: int
    failures: int
    p50_seconds: float
    p95_seconds: float
    maximum_seconds: float
    target_seconds: float


@dataclass(frozen=True)
class RouteProfile:
    path: str
    query_count: int
    sql_seconds: float
    plans: tuple[tuple[str, ...], ...]


def request_sample(opener: OpenerDirector, origin: str, path: str) -> Sample:
    started: float = perf_counter()
    try:
        with opener.open(origin + path, timeout=30) as response:
            response.read()
            status: int = response.status
    except HTTPError as error:
        error.read()
        status = error.code
        error.close()
    return Sample(path, perf_counter() - started, status)


def measure_session(
    session: SessionWorkload, password: str, origin: str, barrier: Barrier, waves: int
) -> tuple[Sample, ...]:
    cookies: CookieJar = CookieJar()
    opener: OpenerDirector = build_opener(HTTPCookieProcessor(cookies))
    with opener.open(origin + "/accounts/login/", timeout=30) as response:
        response.read()
    token: str = next(cookie.value for cookie in cookies if cookie.name == "csrftoken")
    form: bytes = urlencode(
        {
            "username": session.username,
            "password": password,
            "csrfmiddlewaretoken": token,
        }
    ).encode()
    with opener.open(origin + "/accounts/login/", form, timeout=30) as response:
        response.read()
        if response.status != 200 or response.geturl() != origin + session.routes[0]:
            raise RuntimeError(f"Benchmark login failed for fictional user {session.username}.")
    for path in session.routes:
        if request_sample(opener, origin, path).status != 200:
            raise RuntimeError(f"Benchmark warm-up failed for {path}.")
    samples: list[Sample] = []
    for wave in range(waves):
        barrier.wait(timeout=120)
        samples.append(request_sample(opener, origin, session.routes[wave % len(session.routes)]))
    return tuple(samples)


def summarize_routes(samples: tuple[Sample, ...]) -> tuple[RouteResult, ...]:
    results: list[RouteResult] = []
    for path in sorted({sample.path for sample in samples}):
        timings: list[float] = sorted(sample.seconds for sample in samples if sample.path == path)
        target: float = (
            3.0
            if path
            in {
                "/manage/",
                "/portal/",
                "/manage/reports/loans/",
                "/manage/reports/overdue/",
            }
            else 2.0
        )
        results.append(
            RouteResult(
                path,
                len(timings),
                sum(sample.status != 200 for sample in samples if sample.path == path),
                timings[ceil(len(timings) * 0.5) - 1],
                timings[ceil(len(timings) * 0.95) - 1],
                max(timings),
                target,
            )
        )
    return tuple(results)


def profile_routes(sessions: tuple[SessionWorkload, ...]) -> tuple[RouteProfile, ...]:
    """Inspect the three slowest captured SELECT plans per route outside the timed load."""
    profiles: list[RouteProfile] = []
    for session in (sessions[0], sessions[5]):
        client: Client = Client()
        from accounts.models import User

        client.force_login(User.objects.get(pk=session.user_id))
        for path in session.routes:
            with CaptureQueriesContext(connection) as captured:
                response = client.get(path, HTTP_HOST="127.0.0.1")
                if response.status_code != 200:
                    raise RuntimeError(
                        f"SQL profiling failed: {path} returned {response.status_code}."
                    )
            selects: list[str] = [
                query["sql"]
                for query in sorted(
                    captured.captured_queries,
                    key=lambda query: float(query["time"]),
                    reverse=True,
                )
                if query["sql"].startswith("SELECT")
            ][:3]
            plans: list[tuple[str, ...]] = []
            for statement in selects:
                with connection.cursor() as cursor:
                    cursor.execute("EXPLAIN (ANALYZE, BUFFERS) " + statement)
                    plans.append(tuple(row[0] for row in cursor.fetchall()))
            profiles.append(
                RouteProfile(
                    path,
                    len(captured),
                    sum(float(query["time"]) for query in captured.captured_queries),
                    tuple(plans),
                )
            )
    return tuple(profiles)


def run_load(fixture: BenchmarkFixture, origin: str, output: Path) -> None:
    """Write measured results even when an HTTP error or latency target fails."""
    require_benchmark_database()
    if urlsplit(origin).scheme != "http" or urlsplit(origin).hostname != "127.0.0.1":
        raise ValueError("T24 HTTP load is restricted to an explicit http://127.0.0.1 origin.")
    if len(fixture.sessions) != 10:
        raise ValueError("T24 requires exactly ten independent authenticated sessions.")
    if not output.resolve().is_relative_to((settings.BASE_DIR / "output").resolve()):
        raise ValueError("Keep T24 raw measurements under the ignored project output directory.")
    output.mkdir(parents=True, exist_ok=False)
    with connection.cursor() as cursor:
        cursor.execute("ANALYZE")
    barrier: Barrier = Barrier(10)
    waves: int = 20 * max(len(session.routes) for session in fixture.sessions)
    started: float = perf_counter()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = tuple(
            executor.submit(measure_session, session, fixture.password, origin, barrier, waves)
            for session in fixture.sessions
        )
        samples: tuple[Sample, ...] = tuple(
            sample for future in futures for sample in future.result()
        )
    elapsed: float = perf_counter() - started
    results: tuple[RouteResult, ...] = summarize_routes(samples)
    (output / "latency.json").write_text(
        json.dumps(
            {
                "elapsed_seconds_including_login_and_warmup": elapsed,
                "concurrent_sessions": 10,
                "synchronized_request_waves": waves,
                "requests_per_session": waves,
                "warmup_per_route_per_session": 1,
                "routes": [asdict(result) for result in results],
                "samples": [asdict(sample) for sample in samples],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    profiles: tuple[RouteProfile, ...] = profile_routes(fixture.sessions)
    (output / "sql-profiles.json").write_text(
        json.dumps([asdict(profile) for profile in profiles], indent=2),
        encoding="utf-8",
    )
    for result in results:
        print(
            f"{result.path}: n={result.samples}, p95={result.p95_seconds:.3f}s, failures={result.failures}",
            flush=True,
        )
    if any(result.failures or result.p95_seconds > result.target_seconds for result in results):
        raise RuntimeError(
            "T24 measured failures/target misses; inspect latency.json and SQL plans."
        )
