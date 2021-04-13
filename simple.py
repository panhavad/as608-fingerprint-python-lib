import time
import as608_lib

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
uart = serial.Serial("COM8", baudrate=9600, timeout=1)

finger = as608_lib.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != as608_lib.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != as608_lib.OK:
        return False
    print("Searching...")
    if finger.finger_search() != as608_lib.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="", flush=True)
    i = finger.get_image()
    if i == as608_lib.OK:
        print("Image taken")
    else:
        if i == as608_lib.NOFINGER:
            print("No finger detected")
        elif i == as608_lib.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == as608_lib.OK:
        print("Templated")
    else:
        if i == as608_lib.IMAGEMESS:
            print("Image too messy")
        elif i == as608_lib.FEATUREFAIL:
            print("Could not identify features")
        elif i == as608_lib.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == as608_lib.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == as608_lib.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
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
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == as608_lib.OK:
            print("Templated")
        else:
            if i == as608_lib.IMAGEMESS:
                print("Image too messy")
            elif i == as608_lib.FEATUREFAIL:
                print("Could not identify features")
            elif i == as608_lib.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != as608_lib.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == as608_lib.OK:
        print("Created")
    else:
        if i == as608_lib.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == as608_lib.OK:
        print("Stored")
    else:
        if i == as608_lib.BADLOCATION:
            print("Bad storage location")
        elif i == as608_lib.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != as608_lib.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num())
    if c == "f":
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger not found")
    if c == "d":
        if finger.delete_model(get_num()) == as608_lib.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
