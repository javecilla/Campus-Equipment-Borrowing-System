"""Fictional campus activity from August through October 22, 2026."""

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from inventory.models import UnitCondition


@dataclass(frozen=True)
class RequestPlan:
    borrower: str
    purpose: str
    submitted_at: datetime
    due_date: date
    items: tuple[str, ...]


@dataclass(frozen=True)
class ReturnPlan:
    returned_at: datetime
    items: tuple[str, ...]
    condition: UnitCondition
    notes: str
    maintenance_problem: str


@dataclass(frozen=True)
class RepairPlan:
    item: str
    closed_at: datetime
    action: str


@dataclass(frozen=True)
class LoanPlan:
    request: RequestPlan
    issued_at: datetime
    returns: tuple[ReturnPlan, ...]
    repairs: tuple[RepairPlan, ...]


def campus_time(value: str) -> datetime:
    """Interpret this fixed fixture's ISO timestamps in the campus time zone."""
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Manila"))


def request_plan(
    borrower: str, purpose: str, submitted: str, due: str, items: tuple[str, ...]
) -> RequestPlan:
    return RequestPlan(borrower, purpose, campus_time(submitted), date.fromisoformat(due), items)


def completed_loan(
    borrower: str,
    purpose: str,
    submitted: str,
    issued: str,
    due: str,
    items: tuple[str, ...],
    returned: str,
    notes: str,
) -> LoanPlan:
    return LoanPlan(
        request_plan(borrower, purpose, submitted, due, items),
        campus_time(issued),
        (ReturnPlan(campus_time(returned), items, UnitCondition.GOOD, notes, ""),),
        (),
    )


PROJECTOR = "HDMI Projector"
SPEAKER = "Portable PA Speaker"
CAMERA = "DSLR Camera (Canon EOS)"
TRIPOD = "Adjustable Tripod"
LAPTOP = "Lenovo ThinkPad Laptop"
HUB = "USB-C Hub 7-in-1"
KEYBOARD = "Wireless Keyboard & Mouse Combo"
METER = "Digital Multimeter"
SOLDER = "Soldering Iron Station"

