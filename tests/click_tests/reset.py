import shamir_mnemonic as shamir

from trezorlib import messages

from .. import buttons


def confirm_wait(debug, startswith):
    layout = debug.wait_layout()
    assert layout.text.startswith(startswith)
    debug.click(buttons.OK, wait=True)


def confirm_read(debug, startswith):
    layout = debug.read_layout()
    assert layout.text.startswith(startswith)
    debug.click(buttons.OK, wait=True)


def set_selection(debug, button, diff):
    layout = debug.read_layout()
    assert layout.text.startswith("Slip39NumInput")
    for _ in range(diff):
        debug.click(button, wait=False)
    debug.click(buttons.OK, wait=True)


def read_words(debug, is_advanced=False):
    words = []
    layout = debug.read_layout()
    if is_advanced:
        assert layout.text.startswith("Group")
    else:
        assert layout.text.startswith("Recovery share")
    for i in range(6):
        lines = debug.read_layout().lines
        if i == 0:
            words.append(lines[3].split()[1])
            words.append(lines[4].split()[1])
            debug.input(swipe=messages.DebugSwipeDirection.UP, wait=True)
        elif i == 5:
            words.append(lines[1].split()[1])
            words.append(lines[2].split()[1])
        else:
            words.append(lines[1].split()[1])
            words.append(lines[2].split()[1])
            words.append(lines[3].split()[1])
            words.append(lines[4].split()[1])
            debug.input(swipe=messages.DebugSwipeDirection.UP, wait=True)
    debug.press_yes()

    return words


def confirm_words(debug, words):
    # confirm words
    layout = debug.wait_layout()
    layout.text.startswith("Check share")
    for _ in range(3):
        word_pos = int(debug.state().layout_lines[1].split()[2])
        button_pos = debug.state().layout_lines.index(words[word_pos - 1]) - 2
        debug.click(buttons.RESET_WORD_CHECK[button_pos], wait=True)


def validate_mnemonics(mnemonics, expected_ems):
    # We expect these combinations to recreate the secret properly
    # In case of click tests the mnemonics are always XofX so no need for combinations
    ms = shamir.combine_mnemonics(mnemonics)
    identifier, iteration_exponent, _, _, _ = shamir._decode_mnemonics(mnemonics)
    ems = shamir._encrypt(ms, b"", iteration_exponent, identifier)
    assert ems == expected_ems