import time
import as608_lib

import serial

#this is important to set baudrate of 115200 so there are no data lost
uart = serial.Serial("COM8", baudrate=115200, timeout=3)

finger = as608_lib.Operation(uart)

##################################################


def sensor_reset():
    """Reset sensor"""
    print("Resetting sensor...")
    if finger.soft_reset() != as608_lib.OK:
        print("Unable to reset sensor!")
    print("Sensor is reset.")


def fingerprint_check_file():
    """Compares a new fingerprint template to an existing template stored in a file
    This is useful when templates are stored centrally (i.e. in a database)"""
    print("Waiting for finger print...")
    # set_led_local(color=3, mode=1)
    while finger.get_image() != as608_lib.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != as608_lib.OK:
        return False

    print("Loading file template...", end="", flush=True)
    with open("template0.dat", "rb") as file:
        data = file.read()
    finger.send_fpdata(list(data), "char", 2)

    i = finger.compare_templates()
    if i == as608_lib.OK:
        # set_led_local(color=2, speed=150, mode=6)
        print("Fingerprint match template in file.")
        return True
    if i == as608_lib.NOMATCH:
        # set_led_local(color=1, mode=2, speed=20, cycles=10)
        print("Templates do not match!")
    else:
        print("Other error!")
    return False


# pylint: disable=too-many-statements
def enroll_save_to_file():
    """Take a 2 finger images and template it, then store it in a file"""
    # set_led_local(color=3, mode=1)
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == as608_lib.OK:
                print("Image taken")
                break
            if i == as608_lib.NOFINGER:
                print(".", end="", flush=True)
            elif i == as608_lib.IMAGEFAIL:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Imaging error")
                return False
            else:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == as608_lib.OK:
            print("Templated")
        else:
            if i == as608_lib.IMAGEMESS:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Image too messy")
            elif i == as608_lib.FEATUREFAIL:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Could not identify features")
            elif i == as608_lib.INVALIDIMAGE:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Image invalid")
            else:
                # set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            while i != as608_lib.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == as608_lib.OK:
        print("Created")
    else:
        if i == as608_lib.ENROLLMISMATCH:
            # set_led_local(color=1, mode=2, speed=20, cycles=10)
            print("Prints did not match")
        else:
            # set_led_local(color=1, mode=2, speed=20, cycles=10)
            print("Other error")
        return False

    print("Downloading template...")
    data = finger.get_fpdata("char", 1)
    with open("template0.dat", "wb") as file:
        file.write(bytearray(data))
    # set_led_local(color=2, speed=150, mode=6)
    print("Template is saved in template0.dat file.")

    return True


# pylint: disable=broad-except
# def set_led_local(color=1, mode=3, speed=0x80, cycles=0):
#     """this is to make sure LED doesn't interfer with example
#     running on models without LED support - needs testing"""
#     try:
#         finger.set_led(color, mode, speed, cycles)
#     except Exception as exc:
#         print("INFO: Sensor les not support LED. Error:", str(exc))


# set_led_local(color=3, mode=4, speed=10, cycles=10)
# set_led_local(mode=1)

while True:
    print("----------------")
    if finger.read_templates() != as608_lib.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates: ", finger.templates)
    if finger.count_templates() != as608_lib.OK:
        raise RuntimeError("Failed to read templates")
    print("Number of templates found: ", finger.template_count)
    if finger.set_sysparam(6, 2) != as608_lib.OK:
        raise RuntimeError("Unable to set package size to 128!")
    if finger.read_sysparam() != as608_lib.OK:
        raise RuntimeError("Failed to get system parameters")
    print("Package size (x128):", finger.data_packet_size)
    print("Size of template library: ", finger.library_size)
    print("e) enroll print and save to file")
    print("c) compare print to file")
    print("r) soft reset")
    print("x) quit")
    print("----------------")
    c = input("> ")

    if c in ("x", "q"):
        print("Exiting fingerprint example program")
        # turn off LED
        # set_led_local(mode=4)
        raise SystemExit
    if c == "e":
        enroll_save_to_file()
    elif c == "c":
        fingerprint_check_file()
    elif c == "r":
        sensor_reset()
    else:
        print("Invalid choice: Try again")