LOANS: tuple[LoanPlan, ...] = (
    completed_loan(
        "miguel.santos",
        "Student organization orientation sound system",
        "2026-08-06 08:30",
        "2026-08-07 09:00",
        "2026-08-10",
        (SPEAKER,),
        "2026-08-07 16:20",
        "Speaker returned with clear output; controls and power connection intact.",
    ),
    completed_loan(
        "sofia.reyes",
        "First-year study skills presentation",
        "2026-08-16 10:00",
        "2026-08-17 08:30",
        "2026-08-20",
        (PROJECTOR,),
        "2026-08-18 14:10",
        "Projected image checked on return; lens and housing clean.",
    ),
    completed_loan(
        "gabriel.cruz",
        "Programming fundamentals workshop demonstration",
        "2026-08-24 09:15",
        "2026-08-25 08:45",
        "2026-08-28",
        (LAPTOP, HUB),
        "2026-08-27 15:30",
        "Laptop and hub returned together; keyboard, ports and charging connection checked.",
    ),
    completed_loan(
        "isabella.garcia",
        "Student publication campus photo assignment",
        "2026-09-03 08:40",
        "2026-09-04 09:00",
        "2026-09-07",
        (CAMERA, TRIPOD),
        "2026-09-05 15:45",
        "Camera and tripod returned clean; tripod locks secure.",
    ),
    completed_loan(
        "daniel.navarro",
        "Research methods seminar presentation",
        "2026-09-09 09:30",
        "2026-09-10 08:30",
        "2026-09-13",
        (PROJECTOR, SPEAKER),
        "2026-09-11 16:00",
        "Equipment returned after the seminar; image and audio output stable.",
    ),
    completed_loan(
        "camille.torres",
        "Introductory electronics soldering practical",
        "2026-09-16 10:20",
        "2026-09-17 09:10",
        "2026-09-20",
        (SOLDER,),
        "2026-09-18 14:35",
        "Station returned cooled and unplugged; tip and power cord intact.",
    ),
    completed_loan(
        "rafael.ramos",
        "Capstone consultation and prototype demonstration",
        "2026-09-23 08:30",
        "2026-09-24 09:00",
        "2026-09-27",
        (LAPTOP, HUB),
        "2026-09-25 16:10",
        "Personal files removed; laptop and hub returned with working connections.",
    ),
    completed_loan(
        "alyssa.flores",
        "Campus heritage documentation photo session",
        "2026-10-01 09:10",
        "2026-10-02 08:45",
        "2026-10-05",
        (CAMERA, TRIPOD),
        "2026-10-03 15:20",
        "Camera and tripod checked on return; no new damage reported.",
    ),
    LoanPlan(
        request_plan(
            "miguel.santos",
            "Circuit measurements and soldering laboratory exercise",
            "2026-10-04 09:00",
            "2026-10-08",
            (METER, SOLDER),
        ),
        campus_time("2026-10-05 09:00"),
        (
            ReturnPlan(
                campus_time("2026-10-06 14:00"),
                (SOLDER,),
                UnitCondition.GOOD,
                "Station cooled before return; controls and cable intact.",
                "",
            ),
            ReturnPlan(
                campus_time("2026-10-06 14:05"),
                (METER,),
                UnitCondition.DAMAGED,
                "Probe insulation split near the connector; removed from borrowing stock for inspection.",
                "Test lead insulation is split near the probe connector; replace the damaged lead before reuse.",
            ),
        ),
        (
            RepairPlan(
                METER,
                campus_time("2026-10-08 15:00"),
                "Replaced the damaged test lead and checked continuity and resistance readings; returned to service.",
            ),
        ),
    ),
    completed_loan(
        "sofia.reyes",
        "Research proposal oral presentations",
        "2026-10-06 08:30",
        "2026-10-07 08:30",
        "2026-10-10",
        (PROJECTOR, SPEAKER),
        "2026-10-08 16:15",
        "Image and audio output checked; equipment returned after the final presentation.",
    ),
    completed_loan(
        "gabriel.cruz",
        "Spreadsheet skills practice and class demonstration",
        "2026-10-08 09:10",
        "2026-10-09 09:00",
        "2026-10-12",
        (LAPTOP, KEYBOARD),
        "2026-10-10 15:30",
        "Laptop, keyboard and mouse returned together; input devices responsive.",
    ),
    completed_loan(
        "isabella.garcia",
        "Photojournalism workshop field assignment",
        "2026-10-11 10:00",
        "2026-10-12 08:30",
        "2026-10-15",
        (CAMERA, TRIPOD),
        "2026-10-13 16:10",
        "Camera body and tripod inspected; no new scratches or loose locks.",
    ),
    completed_loan(
        "daniel.navarro",
        "Environmental awareness class reporting",
        "2026-10-13 08:30",
        "2026-10-14 09:00",
        "2026-10-17",
        (PROJECTOR,),
        "2026-10-15 14:45",
        "Projector returned after cooling; lens and connection ports intact.",
    ),
    completed_loan(
        "camille.torres",
        "Student leadership seminar audio support",
        "2026-10-14 09:20",
        "2026-10-15 08:40",
        "2026-10-18",
        (SPEAKER,),
        "2026-10-16 15:20",
        "Speaker powered on normally during the return check; volume controls responsive.",
    ),
    completed_loan(
        "rafael.ramos",
        "Capstone prototype review with faculty adviser",
        "2026-10-15 08:50",
        "2026-10-16 09:00",
        "2026-10-20",
        (LAPTOP, HUB),
        "2026-10-18 14:15",
        "Prototype files copied off; laptop and USB-C hub returned in good condition.",
    ),
    completed_loan(
        "alyssa.flores",
        "Electronics project assembly and testing",
        "2026-10-16 10:00",
        "2026-10-17 09:00",
        "2026-10-21",
        (METER, SOLDER),
        "2026-10-18 16:00",
        "Meter leads and soldering station checked; no additional defects found.",
    ),
    LoanPlan(
        request_plan(
            "miguel.santos",
            "Student publication feature interview photography",
            "2026-10-17 09:00",
            "2026-10-21",
            (CAMERA, TRIPOD),
        ),
        campus_time("2026-10-18 09:00"),
        (
            ReturnPlan(
                campus_time("2026-10-20 10:00"),
                (CAMERA,),
                UnitCondition.GOOD,
                "Camera returned clean; tripod retained to finish the interview setup.",
                "",
            ),
        ),
        (),
    ),
    LoanPlan(
        request_plan(
            "sofia.reyes",
            "Midterm presentation preparation and slide editing",
            "2026-10-18 15:30",
            "2026-10-21",
            (LAPTOP,),
        ),
        campus_time("2026-10-19 09:00"),
        (),
        (),
    ),
    LoanPlan(
        request_plan(
            "gabriel.cruz",
            "Department assembly audio support",
            "2026-10-20 09:00",
            "2026-10-24",
            (SPEAKER,),
        ),
        campus_time("2026-10-21 09:00"),
        (),
        (),
    ),
    LoanPlan(
        request_plan(
            "isabella.garcia",
            "Network topology and cable connectivity laboratory",
            "2026-10-22 08:00",
            "2026-10-26",
            ("TP-Link Wi-Fi Router", "5-Port Network Switch", "Cat6 Ethernet Cable (10m)"),
        ),
        campus_time("2026-10-22 09:00"),
        (),
        (),
    ),
)

