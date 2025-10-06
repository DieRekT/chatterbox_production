from pprint import pprint
from mps.settings_loader import resolve_settings


def main() -> None:
    s = resolve_settings()
    pprint(s.model_dump())


if __name__ == "__main__":
    main()

from mps.settings_loader import resolve_settings
from pprint import pprint

if __name__ == "__main__":
    s = resolve_settings()
    pprint(s.model_dump())
