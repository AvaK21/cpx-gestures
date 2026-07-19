print top 

Top Category(index=-1, score=0.8898327350616455, display_name=None, category_name='Closed_Fist')
Top Category(index=-1, score=0.9159883856773376, display_name=None, category_name='Closed_Fist')
Top Category(index=-1, score=0.9189075827598572, display_name=None, category_name='Closed_Fist')
Top Category(index=-1, score=0.8499894738197327, display_name=None, category_name='Closed_Fist')
Top Category(index=-1, score=0.5669384002685547, display_name=None, category_name='None')
Top Category(index=-1, score=0.4751023054122925, display_name=None, category_name='None')

# Learned

## How to do manually non-blocking animations

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