REJECTED: tuple[tuple[RequestPlan, str], ...] = (
    (
        request_plan(
            "daniel.navarro",
            "Class documentary shoot for a proposed venue",
            "2026-10-06 10:00",
            "2026-10-10",
            (CAMERA,),
        ),
        "Venue booking was not confirmed; please resubmit once the schedule is approved.",
    ),
    (
        request_plan(
            "camille.torres",
            "Additional electronics laboratory practice session",
            "2026-10-13 09:00",
            "2026-10-17",
            (METER, SOLDER),
        ),
        "The additional laboratory session was cancelled by the class coordinator.",
    ),
)
CANCELLED: tuple[RequestPlan, ...] = (
    request_plan(
        "alyssa.flores",
        "Study group slide preparation in the library",
        "2026-10-10 09:00",
        "2026-10-14",
        (LAPTOP, HUB),
    ),
)
APPROVED_CANCELLATIONS: tuple[RequestPlan, ...] = (
    request_plan(
        "rafael.ramos",
        "Capstone consultation room presentation",
        "2026-10-19 09:00",
        "2026-10-23",
        (PROJECTOR,),
    ),
    request_plan(
        "alyssa.flores",
        "Campus event publicity photo session",
        "2026-10-20 12:00",
        "2026-10-24",
        (CAMERA,),
    ),
)
APPROVED: tuple[RequestPlan, ...] = (
    request_plan(
        "daniel.navarro",
        "Class project documentation scheduled for the weekend",
        "2026-10-21 09:00",
        "2026-10-25",
        (CAMERA,),
    ),
    request_plan(
        "camille.torres",
        "Research data cleaning and presentation preparation",
        "2026-10-21 10:00",
        "2026-10-26",
        (LAPTOP, HUB),
    ),
)
PENDING: tuple[RequestPlan, ...] = (
    request_plan(
        "rafael.ramos",
        "Circuit diagnostic practice before project assessment",
        "2026-10-22 08:10",
        "2026-10-26",
        (METER,),
    ),
    request_plan(
        "alyssa.flores",
        "Alumni feature photography and interview setup",
        "2026-10-22 08:20",
        "2026-10-26",
        (CAMERA, TRIPOD),
    ),
    request_plan(
        "miguel.santos",
        "Group reporting with interactive classroom discussion",
        "2026-10-22 08:30",
        "2026-10-26",
        ("Portable Whiteboard", "Wireless Presentation Clicker"),
    ),
)
