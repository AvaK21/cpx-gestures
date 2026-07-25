# HEROS


https://github.com/user-attachments/assets/f34ff3f5-212f-4096-b21a-2ea2c2a6bdf5


| Hero | Gesture | Hero | Gesture |
|----|---------|----|---------|
| None | None (idle) | CAPTAIN AMERICA | Thumb_Up |
| HULK | Closed_Fist | THANOS | Thumb_Down |
| IRON MAN | Open_Palm | DOCTOR STRANGE | Victory |
| THOR | Pointing_Up | SPIDERMAN | ILoveYou |

## WHY
- If you are into electronics, there is a good chance that you find Iron Man's technology inspiring. (That is at least the case for me!) This project is my way making Iron Man's Arc Reactor with my growing skill level. 
- This project iteration is to increase customization the experience 
   - Hero names in different colors appear on the screen 
   - Animation with the CPX neopixels. 

## Expected Behavior
 - When the model recognizes a gesture the heros name and the model's confidence is displayed on the screen by cv2 and PILLOW
 - The CPX neopixels displays an animation
 - Terminal of Hero sender with output the index of the Hero
 - Terminal of communication (not data) COM of CPX will print how many bytes are free after loading and right before going to main while True loop

 ## Notes
 - Have the CPX plugged in before running the hero_sender.py so the program can recognize the COM_PORT, 
 - hero_sender program expects you know the data COM of your CPX and hardcode it in COM_PORT = "COM#"
 - The first hand the model identifies will be used for the gesture model.
 - VS Code will have any warnings with from adafruit_circuitplayground import cp and the other imports because it can't see what the CPX has access to

 ## How to Run
 1. load boot.py on CPX and power cycle the CPX
 2. Load the code.py on CPX (so the COM#(s) is open)
 3. Run the hero_sender.py

# Learned


## How to do manually non-blocking polling animations

- If the current gesture has not changed and the INTERVAL of time as pasted, run the function again with the index values updated
- Use time.monotonic(), which will return a float, time.time() on CPX will return a integer which will block the animations to update once a second and not the set INTERVAL
- It would be better to have a dictionary for each animation, however using global references is less RAM intense and I was barely able to make the 7 manual animations
- Make sure to clear the affects and indexes of the animations when the gesture changes

## RAM 

There is an animation library for CPX, but it takes so much RAM... importing 2-3 animations can cause the HEAP is too full for all of consecutive data blocks to be placed. But I didn't want to just animate 2 or 3. I wanted to animate all 7 of the gestures. 
- So I manuallly made non-blocking polling gestures animations, which are cheaper in RAM. Then still, I had issue with RAM
- Instead of using the Animation Library, use non-blocking polling to animate
- I still ran out RAM in the process, like on the last gesture (Hulk), so I had to reduce RAM intensity of the program
- **32 KB of RAM**, after the system initiazation of a 2 line program: **15KB were left to use**

```   Only about 15KB is left after this program
 import gc

print(f"RAM free: {gc.mem_free()} bytes")

```

The error that would appear when the HEAP run out off memory

``` 
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:
MemoryError: memory allocation failed, allocating 376 bytes

Code done running.

Press any key to enter the REPL. Use CTRL-D to reload.
```

Use gc library to understand KB you have left in the RAM, and troubleshoot RAM issues. While gc.enable automatically collects garbage, 
intentional gc.collect after intensive RAM code could help

### CPX only has about 32 KB RAM, and couldn't find a contiguous block of 376 bytes

- ~17 KB is used for initialize a requirements of program:  ~15 KB to use in the program

Ways I went to reduce RAM
 - reduce comments and print statements
 - remove lambdas
 - dictionaries require overhead so globals > dictionaries
 - remove splice
 - turn the 2 big dictionaries to 1
 - import only the used function of random
 - **Changed animations to be less RAM hungry like using a single index (like Hulk)**

 

 ## Possible Improvements or Next Project

- make a mpy file for the animations to have the code.py smaller and less RAM heavy overall
- Try dictionaries for each animation when use .mpy version
- Bluetooth communication instead of usbcdc so there doesn't have to be a wire
- Graphics that appear on screen in response to gestures
- Hand Tracking .task 

## PILLOW
- How to structure the dictionary to key to a tuple to have information for the name and color of the label that appears on the screen with PIL


