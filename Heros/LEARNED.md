

# HEROS

| Hero | Gesture | Hero | Gesture |
|----|---------|----|---------|
| None | None (idle) | CAPTAIN AMERICA | Thumb_Up |
| HULK | Closed_Fist | THANOS | Thumb_Down |
| IRON MAN | Open_Palm | DOCTOR STRANGE | Victory |
| THOR | Pointing_Up | SPIDERMAN | ILoveYou |

## WHY
- If you are into electronics, there is a good chance that you thought/think Iron Man was cool. (That is at least the case for me!) This project is my way making an Iron Man project with my current growing skill level. This iteration of the project is to grow my ability to customize the experience like different hero names appear on the screen instead of the gesture title and in different colors. Also animation with the CPX neopixels. While there is an animation library for CPX, it takes up so much of the RAM that you can only import a few in the project before the HEAP is too full for all of blocks that need  consecutive data to be placed. But I didn't want to just animate 2 or 3. I wanted to animate all 7 of the gestures. So I manuallly made non-blocking polling gestures animations that are cheaper in RAM.

- I with the first gesture (Spiderman) to get it to update faster than 1 second. Then on the last gesture (Hulk), I ran out of RAM

## Expected Behavior
 - When the model recognizes a gesture the heros name and the model's confidence is displayed on the screen by cv2 and PILLOW
 - The CPX neopixels displays an animation

 ## Notes
 - Have the CPX plugged in before running the hero_sender.py so the program can recognize the COM_PORT, 
 - hero_sender program expects you know the data COM of your CPX and hardcode it in COM_PORT = "COM#"
 - The first hand the model identifies it will use in relation to the gestures, if you remove your hands from the computer's vision... 
    - the next hand appears will be used for the gestures

# Learned

## How to do manually non-blocking polling animations

- If the current gesture has not changed and the INTERVAL of time as pasted, run the function again with the index values updated
- Use time.monotonic(), which will return a float, time.time() will return a integer which will block the animations to update once a second and not the set INTERVAL
- It would be better to have a dictionary for each variable used in animation, however using global references is less RAM intense and I was barely able to make the 7 manual animations
- Make sure to clear the affects and indexes of the animations when the gesture changes

## RAM 

I was running out of RAM when on last animation HULK get

```
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:
MemoryError: memory allocation failed, allocating 376 bytes

Code done running.

Press any key to enter the REPL. Use CTRL-D to reload.
```


### CPX only has about 256 KB, and couldn't find a contiguous block of 376 bytes
Ways I went to reduce RAM
 - reduce comments and print statements
 - remove lambdas
 - dictionaries require overhead so globals > dictionaries
 - remove splice
 - turn the 2 big dictionaries to 1
 - import only the used function of random
 - Changed animations to be less RAM hungry like using a single index (like Hulk)

 ## Possible Improvements or Next Learn

- make a mpy file for the animations to have the code.py smaller and less RAM heavy overall
- Try dictionaries for each animation when use .mpy version
- Bluetooth communication instead of usbcdc so there doesn't have to be a wire
- Graphics that appear on screen in response to gestures
- Hand Tracking .task 

## PILLOW
- How to structure the dictionary to key to a tuple to have information for the name and color of the label that appears on the screen with PIL


