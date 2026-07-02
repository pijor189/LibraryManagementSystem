def pytest_addoption(parser):
    parser.addoption("--smoke", action="store_true")
    parser.addoption("--regression", action="store_true")
    parser.addoption("--nightly", action="store_true")
    parser.addoption("--stress", action="store_true")


def pytest_collection_modifyitems(config, items):
    markers = {
        "--smoke": {"smoke"},
        "--regression": {"smoke", "regression"},
        "--nightly": {"smoke", "regression", "nightly"},
        "--stress": {"stress"},
    }
    selected_markers = set()

    for option, marker in markers.items():
        if config.getoption(option):
            selected_markers.update(marker)

    if not selected_markers:
        return

    selected = []
    deselected = []

    for item in items:
        if selected_markers.intersection(item.keywords):
            selected.append(item)
        else:
            deselected.append(item)

    items[:] = selected
    config.hook.pytest_deselected(items=deselected)
