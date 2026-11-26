# # BROKEN 


# from pins import *
# from time import sleep

# from apds9960.const import (
#     APDS9960_DIR_NONE,
#     APDS9960_DIR_LEFT,
#     APDS9960_DIR_RIGHT,
#     APDS9960_DIR_UP,
#     APDS9960_DIR_DOWN,
#     APDS9960_DIR_NEAR,
#     APDS9960_DIR_FAR,
# )

# dirs = {
#     APDS9960_DIR_NONE: "none",
#     APDS9960_DIR_LEFT: "left",
#     APDS9960_DIR_RIGHT: "right",
#     APDS9960_DIR_UP: "up",
#     APDS9960_DIR_DOWN: "down",
#     APDS9960_DIR_NEAR: "near",
#     APDS9960_DIR_FAR: "far",
# }

# def display_gesture():
#     motion = apds.readGesture()
#     display.fill(0)
#     display.text("GESTURE", 45, 20)
#     display.text("Gesture={}".format(dirs.get(motion, "unknown")), 5, 40)
#     display.show()

# async def gesture_menu():
#     print("--- GESTURE ---")
#     apds.setProximityIntLowThreshold(50)
#     apds.enableGestureSensor()
    
#     while True:
#         if MENU_BUTTON.value() == 0:
#             sleep(0.2)
#             return
#         if apds.isGestureAvailable():
#             display_gesture()
#         else:
#             print("No gesture detected")
#         sleep(1)